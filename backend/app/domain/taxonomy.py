from __future__ import annotations

from pathlib import Path

import yaml

_TAXONOMY_PATH = Path(__file__).parent / "taxonomy.yaml"


def _load() -> dict[str, dict]:
    with open(_TAXONOMY_PATH, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return {p["id"]: p for p in raw["pathways"]}


PATHWAYS: dict[str, dict] = _load()
PATHWAY_IDS: frozenset[str] = frozenset(PATHWAYS)


def is_valid_pathway(pathway_id: str) -> bool:
    return pathway_id in PATHWAY_IDS


def get_pathway(pathway_id: str) -> dict:
    if not is_valid_pathway(pathway_id):
        raise KeyError(f"Unknown care pathway: {pathway_id!r}")
    return PATHWAYS[pathway_id]
