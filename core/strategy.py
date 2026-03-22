def check_buy_signal(df):
    last = df.iloc[-1]

    trend_ok = last["ema20"] > last["ema50"]
    momentum_ok = last["close"] > last["ema20"]
    rsi_ok = last["rsi"] > 48
    adx_ok = last["adx"] > 15
    volume_ok = last["volume"] > last["vol_ma20"] * 0.8

    conditions = [trend_ok, momentum_ok, rsi_ok, adx_ok, volume_ok]
    score = sum(conditions)

    signal = score >= 4

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
        "score": score,
    }

    return signal, debug