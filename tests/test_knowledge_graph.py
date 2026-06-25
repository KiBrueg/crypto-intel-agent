#!/usr/bin/env python3
from pathlib import Path
import tempfile
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from trader_assistant.council import run_council
from trader_assistant.journal import init_journal, save_setup, mark_outcome, save_council_review
from trader_assistant.knowledge_graph import build_knowledge_graph
from web_dashboard import handle_journal_api


def sample_snapshot():
    return {
        'symbol': 'BTCUSDT',
        'analysis': {'trend': 'mixed', 'price': 65000},
        'risk_reward': {'risk_reward_ratio': 0.8, 'rr_quality': {'label': 'weak'}},
        'pro_checklist': {'readiness_score': 35, 'status': 'not_clean', 'blockers': ['Weak R/R'], 'next_checks': ['Wait for VWAP reclaim']},
        'multi_timeframe': {'frames': [{'trend': 'bullish'}, {'trend': 'bearish'}]},
        'classic_patterns': [{'name': 'hammer', 'bias': 'bullish'}, {'name': 'bearish_engulfing', 'bias': 'bearish'}],
        'order_book': {'spread_bps': 0.5, 'signals': ['bid wall']},
        'fear_greed': {'label': 'fear', 'confirmation': 'mixed'},
    }


def test_knowledge_graph_links_setups_patterns_outcomes_and_council():
    with tempfile.TemporaryDirectory() as d:
        con = init_journal(Path(d) / 'journal.sqlite3')
        try:
            setup_id = save_setup(con, sample_snapshot())
            mark_outcome(con, setup_id, 'failed')
            council = run_council(sample_snapshot())
            review_id = save_council_review(con, sample_snapshot(), council)
            graph = build_knowledge_graph(con)
        finally:
            con.close()
        node_ids = {n['id'] for n in graph['nodes']}
        edge_keys = {(e['source'], e['target'], e['type']) for e in graph['edges']}
        assert 'symbol:BTCUSDT' in node_ids
        assert 'pattern:hammer' in node_ids
        assert 'outcome:failed' in node_ids
        assert 'chair_verdict:not_clean' in node_ids
        assert (f'setup:{setup_id}', 'pattern:hammer', 'has_pattern') in edge_keys
        assert (f'setup:{setup_id}', 'outcome:failed', 'resulted_in') in edge_keys
        assert (f'council:{review_id}', 'chair_verdict:not_clean', 'chair_verdict') in edge_keys
        assert graph['summary']['node_count'] >= 6
        assert graph['summary']['edge_count'] >= 6


def test_graph_api_returns_nodes_edges_and_top_relations():
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / 'journal.sqlite3'
        con = init_journal(db)
        try:
            setup_id = save_setup(con, sample_snapshot())
            mark_outcome(con, setup_id, 'failed')
            council = run_council(sample_snapshot())
            save_council_review(con, sample_snapshot(), council)
        finally:
            con.close()
        response = handle_journal_api('GET', '/api/graph', qs={'limit': ['50']}, db_path=db)
        assert response['mode'] == 'knowledge_graph'
        assert response['summary']['node_count'] > 0
        assert response['top_relations']
        assert any(r['type'] == 'resulted_in' for r in response['top_relations'])


if __name__ == '__main__':
    test_knowledge_graph_links_setups_patterns_outcomes_and_council()
    test_graph_api_returns_nodes_edges_and_top_relations()
    print('OK knowledge graph tests passed')
