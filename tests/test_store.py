"""Unit tests for the SQLite adherence store."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from store import (  # noqa: E402
    ACTION_ALERT_CAREGIVER,
    ACTION_CONFIRMED,
    ACTION_REMIND,
    ACTION_VERIFICATION_FAILED,
    AdherenceStore,
)


def test_log_event_and_recent_events(tmp_path):
    store = AdherenceStore(str(tmp_path / "events.db"))

    store.log_event(
        compartment=0,
        action=ACTION_CONFIRMED,
        message="Dose confirmed.",
        label="Morning",
        scheduled_hour=8,
    )

    events = store.recent_events()

    assert len(events) == 1
    assert events[0]["compartment"] == 0
    assert events[0]["action"] == ACTION_CONFIRMED
    assert events[0]["label"] == "Morning"
    assert events[0]["notified"] == 0


def test_summary_today_counts_outcomes(tmp_path):
    store = AdherenceStore(str(tmp_path / "events.db"))

    store.log_event(0, action=ACTION_CONFIRMED)
    store.log_event(1, action=ACTION_REMIND, minutes_overdue=10)
    store.log_event(2, action=ACTION_ALERT_CAREGIVER, notified=True)
    store.log_event(3, action=ACTION_VERIFICATION_FAILED)

    assert store.summary_today() == {
        "taken": 1,
        "late": 1,
        "missed": 1,
        "unverified": 1,
        "alerts": 1,
        "total": 4,
    }
