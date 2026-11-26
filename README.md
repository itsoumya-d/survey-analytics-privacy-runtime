# Survey Analytics Privacy Runtime

High-throughput cohort aggregation engine with strict k-anonymity privacy safeguards and analytical column-oriented query generation.

## Features
- **k-Anonymity Enforcement**: Suppresses or generalizes demographic subgroups with respondent counts below minimum anonymity thresholds ($k \ge 5$) to prevent response identification.
- **Demographic Cohort Aggregation**: Vectorized scoring across survey dimensions (engagement, psychological safety, leadership alignment) with participation rate auditing.
- **Analytical Schema & Query Generation**: Generates ClickHouse-compatible analytical aggregations and rollup queries for low-latency multidimensional filtering.

## Quickstart
```bash
pytest -v
```
