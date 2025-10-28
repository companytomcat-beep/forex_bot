# core/indicators.py

def calc_ema(prices, period):
    """EMA - میانگین متحرک نمایی"""
    if not prices:
        return None
    if len(prices) < period:
        return sum(prices)/len(prices)
    k = 2.0 / (period + 1)
    ema = prices[0]
    for p in prices[1:]:
        ema = p * k + ema * (1 - k)
    return ema

def calc_rsi(prices, period=14):
    """RSI ساده روی close"""
    if not prices or len(prices) < period + 1:
        return None
    gains = 0.0
    losses = 0.0
    for i in range(1, len(prices)):
        d = prices[i] - prices[i-1]
        if d > 0:
            gains += d
        else:
            losses -= d
    avg_gain = gains / period
    avg_loss = losses / period
    if avg_loss == 0:
        return 100.0 if avg_gain > 0 else 50.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))

def calc_adx_approx(prices, period=14):
    """ADX تقریبی فقط با close"""
    if not prices or len(prices) < period + 1:
        return None
    diffs = [abs(prices[i] - prices[i-1]) for i in range(1, len(prices))]
    return sum(diffs[-period:]) / period

# ---------------- candlestick patterns ----------------
def is_bullish_engulfing(candles):
    if not candles or len(candles) < 2:
        return False
    prev, cur = candles[-2], candles[-1]
    if prev["close"] < prev["open"] and cur["close"] > cur["open"]:
        if cur["open"] <= prev["close"] and cur["close"] >= prev["open"]:
            return True
    return False

def is_bearish_engulfing(candles):
    if not candles or len(candles) < 2:
        return False
    prev, cur = candles[-2], candles[-1]
    if prev["close"] > prev["open"] and cur["close"] < cur["open"]:
        if cur["open"] >= prev["close"] and cur["close"] <= prev["open"]:
            return True
    return False

def is_hammer(candles):
    if not candles:
        return False
    c = candles[-1]
    body = abs(c["close"] - c["open"])
    lower_shadow = c["open"] - c["low"] if c["close"] > c["open"] else c["close"] - c["low"]
    upper_shadow = c["high"] - c["close"] if c["close"] > c["open"] else c["high"] - c["open"]
    return lower_shadow >= 2 * body and upper_shadow <= body

def is_inverted_hammer(candles):
    if not candles:
        return False
    c = candles[-1]
    body = abs(c["close"] - c["open"])
    upper_shadow = c["high"] - c["close"] if c["close"] > c["open"] else c["high"] - c["open"]
    lower_shadow = c["open"] - c["low"] if c["close"] > c["open"] else c["close"] - c["low"]
    return upper_shadow >= 2 * body and lower_shadow <= body

def is_shooting_star(candles):
    return is_inverted_hammer(candles)

def is_hanging_man(candles):
    return is_hammer(candles)
