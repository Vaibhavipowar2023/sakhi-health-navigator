"""MongoDB connection and collection accessors."""

import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("MONGO_DB", "sakhi")

_client: MongoClient | None = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        # Atlas + OpenSSL 3.x on Windows needs relaxed cert validation.
        # Auth + encryption still active — only the cert-chain check is skipped.
        is_atlas = "mongodb+srv" in MONGO_URI or "mongodb.net" in MONGO_URI
        if is_atlas:
            _client = MongoClient(MONGO_URI, tlsAllowInvalidCertificates=True)
        else:
            _client = MongoClient(MONGO_URI)
    return _client


def get_db():
    return get_client()[DB_NAME]


def get_providers_collection():
    return get_db()["providers"]


def get_sessions_collection():
    return get_db()["sessions"]


def get_audit_collection():
    return get_db()["audit_log"]


def init_db():
    """Create indexes on first run."""
    providers = get_providers_collection()
    providers.create_index("city")
    providers.create_index("specialty")
    providers.create_index("is_active")
    providers.create_index([("city", 1), ("specialty", 1)])
