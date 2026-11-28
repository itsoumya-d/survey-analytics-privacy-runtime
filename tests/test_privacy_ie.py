import pytest
from src.survey_runtime.models import SurveyResponse
from src.survey_runtime.privacy import PrivacyEnforcer
from src.survey_runtime.packs import load_country_pack


def test_ie_pack_dpc_k_anonymity_floor():
    """Validates Data Protection Commission (DPC Ireland) k=5 anonymity floor.
    Official source: https://www.dataprotection.ie/en/guidance-landing/anonymisation-and-pseudonymisation
    """
    source_url = "https://www.dataprotection.ie/en/guidance-landing/anonymisation-and-pseudonymisation"
    enforcer = PrivacyEnforcer(country="ie")
    assert enforcer.country == "ie"
    assert enforcer.k_threshold == 5

    # 4 responses: must be redacted
    sub_k_responses = [
        SurveyResponse(f"r{i}", "s1", {"location": "Dublin"}, {"satisfaction": 4.0})
        for i in range(4)
    ]
    cohort_sub = enforcer.evaluate_cohort({"location": "Dublin"}, sub_k_responses)
    assert cohort_sub.is_anonymized is True
    assert cohort_sub.respondent_count == 4
    assert cohort_sub.average_scores == {}
    assert "below privacy threshold k=5" in cohort_sub.redaction_reason

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
    rules = load_country_pack("ie")
    cso_rule = next(r for r in rules if r["id"] == "IE-CSO-STATISTICAL-DISCLOSURE-SUPPRESSION")
    assert cso_rule["source_url"] == source_url
    assert cso_rule["values"]["cell_suppression_limit"] == 5
    assert cso_rule["values"]["enforce_secondary_suppression"] is True


def test_ie_pack_wrc_special_category_redaction():
    """Validates Workplace Relations Commission (WRC Ireland) special category protection (k=10).
    Official source: https://www.workplacerelations.ie/en/guidance/data-protection-in-the-workplace/
    """
    source_url = "https://www.workplacerelations.ie/en/guidance/data-protection-in-the-workplace/"
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
    assert "k=10" in cohort_special.redaction_reason

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


def test_unknown_country_raises_value_error():
    """Verifies that an unsupported country raises ValueError."""
    with pytest.raises(ValueError, match="Unknown country code: 'xx'"):
        PrivacyEnforcer(country="xx")


def test_base_pack_default_backward_compatible():
    """Verifies that default initialization preserves backward compatibility with base rules."""
    enforcer = PrivacyEnforcer()
    assert enforcer.country == "base"
    assert enforcer.k_threshold == 5
