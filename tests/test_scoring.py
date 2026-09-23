"""Scoring engine tests: exact arithmetic, unverified handling, determinism."""
import random

import pytest

from backend.app.domain.scoring import WEIGHTS, rank_providers, score_provider

FULL_FACTORS = {
    "specialty_match": 95,
    "expertise_match": 90,
    "insurance_match": 100,
    "location": 75,
    "availability": 80,
}


def test_weights_sum_to_one():
    assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9


def test_exact_arithmetic():
    # 0.35*95 + 0.25*90 + 0.15*100 + 0.15*75 + 0.10*80 = 90.0
    result = score_provider("p1", "Dr. A", FULL_FACTORS)
    assert result.total_score == 90.0
    assert result.unverified_factors == []


def test_unverified_factor_scores_zero_and_is_flagged():
    factors = dict(FULL_FACTORS, insurance_match=None)
    result = score_provider("p1", "Dr. A", factors)
    assert result.total_score == 75.0  # 90.0 minus the 15 insurance points
    assert result.unverified_factors == ["insurance_match"]
    assert result.factors["insurance_match"] == 0.0


def test_unknown_factor_keys_rejected():
    with pytest.raises(ValueError):
        score_provider("p1", "Dr. A", dict(FULL_FACTORS, bribery=100))


def test_out_of_range_factor_rejected():
    with pytest.raises(ValueError):
        score_provider("p1", "Dr. A", dict(FULL_FACTORS, location=140))


def test_ranking_is_deterministic_regardless_of_input_order():
    providers = [
        score_provider(f"p{i}", f"Dr. {i}", dict(FULL_FACTORS, location=i * 10))
        for i in range(1, 8)
    ]
    expected = rank_providers(providers)
    for seed in range(5):
        shuffled = providers[:]
        random.Random(seed).shuffle(shuffled)
        assert rank_providers(shuffled) == expected


def test_ties_break_by_provider_id():
    a = score_provider("p2", "Dr. B", FULL_FACTORS)
    b = score_provider("p1", "Dr. A", FULL_FACTORS)
    ranked = rank_providers([a, b])
    assert [p.provider_id for p in ranked] == ["p1", "p2"]
