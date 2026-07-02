from __future__ import annotations

import json
import random
from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc).isoformat()


def _json(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def _loads(text, fallback):
    try:
        return json.loads(text) if text else fallback
    except Exception:
        return fallback


def _pct(a, b):
    try:
        if not a or not b:
            return None
        return abs(float(a) - float(b)) / float(a) * 100
    except Exception:
        return None


def _direction(snapshot):
    analysis = snapshot.get('analysis') or {}
    smc = snapshot.get('smc') or {}
    trend = str(analysis.get('trend') or '').lower()
    smc_bias = str(smc.get('bias') or '').lower()
    if 'bull' in trend or 'bull' in smc_bias:
        return 'up'
    if 'bear' in trend or 'bear' in smc_bias:
        return 'down'
    return 'skip'


def _size_from_quality(readiness, rr_ratio):
    try:
        readiness = int(readiness or 0)
        rr_ratio = float(rr_ratio or 0)
    except Exception:
        readiness, rr_ratio = 0, 0
    if readiness >= 75 and rr_ratio >= 1.8:
        return 'medium'
    if readiness >= 55 and rr_ratio >= 1.2:
        return 'small'
    return 'none'


def _market_regime(snapshot):
    analysis = snapshot.get('analysis') or {}
    trend = str(analysis.get('trend') or 'mixed').lower()
    if 'bull' in trend:
        return 'trend_up'
    if 'bear' in trend:
        return 'trend_down'
    return 'mixed'


def build_mind_card(snapshot, mode='mixed', exchange='BINANCE', horizon_bars=None):
    candles = list(snapshot.get('candles') or [])
    if not candles:
        raise ValueError('mind card requires candles')
    rr = snapshot.get('risk_reward') or {}
    pc = snapshot.get('pro_checklist') or {}
    analysis = snapshot.get('analysis') or {}
    smc = snapshot.get('smc') or {}
    entry = rr.get('entry') or analysis.get('price') or candles[-1].get('close')
    stop = rr.get('stop')
    target = rr.get('target')
    potential = _pct(entry, target)
    risk = _pct(entry, stop)
    rr_ratio = rr.get('risk_reward_ratio')
    readiness = pc.get('readiness_score') or 0
    direction = _direction(snapshot)
    confidence = max(0.05, min(0.9, 0.45 + (float(readiness or 0) / 200.0)))
    rsi = analysis.get('rsi_14') or 50
    try:
        fomo = max(0.0, min(1.0, (float(rsi) - 50.0) / 40.0 if direction == 'up' else (50.0 - float(rsi)) / 40.0))
    except Exception:
        fomo = 0.0
    setup_quality = str(pc.get('status') or 'mixed')
    features = {
        'trend': analysis.get('trend'),
        'price': analysis.get('price') or candles[-1].get('close'),
        'vwap': analysis.get('vwap'),
        'rsi_14': analysis.get('rsi_14'),
        'readiness_score': readiness,
        'checklist_status': pc.get('status'),
        'smc_bias': smc.get('bias'),
        'order_book': snapshot.get('order_book') or {},
    }
    return {
        'exchange': exchange,
        'symbol': str(snapshot.get('symbol', 'UNKNOWN')).upper(),
        'interval': str(snapshot.get('interval', '15m')),
        'mode': str(mode or 'mixed'),
        'snapshot_ts': candles[-1].get('ts'),
        'horizon_bars': int(horizon_bars or 8),
        'chart_window': candles[-80:],
        'order_book': snapshot.get('order_book') or {},
        'features': features,
        'ai_direction': direction,
        'ai_size': _size_from_quality(readiness, rr_ratio),
        'ai_confidence': round(confidence, 3),
        'ai_reason': [
            f"Trend context: {analysis.get('trend') or 'mixed'}.",
            f"Setup quality: {setup_quality}.",
            f"SMC bias: {smc.get('bias') or 'n/a'}.",
        ],
        'potential_profit_pct': potential,
        'risk_loss_pct': risk,
        'risk_reward_ratio': rr_ratio,
        'fomo_score': round(fomo, 3),
        'setup_quality': setup_quality,
        'market_regime': _market_regime(snapshot),
    }
def build_historical_mind_card(snapshot, mode='mixed', exchange='BINANCE', visible_candles=52, outcome_candles=8, seed=None):
    candles = list(snapshot.get('candles') or [])
    visible_candles = int(visible_candles or 52)
    outcome_candles = int(outcome_candles or 8)
    if len(candles) < visible_candles + outcome_candles + 1:
        return build_mind_card(snapshot, mode=mode, exchange=exchange, horizon_bars=outcome_candles)
    rng = random.Random(seed)
    decision_idx = rng.randint(visible_candles - 1, len(candles) - outcome_candles - 1)
    visible = candles[decision_idx - visible_candles + 1:decision_idx + 1]
    future = candles[decision_idx + 1:decision_idx + 1 + outcome_candles]
    decision_close = float(visible[-1].get('close') or 0)
    future_close = float(future[-1].get('close') or decision_close)
    change_pct = ((future_close - decision_close) / decision_close * 100.0) if decision_close else 0.0
    direction = 'up' if change_pct > 0.05 else ('down' if change_pct < -0.05 else 'flat')
    first_close = float(visible[0].get('close') or decision_close or 0)
    trend = 'bullish' if decision_close > first_close else ('bearish' if decision_close < first_close else 'mixed')
    closes = [float(c.get('close') or 0) for c in visible[-14:] if c.get('close') is not None]
    gains = [max(0.0, closes[i] - closes[i - 1]) for i in range(1, len(closes))]
    losses = [max(0.0, closes[i - 1] - closes[i]) for i in range(1, len(closes))]
    avg_gain = sum(gains) / len(gains) if gains else 0.0
    avg_loss = sum(losses) / len(losses) if losses else 0.0
    rsi = 50.0 if not (avg_gain or avg_loss) else (100.0 if avg_loss == 0 else 100.0 - (100.0 / (1.0 + avg_gain / avg_loss)))
    entry = decision_close
    stop = min(c.get('low') or entry for c in visible[-8:]) if trend != 'bearish' else max(c.get('high') or entry for c in visible[-8:])
    target = entry + abs(entry - stop) * (1 if trend != 'bearish' else -1)
    hist_snapshot = dict(snapshot)
    hist_snapshot['candles'] = visible
    hist_snapshot['analysis'] = dict(snapshot.get('analysis') or {}, trend=trend, price=entry, rsi_14=round(rsi, 2))
    hist_snapshot['risk_reward'] = dict(snapshot.get('risk_reward') or {}, entry=entry, stop=stop, target=target, risk_reward_ratio=1.0, valid=True)
    card = build_mind_card(hist_snapshot, mode=mode, exchange=exchange, horizon_bars=outcome_candles)
    card['training_kind'] = 'historical_known_outcome'
    card['snapshot_ts'] = visible[-1].get('ts')
    card['decision_ts'] = visible[-1].get('ts')
    card['known_outcome'] = {
        'direction': direction,
        'change_pct': round(change_pct, 4),
        'entry': entry,
        'final_close': future_close,
        'future_candles': outcome_candles,
        'outcome_ts': future[-1].get('ts'),
    }
    card['features']['known_outcome_hidden'] = True
    return card


def save_mind_card(con, card, session_id=None):
    con.execute('''
        insert into mind_cards(
            session_id, created_at, exchange, symbol, interval, mode, snapshot_ts, horizon_bars,
            chart_window_json, order_book_json, features_json, ai_direction, ai_size, ai_confidence,
            ai_reason_json, potential_profit_pct, risk_loss_pct, risk_reward_ratio, fomo_score,
            setup_quality, market_regime, status
        ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        session_id, _now(), card['exchange'], card['symbol'], card['interval'], card['mode'],
        card.get('snapshot_ts'), int(card.get('horizon_bars') or 8), _json(card.get('chart_window') or []),
        _json(card.get('order_book') or {}), _json(card.get('features') or {}), card['ai_direction'],
        card['ai_size'], card.get('ai_confidence'), _json(card.get('ai_reason') or []),
        card.get('potential_profit_pct'), card.get('risk_loss_pct'), card.get('risk_reward_ratio'),
        card.get('fomo_score'), card.get('setup_quality'), card.get('market_regime'), 'unanswered',
    ))
    con.commit()
    return int(con.execute('select last_insert_rowid()').fetchone()[0])


def record_user_choice(con, card_id, direction, size='none'):
    direction = str(direction or 'skip').lower()
    if direction not in ('up', 'down', 'skip'):
        raise ValueError('direction must be up/down/skip')
    size = 'none' if direction == 'skip' else str(size or 'none').lower()
    if size not in ('none', 'small', 'medium', 'large'):
        raise ValueError('size must be none/small/medium/large')
    row = con.execute('select ai_direction from mind_cards where id=?', (int(card_id),)).fetchone()
    if row is None:
        raise KeyError(f'unknown mind card id {card_id}')
    agreement = 1 if row['ai_direction'] == direction else 0
    con.execute('''
        update mind_cards set user_direction=?, user_size=?, user_decided_at=?, agreement_with_ai=?, status='answered'
        where id=?
    ''', (direction, size, _now(), agreement, int(card_id)))
    con.commit()
    return mind_card_detail(con, card_id)


def mind_card_detail(con, card_id):
    row = con.execute('select * from mind_cards where id=?', (int(card_id),)).fetchone()
    if row is None:
        return {'error': 'not_found', 'id': int(card_id)}
    d = dict(row)
    d['chart_window'] = _loads(d.pop('chart_window_json', None), [])
    d['order_book'] = _loads(d.pop('order_book_json', None), {})
    d['features'] = _loads(d.pop('features_json', None), {})
    d['ai_reason'] = _loads(d.pop('ai_reason_json', None), [])
    return d
