"""Taxonomy integrity and PatientProfile contract tests."""
import pytest

from backend.app.domain.taxonomy import PATHWAY_IDS, PATHWAYS, get_pathway, is_valid_pathway
from backend.app.schemas import PatientProfile, RoutingDecision


def test_taxonomy_has_expected_pathways():
    # 12 women's health + 10 general medical = 22
    assert len(PATHWAY_IDS) == 22
    assert len(PATHWAYS) == 22


def test_every_pathway_is_complete():
    for pathway in PATHWAYS.values():
        for key in ("id", "name", "description", "typical_signals", "escalation_note"):
            assert pathway.get(key), f"{pathway.get('id')} missing {key}"


def test_pathway_validation():
    assert is_valid_pathway("pelvic_pain_endometriosis")
    assert is_valid_pathway("orthopedic")
    assert is_valid_pathway("mental_health")
    assert is_valid_pathway("cardiology")
    assert not is_valid_pathway("made_up_specialty")
    with pytest.raises(KeyError):
        get_pathway("made_up_specialty")


def test_empty_profile_reports_required_fields_missing():
    profile = PatientProfile()
    missing = profile.missing_required_fields()
    # empty profile has no symptoms, so pregnancy_status is skipped
    assert "symptoms" in missing
    assert "severity" in missing
    assert "duration" in missing
    assert "location" in missing
    assert "insurance" in missing
    assert "age_band" in missing
    assert "pregnancy_status" not in missing  # no reproductive symptoms


def test_complete_gynec_profile_reports_nothing_missing():
    profile = PatientProfile(
        symptoms=["pelvic pain"], pregnancy_status="no", severity="moderate",
        duration="6 months", location="Pune", insurance="Star Health", age_band="25-34",
    )
    assert profile.missing_required_fields() == []


def test_non_gynec_profile_skips_pregnancy():
    """Knee pain should not require pregnancy status."""
    profile = PatientProfile(
        symptoms=["knee pain"], severity="moderate",
        duration="3 months", location="Pune", insurance="none", age_band="18_25",
    )
    missing = profile.missing_required_fields()
    assert "pregnancy_status" not in missing


def test_gynec_profile_requires_pregnancy():
    """Irregular periods should require pregnancy status."""
    profile = PatientProfile(
        symptoms=["irregular periods"], severity="moderate",
        duration="3 months", location="Pune", insurance="none", age_band="18_25",
    )
    missing = profile.missing_required_fields()
    assert "pregnancy_status" in missing


def test_routing_decision_rejects_bad_confidence():
    with pytest.raises(ValueError):
        RoutingDecision(recommended_pathway="general_gynecology", confidence=1.4, reasoning="x")
