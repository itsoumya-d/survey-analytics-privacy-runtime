import pytest
from src.survey_runtime.models import SurveyResponse
from src.survey_runtime.privacy import PrivacyEnforcer

def test_privacy_enforcer_redacts_sub_k_cohort():
    enforcer = PrivacyEnforcer(k_threshold=5)
    responses = [
        SurveyResponse("r1", "s1", {"dept": "Infra"}, {"engagement": 4.0}),
        SurveyResponse("r2", "s1", {"dept": "Infra"}, {"engagement": 5.0}),
        SurveyResponse("r3", "s1", {"dept": "Infra"}, {"engagement": 4.5}),
    ]
    cohort = enforcer.evaluate_cohort({"dept": "Infra"}, responses)
    assert cohort.is_anonymized is True
    assert cohort.respondent_count == 3
    assert cohort.average_scores == {}
    assert "below privacy threshold" in cohort.redaction_reason

def test_privacy_enforcer_allows_k_compliant_cohort():
    enforcer = PrivacyEnforcer(k_threshold=3)
    responses = [
        SurveyResponse("r1", "s1", {"dept": "Product"}, {"engagement": 4.0}),
        SurveyResponse("r2", "s1", {"dept": "Product"}, {"engagement": 5.0}),
        SurveyResponse("r3", "s1", {"dept": "Product"}, {"engagement": 3.0}),
    ]
    cohort = enforcer.evaluate_cohort({"dept": "Product"}, responses)
    assert cohort.is_anonymized is False
    assert cohort.respondent_count == 3
    assert cohort.average_scores["engagement"] == 4.0
