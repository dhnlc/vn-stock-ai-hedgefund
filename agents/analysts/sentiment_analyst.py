from agno.tools.googlesearch import GoogleSearchTools

from utils.model_factory import build_default_model

from ..base_agent import BaseAgent
from ..tools import vn_company_overview


class SentimentAnalyst(BaseAgent):
    """Analyzes social media sentiment using web searches."""

    def __init__(self) -> None:  # noqa: D401
        super().__init__(
            model=build_default_model(),
            tools=[GoogleSearchTools(fixed_language="vi"), vn_company_overview],
            instructions=(
                "You are a Social Media Sentiment Analyst. Gauge market mood by searching social sources "
                "and summarize sentiment (Bullish/Bearish/Neutral)."
            ),
            name="sentiment-analyst",
            agent_id="sentiment-analyst",
            description="Sentiment analyst",
            monitoring=False,
        )
