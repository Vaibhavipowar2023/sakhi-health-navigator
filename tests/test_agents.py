"""Tests for agents and graph wiring."""

import pytest

from backend.app.graph.state import NavigatorState
from backend.app.schemas import (
    PatientProfile,
    ProviderRecord,
    RankedProvider,
    RoutingDecision,
    VerifiedField,
)
from backend.app.agents.research import build_search_params, parse_mcp_results, parse_web_results
from backend.app.agents.ranking import rank_providers
from backend.app.safety.red_flags import check_red_flags


# --- research agent ---

def test_build_search_params_maps_gynec_pathway():
    decision = RoutingDecision(
        recommended_pathway="pcos_hormonal",
        confidence=0.8,
        reasoning="test",
    )
    params = build_search_params(decision, "pune")
    assert params == {"city": "pune", "specialty": "pcos_hormonal"}


def test_build_search_params_maps_general_pathway():
    decision = RoutingDecision(
        recommended_pathway="orthopedic",
        confidence=0.8,
        reasoning="test",
    )
    params = build_search_params(decision, "kolhapur")
    assert params == {"city": "kolhapur", "specialty": "orthopedic"}


def test_build_search_params_unknown_pathway_defaults():
    decision = RoutingDecision(
        recommended_pathway="something_unknown",
        confidence=0.5,
        reasoning="test",
    )
    params = build_search_params(decision, "mumbai")
    assert params["specialty"] == "general_medicine"


def test_parse_mcp_results_verified_fields():
    raw = [{
        "provider_id": "p1",
        "name": "Dr. Test",
        "specialty": "gynecology",
        "credentials": "MBBS, MD",
        "clinic_name": "Test Clinic",
        "city": "pune",
        "insurance": ["Star Health"],
        "availability": [{"day": "monday", "start": "09:00", "end": "13:00"}],
    }]
    results = parse_mcp_results(raw)
    assert len(results) == 1
    assert results[0].name.verified is True
    assert results[0].credentials.verified is True
    assert results[0].insurance_networks.verified is True
    assert results[0].availability.verified is True
    assert results[0].name.source == "mongodb:local"


def test_parse_mcp_results_missing_credentials_unverified():
    raw = [{
        "provider_id": "p2",
        "name": "Dr. Probe",
        "specialty": "gynecology",
        "credentials": None,
        "clinic_name": "Probe Clinic",
        "city": "pune",
    }]
    results = parse_mcp_results(raw)
    assert results[0].credentials.verified is False


def test_parse_web_results_never_verified():
    raw = [{"name": "Dr. Web", "specialty": "gynecology", "city": "kolhapur"}]
    results = parse_web_results(raw)
    assert len(results) == 1
    assert results[0].name.verified is False
    assert results[0].provider_id == "web_0"
    assert results[0].name.source == "web:composio"


# --- ranking agent ---

def test_rank_providers_sorts_descending():
    profile = PatientProfile(
        symptoms=["pain"],
        location="pune",
        insurance="Star Health",
    )
    providers = [
        _make_provider("p1", "gynecology", credentials="MBBS", insurance=["Star Health"]),
        _make_provider("p2", "gynecology", credentials=None, insurance=None),
    ]
    ranked = rank_providers(providers, profile, "gynecology_general")
    assert len(ranked) == 2
    assert ranked[0].total_score >= ranked[1].total_score


def test_rank_providers_empty_list():
    profile = PatientProfile(symptoms=["pain"], location="pune")
    ranked = rank_providers([], profile, "gynecology_general")
    assert ranked == []


# --- safety ---

def test_crisis_flag_detected():
    result = check_red_flags("suicidal thoughts want to end it")
    assert result.triggered
    assert result.level == "crisis"


def test_no_flags_for_mild_symptoms():
    result = check_red_flags("mild headache")
    assert not result.triggered


# --- state ---

def test_navigator_state_defaults():
    state = NavigatorState()
    assert state.conversation == ""
    assert state.profile is None
    assert state.crisis_detected is False
    assert state.ranked == []


# --- helpers ---

def _make_provider(pid, specialty, credentials=None, insurance=None):
    return ProviderRecord(
        provider_id=pid,
        name=VerifiedField(value=f"Dr. {pid}", verified=True),
        specialty=VerifiedField(value=specialty, verified=True),
        credentials=VerifiedField(value=credentials, verified=credentials is not None),
        city=VerifiedField(value="pune", verified=True),
        insurance_networks=VerifiedField(value=insurance, verified=insurance is not None),
    )
