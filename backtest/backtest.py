from config import INTERVAL, CANDLE_LIMIT
from core.binance_client import BinanceClient
from core.market_data import klines_to_dataframe
from core.indicators import add_indicators


# Agresif test için coinler
SYMBOLS = ["BTCUSDT", "SOLUSDT", "ETHUSDT"]


def check_signal_on_row(row):
    trend_ok = row["ema20"] > row["ema50"]
    momentum_ok = row["close"] > row["ema20"]
    rsi_ok = row["rsi"] > 52
    adx_ok = row["adx"] > 18

    # Volume filtresini şimdilik kaldırıyoruz: volume_ok = True
    volume_ok = row["volume"] > row["vol_ma20"]  # geri açma

    return trend_ok and momentum_ok and rsi_ok and adx_ok and volume_ok


def run_backtest_for_symbol(client, symbol):
    print(f"\nBACKTEST STARTED: {symbol}")
    print("-" * 70)

    klines = client.get_klines(symbol, INTERVAL, CANDLE_LIMIT)
    df = klines_to_dataframe(klines)
    df = add_indicators(df)
    df = df.dropna().reset_index(drop=True)

    initial_balance = 1000.0
    balance = initial_balance
    risk_per_trade = 0.01

    total_trades = 0
    winning_trades = 0
    losing_trades = 0

    in_position = False
    entry_price = 0.0
    stop_price = 0.0
    take_profit_price = 0.0
    quantity = 0.0

    trade_history = []

    for i in range(1, len(df)):
        row = df.iloc[i]

        if not in_position:
            signal = check_signal_on_row(row)

            if signal:
                entry_price = float(row["close"])
                atr = float(row["atr"])

                # Daha agresif çıkış planı
                stop_price = entry_price - (1.2 * atr)
                take_profit_price = entry_price + (1.8 * atr)

                stop_distance = entry_price - stop_price
                if stop_distance <= 0:
                    continue

                risk_amount_usdt = balance * risk_per_trade
                quantity = risk_amount_usdt / stop_distance

                in_position = True
                total_trades += 1

                trade_history.append({
                    "type": "BUY",
                    "time": str(row["open_time"]),
                    "price": entry_price,
                    "atr": atr,
                    "stop_price": stop_price,
                    "take_profit_price": take_profit_price
                })

        else:
            low_price = float(row["low"])
            high_price = float(row["high"])

            exit_price = None
            result = None

            # Aynı mumda ikisi birden değerse önce stop kabul ediyoruz
            if low_price <= stop_price:
                exit_price = stop_price
                result = "LOSS"
            elif high_price >= take_profit_price:
                exit_price = take_profit_price
                result = "WIN"

            if exit_price is not None:
                pnl = (exit_price - entry_price) * quantity
                balance += pnl

                if result == "WIN":
                    winning_trades += 1
                else:
                    losing_trades += 1

                trade_history.append({
                    "type": "SELL",
                    "time": str(row["open_time"]),
                    "price": exit_price,
                    "result": result,
                    "pnl": float(pnl),
                    "balance": float(balance)
                })

                in_position = False
                entry_price = 0.0
                stop_price = 0.0
                take_profit_price = 0.0
                quantity = 0.0

    net_profit = balance - initial_balance
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0

    print(f"Initial Balance : {initial_balance:.2f}")
    print(f"Final Balance   : {balance:.2f}")
    print(f"Net Profit      : {net_profit:.2f}")
    print(f"Total Trades    : {total_trades}")
    print(f"Winning Trades  : {winning_trades}")
    print(f"Losing Trades   : {losing_trades}")
    print(f"Win Rate        : {win_rate:.2f}%")
    print("-" * 70)

    return {
        "symbol": symbol,
        "initial_balance": initial_balance,
        "final_balance": balance,
        "net_profit": net_profit,
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "win_rate": win_rate,
        "trade_history": trade_history
    }


def main():
    client = BinanceClient()
    results = []

    for symbol in SYMBOLS:
        result = run_backtest_for_symbol(client, symbol)
        results.append(result)

    print("\nSUMMARY")
    print("=" * 70)

    total_net = 0.0
    total_trades = 0
    total_wins = 0
    total_losses = 0

    for r in results:
        total_net += r["net_profit"]
        total_trades += r["total_trades"]
        total_wins += r["winning_trades"]
        total_losses += r["losing_trades"]

        print(
            f"{r['symbol']} | Trades: {r['total_trades']} | "
            f"Win Rate: {r['win_rate']:.2f}% | "
            f"Net Profit: {r['net_profit']:.2f}"
        )

    overall_win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0.0

    print("-" * 70)
    print(f"TOTAL NET PROFIT : {total_net:.2f}")
    print(f"TOTAL TRADES     : {total_trades}")
    print(f"TOTAL WINS       : {total_wins}")
    print(f"TOTAL LOSSES     : {total_losses}")
    print(f"OVERALL WIN RATE : {overall_win_rate:.2f}%")
    print("=" * 70)


if __name__ == "__main__":
    main()