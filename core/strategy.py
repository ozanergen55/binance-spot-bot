def check_buy_signal(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]

    # 1) Trend
    trend_ok = last["ema20"] > last["ema50"]

    # 2) Pullback: fiyat EMA20 altına ya da çok yakınına gelmiş olsun
    pullback_ok = last["close"] <= last["ema20"] * 1.003

    # 3) RSI düşükten toparlanıyor olsun
    rsi_zone_ok = 35 <= last["rsi"] <= 50
    rsi_recover_ok = last["rsi"] > prev["rsi"]

    # 4) VWAP çevresinde olsun (çok yukarı kaçmış olmasın)
    vwap_ok = last["close"] <= last["vwap"] * 1.01

    # 5) Bollinger alt banda yakın veya altından toparlanıyor olsun
    bb_ok = last["close"] <= last["bb_mid"] and last["close"] >= last["bb_low"] * 0.98

    # 6) Hacim tamamen ölü olmasın
    volume_ok = last["volume"] >= last["vol_ma20"] * 0.8

    conditions = [
        trend_ok,
        pullback_ok,
        rsi_zone_ok,
        rsi_recover_ok,
        vwap_ok,
        bb_ok,
        volume_ok,
    ]

    score = sum(conditions)

    # 7 koşuldan en az 5'i sağlanırsa al
    signal = score >= 5

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
        "vwap": float(last["vwap"]),
        "bb_low": float(last["bb_low"]),
        "bb_mid": float(last["bb_mid"]),
        "bb_high": float(last["bb_high"]),
        "trend_ok": trend_ok,
        "pullback_ok": pullback_ok,
        "rsi_zone_ok": rsi_zone_ok,
        "rsi_recover_ok": rsi_recover_ok,
        "vwap_ok": vwap_ok,
        "bb_ok": bb_ok,
        "volume_ok": volume_ok,
        "score": score,
    }

    return signal, debug