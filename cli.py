#!/usr/bin/env python3
"""
cli.py — Entry point for the Binance Futures Testnet Trading Bot.

Run with:  python cli.py --help
"""

import argparse
import os
import sys
import textwrap

from bot.client       import BinanceClientError, BinanceFuturesClient
from bot.logging_config import setup_logging
from bot.orders       import (format_response, place_limit_order,
                               place_market_order, place_stop_market_order)
from bot.validators   import (validate_order_type, validate_price,
                               validate_quantity, validate_side,
                               validate_stop_price, validate_symbol)

# ── Optional colour support ───────────────────────────────────────────────────
try:
    from colorama import Fore, Style, init as _init
    _init(autoreset=True)
    GREEN, RED, YELLOW, CYAN, BOLD, RESET = (
        Fore.GREEN, Fore.RED, Fore.YELLOW, Fore.CYAN, Style.BRIGHT, Style.RESET_ALL
    )
except ImportError:
    GREEN = RED = YELLOW = CYAN = BOLD = RESET = ""


# ── Helpers ───────────────────────────────────────────────────────────────────

def print_banner():
    print(f"""
{BOLD}{CYAN}╔══════════════════════════════════════════════════╗
║   Binance Futures Testnet  –  Trading Bot v1.0  ║
╚══════════════════════════════════════════════════╝{RESET}
""")


def print_summary(symbol, side, order_type, quantity, price, stop_price):
    side_colour = GREEN if side == "BUY" else RED
    print(f"  {BOLD}ORDER SUMMARY{RESET}")
    print("  " + "─" * 46)
    print(f"  Symbol      : {CYAN}{symbol}{RESET}")
    print(f"  Side        : {side_colour}{side}{RESET}")
    print(f"  Type        : {YELLOW}{order_type}{RESET}")
    print(f"  Quantity    : {quantity}")
    if price      is not None: print(f"  Price       : {price}")
    if stop_price is not None: print(f"  Stop Price  : {stop_price}")
    print("  " + "─" * 46 + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place orders on Binance USDT-M Futures Testnet.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          python cli.py --symbol BTCUSDT --side BUY  --type MARKET     --quantity 0.001
          python cli.py --symbol ETHUSDT --side SELL --type LIMIT       --quantity 0.01  --price 3200
          python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 83000

        Set credentials as environment variables (recommended):
          export BINANCE_API_KEY="your_key"
          export BINANCE_API_SECRET="your_secret"
        """),
    )
    parser.add_argument("--symbol",      required=True,  help="e.g. BTCUSDT")
    parser.add_argument("--side",        required=True,  help="BUY or SELL")
    parser.add_argument("--type",        required=True,  dest="order_type",
                        help="MARKET | LIMIT | STOP_MARKET")
    parser.add_argument("--quantity",    required=True,  help="Quantity in base asset")
    parser.add_argument("--price",       default=None,   help="Required for LIMIT orders")
    parser.add_argument("--stop-price",  default=None,   dest="stop_price",
                        help="Required for STOP_MARKET orders")
    parser.add_argument("--api-key",     default=None,   help="Binance API key")
    parser.add_argument("--api-secret",  default=None,   help="Binance API secret")
    parser.add_argument("--log-dir",     default="logs", help="Folder for log files")
    return parser


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = build_parser()
    args   = parser.parse_args()

    logger = setup_logging(log_dir=args.log_dir)
    logger.info("CLI called with: %s", vars(args))

    print_banner()

    # 1. Validate all inputs
    try:
        symbol     = validate_symbol(args.symbol)
        side       = validate_side(args.side)
        order_type = validate_order_type(args.order_type)
        quantity   = validate_quantity(args.quantity)
        price      = validate_price(args.price, order_type)
        stop_price = validate_stop_price(args.stop_price, order_type)
    except ValueError as e:
        logger.error("Validation failed: %s", e)
        print(f"\n{RED}✖  {e}{RESET}\n")
        sys.exit(1)

    print_summary(symbol, side, order_type, quantity, price, stop_price)

    # 2. Resolve credentials
    api_key    = args.api_key    or os.getenv("BINANCE_API_KEY",    "")
    api_secret = args.api_secret or os.getenv("BINANCE_API_SECRET", "")

    if not api_key or not api_secret:
        msg = ("Missing API credentials. "
               "Set BINANCE_API_KEY and BINANCE_API_SECRET as environment variables, "
               "or pass --api-key / --api-secret.")
        logger.error(msg)
        print(f"\n{RED}✖  {msg}{RESET}\n")
        sys.exit(1)

    # 3. Place the order
    try:
        client = BinanceFuturesClient(api_key=api_key, api_secret=api_secret)

        if   order_type == "MARKET":
            response = place_market_order(client, symbol, side, quantity)
        elif order_type == "LIMIT":
            response = place_limit_order(client, symbol, side, quantity, price)
        elif order_type == "STOP_MARKET":
            response = place_stop_market_order(client, symbol, side, quantity, stop_price)

    except BinanceClientError as e:
        logger.error("Order failed → %s | detail=%s", e, e.response)
        print(f"\n{RED}✖  Order failed: {e}{RESET}\n")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        print(f"\n{RED}✖  Unexpected error: {e}{RESET}\n")
        sys.exit(1)

    # 4. Print result
    logger.info("Order successful → %s", response)
    print(format_response(response))
    print(f"\n{GREEN}{BOLD}  ✔  Order placed successfully!{RESET}\n")


if __name__ == "__main__":
    main()
    