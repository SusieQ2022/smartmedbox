"""Unit tests for the fixed reminder scheduler."""

import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from scheduler import ReminderScheduler  # noqa: E402
from sensors import SensorArray  # noqa: E402


def make_sensors():
    return SensorArray(num_compartments=1)


def test_due_event_generated_after_scheduled_time():
    sensors = make_sensors()
    scheduler = ReminderScheduler(sensors, reminder_interval_min=15)

    events = scheduler.due_events(now=datetime(2026, 6, 30, 8, 5))

    assert len(events) >= 1
    assert events[0].compartment == 0
    assert events[0].minutes_overdue == 5
    assert events[0].escalation == "due"


def test_due_event_is_throttled_until_interval_passes():
    sensors = make_sensors()
    scheduler = ReminderScheduler(sensors, reminder_interval_min=15)

    first = datetime(2026, 6, 30, 8, 5)
    events = scheduler.due_events(now=first)
    assert events[0].escalation == "due"

    # No reminder yet, before the interval elapses.
    assert scheduler.due_events(now=first + timedelta(minutes=10)) == []

    # Reminder after the interval.
    events = scheduler.due_events(now=first + timedelta(minutes=15))
    assert len(events) == 1
    assert events[0].escalation == "remind"


def test_multiple_reminders_are_generated_every_interval():
    sensors = make_sensors()
    scheduler = ReminderScheduler(sensors, reminder_interval_min=5)

    # First reminder (due) shortly after the scheduled time.
    first = datetime(2026, 6, 30, 8, 2)
    events = scheduler.due_events(now=first)
    assert events[0].escalation == "due"

    # After one interval → remind.
    events = scheduler.due_events(now=first + timedelta(minutes=5))
    assert events[0].escalation == "remind"

    # After another interval → remind again.
    events = scheduler.due_events(now=first + timedelta(minutes=10))
    assert events[0].escalation == "remind"


def test_alert_generated_once_after_threshold():
    sensors = make_sensors()
    scheduler = ReminderScheduler(sensors, alert_after_min=30)

    first_alert = scheduler.due_events(now=datetime(2026, 6, 30, 8, 35))
    second_alert = scheduler.due_events(now=datetime(2026, 6, 30, 8, 36))

    assert first_alert[0].escalation == "alert_caregiver"
    assert second_alert == []


def test_completed_dose_generates_no_events():
    sensors = make_sensors()
    scheduler = ReminderScheduler(sensors)

    # A dose marked completed produces no further reminders that day.
    scheduler.mark_completed(0, 8, when=datetime(2026, 6, 30, 8, 30))
    assert scheduler.due_events(now=datetime(2026, 6, 30, 9, 0)) == []