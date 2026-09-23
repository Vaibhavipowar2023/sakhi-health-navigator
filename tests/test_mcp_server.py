"""MCP server tool tests.

Tests the tool functions directly (not via MCP protocol) against
a mock MongoDB collection with seed data.
"""
import re

import pytest

from backend.app.db.seed_providers import PROVIDERS


class MockCollection:
    """In-memory stand-in for a pymongo collection.

    Supports the subset of the pymongo API that our MCP tools use:
    find, find_one, distinct, and a chainable limit.
    """

    def __init__(self, docs):
        self._docs = list(docs)

    def find(self, filter_dict=None):
        results = self._apply_filter(filter_dict or {})
        return MockCursor(results)

    def find_one(self, filter_dict=None):
        results = self._apply_filter(filter_dict or {})
        return results[0] if results else None

    def distinct(self, field):
        values = set()
        for doc in self._docs:
            val = doc.get(field)
            if isinstance(val, list):
                values.update(val)
            elif val is not None:
                values.add(val)
        return list(values)

    def _apply_filter(self, f):
        out = []
        for doc in self._docs:
            if self._matches(doc, f):
                out.append(doc)
        return out

    def _matches(self, doc, f):
        for key, condition in f.items():
            val = doc.get(key)
            if isinstance(condition, re.Pattern):
                if val is None:
                    return False
                if isinstance(val, list):
                    if not any(condition.search(str(v)) for v in val):
                        return False
                elif not condition.search(str(val)):
                    return False
            elif val != condition:
                return False
        return True


class MockCursor:
    def __init__(self, docs):
        self._docs = docs

    def limit(self, n):
        self._docs = self._docs[:n]
        return self

    def __iter__(self):
        return iter(self._docs)


def _build_docs():
    """Convert PROVIDERS list into MongoDB-shaped documents."""
    docs = []
    for data in PROVIDERS:
        doc = {
            "_id": data["id"],
            "name": data["name"],
            "specialty": data["specialty"],
            "subspecialty": data.get("subspecialty"),
            "credentials": data.get("credentials"),
            "clinic_name": data.get("clinic_name"),
            "city": data["city"],
            "address": data.get("address"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "phone": data.get("phone"),
            "services": data.get("services", []),
            "insurance": data.get("insurance", []),
            "availability": data.get("availability", []),
            "is_synthetic": True,
            "is_active": True,
        }
        docs.append(doc)
    return docs


@pytest.fixture
def _seeded_db(monkeypatch):
    """Patch MCP server to use our in-memory mock collection."""
    mock = MockCollection(_build_docs())
    monkeypatch.setattr(
        "mcp_server.server.get_providers_collection", lambda: mock,
    )
    monkeypatch.setattr("mcp_server.server.FAULT_MODE", "")


def test_search_pune_returns_results(_seeded_db):
    from mcp_server.server import search_providers
    results = search_providers(city="Pune")
    assert len(results) > 0
    assert all(r["city"] == "Pune" for r in results)


def test_search_mumbai_returns_results(_seeded_db):
    from mcp_server.server import search_providers
    results = search_providers(city="Mumbai")
    assert len(results) > 0


def test_search_unknown_city_returns_empty(_seeded_db):
    from mcp_server.server import search_providers
    results = search_providers(city="Kolhapur")
    assert results == []


def test_search_by_specialty(_seeded_db):
    from mcp_server.server import search_providers
    results = search_providers(city="Pune", specialty="fertility")
    assert len(results) >= 2
    assert all(r["specialty"] == "fertility" for r in results)


def test_search_by_insurance(_seeded_db):
    from mcp_server.server import search_providers
    results = search_providers(city="Pune", insurance="Star Health")
    assert len(results) > 0


def test_search_case_insensitive(_seeded_db):
    from mcp_server.server import search_providers
    lower = search_providers(city="pune")
    upper = search_providers(city="PUNE")
    assert len(lower) == len(upper)
    assert len(lower) > 0


def test_get_provider_details_found(_seeded_db):
    from mcp_server.server import get_provider_details
    details = get_provider_details("p-pune-gyn-001")
    assert details is not None
    assert details["name"] == "Dr. Anita Kulkarni"
    assert len(details["services"]) > 0
    assert len(details["insurance_networks"]) > 0
    assert len(details["availability"]) > 0


def test_get_provider_details_missing_fields(_seeded_db):
    from mcp_server.server import get_provider_details
    details = get_provider_details("p-pune-gyn-004")
    assert details is not None
    assert details["credentials"] is None
    assert details["insurance_networks"] == []
    assert details["availability"] == []


def test_get_provider_details_not_found(_seeded_db):
    from mcp_server.server import get_provider_details
    assert get_provider_details("nonexistent-id") is None


def test_list_insurance_networks(_seeded_db):
    from mcp_server.server import list_insurance_networks
    networks = list_insurance_networks()
    assert "Star Health" in networks
    assert "ICICI Lombard" in networks
    assert networks == sorted(networks)


def test_fault_mode_error(_seeded_db, monkeypatch):
    monkeypatch.setattr("mcp_server.server.FAULT_MODE", "error")
    from mcp_server.server import search_providers
    with pytest.raises(RuntimeError, match="simulated tool failure"):
        search_providers(city="Pune")
