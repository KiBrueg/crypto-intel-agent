#!/usr/bin/env python3
from pathlib import Path
import tempfile
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from trader_assistant.forecast_timeline import build_forecast_timeline
from trader_assistant.journal import init_journal
from trader_assistant.learning_autopilot import create_prediction_from_snapshot, save_prediction


def sample_snapshot(symbol='BTCUSDT', trend='bullish'):
    return {
        'symbol': symbol,
        'interval': '1h',
        'candles': [{'ts': 1_700_000_000_000, 'open': 100, 'high': 101, 'low': 99, 'close': 100, 'volume': 1}],
        'analysis': {'trend': trend, 'price': 100},
        'risk_reward': {'entry': 100, 'stop': 95, 'target': 110, 'risk_reward_ratio': 2.0, 'rr_quality': {'label': 'strong'}},
        'pro_checklist': {'status': 'clean', 'readiness_score': 80},
        'council': {'chair': {'verdict': 'clean'}},
        'smc': {'bias': 'bullish' if trend == 'bullish' else 'bearish', 'score': 2},
    }


def test_forecast_timeline_returns_last_forecast_and_events():
    with tempfile.TemporaryDirectory() as td:
        db = Path(td) / 'test.sqlite3'
        con = init_journal(db)
        try:
            save_prediction(con, create_prediction_from_snapshot(sample_snapshot('BTCUSDT', 'bullish'), horizon_bars=4))
            save_prediction(con, create_prediction_from_snapshot(sample_snapshot('ETHUSDT', 'bearish'), horizon_bars=4))
            timeline = build_forecast_timeline(con, limit=10)
        finally:
            con.close()
        assert timeline['mode'] == 'forecast_timeline'
        assert timeline['summary']['total_events'] == 2
        assert timeline['summary']['pending'] == 2
        assert timeline['last_forecast']['symbol'] == 'ETHUSDT'
        assert timeline['events'][0]['symbol'] == 'ETHUSDT'
        assert timeline['events'][0]['display_status'] == 'pending'
        assert timeline['events'][0]['due']['state'] in ('pending', 'due')
        assert timeline['events'][0]['direction'] in ('up', 'down')


if __name__ == '__main__':
    test_forecast_timeline_returns_last_forecast_and_events()
    print('OK forecast timeline tests passed')
