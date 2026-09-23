"""Deterministic provider scoring and ranking."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Mapping

import yaml

from backend.app.schemas import RankedProvider

_WEIGHTS_PATH = Path(__file__).parent / "scoring_weights.yaml"


def _load_weights() -> dict[str, float]:
    with open(_WEIGHTS_PATH, encoding="utf-8") as f:
        weights = yaml.safe_load(f)["weights"]
    total = sum(weights.values())
    if not math.isclose(total, 1.0, abs_tol=1e-9):
        raise ValueError(f"Scoring weights must sum to 1.0, got {total}")
    return weights


WEIGHTS: dict[str, float] = _load_weights()


def score_provider(
    provider_id: str,
    name: str,
    factors: Mapping[str, float | None],
    weights: Mapping[str, float] | None = None,
    city: str = "",
) -> RankedProvider:
    weights = WEIGHTS if weights is None else weights
    if set(factors) != set(weights):
        raise ValueError(f"Factor keys {sorted(factors)} must match weight keys {sorted(weights)}")

    resolved: dict[str, float] = {}
    unverified: list[str] = []
    for key, val in factors.items():
        if val is None:
            resolved[key] = 0.0
            unverified.append(key)
        elif 0.0 <= val <= 100.0:
            resolved[key] = float(val)
        else:
            raise ValueError(f"Factor {key}={val} outside 0-100")

    total = round(sum(weights[f] * v for f, v in resolved.items()), 1)
    return RankedProvider(
        provider_id=provider_id,
        name=name,
        city=city,
        total_score=total,
        factors=resolved,
        unverified_factors=sorted(unverified),
    )


def rank_providers(scored: list[RankedProvider]) -> list[RankedProvider]:
    """Highest score first; ties broken by provider_id."""
    return sorted(scored, key=lambda p: (-p.total_score, p.provider_id))
