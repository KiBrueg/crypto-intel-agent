#!/usr/bin/env python3
"""Safe CoinGecko market-intelligence monitor. No trading, no financial advice."""
from __future__ import annotations
import argparse, datetime as dt, html, json, math, os, sqlite3, textwrap, urllib.parse, urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any
API='https://api.coingecko.com/api/v3/coins/markets'
@dataclass
class Coin:
    coin_id:str; symbol:str; name:str; price:float|None; rank:int|None; change_24h:float|None; volume_24h:float|None; market_cap:float|None; high_24h:float|None; low_24h:float|None
    @classmethod
    def from_api(cls,r:dict[str,Any]):
        return cls(str(r.get('id') or ''),str(r.get('symbol') or '').upper(),str(r.get('name') or ''),num(r.get('current_price')),to_int(r.get('market_cap_rank')),num(r.get('price_change_percentage_24h')),num(r.get('total_volume')),num(r.get('market_cap')),num(r.get('high_24h')),num(r.get('low_24h')))
    @property
    def vol_to_mcap(self): return None if not self.volume_24h or not self.market_cap or self.market_cap<=0 else self.volume_24h/self.market_cap
    @property
    def range_pct(self): return None if not self.high_24h or not self.low_24h or not self.price or self.price<=0 else (self.high_24h-self.low_24h)/self.price*100
@dataclass(frozen=True)
class Alert: severity:str; symbol:str; name:str; reason:str; value:str
def num(x):
    try:
        if x is None: return None
        y=float(x); return None if math.isnan(y) or math.isinf(y) else y
    except Exception: return None
def to_int(x):
    try: return int(x) if x is not None else None
    except Exception: return None
def fetch_markets(vs='usd', per_page=80):
    q=urllib.parse.urlencode({'vs_currency':vs,'order':'market_cap_desc','per_page':str(per_page),'page':'1','sparkline':'false','price_change_percentage':'24h','locale':'en'})
    req=urllib.request.Request(API+'?'+q,headers={'User-Agent':'crypto-intel-agent/1.0'})
    with urllib.request.urlopen(req,timeout=35) as r: data=json.loads(r.read().decode())
    if not isinstance(data,list): raise RuntimeError('Unexpected API response')
    return [Coin.from_api(x) for x in data]
def init_db(path):
    con=sqlite3.connect(path); con.execute('''CREATE TABLE IF NOT EXISTS snapshots(ts_utc TEXT, coin_id TEXT, symbol TEXT, name TEXT, price REAL, rank INTEGER, change_24h REAL, volume_24h REAL, market_cap REAL, high_24h REAL, low_24h REAL, vol_to_mcap REAL, range_pct REAL, PRIMARY KEY(ts_utc, coin_id))'''); return con
def save_snapshot(con,coins,ts):
    rows=[(ts,c.coin_id,c.symbol,c.name,c.price,c.rank,c.change_24h,c.volume_24h,c.market_cap,c.high_24h,c.low_24h,c.vol_to_mcap,c.range_pct) for c in coins]
    con.executemany('INSERT OR REPLACE INTO snapshots VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',rows); con.commit(); return len(rows)
def pct(x): return 'n/a' if x is None else ('+' if x>0 else '')+f'{x:.2f}%'
def money(x):
    if x is None: return 'n/a'
    if x>=1_000_000_000: return f'${x/1_000_000_000:.2f}B'
    if x>=1_000_000: return f'${x/1_000_000:.1f}M'
    if x>=1: return f'${x:,.2f}'
    return f'${x:.6f}'
def detect_alerts(coins, change_threshold=7.0, range_threshold=10.0, vol_mcap_threshold=.18):
    out=[]
    for c in coins:
        if c.change_24h is not None and abs(c.change_24h)>=change_threshold: out.append(Alert('HIGH' if abs(c.change_24h)>=change_threshold*1.5 else 'MED',c.symbol,c.name,'24h price move',pct(c.change_24h)))
        if c.range_pct is not None and c.range_pct>=range_threshold: out.append(Alert('MED',c.symbol,c.name,'wide intraday range',pct(c.range_pct)))
        if c.vol_to_mcap is not None and c.vol_to_mcap>=vol_mcap_threshold: out.append(Alert('MED',c.symbol,c.name,'high volume/market-cap',f'{c.vol_to_mcap:.2%}'))
    seen=set(); res=[]
    for a in sorted(out,key=lambda x:(0 if x.severity=='HIGH' else 1,x.symbol,x.reason)):
        if (a.symbol,a.reason) not in seen: seen.add((a.symbol,a.reason)); res.append(a)
    return res
def top_movers(coins,n=5):
    v=[c for c in coins if c.change_24h is not None]; return sorted(v,key=lambda c:c.change_24h or -999,reverse=True)[:n], sorted(v,key=lambda c:c.change_24h or 999)[:n]
def coin_line(c): return f'{c.symbol} ({c.name}) - {pct(c.change_24h)}, price {money(c.price)}, vol {money(c.volume_24h)}'
def render_markdown(coins,alerts,ts,vs):
    g,l=top_movers(coins); ab='\n'.join(f'- **{a.severity}** {a.symbol} ({a.name}): {a.reason} = {a.value}' for a in alerts[:15]) or '- No threshold alerts.'
    return textwrap.dedent(f'''# Crypto Intel Agent Report\n\n**Time:** {ts}\n**Universe:** top {len(coins)} coins by market cap, vs `{vs.upper()}`\n**Mode:** research/monitoring only - not financial advice.\n\n## Alerts\n{ab}\n\n## Top gainers 24h\n{chr(10).join('- '+coin_line(c) for c in g)}\n\n## Top losers 24h\n{chr(10).join('- '+coin_line(c) for c in l)}\n''')
def render_html(md):
    body=[]
    for raw in md.splitlines():
        line=html.escape(raw.strip())
        if not line: continue
        if line.startswith('# '): body.append(f'<h1>{line[2:]}</h1>')
        elif line.startswith('## '): body.append(f'<h2>{line[3:]}</h2>')
        elif line.startswith('- '): body.append(f'<li>{line[2:]}</li>')
        else: body.append(f'<p>{line}</p>')
    return '<!doctype html><html><head><meta charset="utf-8"><title>Crypto Intel Agent</title><style>body{background:#070b13;color:#e6edf7;font:16px Arial;padding:30px}main{max-width:980px;margin:auto;background:#111827;border-radius:22px;padding:30px}h2{color:#7dd3fc}li{background:#172033;margin:8px 0;padding:10px;border-radius:10px;list-style:none}</style></head><body><main>'+'\n'.join(body)+'</main></body></html>'
def main():
    p=argparse.ArgumentParser(); p.add_argument('--vs',default='usd'); p.add_argument('--per-page',type=int,default=80); p.add_argument('--db',default='data/crypto_intel.sqlite3'); p.add_argument('--out',default='reports/crypto_intel_report.md'); p.add_argument('--html',default='reports/crypto_intel_report.html'); p.add_argument('--telegram',action='store_true',help='Send the report to Telegram (TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID)')
    a=p.parse_args(); Path(a.db).parent.mkdir(parents=True,exist_ok=True); Path(a.out).parent.mkdir(parents=True,exist_ok=True); Path(a.html).parent.mkdir(parents=True,exist_ok=True)
    ts=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M UTC'); coins=fetch_markets(a.vs,a.per_page); con=init_db(a.db); saved=save_snapshot(con,coins,ts); alerts=detect_alerts(coins); md=render_markdown(coins,alerts,ts,a.vs); Path(a.out).write_text(md,encoding='utf-8'); Path(a.html).write_text(render_html(md),encoding='utf-8'); print(f'OK saved={saved} alerts={len(alerts)} db={a.db} markdown={a.out} html={a.html}\n'+md)
    if a.telegram:
        from telegram_notify import load_env, notify_safe
        load_env(); notify_safe(md)
if __name__=='__main__': main()
