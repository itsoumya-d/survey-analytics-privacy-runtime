from typing import List, Dict, Optional
from pathlib import Path
from src.survey_runtime.models import SurveyResponse, AggregatedCohort
from src.survey_runtime.packs import load_country_pack

class PrivacyEnforcer:
    """Enforces country-specific k-anonymity thresholds on cohort aggregations."""

    def __init__(
        self,
        k_threshold: Optional[int] = None,
        country: str = "us",
        packs_dir: Optional[Path] = None
    ):
        self.country = country.strip().lower()
        self.pack_data = load_country_pack(self.country, base_dir=packs_dir)
        
        if k_threshold is not None:
            if k_threshold < 1:
                raise ValueError("k_threshold must be >= 1")
            self.k_threshold = k_threshold
        else:
            resolved = None
            for rule in self.pack_data.get("rules", []):
                if rule.get("metric") == "k_anonymity":
                    resolved = int(rule["threshold"])
                    break
            if resolved is None or resolved < 1:
                raise ValueError(f"No valid k_anonymity rule defined for country '{self.country}'")
            self.k_threshold = resolved

    def get_rule(self, rule_id: str) -> Dict:
        for r in self.pack_data.get("rules", []):
            if r.get("id") == rule_id:
                return r
        raise KeyError(f"Rule '{rule_id}' not found in country pack '{self.country}'")

    def evaluate_cohort(
        self,
        demographics: Dict[str, str],
        responses: List[SurveyResponse]
    ) -> AggregatedCohort:
        count = len(responses)
        if count < self.k_threshold:
            return AggregatedCohort(
                demographics=demographics,
                respondent_count=count,
                is_anonymized=True,
                average_scores={},
                redaction_reason=f"Cohort size {count} is below privacy threshold k={self.k_threshold} ({self.country.upper()})"
            )

        # Compute averages across numeric score metrics
        score_sums: Dict[str, float] = {}
        score_counts: Dict[str, int] = {}

        for resp in responses:
            for metric, val in resp.scores.items():
                score_sums[metric] = score_sums.get(metric, 0.0) + val
                score_counts[metric] = score_counts.get(metric, 0) + 1

        averages = {
            metric: round(score_sums[metric] / score_counts[metric], 2)
            for metric in score_sums
        }

        return AggregatedCohort(
            demographics=demographics,
            respondent_count=count,
            is_anonymized=False,
            average_scores=averages
        )
