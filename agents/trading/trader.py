"""Trading strategy definition for NautilusTrader.

This module defines :class:`SmaCrossoverStrategy`, an example trading strategy
built for the NautilusTrader engine. The *StrategyAgent* is a lightweight
factory that instantiates strategy instances configured by upstream analysis
agents or user input.
"""

from dataclasses import dataclass
from typing import Any

from nautilus_trader.indicators.average.sma import SimpleMovingAverage
from nautilus_trader.model.enums import OrderSide, PriceType
from nautilus_trader.trading.strategy import Strategy


@dataclass
class SmaCrossoverConfig:
    """Configuration parameters for the SMA crossover strategy."""

    fast_period: int = 20
    slow_period: int = 50


class SmaCrossoverStrategy(Strategy):  # type: ignore[misc]  (baseclass at runtime)
    """Simple Moving Average crossover strategy."""

    config: SmaCrossoverConfig

    def __init__(self, config: SmaCrossoverConfig | None = None) -> None:  # noqa: D401
        super().__init__()
        self.config = config or SmaCrossoverConfig()
        self.fast_ma: SimpleMovingAverage | None = None
        self.slow_ma: SimpleMovingAverage | None = None

    # ------------------------------------------------------------------
    # Strategy lifecycle hooks
    # ------------------------------------------------------------------
    def on_start(self) -> None:  # noqa: D401
        self.fast_ma = SimpleMovingAverage(
            self.config.fast_period, price_type=PriceType.LAST
        )
        self.slow_ma = SimpleMovingAverage(
            self.config.slow_period, price_type=PriceType.LAST
        )

    def on_bar(self, bar) -> None:  # noqa: D401
        if self.fast_ma is None or self.slow_ma is None:
            return
        self.fast_ma.handle_bar(bar)
        self.slow_ma.handle_bar(bar)

        if not self.fast_ma.initialized or not self.slow_ma.initialized:
            return

        if self.fast_ma.value > self.slow_ma.value:
            self.emit_signal(OrderSide.BUY)
        elif self.fast_ma.value < self.slow_ma.value:
            self.emit_signal(OrderSide.SELL)


class StrategyAgent:
    """Factory agent for creating strategy instances for the backtester."""

    def create(self, *, config: dict[str, Any] | None = None) -> Strategy:  # type: ignore[override]
        """Return a :class:`Strategy` instance based on *config*."""
        cfg = SmaCrossoverConfig(**(config or {}))
        return SmaCrossoverStrategy(config=cfg)
