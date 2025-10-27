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
    """
    ADX تقریبی فقط با close (میانگین تغییرات قدر مطلق)
    توجه: ADX دقیق نیاز به H/L/C دارد. این تقریبی برای فیلتر رنج است.
    """
    if not prices or len(prices) < period + 1:
        return None
    diffs = [abs(prices[i] - prices[i-1]) for i in range(1, len(prices))]
    return sum(diffs[-period:]) / period

# ---------------- candlestick patterns (simple) ----------------
def is_bullish_engulfing(candles):
    """
    بررسی Bullish Engulfing ساده:
    نیاز به حداقل 2 کندل: کندل قبلی نزولی (close < open)
    کندل فعلی صعودی (close > open)
    بدن کندل فعلی بدنه کندل قبلی را بپوشاند (open_current < close_prev and close_current > open_prev)
    """
    if not candles or len(candles) < 2:
        return False
    prev = candles[-2]
    cur = candles[-1]
    # prev bearish and cur bullish
    if prev["close"] < prev["open"] and cur["close"] > cur["open"]:
        if cur["open"] <= prev["close"] and cur["close"] >= prev["open"]:
            return True
    return False

def is_bearish_engulfing(candles):
    if not candles or len(candles) < 2:
        return False
    prev = candles[-2]
    cur = candles[-1]
    if prev["close"] > prev["open"] and cur["close"] < cur["open"]:
        if cur["open"] >= prev["close"] and cur["close"] <= prev["open"]:
            return True
    return False
