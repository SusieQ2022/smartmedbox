"""Integration tests for the SmartMedBox controller wiring."""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from config import Config  # noqa: E402
from main import SmartMedBox  # noqa: E402


def test_taken_dose_is_logged_and_removed_from_schedule(tmp_path):
    Config.DB_PATH = str(tmp_path / "events.db")
    Config.SMARTMEDBOX_DB = Config.DB_PATH
    Config.HARDWARE_MODE = "mock"
    Config.KICONNECT_API_KEY = ""
    Config.OPENAI_API_KEY = ""

    box = SmartMedBox()
    box.sensors.simulate_pill_removed(0)

    decision = box.process_medication_event(0)

    assert decision.action == "confirm_taken"
    assert box.sensors.compartments[0].taken_today is True
    assert box.store.events_today()[0]["action"] == "confirm_taken"
    assert box.scheduler.due_events(now=datetime(2026, 6, 30, 9, 0)) == []
