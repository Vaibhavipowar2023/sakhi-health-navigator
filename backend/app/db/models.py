"""MongoDB document shapes for reference.

MongoDB is schema-less, so these are NOT enforced ORM models.
They're just notes for developers about what each collection stores.
Actual validation happens via Pydantic schemas in backend/app/schemas.py.

Collections
-----------
providers    — seeded by seed_providers.py, queried by research agent
sessions     — written by the API layer per conversation
audit_log    — written by graph nodes for observability

Provider document example:
{
    "_id": "p-pune-gyn-001",
    "name": "Dr. Anita Kulkarni",
    "specialty": "general_gynecology",
    "subspecialty": null,
    "credentials": "MBBS, MD (OB-GYN), FICOG",
    "clinic_name": "Kulkarni Women's Clinic",
    "city": "Pune",
    "address": "...",
    "latitude": 18.5089,
    "longitude": 73.8400,
    "phone": "+91-7249362032",
    "services": ["routine gynecological exam", ...],
    "insurance": ["Star Health", "ICICI Lombard"],
    "availability": [{"day": "monday", "start": "09:00", "end": "13:00"}, ...],
    "is_synthetic": true,
    "is_active": true,
    "embedding": [0.0123, -0.045, ...]   # 384-dim from all-MiniLM-L6-v2
}

Session document example:
{
    "_id": "session-uuid",
    "patient_city": "Pune",
    "conversation": "...",
    "red_flag_triggered": false,
    "routing_pathway": "gynecology_general",
    "ranked_providers": [...],
    "created_at": ISODate("..."),
}
"""
