# config/settings.py
import os
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(__file__))
dotenv_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path)

# API
TWELVE_KEY = os.getenv("TWELVE_DATA_KEY", "").strip()

# Telegram
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# Symbols (فلزات، فارکس، کریپتو)
SYMBOLS = [
    "XAU/USD", "XAG/USD",
    "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "NZD/USD", "USD/CAD", "EUR/JPY",
    "BTC/USD", "ETH/USD", "XRP/USD", "LTC/USD", "SOL/USD", "BNB/USD", "DOGE/USD"
]

# Timeframes
TF_TREND = "4h"       # H4 برای جهت روند
TF_ENTRY = "1h"       # H1 برای نقطه ورود
TF_CONFIRM = "30min"  # M30 برای تایید کندلی

# Indicators (تغییر به مقادیر تاییدشده)
EMA_SHORT = 50   # کوتاه‌تر (برای entry/h1 معمولاً 50)
EMA_LONG = 200   # بلندتر (برای trend/h4 معمولاً 200)
RSI_PERIOD = 14
ADX_PERIOD = 14
ADX_THRESHOLD = 20.0

RSI_BUY = 55
RSI_SELL = 45
RSI_RANGE_LOW = 45
RSI_RANGE_HIGH = 55

# Risk management (قابل تغییر)
SL_PERCENT = 0.15
TP_PERCENT = SL_PERCENT * 2

# General
FETCH_RETRIES = 3
FETCH_SLEEP = 2
TZ = "Asia/Tehran"
