"""Routing agent — picks a care pathway from the taxonomy."""

import json
import structlog
from backend.app.domain.taxonomy import PATHWAY_IDS
from backend.app.llm.client import get_llm
from backend.app.llm.prompts.routing import ROUTE_PROMPT, SYSTEM_PROMPT
from backend.app.schemas import PatientProfile, RoutingDecision

log = structlog.get_logger()


def route_patient(profile: PatientProfile) -> RoutingDecision:
    pathway_list = "\n".join(f"- {p}" for p in sorted(PATHWAY_IDS))

    llm = get_llm(temperature=0)

    system = SYSTEM_PROMPT.format(pathways=pathway_list)
    user = ROUTE_PROMPT.format(
        symptoms=profile.symptoms,
        duration=profile.duration,
        severity=profile.severity,
        pregnancy_status=profile.pregnancy_status,
        menstrual_relation=profile.menstrual_relation,
        age_band=profile.age_band,
        prior_consultations=profile.prior_consultations,
        red_flags_detected=profile.red_flags_detected,
    )

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    try:
        structured = llm.with_structured_output(RoutingDecision)
        return structured.invoke(messages)
    except Exception as exc:
        log.warning("structured_output_failed", error=str(exc))

    # fallback: ask for JSON directly
    try:
        messages.append({"role": "user", "content": (
            "Respond with ONLY a JSON object: recommended_pathway (string from the list), "
            "alternative_pathway (string or null), confidence (float 0-1), "
            "reasoning (string), requires_urgent_evaluation (bool)."
        )})
        response = llm.invoke(messages)
        text = response.content.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        data = json.loads(text)
        return RoutingDecision(**data)
    except Exception as exc:
        log.warning("json_fallback_failed", error=str(exc))
        return RoutingDecision(
            recommended_pathway="general_medicine",
            confidence=0.3,
            reasoning="Could not determine pathway from conversation.",
        )
