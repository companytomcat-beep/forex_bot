# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

# API keys (from .env)
TWELVE_KEY = os.getenv("TWELVE_DATA_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Symbols / pairs (final list)
SYMBOLS = [
    "XAU/USD","XAG/USD",
    "EUR/USD","GBP/USD","USD/JPY","USD/CHF","AUD/USD","USD/CAD","NZD/USD","EUR/JPY",
    "BTC/USD","ETH/USD","SOL/USD","DOGE/USD","BNB/USD","LTC/USD","XRP/USD"
]

# Timeframes (final agreed)
TF_TREND = "1h"      # H1
TF_ENTRY = "30min"   # M30
TF_CONFIRM = "5min"  # M5

# Indicators
EMA_SHORT = 20
EMA_LONG = 50
RSI_PERIOD = 14
RSI_BUY = 55
RSI_SELL = 45
ADX_PERIOD = 14
ADX_THRESHOLD = 20.0

# Risk / runtime
SL_PERCENT = 0.15
TP_PERCENT = SL_PERCENT * 2

# Fetch params
FETCH_RETRIES = 3
FETCH_SLEEP = 1

# Bot runtime
CHECK_INTERVAL = 60  # seconds between full scans (you can increase to 120/300)
LOG_LEVEL = "DEBUG"
