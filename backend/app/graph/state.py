"""State : Shared state flowing between all agent nodes"""

from __future__ import annotations

from dataclasses import dataclass, field

from backend.app.schemas import (
    PatientProfile,
    ProviderRecord,
    RankedProvider,
    RoutingDecision,
)

@dataclass
class NavigatorState:
    """Mutable state passed through the graph."""

    # input
    conversation: str = ""
    session_id: str = ""

    # after intake
    profile: PatientProfile | None = None
    missing_fields: list[str] = field(default_factory=list)

    # after safety check
    red_flags: list[dict] = field(default_factory=list)
    crisis_detected: bool = False

    # after routing
    routing: RoutingDecision | None = None

    # after research
    providers: list[ProviderRecord] = field(default_factory=list)

    # after ranking
    ranked: list[RankedProvider] = field(default_factory=list)

    # control flow
    needs_more_info: bool = False
    error: str | None = None