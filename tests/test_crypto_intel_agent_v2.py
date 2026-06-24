#!/usr/bin/env python3
import importlib.util, sys, tempfile
from pathlib import Path
p = Path(__file__).parents[1] / 'crypto_intel_agent_v2.py'
spec = importlib.util.spec_from_file_location('agent', p)
agent = importlib.util.module_from_spec(spec); sys.modules['agent'] = agent; spec.loader.exec_module(agent)
coins = [agent.Coin('a','AAA','Alpha',10,1,12.5,1_000_000,10_000_000,11,9), agent.Coin('b','BBB','Beta',20,2,-11,2_000_000,20_000_000,22,18), agent.Coin('c','CCC','Gamma',5,3,3,3_000_000,6_000_000,5.5,4.5)]
alerts = agent.detect_alerts(coins, 7, 10, .18)
assert any(a.symbol == 'AAA' and a.reason == '24h price move' for a in alerts)
assert any(a.symbol == 'BBB' and a.reason == '24h price move' for a in alerts)
assert any(a.symbol == 'CCC' and a.reason == 'high volume/market-cap' for a in alerts)
md = agent.render_markdown(coins, alerts, 'TEST', 'usd')
assert 'not financial advice' in md.lower()
assert '<html' in agent.render_html(md)
with tempfile.TemporaryDirectory() as d:
    con = agent.init_db(Path(d) / 't.sqlite3')
    assert agent.save_snapshot(con, coins, 'TEST') == 3
    assert con.execute('select count(*) from snapshots').fetchone()[0] == 3
    con.close()
print('OK tests passed')
