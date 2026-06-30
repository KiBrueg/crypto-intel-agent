#!/usr/bin/env python3
from pathlib import Path
import tempfile
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from trader_assistant.forecast_details import build_forecast_detail
from trader_assistant.journal import init_journal
from trader_assistant.learning_autopilot import create_prediction_from_snapshot, save_prediction


def sample_snapshot():
    return {
        'symbol': 'BTCUSDT',
        'interval': '1h',
        'candles': [{'ts': 1_700_000_000_000, 'open': 100, 'high': 101, 'low': 99, 'close': 100, 'volume': 1}],
        'analysis': {'trend': 'bullish', 'price': 100},
        'risk_reward': {'entry': 100, 'stop': 95, 'target': 110, 'risk_reward_ratio': 2.0, 'rr_quality': {'label': 'strong'}},
        'pro_checklist': {'status': 'clean', 'readiness_score': 80},
        'council': {'chair': {'verdict': 'clean'}},
        'smc': {'bias': 'bullish', 'score': 2},
    }


def test_forecast_detail_returns_explainable_prediction_payload():
    with tempfile.TemporaryDirectory() as td:
        db = Path(td) / 'test.sqlite3'
        con = init_journal(db)
        try:
            pred = create_prediction_from_snapshot(sample_snapshot(), horizon_bars=4)
            pred_id = save_prediction(con, pred)
            detail = build_forecast_detail(con, pred_id)
        finally:
            con.close()
        assert detail['mode'] == 'forecast_detail'
        assert detail['forecast']['id'] == pred_id
        assert detail['forecast']['symbol'] == 'BTCUSDT'
        assert detail['risk_plan']['entry'] == 100
        assert detail['risk_plan']['stop'] == 95
        assert detail['risk_plan']['target'] == 110
        assert detail['context']['smc_bias'] == 'bullish'
        assert detail['context']['council_verdict'] == 'clean'
        assert detail['forecast']['due']['state'] in ('pending', 'due')
        assert detail['explanation'][0].startswith('Forecast')


def test_forecast_detail_handles_missing_id():
    with tempfile.TemporaryDirectory() as td:
        con = init_journal(Path(td) / 'test.sqlite3')
        try:
            detail = build_forecast_detail(con, 999)
        finally:
            con.close()
        assert detail['mode'] == 'forecast_detail'
        assert detail['error'] == 'not_found'


if __name__ == '__main__':
    test_forecast_detail_returns_explainable_prediction_payload()
    test_forecast_detail_handles_missing_id()
    print('OK forecast detail tests passed')
