# core/indicators.py
def calc_ema(prices, period):
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
    if not prices or len(prices) < period + 1:
        return None
    gains = 0.0; losses = 0.0
    for i in range(1, len(prices)):
        d = prices[i] - prices[i-1]
        if d > 0: gains += d
        else: losses -= d
    avg_gain = gains / period
    avg_loss = losses / period
    if avg_loss == 0:
        return 100.0 if avg_gain > 0 else 50.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))

def calc_adx_approx(prices, period=14):
    if not prices or len(prices) < period + 1:
        return None
    diffs = [abs(prices[i] - prices[i-1]) for i in range(1, len(prices))]
    return sum(diffs[-period:]) / period

# Candlestick helpers (conservative/simple)
def is_bullish_engulfing(candles):
    if not candles or len(candles) < 2: return False
    a, b = candles[-2], candles[-1]
    return (a["close"] < a["open"] and b["close"] > b["open"]
            and b["open"] <= a["close"] and b["close"] >= a["open"])

def is_bearish_engulfing(candles):
    if not candles or len(candles) < 2: return False
    a, b = candles[-2], candles[-1]
    return (a["close"] > a["open"] and b["close"] < b["open"]
            and b["open"] >= a["close"] and b["close"] <= a["open"])

def _body(c): return abs(c["close"] - c["open"])
def _upper(c): return c["high"] - max(c["open"], c["close"])
def _lower(c): return min(c["open"], c["close"]) - c["low"]

def is_hammer(candles):
    if not candles: return False
    c = candles[-1]
    body = _body(c)
    if body == 0: return False
    return _lower(c) >= 2*body and _upper(c) <= body

def is_inverted_hammer(candles):
    if not candles: return False
    c = candles[-1]
    body = _body(c)
    if body == 0: return False
    return _upper(c) >= 2*body and _lower(c) <= body

def is_shooting_star(candles): return is_inverted_hammer(candles)
def is_hanging_man(candles): return is_hammer(candles)

def is_doji(c):
    rng = c["high"] - c["low"]
    if rng == 0: return False
    return _body(c) <= 0.1 * rng

def is_tweezer_bottom(a,b):
    if not a or not b: return False
    same_low = abs(a["low"] - b["low"]) / max(a["low"], b["low"]) < 0.0006
    return same_low and (b["close"] > b["open"]) and (a["close"] < a["open"])

def is_tweezer_top(a,b):
    if not a or not b: return False
    same_high = abs(a["high"] - b["high"]) / max(a["high"], b["high"]) < 0.0006
    return same_high and (b["close"] < b["open"]) and (a["close"] > a["open"])

# simple 3-candle patterns: morning/evening star (conservative)
def is_morning_star(candles):
    if not candles or len(candles) < 3: return False
    a,b,c = candles[-3], candles[-2], candles[-1]
    if not (a["close"] < a["open"] and c["close"] > c["open"]): return False
    if _body(b) > 0.5 * _body(a): return False
    mid_a = (a["open"] + a["close"])/2.0
    return c["close"] >= mid_a

def is_evening_star(candles):
    if not candles or len(candles) < 3: return False
    a,b,c = candles[-3], candles[-2], candles[-1]
    if not (a["close"] > a["open"] and c["close"] < c["open"]): return False
    if _body(b) > 0.5 * _body(a): return False
    mid_a = (a["open"] + a["close"])/2.0
    return c["close"] <= mid_a

def is_piercing_line(candles):
    if not candles or len(candles) < 2: return False
    prev, cur = candles[-2], candles[-1]
    if not (prev["close"] < prev["open"] and cur["close"] > cur["open"]): return False
    body_prev = _body(prev)
    return cur["close"] >= (prev["close"] + 0.5 * body_prev)

def is_dark_cloud_cover(candles):
    if not candles or len(candles) < 2: return False
    prev, cur = candles[-2], candles[-1]
    if not (prev["close"] > prev["open"] and cur["close"] < cur["open"]): return False
    body_prev = _body(prev)
    return cur["close"] <= (prev["close"] - 0.5 * body_prev)
