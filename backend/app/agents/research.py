"""Research agent — finds providers via MongoDB + semantic search and web search."""

import os
import re
import structlog
from datetime import datetime, timezone

from composio_client import Composio

from backend.app.db.engine import get_providers_collection
from backend.app.db.embeddings import embed_text, find_similar
from backend.app.schemas import ProviderRecord, RoutingDecision, VerifiedField

log = structlog.get_logger()


# ── pathway → DB specialty mapping ──────────────────────────────────

def build_search_params(decision: RoutingDecision, city: str) -> dict:
    """Map taxonomy pathway IDs to search-friendly specialty values."""
    specialty_map = {
        # women's health
        "general_gynecology": "general_gynecology",
        "pelvic_pain_endometriosis": "general_gynecology",
        "pcos_hormonal": "pcos_hormonal",
        "fertility": "fertility",
        "obstetrics": "obstetrics",
        "high_risk_obstetrics": "high_risk_obstetrics",
        "urogynecology": "urogynecology",
        "breast_health": "breast_health",
        "menopause": "menopause",
        "perinatal_mental_health": "perinatal_mental_health",
        "pelvic_floor_physio": "pelvic_floor_physiotherapy",
        "adolescent_gynecology": "adolescent_gynecology",
        # general medical
        "orthopedic": "orthopedic",
        "dermatology": "dermatology",
        "mental_health": "psychiatry",
        "general_medicine": "general_medicine",
        "ent": "ent",
        "ophthalmology": "ophthalmology",
        "dental": "dental",
        "gastroenterology": "gastroenterology",
        "endocrinology": "endocrinology",
        "cardiology": "cardiology",
    }
    specialty = specialty_map.get(decision.recommended_pathway, "general_medicine")
    return {"city": city, "specialty": specialty}


# ── local MongoDB search with semantic ranking ──────────────────────

def query_local_db(
    city: str,
    specialty: str | None = None,
    symptoms: str = "",
    limit: int = 20,
) -> list[dict]:
    """Search MongoDB providers in the user's city only.

    1. Filter by city (case-insensitive) and is_active.
    2. If symptoms text provided, embed it and rank by cosine similarity.
    3. If no results in user's city, return empty. Never broaden to other cities.
    """
    collection = get_providers_collection()

    mongo_filter = {
        "city": re.compile(f"^{re.escape(city)}$", re.IGNORECASE),
        "is_active": True,
    }

    if specialty:
        mongo_filter["specialty"] = specialty

    candidates = list(collection.find(mongo_filter))

    if not candidates:
        return []

    # semantic ranking when we have symptoms text
    if symptoms:
        query_vec = embed_text(symptoms)
        ranked = find_similar(query_vec, candidates, top_k=limit)
    else:
        ranked = candidates[:limit]

    results = []
    for doc in ranked:
        results.append({
            "provider_id": doc["_id"],
            "name": doc["name"],
            "specialty": doc["specialty"],
            "credentials": doc.get("credentials"),
            "clinic_name": doc.get("clinic_name"),
            "city": doc["city"],
            "address": doc.get("address"),
            "phone": doc.get("phone"),
            "services": doc.get("services", []),
            "insurance": doc.get("insurance", []),
            "availability": doc.get("availability", []),
            "is_synthetic": doc.get("is_synthetic", True),
            "similarity_score": doc.get("similarity_score"),
        })

    return results


# ── web search via Composio (Google Maps) ────────────────────────


def _clean_title(title: str) -> str:
    if not title:
        return title
    for sep in [" | ", " - ", " — ", " – "]:
        if sep in title:
            title = title.split(sep)[0]
    if ":" in title and len(title) > 50:
        title = title.split(":")[0]
    return title.strip()


def search_web(city: str, specialty: str, limit: int = 10) -> list[dict]:
    """Search Google Maps for providers using Composio.

    Returns structured business data (name, address, phone, rating,
    type, hours) directly — no LLM extraction needed.
    Web results are NEVER verified.
    """
    readable_specialty = specialty.replace("_", " ")
    gynec_specialties = {
        "general_gynecology", "pcos_hormonal", "fertility", "obstetrics",
        "high_risk_obstetrics", "urogynecology", "breast_health", "menopause",
        "perinatal_mental_health", "pelvic_floor_physiotherapy",
        "adolescent_gynecology",
    }
    if specialty in gynec_specialties:
        query = f"{readable_specialty} women doctor in {city}"
    else:
        query = f"{readable_specialty} doctor in {city}"
    log.info("web_search_composio", query=query)

    try:
        client = Composio(api_key=os.environ.get("COMPOSIO_API_KEY", ""))
        result = client.tools.execute(
            "COMPOSIO_SEARCH_GOOGLE_MAPS",
            arguments={"q": query},
        )
        data = result.model_dump()
        local_results = (
            data.get("data", {})
            .get("results", {})
            .get("local_results", [])
        )
    except Exception as exc:
        log.warning("web_search_failed", error=str(exc))
        return []

    if not local_results:
        log.info("web_search_no_results", city=city, specialty=specialty)
        return []

    log.info("composio_results", count=len(local_results))

    providers = []
    for r in local_results[:limit]:
        gps = r.get("gps_coordinates") or {}
        clean_name = _clean_title(r.get("title") or "")
        providers.append({
            "name": clean_name,
            "specialty": r.get("type"),
            "clinic": clean_name,
            "city": city,
            "address": r.get("address"),
            "phone": r.get("phone"),
            "rating": r.get("rating"),
            "reviews": r.get("reviews"),
            "hours": r.get("operating_hours"),
            "latitude": gps.get("latitude"),
            "longitude": gps.get("longitude"),
        })

    log.info("web_search_extracted", count=len(providers))
    return providers


# ── result parsers ──────────────────────────────────────────────────

def parse_mcp_results(raw_results: list[dict]) -> list[ProviderRecord]:
    """Convert local DB results into ProviderRecords (verified=True)."""
    now = datetime.now(timezone.utc)
    source = "mongodb:local"
    providers = []

    for row in raw_results:
        insurance_list = row.get("insurance") or []
        availability_list = row.get("availability") or []

        record = ProviderRecord(
            provider_id=row["provider_id"],
            is_synthetic=row.get("is_synthetic", True),
            name=VerifiedField(value=row.get("name"), verified=True, source=source, fetched_at=now),
            specialty=VerifiedField(value=row.get("specialty"), verified=True, source=source, fetched_at=now),
            credentials=VerifiedField(
                value=row.get("credentials"),
                verified=row.get("credentials") is not None,
                source=source,
                fetched_at=now,
            ),
            clinic=VerifiedField(value=row.get("clinic_name"), verified=True, source=source, fetched_at=now),
            city=VerifiedField(value=row.get("city"), verified=True, source=source, fetched_at=now),
            address=VerifiedField(
                value=row.get("address"),
                verified=row.get("address") is not None,
                source=source,
                fetched_at=now,
            ),
            phone=VerifiedField(
                value=row.get("phone"),
                verified=row.get("phone") is not None,
                source=source,
                fetched_at=now,
            ),
            insurance_networks=VerifiedField(
                value=insurance_list if insurance_list else None,
                verified=len(insurance_list) > 0,
                source=source,
                fetched_at=now,
            ),
            availability=VerifiedField(
                value=availability_list if availability_list else None,
                verified=len(availability_list) > 0,
                source=source,
                fetched_at=now,
            ),
        )
        providers.append(record)

    return providers


def parse_web_results(raw_results: list[dict]) -> list[ProviderRecord]:
    """Convert web search results into ProviderRecords (verified=False).

    Web results are NEVER verified.
    """
    now = datetime.now(timezone.utc)
    source = "web:composio"
    providers = []

    for i, row in enumerate(raw_results):
        record = ProviderRecord(
            provider_id=f"web_{i}",
            is_synthetic=False,
            name=VerifiedField(value=row.get("name"), verified=False, source=source, fetched_at=now),
            specialty=VerifiedField(value=row.get("specialty"), verified=False, source=source, fetched_at=now),
            credentials=VerifiedField(value=row.get("credentials"), verified=False, source=source, fetched_at=now),
            clinic=VerifiedField(value=row.get("clinic"), verified=False, source=source, fetched_at=now),
            city=VerifiedField(value=row.get("city"), verified=False, source=source, fetched_at=now),
            address=VerifiedField(value=row.get("address"), verified=False, source=source, fetched_at=now),
            phone=VerifiedField(value=row.get("phone"), verified=False, source=source, fetched_at=now),
            latitude=row.get("latitude"),
            longitude=row.get("longitude"),
            rating=row.get("rating"),
            reviews_count=row.get("reviews"),
            hours=row.get("hours"),
        )
        providers.append(record)

    return providers
