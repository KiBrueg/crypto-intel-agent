# Knowledge Graph Prototype

Graphify-style thinking is useful for Crypto Intel Agent because learning creates accumulated memory, and accumulated memory needs structure.

A flat journal answers:

```text
what happened?
```

A graph can answer:

```text
what tends to connect?
which patterns appear with failed outcomes?
which chair verdicts connect to which blockers?
which advisors repeatedly flagged the same risk?
```

## Current prototype

File:

```text
trader_assistant/knowledge_graph.py
```

API:

```text
GET /api/graph?limit=100
```

Dashboard section:

```text
Knowledge Graph
```

## Nodes

The prototype creates nodes for:

- symbols
- setups
- patterns
- outcomes
- R/R quality buckets
- checklist statuses
- council reviews
- advisors
- advisor verdicts
- chair verdicts
- action biases
- blockers

## Edges

Examples:

```text
setup -> symbol               observed_on
setup -> pattern              has_pattern
setup -> outcome              resulted_in
setup -> rr_quality           has_rr_quality
setup -> checklist_status     has_checklist_status
council -> symbol             reviewed_symbol
council -> advisor            consulted_advisor
council -> chair_verdict      chair_verdict
council -> action_bias        action_bias
council -> blocker            has_blocker
```

## Why this matters

This is the bridge from memory to learning:

```text
saved setup/council history -> graph nodes/edges -> recurring relationship discovery -> better Coach/Council warnings
```

## Future upgrades

- visual graph canvas
- graph query UI
- pattern/outcome co-occurrence scores
- advisor accuracy tracking
- "similar past setups" retrieval
- GraphRAG over journal/council memory
- optional external Graphify/Neo4j/NetworkX export

The first version is intentionally lightweight JSON so it remains local, testable and dependency-free.
