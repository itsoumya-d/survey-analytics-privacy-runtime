import pytest
from src.survey_runtime.models import SurveyResponse
from src.survey_runtime.privacy import PrivacyEnforcer
from src.survey_runtime.packs import get_country_rule


def test_ie_pack_dpc_k_anonymity_floor():
    """Validates Data Protection Commission (DPC Ireland) k=5 anonymity floor.
    Official source: https://www.dataprotection.ie/en/guidance-landing/anonymisation-and-pseudonymisation
    """
    source_url = "https://www.dataprotection.ie/en/guidance-landing/anonymisation-and-pseudonymisation"
    enforcer = PrivacyEnforcer(country="ie")
    assert enforcer.country == "ie"
    assert enforcer.k_threshold == 5

    rule = get_country_rule("ie", "ie-dpc-k-anonymity")
    assert rule["source_url"] == source_url
    assert rule["threshold"] == 5

    # 4 responses: must be redacted
    sub_k_responses = [
        SurveyResponse(f"r{i}", "s1", {"location": "Dublin"}, {"satisfaction": 4.0})
        for i in range(4)
    ]
    cohort_sub = enforcer.evaluate_cohort({"location": "Dublin"}, sub_k_responses)
    assert cohort_sub.is_anonymized is True
    assert cohort_sub.respondent_count == 4
    assert cohort_sub.average_scores == {}
    assert "below privacy threshold k=5 (IE)" in cohort_sub.redaction_reason

    # 5 responses: meets k=5 floor
    k_responses = [
        SurveyResponse(f"r{i}", "s1", {"location": "Dublin"}, {"satisfaction": 4.0 + (i * 0.1)})
        for i in range(5)
    ]
    cohort_ok = enforcer.evaluate_cohort({"location": "Dublin"}, k_responses)
    assert cohort_ok.is_anonymized is False
    assert cohort_ok.respondent_count == 5
    assert cohort_ok.average_scores["satisfaction"] == 4.2


def test_ie_pack_cso_statistical_disclosure_suppression():
    """Validates Central Statistics Office (CSO Ireland) Statistical Disclosure Control.
    Official source: https://www.cso.ie/en/aboutus/organisationandmethodology/statisticalmethodology/statisticaldisclosurecontrol/
    """
    source_url = "https://www.cso.ie/en/aboutus/organisationandmethodology/statisticalmethodology/statisticaldisclosurecontrol/"
    rule = get_country_rule("ie", "ie-cso-cell-suppression")
    assert rule["source_url"] == source_url
    assert rule["threshold"] == 5


def test_ie_pack_wrc_special_category_redaction():
    """Validates Workplace Relations Commission (WRC Ireland) special category protection (k=10).
    Official source: https://www.workplacerelations.ie/en/guidance/data-protection-in-the-workplace/
    """
    source_url = "https://www.workplacerelations.ie/en/guidance/data-protection-in-the-workplace/"
    rule = get_country_rule("ie", "ie-wrc-special-category")
    assert rule["source_url"] == source_url
    assert rule["threshold"] == 10

    enforcer = PrivacyEnforcer(country="ie")

    # 8 responses with special category flag: must be suppressed because k < 10
    special_responses = [
        SurveyResponse(f"r{i}", "s1", {"health_support_needed": "yes"}, {"wellbeing": 3.5})
        for i in range(8)
    ]
    cohort_special = enforcer.evaluate_cohort(
        {"health_support_needed": "yes"},
        special_responses,
        is_special_category=True
    )
    assert cohort_special.is_anonymized is True
    assert cohort_special.respondent_count == 8
    assert "special category protection active" in cohort_special.redaction_reason
    assert "k=10 (IE)" in cohort_special.redaction_reason

    # 10 responses with special category flag: allowed
    special_10_responses = [
        SurveyResponse(f"r{i}", "s1", {"health_support_needed": "yes"}, {"wellbeing": 4.0})
        for i in range(10)
    ]
    cohort_special_ok = enforcer.evaluate_cohort(
        {"health_support_needed": "yes"},
        special_10_responses,
        is_special_category=True
    )
    assert cohort_special_ok.is_anonymized is False
    assert cohort_special_ok.respondent_count == 10
    assert cohort_special_ok.average_scores["wellbeing"] == 4.0
