"""
Unit tests for the LLM reasoning fallback logic.

These tests exercise the deterministic rule-based path (no API key required),
verifying that each medication scenario produces the correct action. This
keeps the core decision logic verifiable in CI without external dependencies.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from llm_engine import LLMEngine  # noqa: E402


def make_engine():
    engine = LLMEngine()
    engine.client = None   # Force the deterministic rule-based path
    return engine


def test_double_take_warns_and_notifies():
    engine = make_engine()
    decision = engine.reason({"open_count": 2, "is_empty": True})
    assert decision.action == "warn_double"
    assert decision.notify_caregiver is True


def test_taken_is_confirmed():
    engine = make_engine()
    decision = engine.reason({"open_count": 1, "is_empty": True})
    assert decision.action == "confirm_taken"


def test_long_overdue_alerts_caregiver():
    engine = make_engine()
    decision = engine.reason({"open_count": 0, "is_empty": False,
                              "minutes_overdue": 45})
    assert decision.action == "alert_caregiver"
    assert decision.notify_caregiver is True


def test_slightly_overdue_reminds():
    engine = make_engine()
    decision = engine.reason({"open_count": 0, "is_empty": False,
                              "minutes_overdue": 5})
    assert decision.action == "remind"


def test_nothing_to_do_is_idle():
    engine = make_engine()
    decision = engine.reason({"open_count": 0, "is_empty": False,
                              "minutes_overdue": 0})
    assert decision.action == "idle"
