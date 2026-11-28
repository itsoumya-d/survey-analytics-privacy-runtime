# Survey Analytics Privacy Runtime

High-throughput cohort aggregation engine with strict k-anonymity privacy safeguards, country regulatory compliance packs, and analytical column-oriented query generation.

## Features
- **k-Anonymity Enforcement**: Suppresses or generalizes demographic subgroups with respondent counts below minimum anonymity thresholds ($k \ge 5$ in US and IE, $k \ge 10$ in India and IE special category) to prevent response identification.
- **Country Compliance Packs**: Decoupled, data-driven regulatory rules for jurisdictional data privacy frameworks loaded from `data/packs/<country>/rules.json`.
- **Demographic Cohort Aggregation**: Vectorized scoring across survey dimensions (engagement, psychological safety, leadership alignment) with participation rate auditing.
- **Analytical Schema & Query Generation**: Generates ClickHouse-compatible analytical aggregations and rollup queries for low-latency multidimensional filtering.

## Supported Country Packs

Rules as of 2026-11-28:

| Country | Code | Minimum k Threshold | Regulatory Authority / Standard | Primary Reference |
|---|---|---|---|---|
| United States | `us` | 5 | HHS HIPAA Expert Determination | [HHS De-identification Guidance](https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html) |
| India | `in` | 10 | National Health Authority (ABDM) / MeitY | [ABDM Health Data Management Policy Section 27.2](https://abdm.gov.in/home/ndhm_policy) |
| Ireland | `ie` | 5 (10 for special category) | Data Protection Commission (DPC) / CSO / WRC | [DPC Guidance on Anonymisation](https://www.dataprotection.ie/en/guidance-landing/anonymisation-and-pseudonymisation) |

*Not legal or tax advice - check the official source.*

### Not Covered Yet
- Cross-border health data transfer rules under DPDP Act Section 16 (rules pending notification by the Data Protection Board of India).
- Differential privacy Laplacian noise injection for continuous numerical aggregates.
- Revenue Commissioners employer payroll reporting anonymization thresholds (waiting on statutory guidance update).

## Quickstart

```python
from src.survey_runtime.privacy import PrivacyEnforcer
from src.survey_runtime.models import SurveyResponse

# Initialize enforcer with Ireland compliance pack (k=5 baseline, k=10 special category)
enforcer = PrivacyEnforcer(country="ie")

responses = [
    SurveyResponse(f"resp_{i}", "survey_101", {"location": "Dublin"}, {"engagement": 4.5})
    for i in range(6)
]

cohort = enforcer.evaluate_cohort({"location": "Dublin"}, responses)
print("Anonymized:", cohort.is_anonymized)  # False (6 >= 5)
print("Average scores:", cohort.average_scores)
```

Run test suite:
```bash
pytest -v
```
