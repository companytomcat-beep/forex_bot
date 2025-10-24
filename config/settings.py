# config/settings.py

# ---------------- API Keys ----------------
TWELVE_KEY = "YOUR_TWELVE_KEY"
FINNHUB_KEY = "YOUR_FINNHUB_KEY"  # optional

# ---------------- Telegram Bot ----------------
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

# ---------------- Symbols & Timeframes ----------------
SYMBOLS = ["XAU/USD", "XAG/USD", "EUR/USD", "GBP/USD", "USD/JPY"]
TRADE_TF = "5min"
CONFIRM_TF = "15min"

# ---------------- Indicators ----------------
EMA_SHORT = 20
EMA_LONG = 50
RSI_PERIOD = 14
ADX_PERIOD = 14
ADX_THRESHOLD = 20.0  # ADX must be above this to consider trend strong

RSI_BUY = 55
RSI_SELL = 45
RSI_RANGE_LOW = 45
RSI_RANGE_HIGH = 55

# ---------------- Risk Management ----------------
SL_PERCENT = 0.15   # percent SL
TP_PERCENT = SL_PERCENT * 2  # 1:2 RR

# ---------------- General ----------------
TZ = "Asia/Tehran"
FETCH_RETRIES = 3
FETCH_SLEEP = 2
