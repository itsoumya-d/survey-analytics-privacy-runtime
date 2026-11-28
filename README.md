# Survey Analytics Privacy Runtime

High-throughput cohort aggregation engine with strict k-anonymity privacy safeguards, country regulatory compliance packs, and analytical column-oriented query generation.

## Features
- **k-Anonymity Enforcement**: Suppresses or generalizes demographic subgroups with respondent counts below minimum anonymity thresholds ($k \ge 5$ in US, $k \ge 10$ in India) to prevent response identification.
- **Country Compliance Packs**: Decoupled, data-driven regulatory rules for jurisdictional data privacy frameworks loaded from `data/packs/<country>/rules.json`.
- **Demographic Cohort Aggregation**: Vectorized scoring across survey dimensions (engagement, psychological safety, leadership alignment) with participation rate auditing.
- **Analytical Schema & Query Generation**: Generates ClickHouse-compatible analytical aggregations and rollup queries for low-latency multidimensional filtering.

## Supported Country Packs

Rules as of 2026-11-28:

| Country | Code | Minimum k Threshold | Regulatory Authority / Standard | Primary Reference |
|---|---|---|---|---|
| United States | `us` | 5 | HHS HIPAA Expert Determination | [HHS De-identification Guidance](https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html) |
| India | `in` | 10 | National Health Authority (ABDM) / MeitY | [ABDM Health Data Management Policy Section 27.2](https://abdm.gov.in/home/ndhm_policy) |

*Not legal or tax advice - check the official source.*

### Not Covered Yet
- Cross-border health data transfer rules under DPDP Act Section 16 (rules pending notification by the Data Protection Board of India).
- Differential privacy Laplacian noise injection for continuous numerical aggregates.

## Quickstart

```python
from src.survey_runtime.privacy import PrivacyEnforcer
from src.survey_runtime.models import SurveyResponse

# Initialize enforcer with India compliance pack (k=10)
enforcer = PrivacyEnforcer(country="in")

responses = [
    SurveyResponse(f"resp_{i}", "survey_101", {"dept": "Clinical"}, {"engagement": 4.5})
    for i in range(12)
]

cohort = enforcer.evaluate_cohort({"dept": "Clinical"}, responses)
print("Anonymized:", cohort.is_anonymized)  # False (12 >= 10)
print("Average scores:", cohort.average_scores)
```

Run test suite:
```bash
pytest -v
```
