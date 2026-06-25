#!/usr/bin/env python3
"""Local browser dashboard for Crypto Trader Assistant.

Run:
    python web_dashboard.py
Then open:
    http://127.0.0.1:8765
"""
from __future__ import annotations

import argparse
import json
import traceback
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from trader_assistant.binance_public import fetch_klines, fetch_depth
from trader_assistant.technical_analysis import analyze_candles
from trader_assistant.order_book import analyze_order_book
from trader_assistant.risk_reward import suggest_risk_reward_from_entry
from trader_assistant.fear_greed import fetch_fear_greed_index, evaluate_fear_greed
from trader_assistant.patterns import detect_classic_patterns
from trader_assistant.checklist import build_pro_trader_checklist
from trader_assistant.coach import build_trader_coach, load_learning_stats

DEFAULT_WATCHLIST = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 'LINKUSDT', 'DOGEUSDT', 'ADAUSDT']
DEFAULT_TIMEFRAMES = ('15m', '1h', '4h')
CONFIG_PATH = Path(__file__).with_name('dashboard_config.json')


def _normalize_symbol(value):
    return str(value or '').strip().upper().replace('/', '')


def load_dashboard_config(path=CONFIG_PATH):
    config = {'watchlist': DEFAULT_WATCHLIST[:], 'default_symbol': DEFAULT_WATCHLIST[0], 'default_interval': '1h'}
    p = Path(path)
    if p.exists():
        try:
            raw = json.loads(p.read_text(encoding='utf-8'))
            if isinstance(raw.get('watchlist'), list):
                watchlist = [_normalize_symbol(x) for x in raw['watchlist'] if _normalize_symbol(x)]
                if watchlist:
                    config['watchlist'] = watchlist
                    if not raw.get('default_symbol'):
                        config['default_symbol'] = watchlist[0]
            if raw.get('default_symbol'):
                config['default_symbol'] = _normalize_symbol(raw['default_symbol'])
            if raw.get('default_interval'):
                config['default_interval'] = str(raw['default_interval'])
        except Exception as exc:
            config['config_warning'] = f'Could not load {p}: {exc}'
    if config['default_symbol'] not in config['watchlist']:
        config['watchlist'].insert(0, config['default_symbol'])
    return config


def build_watchlist_payload(path=CONFIG_PATH):
    cfg = load_dashboard_config(path)
    return {'watchlist': cfg['watchlist'], 'default_symbol': cfg['default_symbol'], 'default_interval': cfg['default_interval']}


def get_watchlist():
    return load_dashboard_config()['watchlist']


def _to_float(value, default=None):
    try:
        if value in (None, ''):
            return default
        return float(value)
    except Exception:
        return default


def classify_rr_quality(value):
    v = _to_float(value)
    if v is None:
        return {'label': 'n/a', 'class': 'muted', 'message': 'No valid R/R yet'}
    if v < 1.0:
        return {'label': 'weak', 'class': 'bad', 'message': 'Reward is smaller than risk'}
    if v < 2.0:
        return {'label': 'acceptable', 'class': 'warn', 'message': 'Usable only with strong confirmation'}
    if v < 3.0:
        return {'label': 'strong', 'class': 'good', 'message': 'Good arithmetic if setup confirms'}
    return {'label': 'excellent', 'class': 'good', 'message': 'Excellent arithmetic; still verify liquidity and invalidation'}


def _context_from_analysis(analysis, order_book):
    price = float(analysis.get('price') or 0)
    vwap = float(analysis.get('indicators', {}).get('vwap') or price or 1)
    return {
        'trend': analysis.get('trend', 'mixed'),
        'price_vs_vwap_pct': round((price - vwap) / vwap * 100, 4) if vwap else 0.0,
        'rsi_14': analysis.get('indicators', {}).get('rsi_14', 50),
        'order_book_imbalance': order_book.get('imbalance', 0),
        'spread_bps': order_book.get('spread_bps') or 0,
    }


def _timeframe_row(interval, analysis):
    ind = analysis.get('indicators', {})
    price = float(analysis.get('price') or 0)
    vwap = float(ind.get('vwap') or price or 1)
    return {
        'interval': interval,
        'price': analysis.get('price'),
        'trend': analysis.get('trend'),
        'rsi_14': ind.get('rsi_14'),
        'ema_9': ind.get('ema_9'),
        'ema_21': ind.get('ema_21'),
        'price_vs_vwap_pct': round((price - vwap) / vwap * 100, 4) if vwap else 0.0,
        'note': '; '.join(analysis.get('setup_notes', [])[:2]),
    }


def build_multi_timeframe_payload(symbol='BTCUSDT', intervals=DEFAULT_TIMEFRAMES, limit=120, klines_fetcher=fetch_klines):
    frames = []
    for interval in intervals:
        candles = klines_fetcher(symbol.upper(), interval, int(limit))
        analysis = analyze_candles(symbol.upper(), candles)
        frames.append(_timeframe_row(interval, analysis))
    return {'symbol': symbol.upper(), 'frames': frames, 'generated_at': datetime.now(timezone.utc).isoformat()}


def build_risk_reward_payload(analysis, entry=None, side='long', stop=None, target=None):
    if entry is None:
        entry = analysis.get('price')
    rr = suggest_risk_reward_from_entry(analysis, entry=entry, side=side, stop=stop, target=target)
    rr['rr_quality'] = classify_rr_quality(rr.get('risk_reward_ratio'))
    return rr


def build_snapshot_payload(
    symbol='BTCUSDT', interval='1h', limit=120, entry=None, side='long', stop=None, target=None,
    klines_fetcher=fetch_klines, depth_fetcher=fetch_depth, fear_greed_fetcher=fetch_fear_greed_index,
):
    symbol = symbol.upper()
    candles = klines_fetcher(symbol, interval, int(limit))
    analysis = analyze_candles(symbol, candles)
    bids, asks = depth_fetcher(symbol, 50)
    order_book = analyze_order_book(bids, asks, mid_price=analysis['price'])
    rr = build_risk_reward_payload(analysis, entry=entry, side=side, stop=stop, target=target)
    fg_raw = fear_greed_fetcher()
    fg_value = int(fg_raw.get('value', 50))
    context = _context_from_analysis(analysis, order_book)
    fg = evaluate_fear_greed(fg_value, btc_context=context, eth_context=context, breadth={'share_above_vwap': 0.5, 'median_24h_change': 0.0, 'risk_assets_outperform_btc': False})
    mtf = build_multi_timeframe_payload(symbol, klines_fetcher=klines_fetcher)
    patterns = detect_classic_patterns(analysis.get('candles', []))
    partial = {
        'symbol': symbol,
        'analysis': {k: v for k, v in analysis.items() if k != 'candles'},
        'multi_timeframe': mtf,
        'order_book': order_book,
        'risk_reward': rr,
        'fear_greed': fg,
        'classic_patterns': patterns,
    }
    pro_checklist = build_pro_trader_checklist(partial)
    coach_snapshot = {**partial, 'pro_checklist': pro_checklist}
    return {
        'symbol': symbol,
        'interval': interval,
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'watchlist': get_watchlist(),
        'analysis': {k: v for k, v in analysis.items() if k != 'candles'},
        'multi_timeframe': mtf,
        'candles': analysis.get('candles', [])[-120:],
        'order_book': order_book,
        'risk_reward': rr,
        'fear_greed': fg,
        'classic_patterns': patterns,
        'pro_checklist': pro_checklist,
        'trader_coach': build_trader_coach(coach_snapshot, load_learning_stats()),
    }


def render_dashboard_html():
    config = load_dashboard_config()
    watch_buttons = ''.join(f'<button class="chip" onclick="setSymbol(\'{s}\')">{s}</button>' for s in config['watchlist'])
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Crypto Trader Assistant</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root{{--bg:#070713;--panel:#101114;--panel2:#161625;--text:#f7f7fb;--muted:#9497a9;--line:#2a2b3c;--purple:#7132f5;--purple2:#9b7cff;--green:#149e61;--red:#ef4444;--amber:#f59e0b;}}
    *{{box-sizing:border-box}} body{{margin:0;background:radial-gradient(circle at 20% -10%,rgba(113,50,245,.32),transparent 34%),linear-gradient(135deg,#050510,#101114);font-family:Inter,system-ui,sans-serif;color:var(--text)}}
    .wrap{{max-width:1400px;margin:0 auto;padding:24px}}.hero{{display:flex;justify-content:space-between;gap:20px;align-items:flex-start;margin-bottom:18px}}.kicker{{color:var(--purple2);font-weight:700;font-size:12px;letter-spacing:.12em;text-transform:uppercase}}.title{{font-size:42px;font-weight:800;letter-spacing:-1px;margin:8px 0}}.sub{{color:var(--muted);max-width:850px;line-height:1.5}}.grid{{display:grid;grid-template-columns:360px 1fr;gap:16px}}.card{{background:rgba(16,17,20,.92);border:1px solid rgba(148,151,169,.18);border-radius:18px;padding:18px;box-shadow:rgba(0,0,0,.22) 0 18px 60px}}.controls label{{display:block;color:var(--muted);font-size:12px;margin:12px 0 5px}}.controls input,.controls select{{width:100%;background:#0b0b16;color:var(--text);border:1px solid var(--line);border-radius:12px;padding:12px;font:inherit}}.row{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}.btn{{width:100%;margin-top:14px;border:0;background:var(--purple);color:#fff;border-radius:12px;padding:13px 16px;font-weight:700;cursor:pointer}}.btn.secondary{{background:rgba(113,50,245,.16);color:#c9b8ff;border:1px solid rgba(113,50,245,.45)}}.metrics{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:16px}}.metric{{background:var(--panel2);border:1px solid var(--line);border-radius:16px;padding:14px}}.metric .l{{color:var(--muted);font-size:12px}}.metric .v{{font-size:22px;font-weight:800;margin-top:4px}}.chart{{height:340px;width:100%;background:#080814;border:1px solid var(--line);border-radius:18px}}.sections{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px}}.section h3{{margin:0 0 10px;font-size:16px}}.list{{margin:0;padding-left:18px;color:#dfe3ee;line-height:1.65}}.pill,.chip{{display:inline-flex;align-items:center;border-radius:999px;padding:6px 10px;background:rgba(113,50,245,.18);color:#c9b8ff;font-size:12px;font-weight:700;border:1px solid rgba(113,50,245,.3)}}.chip{{margin:4px 5px 4px 0;cursor:pointer}}.good{{color:#5ee08c}}.bad{{color:#ff7b7b}}.warn{{color:#fbbf24}}.muted{{color:var(--muted)}}.mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}.error{{white-space:pre-wrap;color:#ffb4b4}}.small{{font-size:12px;color:var(--muted);line-height:1.45}}.tfgrid{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}}.tf{{background:#0b0b16;border:1px solid var(--line);border-radius:14px;padding:12px}}.tf b{{display:block;margin-bottom:6px}}@media(max-width:1000px){{.grid,.sections{{grid-template-columns:1fr}}.metrics{{grid-template-columns:1fr 1fr}}.title{{font-size:32px}}}}
  </style>
</head>
<body><div class="wrap">
  <div class="hero"><div><div class="kicker">local browser dashboard</div><h1 class="title">Crypto Trader Assistant</h1><div class="sub">Turnkey decision-support dashboard: watchlist, multi-timeframe context, VWAP/EMA/RSI/ATR, levels, order book, Fear/Greed confirmation and entry-based risk/reward. Not financial advice.</div></div><span class="pill">127.0.0.1 local</span></div>
  <div class="grid">
    <div class="card controls">
      <h2>Controls</h2>
      <label>Watchlist</label><div>{watch_buttons}</div>
      <label>Symbol</label><input id="symbol" value="{config['default_symbol']}">
      <div class="row"><div><label>Interval</label><select id="interval"><option>15m</option><option selected>1h</option><option>4h</option><option>1d</option></select></div><div><label>Side</label><select id="side"><option>long</option><option>short</option></select></div></div>
      <label>Entry</label><input id="entry" type="number" step="any" placeholder="optional, default=current price">
      <div class="row"><div><label>Stop</label><input id="stop" type="number" step="any" placeholder="auto"></div><div><label>Target</label><input id="target" type="number" step="any" placeholder="auto"></div></div>
      <button class="btn" onclick="loadSnapshot()">Refresh dashboard</button>
      <button class="btn secondary" onclick="calcRR()">Calculate R/R only</button>
      <button class="btn secondary" onclick="exportJSON()">Export JSON</button>
      <label><input id="autorefresh" type="checkbox" style="width:auto;margin-right:8px" onchange="toggleAuto()">Auto refresh 60s</label>
      <p class="small">Manual stop/target wins. If empty, the dashboard infers stop/target from nearby support/resistance, pivots, Fibonacci and ATR buffer.</p>
    </div>
    <div>
      <div class="metrics" id="metrics"></div>
      <canvas class="chart" id="chart" width="980" height="340"></canvas>
      <div class="card section" style="margin-top:16px"><h3>Pro Trader Checklist</h3><div id="checklist"></div></div>
      <div class="card section" style="margin-top:16px"><h3>Trader Coach</h3><div id="coach"></div></div>
      <div class="card section" style="margin-top:16px"><h3>Multi-Timeframe</h3><div id="mtf" class="tfgrid"></div></div>
      <div class="sections">
        <div class="card section"><h3>Technical Context</h3><ul class="list" id="tech"></ul></div>
        <div class="card section"><h3>Risk/Reward</h3><ul class="list" id="rr"></ul></div>
        <div class="card section"><h3>Classic Price Patterns</h3><ul class="list" id="patterns"></ul></div>
        <div class="card section"><h3>Fear/Greed Confirmation</h3><ul class="list" id="fg"></ul></div>
        <div class="card section"><h3>Order Book / Levels</h3><ul class="list" id="book"></ul></div>
      </div>
    </div>
  </div>
</div>
<script>
const $=id=>document.getElementById(id); let lastSnapshot=null, autoTimer=null;
function q(){{const p=new URLSearchParams(); ['symbol','interval','side','entry','stop','target'].forEach(id=>{{if($(id).value)p.set(id,$(id).value)}}); return p.toString();}}
function fmt(x){{return x===null||x===undefined?'n/a':(typeof x==='number'?Number(x.toFixed(6)).toString():x)}}
function li(items){{return items.map(x=>`<li>${{x}}</li>`).join('')}}
function setSymbol(s){{$('symbol').value=s; loadSnapshot();}}
async function loadSnapshot(){{setLoading(); try{{const [sr, mr]=await Promise.all([fetch('/api/snapshot?'+q()), fetch('/api/multi-timeframe?symbol='+encodeURIComponent($('symbol').value))]); const data=await sr.json(); const mtf=await mr.json(); if(data.error) throw new Error(data.error); if(mtf.error) throw new Error(mtf.error); data.multi_timeframe=mtf; render(data);}}catch(e){{showError(e)}}}}
async function calcRR(){{try{{const p=new URLSearchParams(q()); const r=await fetch('/api/risk-reward?'+p.toString()); const rr=await r.json(); if(rr.error) throw new Error(rr.error); renderRR(rr);}}catch(e){{showError(e)}}}}
function exportJSON(){{if(!lastSnapshot)return; const blob=new Blob([JSON.stringify(lastSnapshot,null,2)],{{type:'application/json'}}); const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download=`crypto-trader-snapshot-${{lastSnapshot.symbol}}.json`; a.click(); URL.revokeObjectURL(a.href);}}
function toggleAuto(){{if(autoTimer){{clearInterval(autoTimer);autoTimer=null}} if($('autorefresh').checked) autoTimer=setInterval(loadSnapshot,60000)}}
function setLoading(){{ $('metrics').innerHTML='<div class="metric"><div class="l">Status</div><div class="v">Loading…</div></div>'; }}
function showError(e){{$('metrics').innerHTML=`<div class="metric"><div class="l">Error</div><div class="v bad">Failed</div></div>`; $('tech').innerHTML=`<li class="error">${{e.stack||e}}</li>`}}
function render(data){{lastSnapshot=data; const a=data.analysis, ind=a.indicators, ob=data.order_book, rr=data.risk_reward, fg=data.fear_greed, ql=(rr.rr_quality||{{label:'n/a',class:'muted'}});
 $('metrics').innerHTML=[['Symbol',data.symbol,''],['Price',fmt(a.price),''],['Trend',a.trend,a.trend==='bearish'?'bad':(a.trend==='bullish'?'good':'warn')],['R/R',fmt(rr.risk_reward_ratio),ql.class],['Quality',ql.label,ql.class]].map(m=>`<div class="metric"><div class="l">${{m[0]}}</div><div class="v ${{m[2]}}">${{m[1]}}</div></div>`).join('');
 $('tech').innerHTML=li([`EMA9/EMA21: <span class="mono">${{fmt(ind.ema_9)}} / ${{fmt(ind.ema_21)}}</span>`,`VWAP: <span class="mono">${{fmt(ind.vwap)}}</span>`,`RSI14: <span class="mono">${{fmt(ind.rsi_14)}}</span>`,`ATR14: <span class="mono">${{fmt(ind.atr_14)}}</span>`,...(a.setup_notes||[])]);
 renderRR(rr); renderChecklist(data.pro_checklist); renderCoach(data.trader_coach); renderMTF(data.multi_timeframe); renderPatterns(data.classic_patterns||[]); $('fg').innerHTML=li([`Index: <b>${{fg.index_value}}</b> / ${{fg.label}}`,`Confirmation: <b>${{fg.confirmation}}</b>`,`Score: <span class="mono">${{fmt(fg.score)}}</span>`,fg.interpretation]);
 const fib=a.levels.fibonacci||{{}}, piv=a.levels.pivots||{{}}; $('book').innerHTML=li([`Spread: <span class="mono">${{fmt(ob.spread_bps)}}</span> bps`,`Imbalance: <span class="mono">${{fmt(ob.imbalance)}}</span>`,`Signals: ${{(ob.signals||['none']).join(', ')}}`,`Nearest: ${{(a.levels.nearest||[]).map(fmt).join(', ')}}`,`Fib .382/.5/.618: ${{fmt(fib['0.382'])}}, ${{fmt(fib['0.500'])}}, ${{fmt(fib['0.618'])}}`,`Pivot/R1/S1: ${{fmt(piv.pivot)}}, ${{fmt(piv.r1)}}, ${{fmt(piv.s1)}}`]);
 drawChart(data.candles, a.levels); }}
function renderRR(rr){{const q=rr.rr_quality||{{label:'n/a',class:'muted',message:''}}; $('rr').innerHTML=li([`Source: <b>${{rr.source}}</b>`,`Entry: <span class="mono">${{fmt(rr.entry)}}</span>`,`Stop: <span class="mono">${{fmt(rr.stop)}}</span>`,`Target: <span class="mono">${{fmt(rr.target)}}</span>`,`Risk: <span class="mono">${{fmt(rr.risk_per_unit)}}</span>`,`Reward: <span class="mono">${{fmt(rr.reward_per_unit)}}</span>`,`R/R: <b class="${{q.class}}">${{fmt(rr.risk_reward_ratio)}} / ${{q.label}}</b>`,`Quality note: ${{q.message}}`,`Valid: ${{rr.valid}}`,`Invalidation: ${{rr.invalidation||'n/a'}}`,...(rr.warnings||[]).map(w=>`Warning: <span class="warn">${{w}}</span>`)]);}}
function renderChecklist(c){{if(!c) return; const cls=c.status==='clean'?'good':(c.status==='not_clean'?'bad':'warn'); $('checklist').innerHTML=`<div class="metric"><div class="l">Readiness</div><div class="v ${{cls}}">${{c.readiness_score}} / 100 — ${{c.status}}</div></div><p class="small">${{c.summary}}</p><ul class="list">${{c.checklist.map(x=>`<li><b>${{x.name}}</b>: <span class="${{x.status==='pass'?'good':(x.status==='fail'?'bad':'warn')}}">${{x.status}}</span> — ${{x.detail}}</li>`).join('')}}</ul><p class="small"><b>Next checks:</b> ${{(c.next_checks||[]).slice(0,3).join(' · ')}}</p>`;}}
function renderCoach(c){{if(!c) return; $('coach').innerHTML=`<p><b>${{c.headline}}</b></p><p class="small">${{c.explain_like_pro}}</p><h4>Teaching points</h4><ul class="list">${{(c.teaching_points||[]).map(x=>`<li>${{x}}</li>`).join('')}}</ul><h4>What to wait for</h4><ul class="list">${{(c.what_to_wait_for||[]).map(x=>`<li>${{x}}</li>`).join('')}}</ul>${{(c.learning_notes||[]).length?`<h4>Learning memory</h4><ul class="list">${{c.learning_notes.map(x=>`<li>${{x}}</li>`).join('')}}</ul>`:''}}`;}}
function renderMTF(mtf){{if(!mtf||!mtf.frames) return; $('mtf').innerHTML=mtf.frames.map(f=>`<div class="tf"><b>${{f.interval}}</b><div>Trend: <span class="${{f.trend==='bearish'?'bad':(f.trend==='bullish'?'good':'warn')}}">${{f.trend}}</span></div><div>RSI: ${{fmt(f.rsi_14)}}</div><div>VWAP Δ: ${{fmt(f.price_vs_vwap_pct)}}%</div><div class="small">${{f.note||''}}</div></div>`).join('');}}
function renderPatterns(patterns){{if(!patterns.length){{$('patterns').innerHTML='<li>No high-signal classic pattern detected. Wait for cleaner structure.</li>'; return;}} $('patterns').innerHTML=patterns.map(p=>`<li><b class="${{p.bias==='bearish'?'bad':(p.bias==='bullish'?'good':'warn')}}">${{p.name}}</b> — ${{p.bias}}, confidence ${{fmt(p.confidence)}}<br><span class="small">${{p.trader_note}}</span></li>`).join('');}}
function drawChart(candles, levels){{const c=$('chart'), ctx=c.getContext('2d'), w=c.width,h=c.height; ctx.clearRect(0,0,w,h); ctx.fillStyle='#080814'; ctx.fillRect(0,0,w,h); if(!candles||!candles.length)return; const hi=Math.max(...candles.map(x=>x.high)), lo=Math.min(...candles.map(x=>x.low)), span=hi-lo||1, pad=28; const X=i=>pad+i*(w-pad*2)/Math.max(1,candles.length-1), Y=p=>pad+(hi-p)/span*(h-pad*2);
 const all=[...(levels.support_resistance||[]),...Object.values(levels.fibonacci||{{}}),...Object.values(levels.pivots||{{}})]; ctx.font='10px Inter'; all.forEach((lv,i)=>{{const y=Y(lv); if(y<pad||y>h-pad)return; ctx.strokeStyle=i%2?'#7132f5':'#334155'; ctx.setLineDash([4,4]); ctx.beginPath(); ctx.moveTo(pad,y); ctx.lineTo(w-pad,y); ctx.stroke(); ctx.setLineDash([]);}});
 candles.forEach((k,i)=>{{const x=X(i), o=Y(k.open), cl=Y(k.close), hh=Y(k.high), ll=Y(k.low), up=k.close>=k.open; ctx.strokeStyle=up?'#149e61':'#ef4444'; ctx.fillStyle=ctx.strokeStyle; ctx.beginPath(); ctx.moveTo(x,hh); ctx.lineTo(x,ll); ctx.stroke(); ctx.fillRect(x-2,Math.min(o,cl),4,Math.max(1,Math.abs(cl-o)));}});}}
loadSnapshot();
</script></body></html>'''


class DashboardHandler(BaseHTTPRequestHandler):
    def _send(self, status, content, ctype='application/json'):
        raw = content if isinstance(content, bytes) else content.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', ctype + '; charset=utf-8')
        self.send_header('Content-Length', str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        try:
            if parsed.path == '/':
                return self._send(200, render_dashboard_html(), 'text/html')
            if parsed.path == '/api/snapshot':
                return self._send(200, json.dumps(_payload_from_qs(qs), ensure_ascii=False))
            if parsed.path == '/api/risk-reward':
                symbol = (qs.get('symbol') or ['BTCUSDT'])[0].upper()
                interval = (qs.get('interval') or ['1h'])[0]
                candles = fetch_klines(symbol, interval, 120)
                analysis = analyze_candles(symbol, candles)
                rr = build_risk_reward_payload(analysis, entry=_to_float((qs.get('entry') or [None])[0], analysis['price']), side=(qs.get('side') or ['long'])[0], stop=_to_float((qs.get('stop') or [None])[0]), target=_to_float((qs.get('target') or [None])[0]))
                return self._send(200, json.dumps(rr, ensure_ascii=False))
            if parsed.path == '/api/multi-timeframe':
                symbol = (qs.get('symbol') or ['BTCUSDT'])[0].upper()
                return self._send(200, json.dumps(build_multi_timeframe_payload(symbol), ensure_ascii=False))
            if parsed.path == '/api/watchlist':
                return self._send(200, json.dumps(build_watchlist_payload(), ensure_ascii=False))
            return self._send(404, json.dumps({'error': 'not found'}))
        except Exception as e:
            return self._send(500, json.dumps({'error': str(e), 'trace': traceback.format_exc()}))

    def log_message(self, fmt, *args):
        print('[dashboard]', fmt % args)


def _payload_from_qs(qs):
    symbol = (qs.get('symbol') or ['BTCUSDT'])[0]
    interval = (qs.get('interval') or ['1h'])[0]
    side = (qs.get('side') or ['long'])[0]
    return build_snapshot_payload(symbol=symbol, interval=interval, limit=120, entry=_to_float((qs.get('entry') or [None])[0]), side=side, stop=_to_float((qs.get('stop') or [None])[0]), target=_to_float((qs.get('target') or [None])[0]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--host', default='127.0.0.1')
    ap.add_argument('--port', type=int, default=8765)
    args = ap.parse_args()
    srv = ThreadingHTTPServer((args.host, args.port), DashboardHandler)
    print(f'Crypto Trader Assistant dashboard: http://{args.host}:{args.port}')
    srv.serve_forever()


if __name__ == '__main__':
    main()
