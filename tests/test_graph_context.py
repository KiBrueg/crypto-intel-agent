#!/usr/bin/env python3
from pathlib import Path
import tempfile
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from trader_assistant.council import run_council
from trader_assistant.journal import init_journal, save_setup, mark_outcome, save_council_review
from trader_assistant.learning_autopilot import create_prediction_from_snapshot, save_prediction, verify_open_predictions
from trader_assistant.graph_context import build_graph_context
from web_dashboard import handle_journal_api


def candle(ts, open_, high, low, close):
    return {'ts': ts, 'open': open_, 'high': high, 'low': low, 'close': close, 'volume': 1}


def sample_snapshot(symbol='BTCUSDT', status='not_clean', smc_bias='bearish'):
    return {
        'symbol': symbol,
        'interval': '15m',
        'candles': [candle(1000, 100, 101, 99, 100)],
        'analysis': {'trend': 'bearish' if smc_bias == 'bearish' else 'bullish', 'price': 100},
        'risk_reward': {'entry': 100, 'stop': 95, 'target': 110, 'risk_reward_ratio': 0.8, 'rr_quality': {'label': 'weak'}},
        'pro_checklist': {'readiness_score': 35, 'status': status, 'blockers': ['Weak R/R']},
        'classic_patterns': [{'name': 'hammer', 'bias': 'bullish'}, {'name': 'bearish_engulfing', 'bias': 'bearish'}],
        'smc': {'bias': smc_bias, 'score': -2 if smc_bias == 'bearish' else 2, 'zones': [{'type': 'liquidity_sweep', 'direction': smc_bias}]},
        'council': {'chair': {'verdict': status, 'action_bias': 'wait_for_confirmation'}},
    }


def seed_memory(con):
    setup_id = save_setup(con, sample_snapshot())
    mark_outcome(con, setup_id, 'failed')
    council = run_council(sample_snapshot())
    save_council_review(con, sample_snapshot(), council)
    pred_id = save_prediction(con, create_prediction_from_snapshot(sample_snapshot(), horizon_bars=2))
    verify_open_predictions(con, lambda symbol, interval, limit: [
        candle(1000, 100, 101, 99, 100),
        candle(2000, 100, 102, 94, 96),
        candle(3000, 96, 97, 93, 94),
    ])
    return pred_id


def test_graph_context_is_compact_and_contains_calibration_hints():
    with tempfile.TemporaryDirectory() as d:
        con = init_journal(Path(d) / 'journal.sqlite3')
        try:
            seed_memory(con)
            ctx = build_graph_context(con, sample_snapshot(), max_chars=900)
        finally:
            con.close()
        assert ctx['mode'] == 'compact_graph_context'
        assert ctx['char_count'] <= 900
        joined = '\n'.join(ctx['context_lines'])
        assert 'failed' in joined or 'stopped' in joined
        assert ctx['calibration_hints']
        assert any('weak' in h.lower() or 'not_clean' in h.lower() for h in ctx['calibration_hints'])
        assert 'raw_nodes' not in ctx and 'raw_edges' not in ctx


def test_graph_context_api_returns_token_budgeted_summary():
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / 'journal.sqlite3'
        con = init_journal(db)
        try:
            seed_memory(con)
        finally:
            con.close()
        response = handle_journal_api('POST', '/api/graph-context', body={'snapshot': sample_snapshot(), 'max_chars': 700}, db_path=db)
        assert response['mode'] == 'compact_graph_context'
        assert response['char_count'] <= 700
        assert response['context_lines']


if __name__ == '__main__':
    test_graph_context_is_compact_and_contains_calibration_hints()
    test_graph_context_api_returns_token_budgeted_summary()
    print('OK graph context tests passed')
