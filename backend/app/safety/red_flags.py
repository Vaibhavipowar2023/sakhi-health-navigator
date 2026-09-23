"""Deterministic red-flag engine. No LLM involved.

Runs on both raw text and structured profile so a bad extraction
can't suppress an escalation.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from backend.app.schemas import PatientProfile

_RULES_PATH = Path(__file__).parent / "rules.yaml"


class RedFlagResult(BaseModel):
    triggered: bool
    level: str | None = None
    matched_rule_ids: list[str] = Field(default_factory=list)
    message: str = ""


def _load_rules() -> dict:
    with open(_RULES_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


RULES: dict = _load_rules()


def _text_rule_fires(rule: dict, text: str) -> bool:
    # AND-of-ORs: every group needs at least one pattern hit
    return all(
        any(re.search(pat, text, re.IGNORECASE) for pat in group)
        for group in rule["pattern_groups"]
    )


def _profile_rule_fires(rule: dict, profile: PatientProfile) -> bool:
    if profile.pregnancy_status not in rule["pregnancy_status"]:
        return False
    return any(
        re.search(pat, symptom, re.IGNORECASE)
        for pat in rule["symptom_patterns"]
        for symptom in profile.symptoms
    )


def check_red_flags(raw_text: str, profile: PatientProfile | None = None) -> RedFlagResult:
    """Evaluate every rule. Collect all matches, never short-circuit."""
    matched: list[str] = []
    levels: set[str] = set()

    for rule in RULES["text_rules"]:
        if _text_rule_fires(rule, raw_text):
            matched.append(rule["id"])
            levels.add(rule["level"])

    if profile is not None:
        for rule in RULES["profile_rules"]:
            if _profile_rule_fires(rule, profile):
                matched.append(rule["id"])
                levels.add(rule["level"])

    if not matched:
        return RedFlagResult(triggered=False)

    level = "crisis" if "crisis" in levels else "emergency"
    message = RULES["crisis_message"] if level == "crisis" else RULES["emergency_message"]
    return RedFlagResult(triggered=True, level=level, matched_rule_ids=matched, message=message.strip())
