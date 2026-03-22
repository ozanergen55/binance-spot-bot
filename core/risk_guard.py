import json
import os
import datetime


DAILY_STATS_FILE = "daily_stats.json"


def _today():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def load_daily_stats():
    if not os.path.exists(DAILY_STATS_FILE):
        return {
            "date": _today(),
            "trade_count": 0,
            "realized_pnl": 0.0,
            "cooldowns": {}
        }

    try:
        with open(DAILY_STATS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        data = {
            "date": _today(),
            "trade_count": 0,
            "realized_pnl": 0.0,
            "cooldowns": {}
        }

    if data.get("date") != _today():
        data = {
            "date": _today(),
            "trade_count": 0,
            "realized_pnl": 0.0,
            "cooldowns": {}
        }

    return data


def save_daily_stats(data):
    with open(DAILY_STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def can_open_new_trade(max_daily_trades=3, max_daily_loss=-30.0):
    data = load_daily_stats()

    if data["trade_count"] >= max_daily_trades:
        return False, f"DAILY TRADE LIMIT REACHED ({data['trade_count']}/{max_daily_trades})"

    if data["realized_pnl"] <= max_daily_loss:
        return False, f"DAILY LOSS LIMIT REACHED ({data['realized_pnl']:.2f} <= {max_daily_loss:.2f})"

    return True, "OK"


def register_new_trade(symbol, cooldown_hours=6):
    data = load_daily_stats()
    data["trade_count"] += 1

    cooldown_until = datetime.datetime.now() + datetime.timedelta(hours=cooldown_hours)
    data["cooldowns"][symbol] = cooldown_until.strftime("%Y-%m-%d %H:%M:%S")

    save_daily_stats(data)


def is_symbol_on_cooldown(symbol):
    data = load_daily_stats()
    cooldowns = data.get("cooldowns", {})

    if symbol not in cooldowns:
        return False, ""

    try:
        cooldown_until = datetime.datetime.strptime(cooldowns[symbol], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return False, ""

    now = datetime.datetime.now()

    if now < cooldown_until:
        return True, cooldown_until.strftime("%Y-%m-%d %H:%M:%S")

    return False, ""


def register_closed_trade_pnl(symbol, pnl):
    data = load_daily_stats()
    data["realized_pnl"] += float(pnl)
    save_daily_stats(data)