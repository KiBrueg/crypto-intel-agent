#!/usr/bin/env python3
"""Safe DexScreener discovery monitor. No trading, no financial advice."""
from __future__ import annotations
import argparse, datetime as dt, html, json, math, sqlite3, textwrap, urllib.parse, urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any
API='https://api.dexscreener.com/latest/dex/search'
@dataclass
class Pair:
    chain:str; dex:str; pair_address:str; base_symbol:str; base_name:str; quote_symbol:str; price_usd:float|None; volume_24h:float|None; liquidity_usd:float|None; change_24h:float|None; fdv:float|None; url:str
    @classmethod
    def from_api(cls,row:dict[str,Any]):
        b=row.get('baseToken') or {}; q=row.get('quoteToken') or {}; v=row.get('volume') or {}; l=row.get('liquidity') or {}; ch=row.get('priceChange') or {}
        return cls(str(row.get('chainId') or ''),str(row.get('dexId') or ''),str(row.get('pairAddress') or ''),str(b.get('symbol') or ''),str(b.get('name') or ''),str(q.get('symbol') or ''),num(row.get('priceUsd')),num(v.get('h24')),num(l.get('usd')),num(ch.get('h24')),num(row.get('fdv')),str(row.get('url') or ''))
    @property
    def volume_to_liquidity(self): return None if not self.volume_24h or not self.liquidity_usd or self.liquidity_usd<=0 else self.volume_24h/self.liquidity_usd
@dataclass(frozen=True)
class DexAlert: severity:str; symbol:str; chain:str; reason:str; value:str; url:str
def num(x):
    try:
        if x is None: return None
        y=float(x); return None if math.isnan(y) or math.isinf(y) else y
    except Exception: return None
def fetch_pairs(query='SOL', limit=30):
    req=urllib.request.Request(API+'?'+urllib.parse.urlencode({'q':query}),headers={'User-Agent':'dexscreener-monitor/1.0'})
    with urllib.request.urlopen(req,timeout=30) as r: data=json.loads(r.read().decode())
    pairs=data.get('pairs') or []
    if not isinstance(pairs,list): raise RuntimeError('Unexpected DexScreener response')
    return [Pair.from_api(p) for p in pairs[:limit]]
def init_db(path):
    con=sqlite3.connect(path); con.execute('''CREATE TABLE IF NOT EXISTS dex_pairs(ts_utc TEXT, query TEXT, chain TEXT, dex TEXT, pair_address TEXT, base_symbol TEXT, base_name TEXT, quote_symbol TEXT, price_usd REAL, volume_24h REAL, liquidity_usd REAL, change_24h REAL, fdv REAL, volume_to_liquidity REAL, url TEXT, PRIMARY KEY(ts_utc, query, chain, pair_address))'''); return con
def save_pairs(con, query, pairs, ts):
    rows=[(ts,query,p.chain,p.dex,p.pair_address,p.base_symbol,p.base_name,p.quote_symbol,p.price_usd,p.volume_24h,p.liquidity_usd,p.change_24h,p.fdv,p.volume_to_liquidity,p.url) for p in pairs]
    con.executemany('INSERT OR REPLACE INTO dex_pairs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',rows); con.commit(); return len(rows)
def money(x):
    if x is None: return 'n/a'
    if x>=1_000_000_000: return f'${x/1_000_000_000:.2f}B'
    if x>=1_000_000: return f'${x/1_000_000:.1f}M'
    if x>=1: return f'${x:,.2f}'
    return f'${x:.8f}'
def pct(x): return 'n/a' if x is None else ('+' if x>0 else '')+f'{x:.2f}%'
def detect_alerts(pairs,min_liquidity=50_000,min_volume=100_000,change_threshold=25,vol_liq_threshold=2):
    out=[]
    for p in pairs:
        if p.liquidity_usd is not None and p.liquidity_usd>=min_liquidity and p.volume_24h is not None and p.volume_24h>=min_volume: out.append(DexAlert('MED',p.base_symbol,p.chain,'liquidity+volume candidate',f'liq {money(p.liquidity_usd)}, vol {money(p.volume_24h)}',p.url))
        if p.change_24h is not None and abs(p.change_24h)>=change_threshold: out.append(DexAlert('HIGH' if abs(p.change_24h)>=change_threshold*2 else 'MED',p.base_symbol,p.chain,'24h DEX price move',pct(p.change_24h),p.url))
        if p.volume_to_liquidity is not None and p.volume_to_liquidity>=vol_liq_threshold: out.append(DexAlert('MED',p.base_symbol,p.chain,'high volume/liquidity ratio',f'{p.volume_to_liquidity:.2f}x',p.url))
    seen=set(); res=[]
    for a in sorted(out,key=lambda x:(0 if x.severity=='HIGH' else 1,x.symbol,x.reason)):
        k=(a.symbol,a.chain,a.reason,a.url)
        if k not in seen: seen.add(k); res.append(a)
    return res
def pair_line(p):
    vl='n/a' if p.volume_to_liquidity is None else f'{p.volume_to_liquidity:.2f}x'
    return f'{p.base_symbol}/{p.quote_symbol} on {p.chain}/{p.dex} - price {money(p.price_usd)}, change {pct(p.change_24h)}, vol {money(p.volume_24h)}, liq {money(p.liquidity_usd)}, vol/liq {vl}'
def render_markdown(query,pairs,alerts,ts):
    topv=sorted([p for p in pairs if p.volume_24h is not None],key=lambda p:p.volume_24h or 0,reverse=True)[:8]
    ab='\n'.join(f'- **{a.severity}** {a.symbol} on {a.chain}: {a.reason} = {a.value} - {a.url}' for a in alerts[:15]) or '- No DEX threshold alerts.'
    return textwrap.dedent(f'''# DexScreener Monitor Report\n\n**Time:** {ts}\n**Query:** `{query}`\n**Pairs scanned:** {len(pairs)}\n**Mode:** token discovery / monitoring only - not financial advice.\n\n## Alerts\n{ab}\n\n## Top by 24h volume\n{chr(10).join('- '+pair_line(p) for p in topv)}\n''')
def render_html(md):
    body=[]
    for raw in md.splitlines():
        line=html.escape(raw.strip())
        if not line: continue
        if line.startswith('# '): body.append(f'<h1>{line[2:]}</h1>')
        elif line.startswith('## '): body.append(f'<h2>{line[3:]}</h2>')
        elif line.startswith('- '): body.append(f'<li>{line[2:]}</li>')
        else: body.append(f'<p>{line}</p>')
    return '<!doctype html><html><head><meta charset="utf-8"><title>DexScreener Monitor</title><style>body{background:#090d16;color:#e6edf7;font:16px Arial;padding:30px}main{max-width:1050px;margin:auto;background:#111827;border-radius:22px;padding:30px}h2{color:#a7f3d0}li{background:#172033;margin:8px 0;padding:10px;border-radius:10px;list-style:none}</style></head><body><main>'+'\n'.join(body)+'</main></body></html>'
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--query',default='SOL'); ap.add_argument('--limit',type=int,default=30); ap.add_argument('--db',default='data/dexscreener.sqlite3'); ap.add_argument('--out',default='reports/dexscreener_report.md'); ap.add_argument('--html',default='reports/dexscreener_report.html')
    a=ap.parse_args(); Path(a.db).parent.mkdir(parents=True,exist_ok=True); Path(a.out).parent.mkdir(parents=True,exist_ok=True); Path(a.html).parent.mkdir(parents=True,exist_ok=True)
    ts=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M UTC'); pairs=fetch_pairs(a.query,a.limit); con=init_db(a.db); saved=save_pairs(con,a.query,pairs,ts); alerts=detect_alerts(pairs); md=render_markdown(a.query,pairs,alerts,ts); Path(a.out).write_text(md,encoding='utf-8'); Path(a.html).write_text(render_html(md),encoding='utf-8'); print(f'OK query={a.query} saved={saved} alerts={len(alerts)} db={a.db} markdown={a.out} html={a.html}\n'+md)
if __name__=='__main__': main()
