from core.binance_client import BinanceClient


def main():
    client = BinanceClient()

    sell_result = client.market_sell(
        symbol="BTCUSDT",
        quantity="0.00028"
    )

    print("MANUAL SELL TEST")
    print(sell_result)


if __name__ == "__main__":
    main()