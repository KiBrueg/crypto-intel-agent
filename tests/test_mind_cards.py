#!/usr/bin/env python3
from pathlib import Path
import tempfile
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from trader_assistant.journal import init_journal
from trader_assistant.mind_cards import build_mind_card, save_mind_card, record_user_choice, mind_card_detail, build_historical_mind_card


def candle(ts, open_, high, low, close, volume=100):
    return {'ts': ts, 'open': open_, 'high': high, 'low': low, 'close': close, 'volume': volume}


def sample_snapshot():
    candles = [
        candle(1000, 100, 101, 99, 100, 100),
        candle(2000, 100, 103, 99, 102, 140),
        candle(3000, 102, 104, 101, 103, 160),
        candle(4000, 103, 105, 102, 104, 220),
    ]
    return {
        'symbol': 'BTCUSDT',
        'interval': '15m',
        'candles': candles,
        'analysis': {'trend': 'bullish', 'price': 104, 'vwap': 101.5, 'rsi_14': 62},
        'risk_reward': {'entry': 104, 'stop': 101, 'target': 110, 'risk_reward_ratio': 2.0, 'valid': True},
        'pro_checklist': {'status': 'clean', 'readiness_score': 78},
        'council': {'chair': {'verdict': 'clean'}},
        'smc': {'bias': 'bullish', 'score': 2, 'zones': []},
        'order_book': {'spread_pct': 0.03, 'bid_ask_imbalance': 0.12},
    }


def test_build_mind_card_has_compact_cockpit_fields():
    card = build_mind_card(sample_snapshot(), mode='mixed')
    assert card['mode'] == 'mixed'
    assert card['exchange'] == 'BINANCE'
    assert card['symbol'] == 'BTCUSDT'
    assert card['ai_direction'] == 'up'
    assert card['ai_size'] in ('small', 'medium', 'large', 'none')
    assert 0 <= card['ai_confidence'] <= 1
    assert card['potential_profit_pct'] > 0
    assert card['risk_loss_pct'] > 0
    assert card['risk_reward_ratio'] == 2.0
    assert 'fomo_score' in card
    assert 'setup_quality' in card
    assert 'market_regime' in card
    assert len(card['chart_window']) == 4


def test_save_card_and_record_user_choice():
    with tempfile.TemporaryDirectory() as td:
        con = init_journal(Path(td) / 'test.sqlite3')
        try:
            card = build_mind_card(sample_snapshot(), mode='mixed')
            card_id = save_mind_card(con, card)
            record_user_choice(con, card_id, direction='up', size='medium')
            detail = mind_card_detail(con, card_id)
            assert detail['id'] == card_id
            assert detail['user_direction'] == 'up'
            assert detail['user_size'] == 'medium'
            assert detail['agreement_with_ai'] == 1
            assert detail['status'] == 'answered'
            assert detail['features']['trend'] == 'bullish'
        finally:
            con.close()


def test_historical_mind_cards_use_different_known_outcome_windows():
    base = sample_snapshot()
    candles = []
    price = 100.0
    for i in range(90):
        drift = 0.45 if i < 30 else (-0.35 if i < 60 else 0.25)
        open_ = price
        close = price + drift
        high = max(open_, close) + 0.4
        low = min(open_, close) - 0.4
        candles.append(candle(1000 + i * 60, open_, high, low, close, 100 + i))
        price = close
    base['candles'] = candles
    base['analysis'] = {'trend': 'mixed', 'price': candles[-1]['close'], 'vwap': candles[-1]['close'], 'rsi_14': 50}

    first = build_historical_mind_card(base, mode='mixed', seed=1, visible_candles=24, outcome_candles=6)
    second = build_historical_mind_card(base, mode='mixed', seed=2, visible_candles=24, outcome_candles=6)

    assert first['training_kind'] == 'historical_known_outcome'
    assert first['decision_ts'] != second['decision_ts']
    assert first['chart_window'] != second['chart_window']
    assert len(first['chart_window']) == 24
    assert 'known_outcome' in first
    assert first['known_outcome']['direction'] in ('up', 'down', 'flat')
    assert first['known_outcome']['future_candles'] == 6


if __name__ == '__main__':
    test_build_mind_card_has_compact_cockpit_fields()
    test_save_card_and_record_user_choice()
    test_historical_mind_cards_use_different_known_outcome_windows()
    print('OK mind cards tests passed')
