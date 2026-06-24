from __future__ import annotations


def _level_notional(level):
    price, qty = float(level[0]), float(level[1])
    return price * qty


def analyze_order_book(bids, asks, mid_price=None, depth=20):
    bids = list(bids or [])[:depth]
    asks = list(asks or [])[:depth]
    bid_notional = sum(_level_notional(x) for x in bids)
    ask_notional = sum(_level_notional(x) for x in asks)
    total = bid_notional + ask_notional
    imbalance = 0.0 if total == 0 else (bid_notional - ask_notional) / total
    best_bid = float(bids[0][0]) if bids else None
    best_ask = float(asks[0][0]) if asks else None
    if mid_price is None and best_bid and best_ask:
        mid_price = (best_bid + best_ask) / 2
    spread_bps = None
    if best_bid and best_ask and mid_price:
        spread_bps = (best_ask - best_bid) / mid_price * 10000
    signals = []
    if imbalance > 0.35:
        signals.append('bid wall / buy-side depth dominates')
    elif imbalance < -0.35:
        signals.append('ask wall / sell-side depth dominates')
    if spread_bps is not None and spread_bps > 20:
        signals.append('wide spread; execution risk')
    elif spread_bps is not None and spread_bps < 5:
        signals.append('tight spread')
    return {
        'bid_notional': round(bid_notional, 4),
        'ask_notional': round(ask_notional, 4),
        'imbalance': round(imbalance, 6),
        'best_bid': best_bid,
        'best_ask': best_ask,
        'mid_price': mid_price,
        'spread_bps': None if spread_bps is None else round(spread_bps, 4),
        'signals': signals,
    }
