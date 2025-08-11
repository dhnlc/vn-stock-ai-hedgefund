"""Decision and risk management agents inspired by TradingAgents.

Implements a TraderAgent to synthesize debates into a decision, a RiskAgent to
assess risk, and a PortfolioManagerAgent to approve or reject the trade idea.
"""

from agno.team import Team
from agno.tools.reasoning import ReasoningTools  # type: ignore

from utils.model_factory import build_default_model

from ..base_agent import BaseAgent


class TraderAgent(BaseAgent):
    """Synthesizes research and debates into a trade plan."""

    def __init__(self) -> None:  # noqa: D401
        super().__init__(
            model=build_default_model(),
            tools=[ReasoningTools(add_instructions=True)],
            instructions=(
                'You are a trader. Given bullish and bearish debates, output a concise, structured plan in markdown. Use VND for all prices (thousands separators and "₫").\n\n'
                "### Decision\n"
                "- Action: BUY | SELL | HOLD\n"
                "- Entry: <VND (no rounding, VN quotes ×1000), e.g., 75,300 ₫>\n"
                "- Stop: <VND (no rounding), e.g., 71,000 ₫>\n"
                "- Target: <VND (no rounding), e.g., 80,500 ₫>\n"
                "- Rationale:\n"
                "  - bullet 1\n"
                "  - bullet 2\n"
                "- Confidence: <0..1>\n\n"
                "### Forward Plan (7/14/30/90 days)\n"
                "| Horizon (days) | Buy Level (VND) | Sell Level (VND) | Rationale |\n"
                "|---:|---:|---:|---|\n"
                "| 7 | <e.g., 74,800 ₫> | <e.g., 80,000 ₫> | <1 sentence> |\n"
                "| 14 | <e.g., 74,500 ₫> | <e.g., 81,500 ₫> | <1 sentence> |\n"
                "| 30 | <e.g., 73,800 ₫> | <e.g., 83,000 ₫> | <1 sentence> |\n"
                "| 90 | <e.g., 72,000 ₫> | <e.g., 86,000 ₫> | <1 sentence> |\n\n"
                "### Strategy\n"
                "- Primary Strategy: <e.g., Trend-following breakout / Swing / Mean reversion>\n"
                "- Playbook:\n"
                "  - bullet\n"
                "  - bullet\n"
            ),
            name="trader-agent",
            agent_id="trader-agent",
            description="Trader decision agent",
            monitoring=False,
        )

    def decide(self, compiled_debates: str) -> str:
        response = self("Trader decision:\n" + compiled_debates)  # type: ignore[operator]
        content = getattr(response, "content", None)
        return content if isinstance(content, str) else str(content or "")

    # Ensure orchestrator/team .run(...) returns clean content; accept extra kwargs
    def run(self, compiled_debates: str, **kwargs) -> str:  # type: ignore[override]
        response = super().run("Trader decision:\n" + compiled_debates, **kwargs)
        content = getattr(response, "content", None)
        return content if isinstance(content, str) else str(content or "")

    async def arun(self, compiled_debates: str) -> str:
        import asyncio as _asyncio

        response = await _asyncio.to_thread(
            super().run, "Trader decision:\n" + compiled_debates
        )
        content = getattr(response, "content", None)
        return content if isinstance(content, str) else str(content or "")


class RiskAgent(BaseAgent):
    """Evaluates risk of the proposed trade plan."""

    def __init__(self) -> None:  # noqa: D401
        super().__init__(
            model=build_default_model(),
            tools=[ReasoningTools(add_instructions=True)],
            instructions=(
                "You are a risk manager. Assess downside risks, liquidity, gaps, and size constraints.\n"
                "Return markdown as:\n\n"
                "### Risk Assessment\n"
                "- Status: PASS | FAIL\n"
                "- Key Risks:\n"
                "  - bullet 1\n"
                "  - bullet 2\n"
                "- Max Position Size: <percentage or units; if price is referenced, use VND e.g., 75,300 ₫>\n"
            ),
            name="risk-agent",
            agent_id="risk-agent",
            description="Risk management agent",
            monitoring=False,
        )

    def assess(self, trade_plan: str) -> str:
        return str(self("Risk review:\n" + trade_plan))  # type: ignore[operator]

    async def aassess(self, trade_plan: str) -> str:
        import asyncio as _asyncio

        response = await _asyncio.to_thread(self, "Risk review:\n" + trade_plan)
        content = getattr(response, "content", None)
        return content if isinstance(content, str) else str(content or "")


class PortfolioManagerAgent(BaseAgent):
    """Approves or rejects trade plans based on risk and thesis quality."""

    def __init__(self) -> None:  # noqa: D401
        super().__init__(
            model=build_default_model(),
            tools=[ReasoningTools(add_instructions=True)],
            instructions=(
                "You are a portfolio manager. Return a concise final call in markdown:\n\n"
                "### Final Decision\n"
                "- Decision: APPROVE | REJECT\n"
                "- Justification: <one or two sentences; any price levels MUST be in VND, e.g., 75,300 ₫>\n"
            ),
            name="pm-agent",
            agent_id="pm-agent",
            description="Portfolio manager agent",
            monitoring=False,
        )

    def approve(self, trade_plan_with_risk: str) -> str:
        return str(self("PM decision:\n" + trade_plan_with_risk))  # type: ignore[operator]

    async def aapprove(self, trade_plan_with_risk: str) -> str:
        import asyncio as _asyncio

        response = await _asyncio.to_thread(
            self, "PM decision:\n" + trade_plan_with_risk
        )
        content = getattr(response, "content", None)
        return content if isinstance(content, str) else str(content or "")


class DecisionTeam:
    """Container for the decision-making agents."""

    def __init__(self) -> None:
        self.trader_agent = TraderAgent()
        self.risk_agent = RiskAgent()
        self.pm_agent = PortfolioManagerAgent()
        # Use coordinate mode for ordered, role-specific contributions
        self.decision_team = Team(
            name="Decision Team",
            members=[self.trader_agent, self.risk_agent, self.pm_agent],
            mode="coordinate",
            show_members_responses=True,
            markdown=True,
            telemetry=False,
        )

    async def run(self, bull_case: str, bear_case: str, **kwargs) -> str:
        """Run the decision pipeline using Agno Team (coordinate mode).

        The team will synthesize a trader plan, perform risk assessment, and
        produce a PM decision in a single, structured markdown output.
        """
        compiled_debates = (
            f"## Bullish Case\n{bull_case}\n\n## Bearish Case\n{bear_case}"
        )

        team_prompt = (
            "You are the Decision Team (Trader, Risk Manager, Portfolio Manager).\n"
            "Work in order: Trader -> Risk -> PM. Produce ONE consolidated markdown output with these sections only:\n\n"
            "### Decision\n"
            "- Action: BUY | SELL | HOLD\n"
            "- Entry: <VND (no rounding, VN quotes ×1000), e.g., 75,300 ₫>\n"
            "- Stop: <VND (no rounding), e.g., 71,000 ₫>\n"
            "- Target: <VND (no rounding), e.g., 80,500 ₫>\n"
            "- Rationale:\n  - bullet 1\n  - bullet 2\n"
            "- Confidence: <0..1>\n\n"
            "### Forward Plan (7/14/30/90 days)\n"
            "| Horizon (days) | Buy Level (VND) | Sell Level (VND) | Rationale |\n"
            "|---:|---:|---:|---|\n"
            "| 7 | <e.g., 74,800 ₫> | <e.g., 80,000 ₫> | <1 sentence> |\n"
            "| 14 | <e.g., 74,500 ₫> | <e.g., 81,500 ₫> | <1 sentence> |\n"
            "| 30 | <e.g., 73,800 ₫> | <e.g., 83,000 ₫> | <1 sentence> |\n"
            "| 90 | <e.g., 72,000 ₫> | <e.g., 86,000 ₫> | <1 sentence> |\n\n"
            "### Risk Assessment\n"
            "- Status: PASS | FAIL\n"
            "- Key Risks:\n  - bullet\n  - bullet\n"
            "- Max Position Size: <percentage or units; if price referenced, VND>\n\n"
            "### Final Decision\n"
            "- Decision: APPROVE | REJECT\n"
            "- Justification: <one or two sentences>\n\n"
            "Do not include internal steps or tool calls.\n\n"
            f"Context:\n{compiled_debates}"
        )

        import asyncio as _asyncio

        response = await _asyncio.to_thread(
            self.decision_team.run, team_prompt, **kwargs
        )
        content = getattr(response, "content", None)
        return content if isinstance(content, str) else str(response)
