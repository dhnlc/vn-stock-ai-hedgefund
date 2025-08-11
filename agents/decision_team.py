"""Decision and risk management agents inspired by TradingAgents.

Implements a TraderAgent to synthesize debates into a decision, a RiskAgent to
assess risk, and a PortfolioManagerAgent to approve or reject the trade idea.
"""

from agno.tools.reasoning import ReasoningTools  # type: ignore

from utils.model_factory import build_default_model

from .base_agent import BaseAgent


class TraderAgent(BaseAgent):
    """Synthesizes research and debates into a trade plan."""

    def __init__(self) -> None:  # noqa: D401
        super().__init__(
            model=build_default_model(),
            tools=[ReasoningTools(add_instructions=True)],
            instructions=(
                "You are a trader. Given bullish and bearish debates, propose "
                "a clear action (BUY/SELL/HOLD), entry, stop, target, and a "
                "brief rationale (<=5 bullets)."
            ),
            name="trader-agent",
            agent_id="trader-agent",
            description="Trader decision agent",
            monitoring=False,
        )

    def decide(self, compiled_debates: str) -> str:
        return str(self("Trader decision:\n" + compiled_debates))  # type: ignore[operator]


class RiskAgent(BaseAgent):
    """Evaluates risk of the proposed trade plan."""

    def __init__(self) -> None:  # noqa: D401
        super().__init__(
            model=build_default_model(),
            tools=[ReasoningTools(add_instructions=True)],
            instructions=(
                "You are a risk manager. Assess downside risks, liquidity, "
                "gaps, and size constraints. Output pass/fail and key risks."
            ),
            name="risk-agent",
            agent_id="risk-agent",
            description="Risk management agent",
            monitoring=False,
        )

    def assess(self, trade_plan: str) -> str:
        return str(self("Risk review:\n" + trade_plan))  # type: ignore[operator]


class PortfolioManagerAgent(BaseAgent):
    """Approves or rejects trade plans based on risk and thesis quality."""

    def __init__(self) -> None:  # noqa: D401
        super().__init__(
            model=build_default_model(),
            tools=[ReasoningTools(add_instructions=True)],
            instructions=(
                "You are a portfolio manager. Decide APPROVE/REJECT with a "
                "2-sentence justification."
            ),
            name="pm-agent",
            agent_id="pm-agent",
            description="Portfolio manager agent",
            monitoring=False,
        )

    def approve(self, trade_plan_with_risk: str) -> str:
        return str(self("PM decision:\n" + trade_plan_with_risk))  # type: ignore[operator]
