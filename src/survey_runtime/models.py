from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class SurveyResponse:
    response_id: str
    survey_id: str
    demographics: Dict[str, str]  # e.g., {"department": "Engineering", "tenure": "1-2y"}
    scores: Dict[str, float]      # e.g., {"engagement": 4.5, "autonomy": 5.0}

@dataclass
class AggregatedCohort:
    demographics: Dict[str, str]
    respondent_count: int
    is_anonymized: bool
    average_scores: Dict[str, float] = field(default_factory=dict)
    redaction_reason: str = ""
    country: str = "base"
