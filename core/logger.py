from datetime import datetime


LOG_FILE = "trade_log.csv"


def log_trade(
    symbol,
    entry_price,
    quantity,
    take_profit,
    stop_price,
    stop_limit_price,
    buy_order_id,
    oco_order_list_id,
    status
):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    row = (
        f"{timestamp},"
        f"{symbol},"
        f"{entry_price},"
        f"{quantity},"
        f"{take_profit},"
        f"{stop_price},"
        f"{stop_limit_price},"
        f"{buy_order_id},"
        f"{oco_order_list_id},"
        f"{status}\n"
    )

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(row)