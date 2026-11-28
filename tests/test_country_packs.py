import json
import pytest
from pathlib import Path
from src.survey_runtime.models import SurveyResponse
from src.survey_runtime.privacy import PrivacyEnforcer
from src.survey_runtime.packs import load_country_pack, get_country_rule

def test_default_country_pack_us_preserves_k5():
    # HHS De-identification Guidance: https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html
    enforcer = PrivacyEnforcer()
    assert enforcer.country == "us"
    assert enforcer.k_threshold == 5
    
    responses_sub_k = [
        SurveyResponse("r1", "s1", {"dept": "Eng"}, {"score": 4.0}),
        SurveyResponse("r2", "s1", {"dept": "Eng"}, {"score": 5.0}),
        SurveyResponse("r3", "s1", {"dept": "Eng"}, {"score": 4.5}),
        SurveyResponse("r4", "s1", {"dept": "Eng"}, {"score": 4.5}),
    ]
    cohort = enforcer.evaluate_cohort({"dept": "Eng"}, responses_sub_k)
    assert cohort.is_anonymized is True
    assert "below privacy threshold k=5 (US)" in cohort.redaction_reason

def test_india_pack_applies_k10_threshold():
    # ABDM Health Data Management Policy Section 27.2: https://abdm.gov.in/home/ndhm_policy
    enforcer = PrivacyEnforcer(country="in")
    assert enforcer.country == "in"
    assert enforcer.k_threshold == 10

    # 9 respondents -> suppressed
    responses_9 = [SurveyResponse(f"r{i}", "s1", {"dept": "Care"}, {"nps": 9.0}) for i in range(9)]
    cohort_9 = enforcer.evaluate_cohort({"dept": "Care"}, responses_9)
    assert cohort_9.is_anonymized is True
    assert cohort_9.average_scores == {}
    assert "below privacy threshold k=10 (IN)" in cohort_9.redaction_reason

    # 10 respondents -> unredacted
    responses_10 = [SurveyResponse(f"r{i}", "s1", {"dept": "Care"}, {"nps": 9.0}) for i in range(10)]
    cohort_10 = enforcer.evaluate_cohort({"dept": "Care"}, responses_10)
    assert cohort_10.is_anonymized is False
    assert cohort_10.average_scores["nps"] == 9.0

def test_india_pack_rule_definitions_match_official_sources():
    # DPDP Act 2023 Section 9: https://www.meity.gov.in/content/digital-personal-data-protection-act-2023
    minor_rule = get_country_rule("in", "in-dpdp-minor-age-threshold")
    assert minor_rule["threshold"] == 18.0
    assert "meity.gov.in" in minor_rule["source_url"]

    # CERT-In Directions Section 5: https://www.cert-in.org.in/PDF/CERT-In_Directions_70B_28.04.2022.pdf
    log_rule = get_country_rule("in", "in-cert-log-retention-days")
    assert log_rule["threshold"] == 180.0
    assert "cert-in.org.in" in log_rule["source_url"]

def test_unknown_country_raises_clear_error():
    with pytest.raises(ValueError) as exc:
        PrivacyEnforcer(country="de")
    assert "Unknown country pack: 'de'" in str(exc.value)

def test_empty_or_whitespace_country_raises_value_error():
    with pytest.raises(ValueError) as exc1:
        load_country_pack("")
    assert "must be a non-empty string" in str(exc1.value)

    with pytest.raises(ValueError) as exc2:
        load_country_pack("   ")
    assert "Unknown country pack: '   '" in str(exc2.value) or "must be a non-empty string" in str(exc2.value)

def test_country_pack_schema_and_sources_lock_integrity():
    repo_root = Path(__file__).resolve().parent.parent
    packs_dir = repo_root / "data" / "packs"
    sources_path = repo_root / "sources.lock.json"

    assert sources_path.exists()
    with open(sources_path, "r", encoding="utf-8") as f:
        lock_data = json.load(f)
    assert "sources" in lock_data
    assert len(lock_data["sources"]) >= 3

    for pack_dir in packs_dir.iterdir():
        if not pack_dir.is_dir():
            continue
        pack_file = pack_dir / "rules.json"
        assert pack_file.exists()
        with open(pack_file, "r", encoding="utf-8") as f:
            pack = json.load(f)
        assert pack["country"] == pack_dir.name
        for rule in pack["rules"]:
            assert "id" in rule and len(rule["id"]) > 0
            assert "metric" in rule and len(rule["metric"]) > 0
            assert "threshold" in rule
            assert rule["source_url"].startswith("http")
            assert rule["checked_on"] == "2026-11-28"

def test_explicit_k_threshold_override_across_countries():
    enforcer = PrivacyEnforcer(k_threshold=7, country="in")
    assert enforcer.country == "in"
    assert enforcer.k_threshold == 7
    responses = [SurveyResponse(f"r{i}", "s1", {"dept": "Ops"}, {"eff": 4.0}) for i in range(7)]
    cohort = enforcer.evaluate_cohort({"dept": "Ops"}, responses)
    assert cohort.is_anonymized is False
