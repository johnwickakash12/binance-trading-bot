Binance Futures Testnet — Trading Bot
A command-line Python application for placing orders on the Binance USDT-M Futures Testnet. Built with a clean, layered structure — separate modules for the API client, order logic, input validation, and logging.

Overview
This bot lets you place Market, Limit, and Stop-Market orders from your terminal with a single command. It validates all inputs before touching the API, logs every request and response to a rotating log file, and handles errors clearly so you always know what went wrong.

Supported order types:
•	Market — executes immediately at the current price
•	Limit — placed at a specific price, waits to fill
•	Stop-Market — triggers a market order when a stop price is hit

Project Structure
trading_bot/
    bot/
        __init__.py
        client.py          # Binance REST client, request signing
        orders.py          # Order placement logic per type
        validators.py      # Input validation
        logging_config.py  # File and console logging setup
    cli.py                 # Command-line entry point
    .env                   # Your API keys (never share this)
    .gitignore
    requirements.txt
    README.md
    logs/                  # Auto-created on first run

Setup
1. Clone the repository
git clone https://github.com/johnwickakash12/binance-trading-bot.git
cd trading_bot

2. Create and activate a virtual environment
Windows:
python -m venv .venv
.venv\Scripts\activate

Mac / Linux:
python3 -m venv .venv
source .venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

4. Add your API credentials
Create a file called .env in the project root and add your Binance Futures Testnet keys:
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here

You can get these from the Binance Futures Testnet at https://testnet.binancefuture.com by logging in and clicking API Key in the top navigation.

How to Run
Market Order
Executes immediately at the current market price.
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002
python cli.py --symbol BTCUSDT --side SELL --type MARKET --quantity 0.002

Limit Order
Placed at a specific price. Will show status NEW until the price is reached.
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.002 --price 80000
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.04 --price 3500

Stop-Market Order
Triggers a market order once the stop price is hit.
python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.002 --stop-price 83000

All available flags
--symbol       Trading pair, e.g. BTCUSDT
--side         BUY or SELL
--type         MARKET, LIMIT, or STOP_MARKET
--quantity     Order size in base asset units
--price        Required for LIMIT orders
--stop-price   Required for STOP_MARKET orders
--log-dir      Folder for log files (default: logs/)
--api-key      Pass key directly instead of using .env
--api-secret   Pass secret directly instead of using .env

Minimum Order Size
Binance requires every order to be worth at least 100 USDT. If your quantity multiplied by the current price is below that, the order will be rejected. Use these as safe starting points:

•	BTCUSDT at ~$84,000 — use at least 0.002
•	ETHUSDT at ~$3,000 — use at least 0.04
•	SOLUSDT at ~$130 — use at least 1

Logging
Every run appends to a log file in the logs/ folder, named by date (e.g. trading_bot_20250313.log). The log captures:

•	Every outbound API request with its parameters
•	Every response from Binance including the full order details
•	All validation errors and API errors with their error codes

The log file records DEBUG level and above. The terminal only shows INFO level and above to keep screen output clean.

Error Handling
The bot handles three categories of errors:

•	Validation errors — caught before any API call is made. Examples: missing price for a limit order, invalid side value, negative quantity.
•	Binance API errors — the request reached Binance but was rejected. The error code and message are logged and printed clearly.
•	Network errors — timeouts, DNS failures, or connection issues. These are caught and reported without crashing.

In all cases the bot exits with a non-zero status code so it integrates cleanly with scripts or automation.

Assumptions
•	All orders are placed on the USDT-M Futures Testnet only. The base URL is hardcoded to https://testnet.binancefuture.com.
•	Time-in-force defaults to GTC (Good Till Cancelled) for Limit orders.
•	The bot places orders only. It does not manage open positions, cancel orders, or track P&L.
•	API credentials are expected in a .env file in the project root. They can also be passed directly via --api-key and --api-secret flags if preferred.

Requirements
requests>=2.31.0
colorama>=0.4.6
python-dotenv>=1.0.0

Install all with:
pip install -r requirements.txt

References
•	Binance Futures Testnet: https://testnet.binancefuture.com
•	Binance Futures API documentation: https://binance-docs.github.io/apidocs/futures/en/
•	Binance error codes: https://binance-docs.github.io/apidocs/futures/en/#error-codes
•	Python requests library: https://docs.python-requests.org
•	Python argparse documentation: https://docs.python.org/3/library/argparse.html
