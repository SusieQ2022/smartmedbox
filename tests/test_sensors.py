"""Unit tests for the sensor array (mock mode)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

os.environ["HARDWARE_MODE"] = "mock"
from sensors import SensorArray  # noqa: E402


def test_compartments_initialised():
    arr = SensorArray(num_compartments=4)
    assert len(arr.compartments) == 4


def test_simulate_open_increments_count():
    arr = SensorArray(num_compartments=1)
    arr.simulate_open(0)
    assert arr.compartments[0].open_count == 1


def test_poll_reports_newly_opened_compartment():
    arr = SensorArray(num_compartments=1)
    arr.simulate_open(0)
    assert arr.poll() == [0]
    # A second poll with no new opening returns nothing.
    assert arr.poll() == []


def test_refill_resets_open_count():
    arr = SensorArray(num_compartments=1)
    arr.simulate_open(0)
    arr.simulate_refill(0)
    assert arr.compartments[0].open_count == 0