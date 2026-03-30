import pandas as pd
import ta


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # EMA
    df["ema20"] = ta.trend.ema_indicator(df["close"], window=20)
    df["ema50"] = ta.trend.ema_indicator(df["close"], window=50)
    df["ema200"] = ta.trend.ema_indicator(df["close"], window=200)

    # RSI
    df["rsi"] = ta.momentum.rsi(df["close"], window=14)

    # ATR
    df["atr"] = ta.volatility.average_true_range(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        window=14
    )

    # ADX
    df["adx"] = ta.trend.adx(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        window=14
    )

    # Volume MA
    df["vol_ma20"] = df["volume"].rolling(window=20).mean()

    # VWAP
    typical_price = (df["high"] + df["low"] + df["close"]) / 3
    cumulative_tpv = (typical_price * df["volume"]).cumsum()
    cumulative_volume = df["volume"].cumsum()
    df["vwap"] = cumulative_tpv / cumulative_volume

    # Bollinger Bands
    bb = ta.volatility.BollingerBands(df["close"], window=20, window_dev=2)
    df["bb_high"] = bb.bollinger_hband()
    df["bb_mid"] = bb.bollinger_mavg()
    df["bb_low"] = bb.bollinger_lband()

    return df