from config import SYMBOLS, INTERVAL, CANDLE_LIMIT, TRADE_USDT_AMOUNT, MAX_OPEN_POSITIONS
from core.binance_client import BinanceClient
from core.market_data import klines_to_dataframe
from core.indicators import add_indicators
from core.strategy import check_buy_signal
from core.position_store import load_positions, has_open_position, add_position, remove_position
from core.logger import log_trade
from core.notifier import send_telegram_message

import datetime

now = datetime.datetime.now()

# sabah 09:00 civarı
if now.hour == 9:
    send_telegram_message("☀️ BOT AKTİF - Sabah kontrol")

# akşam 21:00 civarı
if now.hour == 21:
    send_telegram_message("🌙 BOT AKTİF - Akşam kontrol")


def sync_open_positions_with_account(client):
    positions = load_positions()

    if not positions:
        print("NO OPEN POSITIONS TO SYNC")
        print("-" * 70)
        return

    print("SYNCING OPEN POSITIONS...")
    print("-" * 70)

    symbols_to_remove = []

    for symbol, pos in positions.items():
        print(f"Checking {symbol}")

        order_list_id = pos.get("oco_order_list_id")

        if not order_list_id:
            print(f"No OCO order found for {symbol}, skipping...")
            print("-" * 70)
            continue

        try:
            oco_status = client.get_oco_order(order_list_id)
            list_status = oco_status.get("listStatusType")

            print(f"OCO STATUS: {list_status}")

            if list_status != "EXEC_STARTED":
                print(f"POSITION CLOSED DETECTED FOR {symbol}")

                log_trade(
                    symbol=symbol,
                    entry_price=pos.get("entry_price", 0),
                    quantity=pos.get("quantity", 0),
                    take_profit=pos.get("take_profit_price", 0),
                    stop_price=pos.get("stop_price", 0),
                    stop_limit_price=pos.get("stop_limit_price", 0),
                    buy_order_id=pos.get("buy_order_id", ""),
                    oco_order_list_id=order_list_id,
                    status="CLOSED"
                )

                send_telegram_message(
                    f"❌ POSITION CLOSED\n"
                    f"{symbol}\n"
                    f"OCO Status: {list_status}"
                )

                symbols_to_remove.append(symbol)
            else:
                print(f"POSITION STILL OPEN FOR {symbol}")

        except Exception as e:
            print(f"OCO CHECK FAILED FOR {symbol}")
            print("Hata:", e)

            send_telegram_message(
                f"⚠️ OCO CHECK FAILED\n"
                f"{symbol}\n"
                f"Hata: {e}"
            )

        print("-" * 70)

    for symbol in symbols_to_remove:
        remove_position(symbol)
        print(f"REMOVED FROM open_positions.json -> {symbol}")

    if not symbols_to_remove:
        print("NO CLOSED POSITIONS FOUND")
        print("-" * 70)


def main():
    client = BinanceClient()

    print("Server time:", client.get_server_time())
    print("-" * 70)

    # 1) Önce açık pozisyonları senkronla
    sync_open_positions_with_account(client)

    # 2) Güncel açık pozisyonları tekrar yükle
    open_positions = load_positions()
    print(f"OPEN POSITIONS COUNT: {len(open_positions)}")
    print("-" * 70)

    if len(open_positions) >= MAX_OPEN_POSITIONS:
        print("MAX OPEN POSITIONS LIMIT REACHED")
        return

    # 3) Yeni sinyal tara
    for symbol in SYMBOLS:
        print(f"SCANNING: {symbol}")

        if has_open_position(symbol):
            print(f"SKIP: {symbol} already has an open position")
            print("-" * 70)
            continue

        try:
            klines = client.get_klines(symbol, INTERVAL, CANDLE_LIMIT)
            df = klines_to_dataframe(klines)
            df = add_indicators(df)

            signal, info = check_buy_signal(df)

            print(f"Close         : {info['close']:.4f}")
            print(f"EMA20         : {info['ema20']:.4f}")
            print(f"EMA50         : {info['ema50']:.4f}")
            print(f"EMA200        : {info['ema200']:.4f}")
            print(f"RSI           : {info['rsi']:.2f}")
            print(f"ATR           : {info['atr']:.4f}")
            print(f"ADX           : {info['adx']:.2f}")
            print(f"Volume        : {info['volume']:.4f}")
            print(f"Vol_MA20      : {info['vol_ma20']:.4f}")
            print(f"Trend OK      : {info['trend_ok']}")
            print(f"Momentum OK   : {info['momentum_ok']}")
            print(f"RSI OK        : {info['rsi_ok']}")
            print(f"Volume OK     : {info['volume_ok']}")
            print(f"ADX OK        : {info['adx_ok']}")
            print(f"BUY SIGNAL    : {signal}")

            if not signal:
                print("NO TRADE - Conditions not met")
                print("-" * 70)
                continue

            price = info["close"]

            print(f"BUY SIGNAL DETECTED FOR {symbol}")
            print("-" * 70)

            send_telegram_message(
                f"🚀 BUY SIGNAL\n"
                f"{symbol}\n"
                f"Price: {price:.2f}"
            )

            buy_result = client.market_buy(
                symbol=symbol,
                quote_order_qty=str(TRADE_USDT_AMOUNT)
            )

            print("MARKET BUY OK")
            print(buy_result)
            print("-" * 70)

            executed_qty = float(buy_result["executedQty"])
            cumm_quote = float(buy_result["cummulativeQuoteQty"])

            if executed_qty <= 0:
                print("BUY FAILED: executedQty = 0")
                print("-" * 70)

                send_telegram_message(
                    f"⚠️ BUY FAILED\n"
                    f"{symbol}\n"
                    f"executedQty = 0"
                )
                continue

            entry_price = cumm_quote / executed_qty

            send_telegram_message(
                f"✅ BUY EXECUTED\n"
                f"{symbol}\n"
                f"Qty: {executed_qty:.8f}\n"
                f"Entry: {entry_price:.2f}"
            )

            take_profit_price = entry_price * 1.02
            stop_price = entry_price * 0.99
            stop_limit_price = entry_price * 0.989

            print("EXIT PLAN")
            print(f"Entry Price   : {entry_price:.4f}")
            print(f"Executed Qty  : {executed_qty:.8f}")
            print(f"Take Profit   : {take_profit_price:.4f}")
            print(f"Stop Trigger  : {stop_price:.4f}")
            print(f"Stop Limit    : {stop_limit_price:.4f}")
            print("-" * 70)

            oco_result = client.place_exit_oco_sell(
                symbol=symbol,
                quantity=executed_qty,
                take_profit_price=take_profit_price,
                stop_price=stop_price,
                stop_limit_price=stop_limit_price
            )

            print("OCO EXIT ORDER OK")
            print(oco_result)
            print("-" * 70)

            send_telegram_message(
                f"🎯 EXIT SET\n"
                f"{symbol}\n"
                f"TP: {take_profit_price:.2f}\n"
                f"SL: {stop_price:.2f}"
            )

            order_list_id = oco_result.get("orderListId", "")

            position_data = {
                "symbol": symbol,
                "entry_price": entry_price,
                "quantity": executed_qty,
                "take_profit_price": take_profit_price,
                "stop_price": stop_price,
                "stop_limit_price": stop_limit_price,
                "buy_order_id": buy_result.get("orderId"),
                "oco_order_list_id": order_list_id,
                "status": "OPEN"
            }

            add_position(symbol, position_data)

            log_trade(
                symbol=symbol,
                entry_price=entry_price,
                quantity=executed_qty,
                take_profit=take_profit_price,
                stop_price=stop_price,
                stop_limit_price=stop_limit_price,
                buy_order_id=buy_result.get("orderId"),
                oco_order_list_id=order_list_id,
                status="OPEN"
            )

            print(f"POSITION SAVED FOR {symbol}")
            print("AUTOMATIC FLOW COMPLETED")
            print("-" * 70)

            send_telegram_message(
                f"📌 POSITION SAVED\n"
                f"{symbol}\n"
                f"Order ID: {buy_result.get('orderId')}\n"
                f"OCO ID: {order_list_id}"
            )

            # Tek seferde yalnızca 1 işlem aç
            break

        except Exception as e:
            print(f"ERROR WHILE PROCESSING {symbol}")
            print("Hata:", e)
            print("-" * 70)

            send_telegram_message(
                f"⚠️ BOT ERROR\n"
                f"{symbol}\n"
                f"Hata: {e}"
            )


if __name__ == "__main__":
    main()