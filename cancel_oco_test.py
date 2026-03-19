from core.binance_client import BinanceClient
from core.position_store import load_positions


def main():
    client = BinanceClient()
    positions = load_positions()

    if "BTCUSDT" not in positions:
        print("BTCUSDT için açık pozisyon kaydı yok.")
        return

    position = positions["BTCUSDT"]
    order_list_id = position.get("oco_order_list_id")
    symbol = position.get("symbol", "BTCUSDT")

    if not order_list_id:
        print("BTCUSDT için OCO orderListId bulunamadı.")
        return

    result = client.cancel_oco_order(symbol, order_list_id)
    print("OCO CANCEL RESULT")
    print(result)


if __name__ == "__main__":
    main()