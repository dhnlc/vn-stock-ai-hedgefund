"""Research team using Agno Team in coordinate mode.

We form an Agno `Team` of fundamentals, sentiment and news agents which
coordinates a unified research synthesis. A technical snapshot is computed and
provided as context. The synthesis is then debated by bullish/bearish
researchers.
"""

from __future__ import annotations

import asyncio
from typing import Sequence

import pandas as pd
from agno.team import Team
from agno.tools.reasoning import ReasoningTools  # type: ignore

from utils import technical_analysis as ta_utils
from utils.logging import log_info
from utils.model_factory import build_default_model

from ..base_agent import BaseAgent


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
        resp = super().run(
            f"Provide a concise fundamentals analysis plan for {symbol}."
        )
        content = getattr(resp, "content", None)
        return content if isinstance(content, str) else str(content or "")


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
        resp = super().run(f"Summarize sentiment drivers and risks for {symbol}.")
        content = getattr(resp, "content", None)
        return content if isinstance(content, str) else str(content or "")


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
        resp = super().run(f"Outline likely news/macro catalysts for {symbol}.")
        content = getattr(resp, "content", None)
        return content if isinstance(content, str) else str(content or "")


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
        resp = super().run(prompt)
        content = getattr(resp, "content", None)
        return content if isinstance(content, str) else str(content or "")


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

    def debate(self, compiled_report: str, **kwargs) -> str:
        resp = super().run("Bullish case:\n" + compiled_report, **kwargs)
        content = getattr(resp, "content", None)
        return content if isinstance(content, str) else str(content or "")


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

    def debate(self, compiled_report: str, **kwargs) -> str:
        resp = super().run("Bearish case:\n" + compiled_report, **kwargs)
        content = getattr(resp, "content", None)
        return content if isinstance(content, str) else str(content or "")


class ResearchTeam:
    """Research team orchestrated via Agno `Team` (coordinate mode)."""

    def __init__(self) -> None:
        # Specialists
        self.fundamentals_agent = FundamentalsAgent()
        self.sentiment_agent = SentimentAgent()
        self.news_agent = NewsAgent()
        self.technical_agent = TechnicalResearchAgent()

        # Agno Team for coordinated synthesis
        self.team = Team(
            name="Research Team",
            mode="coordinate",
            members=[
                self.fundamentals_agent,
                self.sentiment_agent,
                self.news_agent,
            ],
            show_members_responses=False,
            markdown=True,
            telemetry=False,
        )

        # Debate agents
        self.bullish_researcher = BullishResearcher()
        self.bearish_researcher = BearishResearcher()

    async def run(self, symbol: str, ohlcv: pd.DataFrame) -> tuple[str, str]:
        """Run the full research and debate pipeline.

        Args:
            symbol: Ticker symbol for the equity.
            ohlcv: Historical OHLCV data.

        Returns
        -------
        tuple[str, str]
            A tuple containing the bullish and bearish arguments.
        """
        # 1. Compute technical snapshot to provide context to the team
        log_info("[ResearchTeam] Computing technical snapshot for context...")
        enriched = await asyncio.to_thread(ta_utils.compute_indicators, ohlcv)
        latest = enriched.tail(1).T.reset_index()
        latest.columns = ["Indicator", "Value"]
        tech_table = latest.to_markdown(index=False)  # type: ignore[arg-type]

        # 2. Run coordinated synthesis via Agno Team
        log_info("[ResearchTeam] Running coordinated synthesis via Agno Team...")
        team_prompt = (
            f"You are a financial research team analyzing {symbol}.\n"
            f"Coordinate among members to produce a concise synthesis with this exact structure (markdown):\n\n"
            "### Synthesis\n"
            "- Fundamentals: <2 short bullets>\n"
            "- Sentiment: <2 short bullets>\n"
            "- News/Catalysts: <2 short bullets>\n\n"
            "### Key Risks\n"
            "- bullet\n- bullet\n\n"
            "### Watchlist\n"
            "- bullet\n- bullet\n\n"
            "Do not include any internal steps or tool metadata.\n\n"
            f"Technical Snapshot (latest):\n{tech_table}"
        )
        team_response = await asyncio.to_thread(self.team.run, team_prompt)
        team_text = getattr(team_response, "content", None)
        team_text_str = (
            team_text if isinstance(team_text, str) else str(team_text or "")
        )

        compiled_report = f"--- Team Synthesis ---\n{team_text_str}\n\n--- Technicals (latest) ---\n{tech_table}"

        # 3. Debate
        log_info("[ResearchTeam] Running bull/bear debate...")
        bull_case, bear_case = await asyncio.gather(
            asyncio.to_thread(self.bullish_researcher.debate, compiled_report),
            asyncio.to_thread(self.bearish_researcher.debate, compiled_report),
        )

        return bull_case, bear_case
