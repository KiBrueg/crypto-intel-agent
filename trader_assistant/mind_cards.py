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


def _window_trend(candles):
    if not candles:
        return 'mixed'
    try:
        first = float(candles[0].get('close') or candles[0].get('open') or 0)
        last = float(candles[-1].get('close') or candles[-1].get('open') or first)
        change = ((last - first) / first * 100.0) if first else 0.0
    except Exception:
        return 'mixed'
    if change > 0.15:
        return 'bullish'
    if change < -0.15:
        return 'bearish'
    return 'mixed'


def _direction_from_change(change_pct, threshold=0.05):
    if change_pct > threshold:
        return 'up'
    if change_pct < -threshold:
        return 'down'
    return 'flat'


def _rsi_from_window(candles):
    closes = [float(c.get('close') or 0) for c in candles[-14:] if c.get('close') is not None]
    if len(closes) < 2:
        return 50.0
    gains = [max(0.0, closes[i] - closes[i - 1]) for i in range(1, len(closes))]
    losses = [max(0.0, closes[i - 1] - closes[i]) for i in range(1, len(closes))]
    avg_gain = sum(gains) / len(gains) if gains else 0.0
    avg_loss = sum(losses) / len(losses) if losses else 0.0
    return 50.0 if not (avg_gain or avg_loss) else (100.0 if avg_loss == 0 else 100.0 - (100.0 / (1.0 + avg_gain / avg_loss)))


def _rsi_bucket(rsi):
    rsi = float(rsi or 50)
    if rsi < 30:
        return 'oversold'
    if rsi < 45:
        return 'low'
    if rsi <= 55:
        return 'neutral'
    if rsi <= 70:
        return 'high'
    return 'overbought'


def _vwap_bucket(candles):
    if not candles:
        return 'near_vwap'
    try:
        close = float(candles[-1].get('close') or 0)
        volumes = [float(c.get('volume') or 0) for c in candles]
        total_v = sum(volumes)
        if total_v:
            vwap = sum(float(c.get('close') or 0) * float(c.get('volume') or 0) for c in candles) / total_v
        else:
            vwap = sum(float(c.get('close') or 0) for c in candles) / len(candles)
        diff = ((close - vwap) / vwap * 100.0) if vwap else 0.0
    except Exception:
        return 'near_vwap'
    if diff > 0.15:
        return 'above_vwap'
    if diff < -0.15:
        return 'below_vwap'
    return 'near_vwap'


def _rr_bucket(rr_ratio):
    try:
        rr = float(rr_ratio or 0)
    except Exception:
        rr = 0.0
    if rr >= 1.8:
        return 'good_rr'
    if rr >= 1.1:
        return 'ok_rr'
    return 'poor_rr'


def _fomo_bucket(rsi, direction):
    try:
        rsi = float(rsi or 50)
        fomo = max(0.0, min(1.0, (rsi - 50.0) / 40.0 if direction == 'up' else (50.0 - rsi) / 40.0))
    except Exception:
        fomo = 0.0
    if fomo >= 0.55:
        return 'high_fomo'
    if fomo >= 0.22:
        return 'mid_fomo'
    return 'low_fomo'


def _volume_bucket(candles):
    vols = [float(c.get('volume') or 0) for c in candles if c.get('volume') is not None]
    if len(vols) < 6:
        return 'normal_volume'
    recent = sum(vols[-3:]) / 3.0
    baseline = sum(vols[:-3]) / max(1, len(vols[:-3]))
    if baseline <= 0:
        return 'normal_volume'
    ratio = recent / baseline
    if ratio >= 1.45:
        return 'spike_volume'
    if ratio <= 0.72:
        return 'quiet_volume'
    return 'normal_volume'


def _range_bucket(candles):
    if not candles:
        return 'normal_range'
    try:
        closes = [float(c.get('close') or 0) for c in candles]
        highs = [float(c.get('high') or 0) for c in candles]
        lows = [float(c.get('low') or 0) for c in candles]
        mid = sum(closes) / len(closes)
        width_pct = ((max(highs) - min(lows)) / mid * 100.0) if mid else 0.0
    except Exception:
        return 'normal_range'
    if width_pct < 1.2:
        return 'tight_range'
    if width_pct > 4.5:
        return 'wide_range'
    return 'normal_range'


def _fakeout_bucket(candles):
    if len(candles) < 12:
        return 'no_fakeout'
    prior = candles[:-1]
    last = candles[-1]
    try:
        prior_high = max(float(c.get('high') or 0) for c in prior[-12:])
        prior_low = min(float(c.get('low') or 0) for c in prior[-12:])
        high = float(last.get('high') or 0)
        low = float(last.get('low') or 0)
        close = float(last.get('close') or 0)
    except Exception:
        return 'no_fakeout'
    upper = high > prior_high and close < prior_high
    lower = low < prior_low and close > prior_low
    if upper and lower:
        return 'two_sided_fakeout'
    if upper:
        return 'upper_fakeout'
    if lower:
        return 'lower_fakeout'
    return 'no_fakeout'


def _window_profile(candles, rr_ratio=1.0):
    trend = _window_trend(candles)
    rsi = _rsi_from_window(candles)
    direction = 'up' if trend == 'bullish' else ('down' if trend == 'bearish' else 'skip')
    return {
        'trend_bucket': trend,
        'rsi_bucket': _rsi_bucket(rsi),
        'vwap_bucket': _vwap_bucket(candles),
        'rr_bucket': _rr_bucket(rr_ratio),
        'fomo_bucket': _fomo_bucket(rsi, direction),
        'volume_bucket': _volume_bucket(candles),
        'range_bucket': _range_bucket(candles),
        'fakeout_bucket': _fakeout_bucket(candles),
    }


def _profile_matches(profile, target, filter_name):
    keys = {
        'trend+rsi+vwap+rr+fomo+volume+range+fakeout': ['trend_bucket', 'rsi_bucket', 'vwap_bucket', 'rr_bucket', 'fomo_bucket', 'volume_bucket', 'range_bucket', 'fakeout_bucket'],
        'trend+rsi+vwap+rr+fomo': ['trend_bucket', 'rsi_bucket', 'vwap_bucket', 'rr_bucket', 'fomo_bucket'],
        'trend+rsi+vwap': ['trend_bucket', 'rsi_bucket', 'vwap_bucket'],
        'trend+rsi': ['trend_bucket', 'rsi_bucket'],
        'trend': ['trend_bucket'],
        'all': [],
    }[filter_name]
    return all(profile.get(k) == target.get(k) for k in keys)


def build_historical_setup_stats(candles, visible_candles=52, outcome_candles=8, current_trend=None, current_profile=None):
    candles = list(candles or [])
    visible_candles = int(visible_candles or 52)
    outcome_candles = int(outcome_candles or 8)
    current_trend = (current_trend or '').lower() or None
    target_profile = dict(current_profile or {})
    if current_trend and not target_profile.get('trend_bucket'):
        target_profile['trend_bucket'] = current_trend
    filters = ['trend+rsi+vwap+rr+fomo+volume+range+fakeout', 'trend+rsi+vwap+rr+fomo', 'trend+rsi+vwap', 'trend+rsi', 'trend', 'all']
    selected_filter = filters[-1]
    selected_rows = []
    for filter_name in filters:
        rows = []
        for end in range(visible_candles - 1, len(candles) - outcome_candles - 1):
            visible = candles[end - visible_candles + 1:end + 1]
            profile = _window_profile(visible, rr_ratio=1.0)
            if target_profile and not _profile_matches(profile, target_profile, filter_name):
                continue
            try:
                entry = float(visible[-1].get('close') or 0)
                final = float(candles[end + outcome_candles].get('close') or entry)
                change = ((final - entry) / entry * 100.0) if entry else 0.0
            except Exception:
                continue
            rows.append((change, _direction_from_change(change), profile))
        selected_filter = filter_name
        selected_rows = rows
        if len(rows) >= 12 or filter_name == 'all':
            break
    counts = {'up': 0, 'down': 0, 'flat': 0}
    changes = []
    for change, direction, _profile in selected_rows:
        counts[direction] += 1
        changes.append(change)
    total = len(changes)
    if total == 0:
        return {
            'sample_size': 0, 'up_rate': 0.0, 'down_rate': 0.0, 'flat_rate': 0.0,
            'avg_change_pct': 0.0, 'stat_direction': 'skip', 'stat_confidence': 0.0,
            'stat_edge': 0.0, 'basis': 'no historical windows available',
            'match_profile': target_profile, 'similarity_filters': filters,
            'selected_filter': selected_filter,
        }
    rates = {k: counts[k] / total for k in counts}
    ranked = sorted(rates.items(), key=lambda kv: kv[1], reverse=True)
    best_dir, best_rate = ranked[0]
    second_rate = ranked[1][1] if len(ranked) > 1 else 0.0
    edge = best_rate - second_rate
    stat_direction = 'skip' if best_rate < 0.45 or edge < 0.08 else best_dir
    confidence = 0.35 + min(0.45, max(0.0, edge) * 1.2) + min(0.15, total / 400.0)
    if stat_direction == 'skip':
        confidence = min(confidence, 0.52)
    basis = f'{total} historical windows matched by {selected_filter}'
    return {
        'sample_size': total,
        'up_count': counts['up'],
        'down_count': counts['down'],
        'flat_count': counts['flat'],
        'up_rate': round(rates['up'], 3),
        'down_rate': round(rates['down'], 3),
        'flat_rate': round(rates['flat'], 3),
        'avg_change_pct': round(sum(changes) / total, 4),
        'stat_direction': stat_direction,
        'stat_confidence': round(max(0.0, min(0.9, confidence)), 3),
        'stat_edge': round(edge, 3),
        'basis': basis,
        'match_profile': target_profile,
        'similarity_filters': filters,
        'selected_filter': selected_filter,
    }


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
    current_profile = _window_profile(visible, rr_ratio=1.0)
    card = build_mind_card(hist_snapshot, mode=mode, exchange=exchange, horizon_bars=outcome_candles)
    stats = build_historical_setup_stats(candles, visible_candles=visible_candles, outcome_candles=outcome_candles, current_trend=trend, current_profile=current_profile)
    card['historical_stats'] = stats
    card['features']['historical_stats'] = stats
    card['ai_reason'].append(
        f"Historical stats: {stats['basis']} → up {round(stats['up_rate']*100)}%, down {round(stats['down_rate']*100)}%, flat {round(stats['flat_rate']*100)}%, avg {stats['avg_change_pct']}%, edge {round(stats.get('stat_edge', 0)*100)}%, statistical view: {stats['stat_direction']}."
    )
    p = stats.get('match_profile') or {}
    card['ai_reason'].append(
        f"Similarity profile: trend={p.get('trend_bucket')}, RSI={p.get('rsi_bucket')}, VWAP={p.get('vwap_bucket')}, R/R={p.get('rr_bucket')}, FOMO={p.get('fomo_bucket')}."
    )
    card['ai_reason'].append(
        f"Structure profile: Volume={p.get('volume_bucket')}, Range={p.get('range_bucket')}, Fakeout={p.get('fakeout_bucket')}."
    )
    if stats.get('sample_size', 0) >= 20:
        stat_dir = stats.get('stat_direction')
        if stat_dir in ('up', 'down') and stat_dir != card.get('ai_direction'):
            card['ai_reason'].append('Conflict: chart trend and historical stats disagree, so AI confidence is reduced and Skip becomes safer.')
            card['ai_confidence'] = round(min(card.get('ai_confidence', 0.5), max(0.35, stats.get('stat_confidence', 0.45) - 0.08)), 3)
        elif stat_dir in ('up', 'down'):
            card['ai_confidence'] = round(max(card.get('ai_confidence', 0.5), stats.get('stat_confidence', 0.5)), 3)
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
    card['features']['known_outcome'] = card['known_outcome']
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
