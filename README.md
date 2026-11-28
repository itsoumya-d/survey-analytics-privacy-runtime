# Survey Analytics Privacy Runtime

High-throughput cohort aggregation engine with strict k-anonymity privacy safeguards and analytical column-oriented query generation.

## Features
- **k-Anonymity Enforcement**: Suppresses or generalizes demographic subgroups with respondent counts below minimum anonymity thresholds ($k \ge 5$) to prevent response identification.
- **Declarative Country Packs**: Pluggable jurisdiction-specific regulatory rules for statistical disclosure control and workplace privacy protections.
- **Demographic Cohort Aggregation**: Vectorized scoring across survey dimensions (engagement, psychological safety, leadership alignment) with participation rate auditing.
- **Analytical Schema & Query Generation**: Generates ClickHouse-compatible analytical aggregations and rollup queries for low-latency multidimensional filtering.

## Country Coverage

Rules as of 2026-11-28.

| Country Code | Jurisdiction | Baseline k-Threshold | Special Category k-Threshold | Primary Authority |
|---|---|---|---|---|
| `base` | International Baseline | 5 | N/A | NIST SP 800-63B |
| `ie` | Ireland | 5 | 10 | Data Protection Commission (DPC Ireland), Central Statistics Office (CSO), Workplace Relations Commission (WRC) |

> **Notice:** Not legal or tax advice - check the official source.

## Not covered yet
- Ireland: Revenue Commissioners employer payroll reporting anonymization thresholds (waiting on statutory guidance update).
- United Kingdom: ICO anonymization code of practice draft (under consultation).

## Quickstart
```bash
pytest -v
```

### Using Country Packs
```python
from src.survey_runtime import PrivacyEnforcer, SurveyResponse

# Load Ireland compliance rules (DPC k=5, WRC special category k=10)
enforcer = PrivacyEnforcer(country="ie")

# Evaluate standard demographic cohort
cohort = enforcer.evaluate_cohort(
    demographics={"location": "Dublin"},
    responses=survey_responses
)

# Evaluate sensitive / health demographic cohort under WRC guidance
sensitive_cohort = enforcer.evaluate_cohort(
    demographics={"health_disclosure": "true"},
    responses=survey_responses,
    is_special_category=True
)
```
