from agno.agent import Agent

from ..base_agent import BaseAgent


class PortfolioManager(BaseAgent):
    """Approves or rejects trading plans based on risk and potential."""

    def __init__(self):  # noqa: D107
        self._agent = Agent(
            system_message=(
                "You are the Portfolio Manager. Your decision is final. "
                "You must weigh the potential rewards of the trading plan against the risks "
                "identified by the Risk Manager. Provide a clear 'APPROVE' or 'REJECT' decision "
                "with a brief, decisive justification."
            )
        )

    def run(self, trade_plan: str) -> str:
        """Makes the final trade decision."""
        user_prompt = (
            "Here is the trading plan. "
            "Please make a final decision.\n\n"
            f"--- TRADE PLAN ---\n{trade_plan}"
        )
        response = self._agent.run(user_prompt)
        return response.content or "No content"
