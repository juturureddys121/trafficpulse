import json

import pytest

from app import classify_input, build_action_plan


def test_classify_input_detects_medical_case():
    result = classify_input(
        "My grandmother is short of breath and has asthma. She missed her inhaler during a heat advisory."
    )

    assert result["intent"] == "Medical triage"
    assert result["risk_level"] == "High"
    assert result["risk_score"] >= 85


def test_build_action_plan_returns_three_actions():
    analysis = {
        "intent": "Medical triage",
        "risk_level": "High",
        "risk_score": 92,
        "sources": ["Emergency guidance protocol", "Medication history review"],
    }

    plan = build_action_plan(analysis)

    assert isinstance(plan, list)
    assert len(plan) == 3
    assert plan[0]["title"]
    assert plan[0]["tag"]
