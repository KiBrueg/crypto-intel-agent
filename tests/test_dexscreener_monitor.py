#!/usr/bin/env python3
import importlib.util, sys, tempfile
from pathlib import Path
p = Path(__file__).parents[1] / 'dexscreener_monitor.py'
spec = importlib.util.spec_from_file_location('dex', p)
dex = importlib.util.module_from_spec(spec); sys.modules['dex'] = dex; spec.loader.exec_module(dex)
pairs = [dex.Pair('solana','raydium','p1','AAA','Alpha','SOL',0.01,200_000,80_000,35,1_000_000,'https://dex/a'), dex.Pair('ethereum','uniswap','p2','BBB','Beta','WETH',1.2,10_000,2_000_000,-5,5_000_000,'https://dex/b'), dex.Pair('base','aerodrome','p3','CCC','Gamma','USDC',0.5,500_000,100_000,-60,2_000_000,'https://dex/c')]
alerts = dex.detect_alerts(pairs, min_liquidity=50_000, min_volume=100_000, change_threshold=25, vol_liq_threshold=2)
assert any(a.symbol == 'AAA' and a.reason == 'liquidity+volume candidate' for a in alerts)
assert any(a.symbol == 'CCC' and a.severity == 'HIGH' for a in alerts)
md = dex.render_markdown('TEST', pairs, alerts, 'NOW')
assert 'not financial advice' in md.lower()
assert '<html' in dex.render_html(md)
with tempfile.TemporaryDirectory() as d:
    con = dex.init_db(Path(d) / 'dex.sqlite3')
    assert dex.save_pairs(con, 'TEST', pairs, 'NOW') == 3
    assert con.execute('select count(*) from dex_pairs').fetchone()[0] == 3
    con.close()
print('OK DexScreener tests passed')
