from typing import List, Dict
from src.survey_runtime.models import SurveyResponse, AggregatedCohort

class PrivacyEnforcer:
    """Enforces k-anonymity thresholds on cohort aggregations."""

    def __init__(self, k_threshold: int = 5):
        if k_threshold < 1:
            raise ValueError("k_threshold must be >= 1")
        self.k_threshold = k_threshold

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
                redaction_reason=f"Cohort size {count} is below privacy threshold k={self.k_threshold}"
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
