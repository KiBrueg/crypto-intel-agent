from __future__ import annotations
import math
from statistics import mean, pstdev


def _returns(xs):
    out = []
    for i in range(1, len(xs)):
        prev = float(xs[i-1])
        out.append(0.0 if prev == 0 else float(xs[i]) / prev - 1.0)
    return out


def correlation(a, b):
    n = min(len(a), len(b))
    if n < 3:
        return 0.0
    a = [float(x) for x in a[-n:]]
    b = [float(x) for x in b[-n:]]
    ma, mb = mean(a), mean(b)
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    if va <= 1e-12 or vb <= 1e-12:
        return 0.0
    cov = sum((a[i] - ma) * (b[i] - mb) for i in range(n))
    return cov / math.sqrt(va * vb)


def hedge_ratio(base_prices, quote_prices):
    n = min(len(base_prices), len(quote_prices))
    if n < 3:
        return 1.0
    x = [float(v) for v in quote_prices[-n:]]
    y = [float(v) for v in base_prices[-n:]]
    mx, my = mean(x), mean(y)
    var = sum((v - mx) ** 2 for v in x)
    if var <= 1e-12:
        return 1.0
    cov = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    return cov / var


def analyze_pair(base_symbol, quote_symbol, base_prices, quote_prices, window=30):
    n = min(len(base_prices), len(quote_prices))
    if n < 4:
        raise ValueError('need at least 4 price points')
    base = [float(x) for x in base_prices[-n:]]
    quote = [float(x) for x in quote_prices[-n:]]
    beta = hedge_ratio(base, quote)
    spreads = [base[i] - beta * quote[i] for i in range(n)]
    win = spreads[-min(window, len(spreads)):]
    mu = mean(win)
    sd = pstdev(win) if len(win) > 1 else 0.0
    z = 0.0 if sd <= 1e-12 else (spreads[-1] - mu) / sd
    corr = correlation(_returns(base[-min(window, n):]), _returns(quote[-min(window, n):]))
    flags = []
    if abs(z) >= 1:
        flags.append('spread is statistically extended')
    if corr < 0.3:
        flags.append('correlation breakdown risk')
    direction = 'base rich vs quote' if z > 0 else 'base cheap vs quote' if z < 0 else 'neutral'
    return {
        'pair': f'{base_symbol}/{quote_symbol}',
        'hedge_ratio': round(beta, 6),
        'spread': round(spreads[-1], 8),
        'spread_zscore': round(z, 4),
        'correlation': round(corr, 4),
        'direction': direction,
        'risk_flags': flags,
        'confirmation': 'watch for spread mean reversion while correlation remains stable',
        'invalidation': 'discard if correlation breaks or spread keeps trending without reversion',
    }
