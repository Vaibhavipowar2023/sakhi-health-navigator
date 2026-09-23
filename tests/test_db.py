"""Provider seed data validation tests.

These test the PROVIDERS list structure directly — no MongoDB needed.
"""
from collections import Counter

from backend.app.db.seed_providers import PROVIDERS


def test_seed_data_count():
    assert len(PROVIDERS) >= 40


def test_pune_and_mumbai_split():
    pune = [p for p in PROVIDERS if p["city"] == "Pune"]
    mumbai = [p for p in PROVIDERS if p["city"] == "Mumbai"]
    assert len(pune) + len(mumbai) == len(PROVIDERS)
    assert len(pune) > 0 and len(mumbai) > 0


def test_all_twelve_specialties_covered():
    specs = {p["specialty"] for p in PROVIDERS}
    assert len(specs) == 12


def test_every_specialty_has_at_least_two_providers():
    counts = Counter(p["specialty"] for p in PROVIDERS)
    for spec, n in counts.items():
        assert n >= 2, f"{spec} has only {n} provider(s)"


def test_hallucination_probes_exist():
    no_creds = [p for p in PROVIDERS if p.get("credentials") is None]
    assert len(no_creds) >= 3, "need providers with missing credentials"

    no_coords = [p for p in PROVIDERS if p.get("latitude") is None]
    assert len(no_coords) >= 3, "need providers with missing coordinates"

    no_insurance = [p for p in PROVIDERS if not p.get("insurance")]
    assert len(no_insurance) >= 3, "need providers with no insurance"


def test_provider_ids_are_unique():
    ids = [p["id"] for p in PROVIDERS]
    assert len(ids) == len(set(ids)), "duplicate provider IDs found"


def test_all_specialties_are_valid_taxonomy():
    from backend.app.domain.taxonomy import PATHWAY_IDS
    for p in PROVIDERS:
        assert p["specialty"] in PATHWAY_IDS, (
            f"{p['id']} has invalid specialty {p['specialty']!r}"
        )


def test_every_provider_has_required_fields():
    required = ["id", "name", "specialty", "city"]
    for p in PROVIDERS:
        for field in required:
            assert field in p, f"{p.get('id', '?')} missing {field}"


def test_services_are_lists():
    for p in PROVIDERS:
        services = p.get("services", [])
        assert isinstance(services, list), f"{p['id']} services is not a list"
        assert len(services) > 0, f"{p['id']} has no services"
