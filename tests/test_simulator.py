"""
Tests for the demo simulator's reminder line.

Only the deterministic (rule-based) reminder escalation is tested here — the
vision-verification line depends on a live LLM and image files, so it is not
part of the automated suite. Forcing client=None guarantees stable, offline
output for the three scheduler escalation levels.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from llm_engine import LLMEngine  # noqa: E402


def make_engine():
    """LLM engine forced onto the deterministic rule-based path."""
    engine = LLMEngine()
    engine.client = None
    return engine


def test_due_reminder_message():
    engine = make_engine()
    result = engine.generate_reminder({"escalation": "due"})
    assert "time to take" in result.message.lower()
    assert result.confidence == 1.0


def test_remind_reminder_message():
    engine = make_engine()
    result = engine.generate_reminder({"escalation": "remind"})
    assert "gentle reminder" in result.message.lower()


def test_alert_caregiver_message():
    engine = make_engine()
    result = engine.generate_reminder({"escalation": "alert_caregiver"})
    assert "caregiver" in result.message.lower()


def test_unknown_escalation_returns_empty():
    """An unrecognised escalation level yields no message."""
    engine = make_engine()
    result = engine.generate_reminder({"escalation": "something_else"})
    assert result.message == ""