"""
Tests for the automated demo simulator.

These verify that each scripted scene produces the expected safety-critical
action. The simulator is run in deterministic (rule-based) mode so the results
are stable and independent of the live LLM.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from main import SmartMedBox  # noqa: E402


def make_box():
    """Create a SmartMedBox forced onto the deterministic rule-based path."""
    box = SmartMedBox()
    box.llm.client = None
    return box


def test_morning_dose_confirmed():
    """Taking the morning dose should be confirmed."""
    box = make_box()
    box.sensors.simulate_pill_removed(0)
    decision = box.process_medication_event(0)
    assert decision.action == "confirm_taken"


def test_noon_dose_overdue_reminds():
    """A slightly overdue dose should trigger a gentle reminder."""
    box = make_box()
    decision = box.process_medication_event(1, minutes_overdue=10)
    assert decision.action == "remind"


def test_long_overdue_alerts_caregiver():
    """A dose overdue past the threshold should alert the caregiver."""
    box = make_box()
    decision = box.process_medication_event(1, minutes_overdue=35)
    assert decision.action == "alert_caregiver"
    assert decision.notify_caregiver is True


def test_double_take_warns():
    """Opening a compartment twice should trigger a double-take warning."""
    box = make_box()
    box.sensors.simulate_open(2)
    box.sensors.simulate_open(2)
    decision = box.process_medication_event(2)
    assert decision.action == "warn_double"
    assert decision.notify_caregiver is True