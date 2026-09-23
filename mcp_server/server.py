"""MCP server: women-health-directory

The only way agents access provider data from the local DB.
Web search, booking, and notifications go through Composio
directly in the agents.
"""
import os
import re
import time

try:
    from mcp.server.fastmcp import FastMCP  # mcp v1
except ImportError:
    from mcp.server.mcpserver import MCPServer as FastMCP  # mcp v2

from backend.app.db.engine import get_providers_collection, init_db

mcp = FastMCP("women-health-directory")

FAULT_MODE = os.environ.get("MCP_FAULT_MODE", "")


def _check_fault():
    if FAULT_MODE == "timeout":
        time.sleep(999)
    elif FAULT_MODE == "error":
        raise RuntimeError("simulated tool failure (MCP_FAULT_MODE=error)")


@mcp.tool()
def search_providers(
    city: str,
    specialty: str | None = None,
    insurance: str | None = None,
    limit: int = 20,
) -> list[dict]:
    """Find providers by city, optionally filtered by specialty and insurance.

    Returns basic info only. Call get_provider_details for the full record.
    """
    _check_fault()
    collection = get_providers_collection()

    mongo_filter = {
        "city": re.compile(f"^{re.escape(city)}$", re.IGNORECASE),
        "is_active": True,
    }
    if specialty:
        mongo_filter["specialty"] = specialty
    if insurance:
        mongo_filter["insurance"] = re.compile(re.escape(insurance), re.IGNORECASE)

    results = []
    for doc in collection.find(mongo_filter).limit(limit):
        results.append({
            "provider_id": doc["_id"],
            "name": doc["name"],
            "specialty": doc["specialty"],
            "clinic_name": doc.get("clinic_name"),
            "city": doc["city"],
            "is_synthetic": doc.get("is_synthetic", True),
        })
    return results


@mcp.tool()
def get_provider_details(provider_id: str) -> dict | None:
    """Full details for one provider including services, insurance, availability."""
    _check_fault()
    collection = get_providers_collection()
    doc = collection.find_one({"_id": provider_id, "is_active": True})
    if not doc:
        return None
    return {
        "provider_id": doc["_id"],
        "name": doc["name"],
        "specialty": doc["specialty"],
        "subspecialty": doc.get("subspecialty"),
        "credentials": doc.get("credentials"),
        "clinic_name": doc.get("clinic_name"),
        "city": doc["city"],
        "address": doc.get("address"),
        "latitude": doc.get("latitude"),
        "longitude": doc.get("longitude"),
        "phone": doc.get("phone"),
        "is_synthetic": doc.get("is_synthetic", True),
        "services": doc.get("services", []),
        "insurance_networks": doc.get("insurance", []),
        "availability": doc.get("availability", []),
    }


@mcp.tool()
def list_insurance_networks() -> list[str]:
    """All distinct insurance names in the local directory."""
    _check_fault()
    collection = get_providers_collection()
    return sorted(collection.distinct("insurance"))


if __name__ == "__main__":
    init_db()
    mcp.run(transport="stdio")
