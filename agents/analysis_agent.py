"""Agent responsible for running technical analysis on OHLCV data.

This agent consumes a :class:`pandas.DataFrame` containing historical market
prices and computes a suite of technical indicators using the *ta* library.
It then explains the results leveraging the reasoning capabilities of the
underlying LLM via Agno.
"""

import asyncio
from functools import partial
from textwrap import dedent
from typing import Sequence

import pandas as pd
from agno.tools.reasoning import ReasoningTools  # type: ignore

from utils import technical_analysis as ta_utils
from utils.logging import log_markdown
from utils.model_factory import build_default_model

# Project imports
from .base_agent import BaseAgent


def _build_model() -> object:
    return build_default_model()


class AnalysisAgent(BaseAgent):
    """Agent that performs and explains technical analysis."""

    def __init__(self) -> None:
        expected_output = dedent(
            """
            A markdown-formatted technical analysis report:

            # Technical Analysis Report for {symbol}

            ## Latest Indicator Readings
            {indicator_table}

            ## Interpretation
            {analysis_summary}

            ---
            _Report generated on {current_date}_
            """
        )

        super().__init__(
            model=_build_model(),
            tools=[ReasoningTools(add_instructions=True)],
            instructions=(
                "You are an expert technical analyst. Compute relevant "
                "indicators and provide a concise explanation of market "
                "structure, trends and momentum. Where appropriate, include "
                "tables and bullet points."
            ),
            markdown=True,
            name="analysis-agent",
            agent_id="analysis-agent",
            description="LLM-powered technical analysis agent",
            monitoring=False,
            expected_output=expected_output,
            show_tool_calls=True,
            add_datetime_to_instructions=True,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def analyse(
        self, ohlcv: pd.DataFrame, *, indicators: Sequence[str] | None = None
    ) -> str:  # noqa: D401
        """Run technical analysis on *ohlcv* and return markdown explanation.

        Args:
            ohlcv: Historical OHLCV data.
            indicators: Optional subset of indicator names to compute. When
                *None*, a default indicator set (SMA, EMA, RSI, MACD, Bollinger
                Bands) is used.

        Returns
        -------
        str
            A markdown-formatted explanation ready for display or further
            processing by downstream agents.
        """
        # Compute indicators using the utility class
        enriched_df = ta_utils.compute_indicators(ohlcv, indicators=indicators)
        # Convert DataFrame (last row) to markdown table for the LLM
        latest = enriched_df.tail(1).T.reset_index()
        latest.columns = ["Indicator", "Value"]
        table_md = latest.to_markdown(index=False)  # type: ignore[arg-type]

        prompt = (
            "Given the following technical indicator readings for the most "
            "recent candle, explain the current market situation:\n\n" + table_md
        )
        log_markdown("## Indicator Snapshot\n\n" + table_md)
        response = self(prompt)  # type: ignore[operator]
        return str(response)

    async def aanalyse(
        self, ohlcv: pd.DataFrame, *, indicators: Sequence[str] | None = None
    ) -> str:
        enriched_df = await asyncio.to_thread(
            ta_utils.compute_indicators, ohlcv, indicators=indicators
        )
        latest = enriched_df.tail(1).T.reset_index()
        latest.columns = ["Indicator", "Value"]
        table_md = await asyncio.to_thread(partial(latest.to_markdown, index=False))
        prompt = (
            "Given the following technical indicator readings for the most "
            "recent candle, explain the current market situation:\n\n" + table_md
        )
        response = await asyncio.to_thread(self, prompt)  # type: ignore[operator]
        return str(response)
