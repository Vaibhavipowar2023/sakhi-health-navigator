"""FastAPI routes for the Sakhi navigator."""

import json
import re
import uuid
import urllib.parse
from collections import OrderedDict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

MAX_CACHED_SESSIONS = 200

from backend.app.db.engine import get_providers_collection
from backend.app.graph.builder import build_graph
from backend.app.llm.client import get_llm
from backend.app.llm.prompts.followup import FOLLOWUP_PROMPT
from backend.app.llm.prompts.provider_qa import ANSWER_PROMPT, CASUAL_PROMPT, CLASSIFY_PROMPT

router = APIRouter(prefix="/api")

_graph = build_graph()

# in-memory cache: session_id → list of provider IDs from last search
# web providers also get their details cached since they aren't in MongoDB
# OrderedDict so we can evict oldest sessions when cache is full
_session_providers: OrderedDict[str, list[str]] = OrderedDict()
_web_provider_cache: OrderedDict[str, list[dict]] = OrderedDict()
# tracks which provider the user last asked about, for WhatsApp follow-up
_whatsapp_pending: dict[str, dict] = {}

# diagnosis/prescription refusal — one compiled regex, runs before any LLM
_DIAG_RE = re.compile(
    r"what disease|what.s (?:my )?diagnosis|diagnose me|tell me what.s wrong|"
    r"what (?:condition|illness) .* have|prescribe .*medic|what medic.* should|"
    r"can you diagnose|give me a diagnosis|which medic|what treatment should|"
    r"mujhe kya bimari|meri bimari|dawai? batao|kya (?:rog|bimari) hai",
    re.IGNORECASE,
)

_REFUSAL = {
    "en": "I'm a health navigator, not a diagnostic tool. I can't tell you what "
          "condition you have or prescribe any medicine. What I can do is help you "
          "find the right specialist based on your symptoms. Want me to look for "
          "a doctor near you?",
    "hi": "मैं एक हेल्थ नेविगेटर हूँ, डॉक्टर नहीं। मैं आपको बीमारी का नाम या "
          "दवाई नहीं बता सकती। लेकिन मैं आपके लक्षणों के हिसाब से सही डॉक्टर "
          "ढूंढने में मदद कर सकती हूँ। क्या मैं आपके पास के डॉक्टर खोजूं?",
    "mr": "मी एक हेल्थ नेविगेटर आहे, डॉक्टर नाही. मी तुम्हाला आजार किंवा "
          "औषध सांगू शकत नाही. पण मी तुमच्या लक्षणांनुसार योग्य डॉक्टर "
          "शोधण्यात मदत करू शकते. तुमच्या जवळचे डॉक्टर शोधू का?",
}

_LANG_TAG = {"hi": "\n[Respond in Hindi]", "mr": "\n[Respond in Marathi]"}

_WA_CONFIRM = {
    "en": "Here's the link. Tap the button below to share on WhatsApp.",
    "hi": "यह रहा लिंक। WhatsApp पर शेयर करने के लिए नीचे बटन दबाएं।",
    "mr": "हा लिंक आहे. WhatsApp वर शेअर करण्यासाठी खालचे बटण दाबा.",
}

_WA_OFFER = {
    "en": "\n\nWant me to send the map location to your WhatsApp?",
    "hi": "\n\nक्या मैं WhatsApp पर मैप लोकेशन भेजूं?",
    "mr": "\n\nWhatsApp वर मॅप लोकेशन पाठवू का?",
}


def _last_msg(convo: str) -> str:
    last = convo.strip().rsplit("\n", 1)[-1]
    return last.split(":", 1)[1].strip() if ":" in last else last.strip()


def _wants_diagnosis(convo: str) -> bool:
    return bool(_DIAG_RE.search(_last_msg(convo)))


def _detect_lang(convo: str) -> str:
    if "[Respond in Marathi]" in convo:
        return "mr"
    if "[Respond in Hindi]" in convo:
        return "hi"
    patient_text = " ".join(l for l in convo.split("\n") if l.startswith("Patient:"))
    if sum(1 for c in patient_text if "ऀ" <= c <= "ॿ") > 5:
        if any(m in patient_text for m in ("ते", "आहे", "करा", "सांग", "शकत")):
            return "mr"
        return "hi"
    return "en"


def _cache_session(session_id: str, provider_ids: list[str]) -> None:
    """Store provider IDs for a session, evicting oldest if cache is full."""
    _session_providers[session_id] = provider_ids
    _session_providers.move_to_end(session_id)
    while len(_session_providers) > MAX_CACHED_SESSIONS:
        evicted_id, _ = _session_providers.popitem(last=False)
        _web_provider_cache.pop(evicted_id, None)
        _whatsapp_pending.pop(evicted_id, None)


class ChatRequest(BaseModel):
    conversation: str
    session_id: str = ""


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    crisis: bool = False
    needs_more_info: bool = False
    missing_fields: list[str] = []
    ranked_providers: list[dict] = []
    whatsapp_link: str = ""


def _generate_followup(conversation: str, missing: list[str], lang: str = "en") -> str:
    llm = get_llm(temperature=0.3)
    prompt = FOLLOWUP_PROMPT.format(
        missing_fields=", ".join(missing),
        conversation=conversation,
    ) + _LANG_TAG.get(lang, "")
    return llm.invoke(prompt).content.strip()


def _classify_message(conversation: str) -> str:
    llm = get_llm(temperature=0)
    text = llm.invoke(CLASSIFY_PROMPT.format(conversation=conversation)).content.strip().lower()
    for label in ("refuse", "followup", "casual"):
        if label in text:
            return label
    return "new"


def _get_all_provider_summaries(provider_ids: list[str], session_id: str) -> list[dict]:
    """Get provider summaries from both DB and web cache."""
    collection = get_providers_collection()

    db_ids = [pid for pid in provider_ids if not pid.startswith("web_")]
    docs = list(collection.find({"_id": {"$in": db_ids}}))

    summaries = []
    for doc in docs:
        summaries.append({
            "name": doc["name"],
            "specialty": doc["specialty"],
            "credentials": doc.get("credentials", "Not available"),
            "clinic_name": doc.get("clinic_name", "Not available"),
            "address": doc.get("address", "Not available"),
            "city": doc.get("city"),
            "phone": doc.get("phone", "Not available"),
            "services": doc.get("services", []),
            "insurance": doc.get("insurance", []),
            "availability": doc.get("availability", []),
        })

    if session_id in _web_provider_cache:
        summaries.extend(_web_provider_cache[session_id])
    return summaries


def _answer_provider_question(conversation: str, provider_ids: list[str], session_id: str = "", lang: str = "en") -> str:
    """Look up provider details from MongoDB (and web cache) and answer."""
    summaries = _get_all_provider_summaries(provider_ids, session_id)
    question = conversation.strip().rsplit("\n", 1)[-1]

    llm = get_llm(temperature=0.3)
    prompt = ANSWER_PROMPT.format(
        provider_data=json.dumps(summaries, indent=2),
        question=question,
    ) + _LANG_TAG.get(lang, "")
    return llm.invoke(prompt).content.strip()


def _find_provider_in_response(response_text: str, providers: list[dict]) -> dict | None:
    text_lower = response_text.lower()
    for p in providers:
        name = p.get("name", "")
        if name and len(name) > 3 and name.lower() in text_lower:
            return p
    return None


def _build_whatsapp_link(provider: dict) -> str:
    name = provider.get("name", "Doctor")
    specialty = provider.get("specialty", "")
    address = provider.get("address", "")
    phone = provider.get("phone", "")
    lat = provider.get("latitude")
    lng = provider.get("longitude")

    lines = [name]
    if specialty:
        lines.append(specialty)
    if address:
        lines.append(address)
    if phone:
        lines.append(f"Phone: {phone}")

    lines.append("")
    if lat and lng:
        lines.append(f"Map: https://maps.google.com/?q={lat},{lng}")
    elif address:
        lines.append(f"Map: https://maps.google.com/maps?q={urllib.parse.quote(address)}")

    lines.append("")
    lines.append("Found via Sakhi Health Navigator")

    text = "\n".join(lines)
    return f"https://wa.me/?text={urllib.parse.quote(text)}"


def _is_whatsapp_yes(conversation: str) -> bool:
    last = _last_msg(conversation).lower().rstrip(".!,")
    return last in {
        "yes", "yeah", "yep", "sure", "ok", "okay", "send it",
        "yes please", "yea", "ya", "haan", "ha", "ho", "send",
        "please", "yes send", "do it", "go ahead",
    }


def _handle_casual(conversation: str, lang: str = "en") -> str:
    llm = get_llm(temperature=0.5)
    prompt = CASUAL_PROMPT.format(conversation=conversation) + _LANG_TAG.get(lang, "")
    return llm.invoke(prompt).content.strip()


def _has_contact_info(text: str) -> bool:
    t = text.lower()
    return any(w in t for w in ("address", "phone", "call", "located at", "reach them", "contact"))


RESULTS_PROMPT = """You are Sakhi, a women's health navigator. You talk
like a normal person, not a chatbot.

You just found doctors for someone. Tell them what you found.

Details:
- Care pathway: {pathway}
- Number of specialists found: {count}
- Patient's city: {city}
- Source: {source}

STRICT STYLE RULES:
- Talk like a real person. Short sentences. Use contractions.
- NEVER use em-dashes. Use commas or periods instead.
- NEVER start with "Hey there!", "Great news!", or "I'm happy to".
- NEVER say "may be a good fit" or "pathway may be appropriate".
- If source is "web search", mention that the info is from the web
  and they should verify details before visiting.
- Mention the type of doctor naturally, like "gynecologists" not
  "General Gynecology pathway specialists".
- Tell them to check the list and ask if they want details on anyone.
- No emoji. 2 sentences max.

Good example (database): "I found 20 gynecologists in Pune. Check the
list and ask me about any doctor you're interested in."

Good example (web): "I found 3 gynecologists in Kolhapur from web
search. You might want to verify their details before visiting."

Bad example: "Hey there! I looked into general gynecology specialists
for you and found some wonderful options that may be a good fit! 😊"
{lang_tag}"""


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    lang = _detect_lang(req.conversation)

    if _wants_diagnosis(req.conversation):
        return ChatResponse(reply=_REFUSAL.get(lang, _REFUSAL["en"]), session_id=session_id)

    if session_id in _session_providers:
        if session_id in _whatsapp_pending and _is_whatsapp_yes(req.conversation):
            provider = _whatsapp_pending.pop(session_id)
            return ChatResponse(
                reply=_WA_CONFIRM.get(lang, _WA_CONFIRM["en"]),
                session_id=session_id,
                whatsapp_link=_build_whatsapp_link(provider),
            )

        _whatsapp_pending.pop(session_id, None)
        msg_type = _classify_message(req.conversation)

        if msg_type == "refuse":
            return ChatResponse(reply=_REFUSAL.get(lang, _REFUSAL["en"]), session_id=session_id)

        if msg_type == "followup":
            answer = _answer_provider_question(
                req.conversation, _session_providers[session_id],
                session_id=session_id, lang=lang,
            )
            providers = _get_all_provider_summaries(_session_providers[session_id], session_id)
            matched = _find_provider_in_response(answer, providers)
            if matched and _has_contact_info(answer):
                _whatsapp_pending[session_id] = matched
                answer += _WA_OFFER.get(lang, _WA_OFFER["en"])
            return ChatResponse(reply=answer, session_id=session_id)

        if msg_type == "casual":
            return ChatResponse(
                reply=_handle_casual(req.conversation, lang=lang),
                session_id=session_id,
            )

        # msg_type == "new" → fall through to full pipeline

    try:
        result = _graph.invoke({
            "conversation": req.conversation,
            "session_id": session_id,
        })
    except Exception:
        raise HTTPException(status_code=500, detail="Something went wrong. Please try again.")

    if result.get("crisis_detected"):
        red_flags = result.get("red_flags", [])
        reply = red_flags[0]["message"] if red_flags else (
            "This may need urgent attention. Please contact emergency "
            "services (112) or go to the nearest emergency department."
        )
        return ChatResponse(reply=reply, session_id=session_id, crisis=True)

    if result.get("needs_more_info"):
        missing = result.get("missing_fields", [])
        return ChatResponse(
            reply=_generate_followup(req.conversation, missing, lang=lang),
            session_id=session_id,
            needs_more_info=True,
            missing_fields=missing,
        )

    # normal flow — return ranked providers
    ranked = result.get("ranked", [])
    pathway = ""
    city = ""
    if result.get("routing"):
        pathway = result["routing"].recommended_pathway.replace("_", " ").title()
    if result.get("profile"):
        city = result["profile"].location

    if ranked:
        _cache_session(session_id, [r.provider_id for r in ranked])

        web_summaries = []
        for p in result.get("providers", []):
            if p.provider_id.startswith("web_"):
                web_summaries.append({
                    "name": p.name.value or "Not available",
                    "specialty": p.specialty.value or "Not available",
                    "credentials": p.credentials.value or "Not available",
                    "clinic_name": p.clinic.value or "Not available",
                    "address": p.address.value or "Not available",
                    "city": p.city.value or "Not available",
                    "phone": p.phone.value or "Not available",
                    "latitude": p.latitude, "longitude": p.longitude,
                    "rating": p.rating, "reviews_count": p.reviews_count,
                    "hours": p.hours,
                    "source": "web search (unverified)",
                })
        if web_summaries:
            _web_provider_cache[session_id] = web_summaries

    has_web = any(p.provider_id.startswith("web_") for p in result.get("providers", []))
    has_db = any(not p.provider_id.startswith("web_") for p in result.get("providers", []))
    if has_web and not has_db:
        source = "web search (unverified)"
    elif has_web and has_db:
        source = "database and web search"
    else:
        source = "database (verified)"

    provider_lookup = {p.provider_id: p for p in result.get("providers", [])}
    ranked_data = []
    for r in ranked:
        data = r.model_dump()
        p = provider_lookup.get(r.provider_id)
        if p:
            data.update({
                "address": p.address.value or "", "phone": p.phone.value or "",
                "specialty": p.specialty.value or "", "credentials": p.credentials.value or "",
                "clinic": p.clinic.value or "",
                "latitude": p.latitude, "longitude": p.longitude,
                "rating": p.rating, "reviews_count": p.reviews_count, "hours": p.hours,
            })
        ranked_data.append(data)

    llm = get_llm(temperature=0.3)
    prompt = RESULTS_PROMPT.format(
        pathway=pathway, count=len(ranked), city=city,
        source=source, lang_tag=_LANG_TAG.get(lang, ""),
    )
    reply = llm.invoke(prompt).content.strip()

    return ChatResponse(reply=reply, session_id=session_id, ranked_providers=ranked_data)


@router.get("/health")
async def health():
    return {"status": "ok"}
