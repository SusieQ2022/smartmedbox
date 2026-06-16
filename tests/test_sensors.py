"""Unit tests for the sensor array (mock mode)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

os.environ["HARDWARE_MODE"] = "mock"
from sensors import SensorArray  # noqa: E402


def test_compartments_initialised():
    arr = SensorArray(num_compartments=4)
    assert len(arr.compartments) == 4


def test_pill_removal_makes_compartment_empty():
    arr = SensorArray(num_compartments=2)
    arr.simulate_pill_removed(0)
    arr.poll()
    assert arr.compartments[0].is_empty is True
    assert arr.compartments[1].is_empty is False


def test_refill_resets_compartment():
    arr = SensorArray(num_compartments=1)
    arr.simulate_pill_removed(0)
    arr.simulate_refill(0)
    arr.poll()
    assert arr.compartments[0].is_empty is False
    assert arr.compartments[0].open_count == 0

def test_compartments_have_schedule():
    """Each compartment should be assigned a label and scheduled hour."""
    arr = SensorArray(num_compartments=4)
    assert arr.compartments[0].label == "Morning"
    assert arr.compartments[0].scheduled_hour == 8
    assert arr.compartments[3].label == "Night"
    assert arr.compartments[3].scheduled_hour == 22


def test_minutes_overdue_zero_when_taken():
    """A dose already taken today is never overdue."""
    arr = SensorArray(num_compartments=1)
    arr.compartments[0].taken_today = True
    assert arr.minutes_overdue(0) == 0
