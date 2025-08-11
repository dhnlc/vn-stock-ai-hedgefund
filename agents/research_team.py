"""Research team agents inspired by TradingAgents roles.

Implements Fundamentals, Sentiment, News, and Technical research agents, plus
Bullish/Bearish researchers who debate the findings.

Reference architecture: `TradingAgents` by TauricResearch
(`https://github.com/TauricResearch/TradingAgents`).
"""

from typing import Sequence

import pandas as pd
from agno.tools.reasoning import ReasoningTools  # type: ignore

from utils import technical_analysis as ta_utils
from utils.model_factory import build_default_model

from .base_agent import BaseAgent


class FundamentalsAgent(BaseAgent):
    """Agent focusing on company fundamentals given a ticker symbol."""

    def __init__(self) -> None:  # noqa: D401
        super().__init__(
            model=build_default_model(),
            tools=[ReasoningTools(add_instructions=True)],
            instructions=(
                "You are a fundamentals analyst. Given a VN equity ticker, "
                "outline key financial aspects to consider (growth, margins, "
                "leverage, cash flows) and list data you would seek. If data "
                "is not provided, infer cautiously and state assumptions."
            ),
            name="fundamentals-agent",
            agent_id="fundamentals-agent",
            description="Fundamentals analysis agent",
            monitoring=False,
        )

    def analyse(self, symbol: str) -> str:
        return str(self(f"Provide a concise fundamentals analysis plan for {symbol}."))  # type: ignore[operator]


class SentimentAgent(BaseAgent):
    """Agent focusing on market sentiment and crowd mood."""

    def __init__(self) -> None:  # noqa: D401
        super().__init__(
            model=build_default_model(),
            tools=[ReasoningTools(add_instructions=True)],
            instructions=(
                "You are a sentiment analyst. Summarize likely investor "
                "sentiment drivers for the ticker from social and news, "
                "noting uncertainty when data is not provided."
            ),
            name="sentiment-agent",
            agent_id="sentiment-agent",
            description="Sentiment analysis agent",
            monitoring=False,
        )

    def analyse(self, symbol: str) -> str:
        return str(self(f"Summarize sentiment drivers and risks for {symbol}."))  # type: ignore[operator]


class NewsAgent(BaseAgent):
    """Agent focusing on macro/news catalysts impacting the ticker."""

    def __init__(self) -> None:  # noqa: D401
        super().__init__(
            model=build_default_model(),
            tools=[ReasoningTools(add_instructions=True)],
            instructions=(
                "You are a news analyst. Identify plausible macro/company "
                "catalysts, potential scenarios and how they might affect the "
                "ticker. Note assumptions explicitly."
            ),
            name="news-agent",
            agent_id="news-agent",
            description="News & macro analysis agent",
            monitoring=False,
        )

    def analyse(self, symbol: str) -> str:
        return str(self(f"Outline likely news/macro catalysts for {symbol}."))  # type: ignore[operator]


class TechnicalResearchAgent(BaseAgent):
    """Agent that computes indicators and frames a technical narrative."""

    def __init__(self) -> None:  # noqa: D401
        super().__init__(
            model=build_default_model(),
            tools=[ReasoningTools(add_instructions=True)],
            instructions=(
                "You are a technical analyst. Interpret the technical "
                "indicators provided and describe trend, momentum, support/"
                "resistance, and risk. Be concise."
            ),
            name="technical-research-agent",
            agent_id="technical-research-agent",
            description="Technical analysis agent (research team)",
            monitoring=False,
        )

    def analyse(
        self, ohlcv: pd.DataFrame, *, indicators: Sequence[str] | None = None
    ) -> str:
        enriched = ta_utils.compute_indicators(ohlcv, indicators=indicators)
        latest = enriched.tail(1).T.reset_index()
        latest.columns = ["Indicator", "Value"]
        table = latest.to_markdown(index=False)  # type: ignore[arg-type]
        prompt = (
            "Given the following indicator readings for the most recent candle, "
            "provide a short technical view and key levels.\n\n" + table
        )
        return str(self(prompt))  # type: ignore[operator]


class BullishResearcher(BaseAgent):
    """Bullish researcher debating for long bias."""

    def __init__(self) -> None:  # noqa: D401
        super().__init__(
            model=build_default_model(),
            tools=[ReasoningTools(add_instructions=True)],
            instructions=(
                "You argue for a bullish case using the team reports. "
                "Acknowledge risks. Provide a 3-bullet summary."
            ),
            name="bullish-researcher",
            agent_id="bullish-researcher",
            description="Bullish researcher",
            monitoring=False,
        )

    def debate(self, compiled_report: str) -> str:
        return str(self("Bullish case:\n" + compiled_report))  # type: ignore[operator]


class BearishResearcher(BaseAgent):
    """Bearish researcher debating for short/defensive bias."""

    def __init__(self) -> None:  # noqa: D401
        super().__init__(
            model=build_default_model(),
            tools=[ReasoningTools(add_instructions=True)],
            instructions=(
                "You argue for a bearish case using the team reports. "
                "Acknowledge opportunities. Provide a 3-bullet summary."
            ),
            name="bearish-researcher",
            agent_id="bearish-researcher",
            description="Bearish researcher",
            monitoring=False,
        )

    def debate(self, compiled_report: str) -> str:
        return str(self("Bearish case:\n" + compiled_report))  # type: ignore[operator]
