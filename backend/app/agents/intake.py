"""Intake agent - extracts a Patient Profile from conversation"""

import json
import structlog
from langchain_core.messages import HumanMessage, SystemMessage

from backend.app.llm.client import get_llm
from backend.app.llm.prompts.intake import EXTRACT_PROMPT, SYSTEM_PROMPT
from backend.app.schemas import PatientProfile

log = structlog.get_logger()


def extract_profile(conversation: str) -> PatientProfile:
    llm = get_llm(temperature=0)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=EXTRACT_PROMPT.format(conversation=conversation)),
    ]

    try:
        structured = llm.with_structured_output(PatientProfile)
        return structured.invoke(messages)
    except Exception as exc:
        log.warning("structured_output_failed", error=str(exc))

    # fallback: ask for JSON directly
    try:
        messages.append(HumanMessage(
            content="Respond with ONLY a JSON object matching PatientProfile fields: "
            "symptoms (list), duration, severity, location, insurance, language, "
            "age_band, pregnancy_status, menstrual_relation, prior_consultations (list), "
            "preferences (dict), red_flags_detected (bool). Use 'unknown' for missing values.",
        ))
        response = llm.invoke(messages)
        text = response.content.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        data = json.loads(text)
        return PatientProfile(**data)
    except Exception as exc:
        log.warning("json_fallback_failed", error=str(exc))
        return PatientProfile()