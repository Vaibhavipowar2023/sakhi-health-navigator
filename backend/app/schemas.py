"""Pydantic data contracts for the Sakhi navigator."""
from __future__ import annotations

from datetime import datetime
from typing import Any, ClassVar, Literal

from pydantic import BaseModel, Field

Severity = Literal["mild", "moderate", "severe", "unknown"]
PregnancyStatus = Literal["no", "pregnant", "possibly", "postpartum", "declined", "not_applicable", "unknown"]
YesNoUnknown = Literal["yes", "no", "unknown"]


class PatientProfile(BaseModel):
    """Structured output of the Intake Agent."""

    symptoms: list[str] = Field(default_factory=list)
    duration: str = "unknown"
    severity: Severity = "unknown"
    location: str = "unknown"
    insurance: str = "unknown"
    language: str = "English"
    age_band: str = "unknown"
    pregnancy_status: PregnancyStatus = "unknown"
    menstrual_relation: YesNoUnknown = "unknown"
    prior_consultations: list[str] = Field(default_factory=list)
    preferences: dict[str, Any] = Field(default_factory=dict)
    red_flags_detected: bool = False

    # pregnancy_status is required because the red-flag rules depend on it
    REQUIRED_FIELDS: ClassVar[tuple[str, ...]] = (
        "symptoms", "pregnancy_status", "severity", "duration",
        "location", "insurance", "age_band",
    )

    def missing_required_fields(self) -> list[str]:
        missing = []
        for field in self.REQUIRED_FIELDS:
            value = getattr(self, field)
            if value == [] or value == "unknown":
                # pregnancy_status is not needed for non-reproductive issues
                if field == "pregnancy_status" and self.pregnancy_status == "unknown":
                    if not self._symptoms_need_pregnancy_check():
                        continue
                missing.append(field)
        return missing

    def _symptoms_need_pregnancy_check(self) -> bool:
        """Check if symptoms are reproductive/gynecological."""
        reproductive_keywords = [
            "period", "menstrual", "pregnant", "pregnancy", "fertility",
            "conceive", "pelvic", "vaginal", "discharge", "breast",
            "ovary", "uterus", "womb", "hormonal", "cramp", "bleeding",
            "spotting", "missed period", "irregular period", "postpartum",
        ]
        all_symptoms = " ".join(self.symptoms).lower()
        return any(kw in all_symptoms for kw in reproductive_keywords)


class RoutingDecision(BaseModel):
    """Which care pathway the patient should take.

    recommended_pathway must be a valid id from taxonomy.yaml.
    """

    recommended_pathway: str
    alternative_pathway: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    requires_urgent_evaluation: bool = False


class VerifiedField(BaseModel):
    """A provider attribute with provenance tracking.

    verified=False + value=None → "we don't know" → ranking scores it as 0.
    """

    value: Any = None
    verified: bool = False
    source: str | None = None
    fetched_at: datetime | None = None


class ProviderRecord(BaseModel):
    """Provider assembled from tool results. The LLM never builds this."""

    provider_id: str
    is_synthetic: bool = True
    name: VerifiedField = Field(default_factory=VerifiedField)
    specialty: VerifiedField = Field(default_factory=VerifiedField)
    subspecialty: VerifiedField = Field(default_factory=VerifiedField)
    credentials: VerifiedField = Field(default_factory=VerifiedField)
    clinic: VerifiedField = Field(default_factory=VerifiedField)
    city: VerifiedField = Field(default_factory=VerifiedField)
    address: VerifiedField = Field(default_factory=VerifiedField)
    phone: VerifiedField = Field(default_factory=VerifiedField)
    services: VerifiedField = Field(default_factory=VerifiedField)
    insurance_networks: VerifiedField = Field(default_factory=VerifiedField)
    availability: VerifiedField = Field(default_factory=VerifiedField)
    distance_km: VerifiedField = Field(default_factory=VerifiedField)
    latitude: float | None = None
    longitude: float | None = None
    rating: float | None = None
    reviews_count: int | None = None
    hours: dict | None = None


class RankedProvider(BaseModel):
    """Deterministic scoring result for one provider."""

    provider_id: str
    name: str
    city: str = ""
    total_score: float
    factors: dict[str, float]
    unverified_factors: list[str] = Field(default_factory=list)
    explanation: str = ""
    rating: float | None = None
