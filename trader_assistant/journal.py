from __future__ import annotations

import json
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parents[1] / 'data' / 'setup_journal.sqlite3'
VALID_OUTCOMES = {'watching', 'target', 'stopped', 'failed', 'neutral', 'missed'}


def _now():
    return datetime.now(timezone.utc).isoformat()


def _json(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True)


def _patterns(snapshot):
    return [p.get('name') for p in snapshot.get('classic_patterns', []) if p.get('name')]


def _rr_quality(snapshot):
    return ((snapshot.get('risk_reward') or {}).get('rr_quality') or {}).get('label') or 'n/a'


def _row_to_dict(row):
    return dict(row) if row is not None else None


def init_journal(path=DEFAULT_DB):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(path))
    con.row_factory = sqlite3.Row
    con.execute('''
        create table if not exists setups (
            id integer primary key autoincrement,
            created_at text not null,
            updated_at text not null,
            symbol text not null,
            outcome text not null default 'watching',
            readiness_score integer,
            checklist_status text,
            rr_ratio real,
            rr_quality text,
            patterns_json text not null,
            snapshot_json text not null,
            notes text not null default ''
        )
    ''')
    con.commit()
    return con


def save_setup(con, snapshot, notes=''):
    pc = snapshot.get('pro_checklist') or {}
    rr = snapshot.get('risk_reward') or {}
    patterns = _patterns(snapshot)
    con.execute('''
        insert into setups(created_at, updated_at, symbol, outcome, readiness_score, checklist_status, rr_ratio, rr_quality, patterns_json, snapshot_json, notes)
        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        _now(), _now(), str(snapshot.get('symbol', 'UNKNOWN')).upper(), 'watching',
        pc.get('readiness_score'), pc.get('status'), rr.get('risk_reward_ratio'), _rr_quality(snapshot),
        _json(patterns), _json(snapshot), str(notes or ''),
    ))
    con.commit()
    return int(con.execute('select last_insert_rowid()').fetchone()[0])


def mark_outcome(con, setup_id, outcome, notes=None):
    outcome = str(outcome or '').lower()
    if outcome not in VALID_OUTCOMES:
        raise ValueError(f'Invalid outcome: {outcome}')
    row = con.execute('select notes from setups where id=?', (int(setup_id),)).fetchone()
    if row is None:
        raise KeyError(f'Unknown setup_id: {setup_id}')
    final_notes = row['notes']
    if notes:
        final_notes = (final_notes + '\n' if final_notes else '') + str(notes)
    con.execute('update setups set outcome=?, notes=?, updated_at=? where id=?', (outcome, final_notes, _now(), int(setup_id)))
    con.commit()
    return _row_to_dict(con.execute('select * from setups where id=?', (int(setup_id),)).fetchone())


def recent_setups(con, limit=20):
    rows = con.execute('select * from setups order by id desc limit ?', (int(limit),)).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        try:
            d['patterns'] = json.loads(d.pop('patterns_json'))
        except Exception:
            d['patterns'] = []
        d.pop('snapshot_json', None)
        out.append(d)
    return out


def learning_stats(con):
    rows = con.execute('select symbol,outcome,rr_quality,patterns_json,readiness_score,checklist_status from setups').fetchall()
    stats = {'total': len(rows), 'patterns': {}, 'rr_quality': {}, 'symbols': {}, 'checklist_status': {}, 'readiness_buckets': {}}
    counters = {
        'patterns': defaultdict(Counter),
        'rr_quality': defaultdict(Counter),
        'symbols': defaultdict(Counter),
        'checklist_status': defaultdict(Counter),
        'readiness_buckets': defaultdict(Counter),
    }
    for r in rows:
        outcome = r['outcome'] or 'unknown'
        counters['symbols'][r['symbol']][outcome] += 1
        counters['rr_quality'][r['rr_quality'] or 'n/a'][outcome] += 1
        counters['checklist_status'][r['checklist_status'] or 'n/a'][outcome] += 1
        score = r['readiness_score']
        bucket = 'n/a'
        if score is not None:
            score = int(score)
            bucket = '0-39' if score < 40 else ('40-59' if score < 60 else ('60-79' if score < 80 else '80-100'))
        counters['readiness_buckets'][bucket][outcome] += 1
        try:
            pats = json.loads(r['patterns_json'] or '[]')
        except Exception:
            pats = []
        for p in pats:
            counters['patterns'][p][outcome] += 1
    for k, c in counters.items():
        stats[k] = {name: dict(vals) for name, vals in c.items()}
    return stats
