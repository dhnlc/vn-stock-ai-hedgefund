"""Base classes for building trading strategies.

Inspired by the `TradingAgents` project by Tauric Research.
"""

from typing import Any


class Strategy:
    """Base class for all trading strategies."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}


class StrategyAgent:
    """Agent responsible for creating strategy instances."""

    def create(self, config: dict[str, Any] | None = None) -> Strategy:
        """Factory method to build a new strategy."""
        return Strategy(config=config)
