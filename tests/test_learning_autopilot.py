#!/usr/bin/env python3
from pathlib import Path
import tempfile
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from trader_assistant.journal import init_journal
from trader_assistant.learning_autopilot import (
    create_prediction_from_snapshot,
    save_prediction,
    verify_open_predictions,
    prediction_stats,
)


def candle(ts, open_, high, low, close):
    return {'ts': ts, 'open': open_, 'high': high, 'low': low, 'close': close, 'volume': 1}


def sample_snapshot():
    return {
        'symbol': 'BTCUSDT',
        'interval': '1h',
        'candles': [candle(1000, 100, 101, 99, 100)],
        'analysis': {'trend': 'bullish', 'price': 100},
        'risk_reward': {
            'entry': 100,
            'stop': 95,
            'target': 110,
            'risk_reward_ratio': 2.0,
            'rr_quality': {'label': 'strong'},
            'valid': True,
        },
        'pro_checklist': {'status': 'clean', 'readiness_score': 82},
        'council': {'chair': {'verdict': 'clean', 'action_bias': 'wait_for_confirmation'}},
        'smc': {'bias': 'bullish', 'score': 3, 'zones': [{'type': 'liquidity_sweep', 'direction': 'bullish'}]},
    }


def test_prediction_is_created_from_snapshot_features():
    pred = create_prediction_from_snapshot(sample_snapshot(), horizon_bars=3)
    assert pred['symbol'] == 'BTCUSDT'
    assert pred['predicted_direction'] == 'up'
    assert pred['predicted_status'] == 'clean'
    assert pred['entry'] == 100
    assert pred['start_ts'] == 1000
    assert pred['feature_summary']['smc_bias'] == 'bullish'


def test_autopilot_saves_and_verifies_prediction_target():
    with tempfile.TemporaryDirectory() as td:
        con = init_journal(Path(td) / 'test.sqlite3')
        pred_id = save_prediction(con, create_prediction_from_snapshot(sample_snapshot(), horizon_bars=3))
        future = [
            candle(1000, 100, 101, 99, 100),
            candle(2000, 100, 104, 99, 103),
            candle(3000, 103, 111, 102, 110),
            candle(4000, 110, 112, 109, 111),
        ]
        result = verify_open_predictions(con, lambda symbol, interval, limit: future)
        assert result['verified'] == 1
        stats = prediction_stats(con)
        assert stats['total'] == 1
        assert stats['verified'] == 1
        assert stats['outcomes']['target'] == 1
        row = con.execute('select * from predictions where id=?', (pred_id,)).fetchone()
        assert row['verified_outcome'] == 'target'
        assert row['correct_direction'] == 1
        con.close()


if __name__ == '__main__':
    test_prediction_is_created_from_snapshot_features()
    test_autopilot_saves_and_verifies_prediction_target()
    print('OK learning autopilot tests passed')
