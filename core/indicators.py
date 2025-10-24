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
    """RSI - شاخص قدرت نسبی"""
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

def calc_adx(prices, period=14):
    """ADX - قدرت روند (تقریبی با قیمت Close)"""
    # ADX واقعی نیاز به High/Low/Close دارد، اگر در آینده HLC داشتیم دقیق می‌کنیم
    return None
