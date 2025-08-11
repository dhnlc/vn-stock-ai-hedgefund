"""Backtest agent using Backtesting.py (lightweight alternative to NautilusTrader)."""

from typing import Any, Callable

import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover


class _SMAStrategy(Strategy):
    n_fast = 20
    n_slow = 50

    def init(self):  # noqa: D401
        close = pd.Series(self.data.Close)
        self.sma_fast = self.I(close.rolling(self.n_fast).mean)
        self.sma_slow = self.I(close.rolling(self.n_slow).mean)

    def next(self):  # noqa: D401
        if crossover(self.sma_fast, self.sma_slow):
            self.position.close()
            self.buy()
        elif crossover(self.sma_slow, self.sma_fast):
            self.position.close()
            self.sell()


class BacktestAgent:
    """Run a backtest over OHLCV using Backtesting.py.

    If `strategy_fn` is provided, it should return a subclass of backtesting.Strategy.
    """

    def __init__(self, strategy_fn: Callable[[], type[Strategy]] | None = None) -> None:  # noqa: D401
        self._strategy_fn = strategy_fn or (lambda: _SMAStrategy)

    def run(
        self, ohlcv: pd.DataFrame, *, strategy_config: dict[str, Any] | None = None
    ) -> dict[str, Any]:  # noqa: D401
        if not isinstance(ohlcv.index, pd.DatetimeIndex):
            ohlcv = ohlcv.copy()
            ohlcv.index = pd.to_datetime(ohlcv.index)

        strategy_cls = self._strategy_fn()
        bt = Backtest(ohlcv, strategy_cls, cash=100_000, commission=0.001)
        stats = bt.run()
        return dict(stats)
