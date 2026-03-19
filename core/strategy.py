def check_buy_signal(df):
    last = df.iloc[-1]

    trend_ok = last["ema20"] > last["ema50"]
    momentum_ok = last["close"] > last["ema20"]
    rsi_ok = last["rsi"] > 52
    adx_ok = last["adx"] > 18
    volume_ok = last["volume"] > last["vol_ma20"]

    signal = trend_ok and momentum_ok and rsi_ok and adx_ok and volume_ok

    debug = {
        "close": float(last["close"]),
        "ema20": float(last["ema20"]),
        "ema50": float(last["ema50"]),
        "ema200": float(last["ema200"]),
        "rsi": float(last["rsi"]),
        "atr": float(last["atr"]),
        "adx": float(last["adx"]),
        "volume": float(last["volume"]),
        "vol_ma20": float(last["vol_ma20"]),
        "trend_ok": trend_ok,
        "momentum_ok": momentum_ok,
        "rsi_ok": rsi_ok,
        "volume_ok": volume_ok,
        "adx_ok": adx_ok,
    }

    return signal, debug