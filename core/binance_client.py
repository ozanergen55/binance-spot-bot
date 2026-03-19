import math
import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode

from config import API_KEY, API_SECRET, BASE_URL


class BinanceClient:
    def __init__(self):
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key or ""})

    def _sign_params(self, params: dict) -> str:
        if not self.api_secret:
            raise ValueError("API secret eksik. .env dosyasını kontrol et.")

        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return f"{query_string}&signature={signature}"

    def get_server_time(self):
        url = f"{self.base_url}/api/v3/time"
        r = self.session.get(url, timeout=10)
        r.raise_for_status()
        return r.json()

    def get_exchange_info(self, symbol=None):
        url = f"{self.base_url}/api/v3/exchangeInfo"
        params = {}
        if symbol:
            params["symbol"] = symbol
        r = self.session.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()

    def get_klines(self, symbol, interval="1h", limit=300):
        url = f"{self.base_url}/api/v3/klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        r = self.session.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()

    def get_account_info(self):
        url = f"{self.base_url}/api/v3/account"
        params = {
            "timestamp": int(time.time() * 1000),
            "recvWindow": 5000
        }
        signed = self._sign_params(params)
        r = self.session.get(f"{url}?{signed}", timeout=10)
        r.raise_for_status()
        return r.json()

    def get_asset_balance(self, asset="USDT"):
        account_info = self.get_account_info()
        balances = account_info.get("balances", [])

        for balance in balances:
            if balance["asset"] == asset:
                return {
                    "asset": balance["asset"],
                    "free": float(balance["free"]),
                    "locked": float(balance["locked"])
                }

        return {
            "asset": asset,
            "free": 0.0,
            "locked": 0.0
        }

    def test_order_market_buy(self, symbol, quote_order_qty):
        """
        Gerçek emir açmaz.
        Sadece order parametrelerini ve imzayı doğrular.
        """
        url = f"{self.base_url}/api/v3/order/test"
        params = {
            "symbol": symbol,
            "side": "BUY",
            "type": "MARKET",
            "quoteOrderQty": quote_order_qty,
            "timestamp": int(time.time() * 1000),
            "recvWindow": 5000
        }
        signed = self._sign_params(params)
        headers = {"X-MBX-APIKEY": self.api_key or ""}
        r = self.session.post(f"{url}?{signed}", headers=headers, timeout=10)
        r.raise_for_status()
        return {"success": True, "symbol": symbol, "quoteOrderQty": quote_order_qty}
    
    def market_buy(self, symbol, quote_order_qty):
        url = f"{self.base_url}/api/v3/order"

        params = {
            "symbol": symbol,
            "side": "BUY",
            "type": "MARKET",
            "quoteOrderQty": quote_order_qty,
            "timestamp": int(time.time() * 1000),
            "recvWindow": 5000
        }

        signed = self._sign_params(params)

        headers = {
            "X-MBX-APIKEY": self.api_key
        }   

        r = self.session.post(f"{url}?{signed}", headers=headers, timeout=10)
        r.raise_for_status()
        return r.json()

    def _signed_post(self, path, params: dict):
        url = f"{self.base_url}{path}"
        signed = self._sign_params(params)
        r = self.session.post(f"{url}?{signed}", timeout=10)
        r.raise_for_status()
        return r.json()

    def get_symbol_filters(self, symbol):
        info = self.get_exchange_info(symbol)
        symbol_info = info["symbols"][0]

        filters = {}
        for f in symbol_info["filters"]:
            filters[f["filterType"]] = f

        return filters

    def floor_to_step(self, value, step):
        value = float(value)
        step = float(step)
        return math.floor(value / step) * step

    def floor_to_tick(self, value, tick):
        value = float(value)
        tick = float(tick)
        return math.floor(value / tick) * tick

    def place_exit_oco_sell(self, symbol, quantity, take_profit_price, stop_price, stop_limit_price):
        filters = self.get_symbol_filters(symbol)

        lot_step = float(filters["LOT_SIZE"]["stepSize"])
        min_qty = float(filters["LOT_SIZE"]["minQty"])
        tick_size = float(filters["PRICE_FILTER"]["tickSize"])

        quantity = self.floor_to_step(quantity, lot_step)
        take_profit_price = self.floor_to_tick(take_profit_price, tick_size)
        stop_price = self.floor_to_tick(stop_price, tick_size)
        stop_limit_price = self.floor_to_tick(stop_limit_price, tick_size)

        if quantity < min_qty:
            raise ValueError(f"Quantity çok küçük. quantity={quantity}, minQty={min_qty}")

        params = {
            "symbol": symbol,
            "side": "SELL",
            "quantity": f"{quantity:.8f}",
            "aboveType": "LIMIT_MAKER",
            "abovePrice": f"{take_profit_price:.8f}",
            "belowType": "STOP_LOSS_LIMIT",
            "belowStopPrice": f"{stop_price:.8f}",
            "belowPrice": f"{stop_limit_price:.8f}",
            "belowTimeInForce": "GTC",
            "timestamp": int(time.time() * 1000),
            "recvWindow": 5000
        }

        return self._signed_post("/api/v3/orderList/oco", params)
        
    def get_asset_free_balance(self, asset):
        account_info = self.get_account_info()
        balances = account_info.get("balances", [])

        for balance in balances:
            if balance["asset"] == asset:
                return float(balance["free"])

        return 0.0
    
    def get_oco_order(self, order_list_id):
        url = f"{self.base_url}/api/v3/orderList"

        params = {
            "orderListId": order_list_id,
            "timestamp": int(time.time() * 1000),
            "recvWindow": 5000
        }

        signed = self._sign_params(params)

        r = self.session.get(f"{url}?{signed}", timeout=10)
        r.raise_for_status()
        return r.json()
    
    def market_sell(self, symbol, quantity):
        url = f"{self.base_url}/api/v3/order"

        params = {
            "symbol": symbol,
            "side": "SELL",
            "type": "MARKET",
            "quantity": quantity,
            "timestamp": int(time.time() * 1000),
            "recvWindow": 5000
        }

        signed = self._sign_params(params)

        r = self.session.post(f"{url}?{signed}", timeout=10)
        r.raise_for_status()

        return r.json()

    def cancel_oco_order(self, symbol, order_list_id):
        url = f"{self.base_url}/api/v3/orderList"

        params = {
            "symbol": symbol,
            "orderListId": order_list_id,
            "timestamp": int(time.time() * 1000),
            "recvWindow": 5000
        }

        signed = self._sign_params(params)

        r = self.session.delete(f"{url}?{signed}", timeout=10)
        r.raise_for_status()
        return r.json()    
