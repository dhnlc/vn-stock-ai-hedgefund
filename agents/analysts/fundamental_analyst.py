from agno.tools.googlesearch import GoogleSearchTools

from utils.model_factory import build_default_model

from ..base_agent import BaseAgent
from ..tools import vn_company_overview, vn_finance_report


class FundamentalAnalyst(BaseAgent):
    """Analyzes company financials and fundamentals (Agno Agent)."""

    def __init__(self) -> None:  # noqa: D401
        super().__init__(
            model=build_default_model(),
            tools=[GoogleSearchTools(), vn_company_overview, vn_finance_report],
            instructions=(
                "You are a meticulous Fundamental Analyst for a trading firm. "
                "Analyze company's financial health (P/E, D/E, growth, margins, cash flows). "
                "Use tools when needed. Return a concise data-driven summary and a Bullish/Bearish/Neutral view."
            ),
            name="fundamental-analyst",
            agent_id="fundamental-analyst",
            description="Fundamentals analyst",
            monitoring=False,
        )
