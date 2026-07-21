"""Integration tests for the SmartMedBox controller wiring."""

import os
import sys
from datetime import datetime
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from config import Config  # noqa: E402
import main as main_module  # noqa: E402
from main import SmartMedBox  # noqa: E402
from store import AdherenceStore  # noqa: E402


def make_box(monkeypatch, tmp_path, visually_confirmed):
    db_path = str(tmp_path / "events.db")
    Config.DB_PATH = db_path
    Config.SMARTMEDBOX_DB = Config.DB_PATH
    Config.HARDWARE_MODE = "mock"
    Config.KICONNECT_API_KEY = ""
    Config.OPENAI_API_KEY = ""

    monkeypatch.setattr(
        main_module,
        "AdherenceStore",
        lambda: AdherenceStore(db_path),
    )
    monkeypatch.setattr(main_module.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(
        main_module.Camera,
        "encode_base64",
        staticmethod(lambda _path: "encoded-image"),
    )

    box = SmartMedBox()
    box.camera.capture = lambda: "capture.jpg"
    box.voice.speak = lambda _message: None
    box.llm.verify_intake = lambda **_kwargs: SimpleNamespace(
        visually_confirmed=visually_confirmed,
        message=("Dose confirmed." if visually_confirmed else "Please try again."),
        confidence=1.0,
        explanation="Deterministic integration test.",
    )
    return box


def test_confirmed_dose_is_logged_and_removed_from_schedule(monkeypatch, tmp_path):
    box = make_box(monkeypatch, tmp_path, visually_confirmed=True)

    box.process_compartment_open(0)

    assert box.sensors.compartments[0].taken_today is True
    assert box.store.events_today()[0]["action"] == "confirmed"

    today_at_nine = datetime.now().replace(
        hour=9,
        minute=0,
        second=0,
        microsecond=0,
    )
    assert box.scheduler.due_events(now=today_at_nine) == []


def test_failed_verification_stays_visible_and_dose_remains_due(monkeypatch, tmp_path):
    box = make_box(monkeypatch, tmp_path, visually_confirmed=False)

    box.process_compartment_open(0)

    assert box.sensors.compartments[0].taken_today is False
    assert box.store.events_today()[0]["action"] == "verification_failed"

    today_at_nine = datetime.now().replace(
        hour=9,
        minute=0,
        second=0,
        microsecond=0,
    )
    events = box.scheduler.due_events(now=today_at_nine)
    assert len(events) == 1
    assert events[0].compartment == 0
