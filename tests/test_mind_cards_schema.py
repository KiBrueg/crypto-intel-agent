#!/usr/bin/env python3
from pathlib import Path
import tempfile
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from trader_assistant.journal import init_journal


def test_mind_card_tables_are_created_by_journal_init():
    with tempfile.TemporaryDirectory() as td:
        con = init_journal(Path(td) / 'test.sqlite3')
        try:
            tables = {r[0] for r in con.execute("select name from sqlite_master where type='table'").fetchall()}
            assert 'mind_card_sessions' in tables
            assert 'mind_cards' in tables
            assert 'mind_card_learning_events' in tables
        finally:
            con.close()


def test_mind_cards_table_has_user_ai_market_learning_columns():
    with tempfile.TemporaryDirectory() as td:
        con = init_journal(Path(td) / 'test.sqlite3')
        try:
            cols = {r[1] for r in con.execute('pragma table_info(mind_cards)').fetchall()}
            required = {
                'exchange', 'symbol', 'interval', 'mode', 'chart_window_json', 'features_json',
                'ai_direction', 'ai_size', 'ai_confidence', 'potential_profit_pct', 'risk_loss_pct',
                'risk_reward_ratio', 'fomo_score', 'setup_quality', 'market_regime', 'user_direction',
                'user_size', 'agreement_with_ai', 'actual_outcome', 'actual_direction',
                'user_scenario_confirmed', 'ai_scenario_confirmed', 'user_r_score', 'ai_r_score',
                'focus_area', 'coach_note'
            }
            assert required.issubset(cols)
        finally:
            con.close()


if __name__ == '__main__':
    test_mind_card_tables_are_created_by_journal_init()
    test_mind_cards_table_has_user_ai_market_learning_columns()
    print('OK mind cards schema tests passed')
