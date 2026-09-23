"""Ranking agent — deterministic scoring, no LLM involved."""

from backend.app.domain.scoring import score_provider
from backend.app.schemas import PatientProfile, ProviderRecord, RankedProvider


def rank_providers(
    providers: list[ProviderRecord],
    profile: PatientProfile,
    pathway: str,
) -> list[RankedProvider]:
    scored = []
    for provider in providers:
        factors = _extract_factors(provider, profile, pathway)
        result = score_provider(
            provider_id=provider.provider_id,
            name=provider.name.value or "Unknown",
            city=provider.city.value or "",
            factors=factors,
        )
        result.rating = provider.rating
        scored.append(result)

    # highest score first, Google Maps rating as tiebreaker
    scored.sort(key=lambda r: (-r.total_score, -(r.rating or 0), r.provider_id))
    return scored


def _field_score(field):
    """verified + has value = 100, verified + no value = 0, unverified with value = 50, unverified no value = None."""
    if field.verified:
        return 100.0 if field.value else 0.0
    if field.value:
        return 50.0
    return None


def _extract_factors(provider: ProviderRecord, profile: PatientProfile, pathway: str = "") -> dict:
    """Turn ProviderRecord verified fields into 0-100 factor scores.

    Verified + value = 100, unverified + value = 50 (partial credit),
    unverified + no value = None → scoring engine treats as 0 and flags it.
    """
    factors = {}

    # specialty_match: does the provider's specialty align with the care pathway?
    if not provider.specialty.value:
        factors["specialty_match"] = None
    elif pathway:
        match = provider.specialty.value.lower() == pathway.lower()
        base = 100.0 if match else 0.0
        factors["specialty_match"] = base if provider.specialty.verified else (base * 0.5 if match else 0.0)
    else:
        factors["specialty_match"] = _field_score(provider.specialty)

    factors["expertise_match"] = _field_score(provider.credentials)

    # insurance — check if patient's plan is in the provider's networks
    if not provider.insurance_networks.verified and not provider.insurance_networks.value:
        factors["insurance_match"] = None
    elif provider.insurance_networks.value and profile.insurance != "unknown":
        nets = provider.insurance_networks.value
        base = 100.0 if profile.insurance in nets else 0.0
        factors["insurance_match"] = base if provider.insurance_networks.verified else base * 0.5
    else:
        factors["insurance_match"] = 0.0

    # location — same city?
    if not provider.city.value:
        factors["location"] = None
    elif profile.location != "unknown":
        match = provider.city.value.lower() == profile.location.lower()
        base = 100.0 if match else 0.0
        factors["location"] = base if provider.city.verified else (base * 0.5 if match else 0.0)
    else:
        factors["location"] = 0.0

    factors["availability"] = _field_score(provider.availability)

    return factors
