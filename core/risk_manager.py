def build_trade_plan(entry_price, atr, stop_atr_multiplier=1.5, tp_atr_multiplier=2.5):
    stop_loss = entry_price - (atr * stop_atr_multiplier)
    take_profit = entry_price + (atr * tp_atr_multiplier)

    risk_amount = entry_price - stop_loss
    reward_amount = take_profit - entry_price

    if risk_amount == 0:
        rr_ratio = 0
    else:
        rr_ratio = reward_amount / risk_amount

    return {
        "entry_price": float(entry_price),
        "atr": float(atr),
        "stop_loss": float(stop_loss),
        "take_profit": float(take_profit),
        "risk_amount": float(risk_amount),
        "reward_amount": float(reward_amount),
        "rr_ratio": float(rr_ratio),
    }


def calculate_position_size(balance, risk_percent, entry_price, stop_loss):
    risk_amount = balance * risk_percent

    stop_distance = abs(entry_price - stop_loss)

    if stop_distance == 0:
        return {
            "balance": balance,
            "risk_percent": risk_percent,
            "risk_amount": risk_amount,
            "position_size": 0,
            "position_value": 0
        }

    position_size = risk_amount / stop_distance
    position_value = position_size * entry_price

    return {
        "balance": balance,
        "risk_percent": risk_percent,
        "risk_amount": risk_amount,
        "position_size": position_size,
        "position_value": position_value
    }