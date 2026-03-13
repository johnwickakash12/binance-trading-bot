from __future__ import annotations

import logging
from .client import BinanceFuturesClient

logger = logging.getLogger("trading_bot.orders")


def place_market_order(client: BinanceFuturesClient,
                       symbol: str, side: str, quantity: float) -> dict:
    params = {
        "symbol":   symbol,
        "side":     side,
        "type":     "MARKET",
        "quantity": quantity,
    }
    logger.info("MARKET order → %s %s qty=%s", side, symbol, quantity)
    response = client.place_order(params)
    logger.info("MARKET accepted → orderId=%s status=%s",
                response.get("orderId"), response.get("status"))
    return response


def place_limit_order(client: BinanceFuturesClient,
                      symbol: str, side: str, quantity: float,
                      price: float, time_in_force: str = "GTC") -> dict:
    params = {
        "symbol":      symbol,
        "side":        side,
        "type":        "LIMIT",
        "quantity":    quantity,
        "price":       price,
        "timeInForce": time_in_force,
    }
    logger.info("LIMIT order → %s %s qty=%s price=%s TIF=%s",
                side, symbol, quantity, price, time_in_force)
    response = client.place_order(params)
    logger.info("LIMIT accepted → orderId=%s status=%s",
                response.get("orderId"), response.get("status"))
    return response


def place_stop_market_order(client: BinanceFuturesClient,
                             symbol: str, side: str,
                             quantity: float, stop_price: float) -> dict:
    params = {
        "symbol":    symbol,
        "side":      side,
        "type":      "STOP_MARKET",
        "quantity":  quantity,
        "stopPrice": stop_price,
    }
    logger.info("STOP_MARKET order → %s %s qty=%s stopPrice=%s",
                side, symbol, quantity, stop_price)
    response = client.place_order(params)
    logger.info("STOP_MARKET accepted → orderId=%s status=%s",
                response.get("orderId"), response.get("status"))
    return response


def format_response(response: dict) -> str:
    """Nicely format the order response for display."""
    lines = [
        "\n" + "─" * 52,
        "  ORDER RESPONSE",
        "─" * 52,
        f"  Order ID      : {response.get('orderId',      'N/A')}",
        f"  Symbol        : {response.get('symbol',       'N/A')}",
        f"  Side          : {response.get('side',         'N/A')}",
        f"  Type          : {response.get('type',         'N/A')}",
        f"  Status        : {response.get('status',       'N/A')}",
        f"  Orig Qty      : {response.get('origQty',      'N/A')}",
        f"  Executed Qty  : {response.get('executedQty',  'N/A')}",
        f"  Avg Price     : {response.get('avgPrice',     'N/A')}",
        f"  Price         : {response.get('price',        'N/A')}",
        f"  Stop Price    : {response.get('stopPrice',    'N/A')}",
        f"  Time-in-Force : {response.get('timeInForce',  'N/A')}",
        f"  Client OID    : {response.get('clientOrderId','N/A')}",
        "─" * 52,
    ]
    return "\n".join(lines)