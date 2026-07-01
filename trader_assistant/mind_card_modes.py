from __future__ import annotations

MIND_CARD_MODES = {
    'mixed': {
        'key': 'mixed',
        'label': 'Смешанная тренировка',
        'description': 'Разные реальные рыночные ситуации без перегруза терминами.',
        'symbols': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'],
        'interval': '15m',
        'intervals': ['15m', '1h'],
        'horizon_bars': 8,
        'feature_focus': ['trend', 'levels', 'volume', 'risk'],
    },
    'quick_scalps': {
        'key': 'quick_scalps',
        'label': 'Быстрые движения',
        'description': '5–15m карточки: ликвидность, стакан, spread и быстрый импульс.',
        'symbols': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'],
        'interval': '15m',
        'intervals': ['5m', '15m'],
        'horizon_bars': 4,
        'feature_focus': ['order_book', 'spread', 'volume_burst', 'liquidity'],
    },
    'breakout_reads': {
        'key': 'breakout_reads',
        'label': 'Пробои',
        'description': 'Уровни, range high/low, объём и продолжение движения.',
        'symbols': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT'],
        'interval': '15m',
        'intervals': ['15m', '1h'],
        'horizon_bars': 8,
        'feature_focus': ['range_high_low', 'volume_expansion', 'breakout'],
    },
    'fakeout_defense': {
        'key': 'fakeout_defense',
        'label': 'Ложные пробои',
        'description': 'Тренировка защиты от fakeout: вынос, возврат под уровень, слабое подтверждение.',
        'symbols': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'],
        'interval': '15m',
        'intervals': ['15m', '1h'],
        'horizon_bars': 8,
        'feature_focus': ['liquidity_sweep', 'failed_breakout', 'volume_fade'],
    },
    'vwap_level_reclaim': {
        'key': 'vwap_level_reclaim',
        'label': 'Отскоки / возврат к уровню',
        'description': 'VWAP, support/resistance, reclaim и реакция возле диапазона.',
        'symbols': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'],
        'interval': '15m',
        'intervals': ['15m', '1h'],
        'horizon_bars': 8,
        'feature_focus': ['vwap', 'support_resistance', 'mean_reversion'],
    },
    'order_book_sense': {
        'key': 'order_book_sense',
        'label': 'Стакан и ликвидность',
        'description': 'Bid/ask imbalance, walls, spread и короткий market microstructure context.',
        'symbols': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'],
        'interval': '15m',
        'intervals': ['5m', '15m'],
        'horizon_bars': 4,
        'feature_focus': ['order_book', 'imbalance', 'walls', 'spread'],
    },
}


def get_mind_card_mode(key='mixed'):
    return dict(MIND_CARD_MODES.get(str(key or 'mixed'), MIND_CARD_MODES['mixed']))


def available_mind_card_modes():
    return [dict(v) for v in MIND_CARD_MODES.values()]
