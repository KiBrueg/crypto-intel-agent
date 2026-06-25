from __future__ import annotations

import json
from collections import Counter


def _add_node(nodes, node_id, label, kind, **props):
    if node_id not in nodes:
        nodes[node_id] = {'id': node_id, 'label': label, 'kind': kind, **props}
    else:
        nodes[node_id].update({k: v for k, v in props.items() if v is not None})
    return node_id


def _add_edge(edges, source, target, edge_type, **props):
    edges.append({'source': source, 'target': target, 'type': edge_type, **props})


def _safe_json(text, fallback):
    try:
        return json.loads(text or '')
    except Exception:
        return fallback


def _setup_graph(con, nodes, edges, limit):
    rows = con.execute('select * from setups order by id desc limit ?', (int(limit),)).fetchall()
    for row in rows:
        setup_id = f"setup:{row['id']}"
        symbol_id = f"symbol:{row['symbol']}"
        outcome_id = f"outcome:{row['outcome']}"
        rr_id = f"rr_quality:{row['rr_quality'] or 'n/a'}"
        checklist_id = f"checklist_status:{row['checklist_status'] or 'n/a'}"
        _add_node(nodes, setup_id, f"Setup #{row['id']}", 'setup', created_at=row['created_at'], readiness_score=row['readiness_score'])
        _add_node(nodes, symbol_id, row['symbol'], 'symbol')
        _add_node(nodes, outcome_id, row['outcome'], 'outcome')
        _add_node(nodes, rr_id, row['rr_quality'] or 'n/a', 'rr_quality')
        _add_node(nodes, checklist_id, row['checklist_status'] or 'n/a', 'checklist_status')
        _add_edge(edges, setup_id, symbol_id, 'observed_on')
        _add_edge(edges, setup_id, outcome_id, 'resulted_in')
        _add_edge(edges, setup_id, rr_id, 'has_rr_quality')
        _add_edge(edges, setup_id, checklist_id, 'has_checklist_status')
        for p in _safe_json(row['patterns_json'], []):
            pattern_id = f"pattern:{p}"
            _add_node(nodes, pattern_id, p, 'pattern')
            _add_edge(edges, setup_id, pattern_id, 'has_pattern')


def _council_graph(con, nodes, edges, limit):
    rows = con.execute('select * from council_reviews order by id desc limit ?', (int(limit),)).fetchall()
    for row in rows:
        council_id = f"council:{row['id']}"
        symbol_id = f"symbol:{row['symbol']}"
        verdict_id = f"chair_verdict:{row['chair_verdict']}"
        action_id = f"action_bias:{row['action_bias']}"
        _add_node(nodes, council_id, f"Council #{row['id']}", 'council_review', created_at=row['created_at'], readiness_score=row['readiness_score'])
        _add_node(nodes, symbol_id, row['symbol'], 'symbol')
        _add_node(nodes, verdict_id, row['chair_verdict'], 'chair_verdict')
        _add_node(nodes, action_id, row['action_bias'], 'action_bias')
        _add_edge(edges, council_id, symbol_id, 'reviewed_symbol')
        _add_edge(edges, council_id, verdict_id, 'chair_verdict')
        _add_edge(edges, council_id, action_id, 'action_bias')
        council = _safe_json(row['council_json'], {})
        for advisor in council.get('advisors') or []:
            name = advisor.get('advisor')
            verdict = advisor.get('verdict')
            if name:
                advisor_id = f"advisor:{name}"
                _add_node(nodes, advisor_id, name, 'advisor')
                _add_edge(edges, council_id, advisor_id, 'consulted_advisor', verdict=verdict)
            if verdict:
                av_id = f"advisor_verdict:{verdict}"
                _add_node(nodes, av_id, verdict, 'advisor_verdict')
                _add_edge(edges, advisor_id, av_id, 'advisor_concluded')
        for blocker in ((council.get('chair') or {}).get('blockers') or [])[:5]:
            b_label = str(blocker)[:90]
            blocker_id = f"blocker:{b_label.lower()}"
            _add_node(nodes, blocker_id, b_label, 'blocker')
            _add_edge(edges, council_id, blocker_id, 'has_blocker')


def build_knowledge_graph(con, limit=100):
    """Build a lightweight graph from setup journal and council review memory.

    This is a Graphify-style prototype: accumulated facts become nodes and the
    relationships between setups, patterns, outcomes, advisor verdicts and chair
    decisions become edges.
    """
    nodes = {}
    edges = []
    _setup_graph(con, nodes, edges, limit)
    _council_graph(con, nodes, edges, limit)
    relation_counts = Counter(edge['type'] for edge in edges)
    kind_counts = Counter(node['kind'] for node in nodes.values())
    top_relations = [{'type': k, 'count': v} for k, v in relation_counts.most_common()]
    return {
        'mode': 'knowledge_graph',
        'summary': {
            'node_count': len(nodes),
            'edge_count': len(edges),
            'node_kinds': dict(kind_counts),
        },
        'nodes': list(nodes.values()),
        'edges': edges,
        'top_relations': top_relations,
    }
