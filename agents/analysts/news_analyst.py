from agno.tools.googlesearch import GoogleSearchTools

from utils.model_factory import build_default_model

from ..base_agent import BaseAgent
from ..tools import vn_company_overview


class NewsAnalyst(BaseAgent):
    """Analyzes news articles for sentiment and impact."""

    def __init__(self) -> None:  # noqa: D401
        super().__init__(
            model=build_default_model(),
            tools=[GoogleSearchTools(), vn_company_overview],
            instructions=(
                "You are a sharp News Analyst. Search for and summarize recent headlines for a stock "
                "and assess their likely impact and sentiment (Bullish/Bearish/Neutral)."
            ),
            name="news-analyst",
            agent_id="news-analyst",
            description="News analyst",
            monitoring=False,
        )
