# config/settings.py
import os
from dotenv import load_dotenv

# load .env from project root
project_root = os.path.dirname(os.path.dirname(__file__))
dotenv_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path)

# ---------------- API Keys ----------------
TWELVE_KEY = os.getenv("TWELVE_DATA_KEY", "").strip()

# ---------------- Telegram ----------------
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()  # as string

# ---------------- Symbols & Timeframes ----------------
SYMBOLS = ["XAU/USD", "XAG/USD", "EUR/USD", "GBP/USD", "USD/JPY"]
TRADE_TF = "5min"
CONFIRM_TF = "15min"

# ---------------- Indicators ----------------
EMA_SHORT = 20
EMA_LONG = 50
RSI_PERIOD = 14
ADX_PERIOD = 14
ADX_THRESHOLD = 20.0

RSI_BUY = 55
RSI_SELL = 45
RSI_RANGE_LOW = 45
RSI_RANGE_HIGH = 55

# ---------------- Risk Management ----------------
SL_PERCENT = 0.15
TP_PERCENT = SL_PERCENT * 2

# ---------------- General ----------------
TZ = "Asia/Tehran"
FETCH_RETRIES = 3
FETCH_SLEEP = 2
