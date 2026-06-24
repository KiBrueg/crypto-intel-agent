from __future__ import annotations
import json
import urllib.parse
import urllib.request


def fetch_klines(symbol='BTCUSDT', interval='1h', limit=160):
    url = 'https://api.binance.com/api/v3/klines?' + urllib.parse.urlencode({'symbol': symbol.upper(), 'interval': interval, 'limit': int(limit)})
    req = urllib.request.Request(url, headers={'User-Agent': 'crypto-pro-trader-assistant/1.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode('utf-8'))
    return [
        {'ts': int(k[0]), 'open': float(k[1]), 'high': float(k[2]), 'low': float(k[3]), 'close': float(k[4]), 'volume': float(k[5])}
        for k in data
    ]


def fetch_depth(symbol='BTCUSDT', limit=50):
    url = 'https://api.binance.com/api/v3/depth?' + urllib.parse.urlencode({'symbol': symbol.upper(), 'limit': int(limit)})
    req = urllib.request.Request(url, headers={'User-Agent': 'crypto-pro-trader-assistant/1.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode('utf-8'))
    return data.get('bids', []), data.get('asks', [])
