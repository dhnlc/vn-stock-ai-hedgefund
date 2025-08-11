"""Helper utilities for computing technical indicators with *ta*.

For simplicity the module wraps common *ta* indicators and appends them to the
input ``pandas.DataFrame``. All columns are suffixed, avoiding collisions with
existing OHLCV fields.
"""

from typing import Sequence

import pandas as pd
import ta

_DEFAULT_INDICATORS: list[str] = [
    "sma",
    "ema",
    "rsi",
    "macd",
    "bbands",
    "atr",
    "adx",
    "stoch",
    "cci",
    "obv",
    "vwap",
]


def compute_indicators(
    ohlcv: pd.DataFrame, *, indicators: Sequence[str] | None = None
) -> pd.DataFrame:  # noqa: D401
    """Return *ohlcv* dataframe with extra technical indicator columns.

    Parameters
    ----------
    ohlcv : pandas.DataFrame
        Historical OHLCV data.
    indicators : Sequence[str] | None, optional
        Which indicators to compute, by default ``None`` (compute default set).

    Returns
    -------
    pandas.DataFrame
        New dataframe with additional columns.
    """

    if indicators is None:
        indicators = _DEFAULT_INDICATORS

    df = ohlcv.copy()

    if "sma" in indicators:
        df["SMA_20"] = ta.trend.sma_indicator(df["Close"], window=20)
    if "ema" in indicators:
        df["EMA_20"] = ta.trend.ema_indicator(df["Close"], window=20)
    if "rsi" in indicators:
        df["RSI_14"] = ta.momentum.rsi(df["Close"], window=14)
    if "macd" in indicators:
        macd = ta.trend.MACD(df["Close"])
        df["MACD"] = macd.macd()
        df["MACD_signal"] = macd.macd_signal()
    if "bbands" in indicators:
        bb = ta.volatility.BollingerBands(df["Close"])
        df["BB_high"] = bb.bollinger_hband()
        df["BB_low"] = bb.bollinger_lband()

    # Additional indicators (explicit column checks, no silent suppression)
    def _require(columns: list[str]) -> None:
        missing = [c for c in columns if c not in df.columns]
        if missing:
            raise ValueError(
                f"Missing required columns {missing} to compute indicators; have {list(df.columns)}"
            )

    if "atr" in indicators:
        _require(["High", "Low", "Close"])
        atr = ta.volatility.AverageTrueRange(
            df["High"], df["Low"], df["Close"], window=14
        )
        df["ATR_14"] = atr.average_true_range()

    if "adx" in indicators:
        _require(["High", "Low", "Close"])
        adx = ta.trend.ADXIndicator(df["High"], df["Low"], df["Close"], window=14)
        df["ADX_14"] = adx.adx()

    if "stoch" in indicators:
        _require(["High", "Low", "Close"])
        st = ta.momentum.StochasticOscillator(
            df["High"], df["Low"], df["Close"], window=14, smooth_window=3
        )
        df["STOCH_%K"] = st.stoch()
        df["STOCH_%D"] = st.stoch_signal()

    if "cci" in indicators:
        _require(["High", "Low", "Close"])
        cci = ta.trend.CCIIndicator(df["High"], df["Low"], df["Close"], window=20)
        df["CCI_20"] = cci.cci()

    if "obv" in indicators:
        _require(["Close", "Volume"])
        obv = ta.volume.OnBalanceVolumeIndicator(df["Close"], df["Volume"])
        df["OBV"] = obv.on_balance_volume()

    if "vwap" in indicators:
        _require(["High", "Low", "Close", "Volume"])
        vwap = ta.volume.VolumeWeightedAveragePrice(
            df["High"], df["Low"], df["Close"], df["Volume"], window=14
        )
        df["VWAP_14"] = vwap.volume_weighted_average_price()

    return df
