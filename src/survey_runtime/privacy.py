from typing import List, Dict, Optional, Any
from src.survey_runtime.models import SurveyResponse, AggregatedCohort
from src.survey_runtime.packs import load_country_pack


class PrivacyEnforcer:
    """Enforces k-anonymity thresholds and regulatory disclosure control rules on cohort aggregations."""

    def __init__(self, k_threshold: Optional[int] = None, country: str = "base"):
        self.country = country
        self.rules = load_country_pack(country)

        # Derive defaults from country pack
        self.pack_k = 5
        self.special_category_k = 10

        for rule in self.rules:
            vals = rule.get("values", {})
            if "min_k_threshold" in vals:
                self.pack_k = int(vals["min_k_threshold"])
            if "special_category_min_k" in vals:
                self.special_category_k = int(vals["special_category_min_k"])

        if k_threshold is not None:
            if k_threshold < 1:
                raise ValueError("k_threshold must be >= 1")
            self.k_threshold = k_threshold
        else:
            self.k_threshold = self.pack_k

    def evaluate_cohort(
        self,
        demographics: Dict[str, str],
        responses: List[SurveyResponse],
        is_special_category: bool = False
    ) -> AggregatedCohort:
        count = len(responses)
        effective_k = self.special_category_k if is_special_category else self.k_threshold

        if count < effective_k:
            reason = f"Cohort size {count} is below privacy threshold k={effective_k} for country pack '{self.country}'"
            if is_special_category:
                reason += " (special category protection active)"
            return AggregatedCohort(
                demographics=demographics,
                respondent_count=count,
                is_anonymized=True,
                average_scores={},
                redaction_reason=reason,
                country=self.country
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
            average_scores=averages,
            country=self.country
        )
