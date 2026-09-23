import pytest

from backend.app.safety.red_flags import check_red_flags
from backend.app.schemas import PatientProfile

DANGER_CASES = [
    ("pregnancy_bleeding", "I am pregnant and I noticed bleeding this morning", "emergency"),
    ("ectopic_pattern", "I missed my period and now have severe pain on one side", "emergency"),
    ("heavy_hemorrhage", "I am soaking through a pad every hour", "emergency"),
    ("fainting_with_bleeding", "I fainted today and my bleeding is very heavy", "emergency"),
    ("fever_pelvic_pain", "I have a fever and bad pain in my lower abdomen", "emergency"),
    ("preeclampsia_pattern", "I'm pregnant and having a severe headache with blurry vision", "emergency"),
    ("breast_lump_skin_changes", "There is a lump in my breast and the skin looks dimpled", "emergency"),
    ("self_harm", "Sometimes I feel like I want to end my life", "crisis"),
    ("harm_to_baby", "I keep having thoughts of harming my baby", "crisis"),
]


@pytest.mark.parametrize("rule_id,text,level", DANGER_CASES, ids=[c[0] for c in DANGER_CASES])
def test_danger_text_triggers(rule_id, text, level):
    result = check_red_flags(text)
    assert result.triggered, f"MUST trigger: {text!r}"
    assert rule_id in result.matched_rule_ids
    assert result.level == level
    assert result.message  # patient always gets guidance text


BENIGN_CASES = [
    "I've had pelvic pain for six months, worse during my periods",
    "My periods are irregular and I have acne",
    "I leak a little urine when I sneeze",
    "I get hot flashes at night and I'm 51",
    "We've been trying to conceive for a year",
    "I have breast pain before my periods",  # breast, but no lump + skin change
]


@pytest.mark.parametrize("text", BENIGN_CASES)
def test_benign_text_does_not_trigger(text):
    result = check_red_flags(text)
    assert not result.triggered, f"False alarm on: {text!r} -> {result.matched_rule_ids}"


def test_profile_rule_catches_what_text_missed():
    # Raw text in another language could evade text patterns; the structured
    # profile still catches it.
    profile = PatientProfile(pregnancy_status="pregnant", symptoms=["bleeding", "cramps"])
    result = check_red_flags("(text the rules cannot parse)", profile)
    assert result.triggered
    assert "pregnant_severe_symptoms" in result.matched_rule_ids


def test_crisis_outranks_emergency():
    text = "I am pregnant and bleeding and I want to end my life"
    result = check_red_flags(text)
    assert result.level == "crisis"
    assert "self_harm" in result.matched_rule_ids
    assert "pregnancy_bleeding" in result.matched_rule_ids  # still recorded


def test_postpartum_mood_profile_rule():
    profile = PatientProfile(pregnancy_status="postpartum", symptoms=["feeling hopeless"])
    result = check_red_flags("", profile)
    assert result.triggered
    assert result.level == "crisis"
