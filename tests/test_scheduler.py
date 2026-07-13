"""Unit tests for the fixed reminder scheduler."""

import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from scheduler import ReminderScheduler  # noqa: E402
from sensors import SensorArray  # noqa: E402


def make_sensors():
    sensors = SensorArray(num_compartments=1)
    sensors.compartments[0].scheduled_hour = 8
    return sensors


def test_due_event_generated_after_scheduled_time():
    sensors = make_sensors()
    scheduler = ReminderScheduler(sensors, reminder_interval_min=15)

    events = scheduler.due_events(now=datetime(2026, 6, 30, 8, 5))

    assert len(events) == 1
    assert events[0].compartment == 0
    assert events[0].minutes_overdue == 5
    assert events[0].escalation == "due"


def test_due_event_is_throttled_until_interval_passes():

    sensors = make_sensors()

    scheduler = ReminderScheduler(
        sensors,
        reminder_interval_min=15,
    )

    first = datetime(2026, 6, 30, 8, 5)

    events = scheduler.due_events(now=first)

    assert events[0].escalation == "due"

    # No reminder yet
    assert scheduler.due_events(
        now=first + timedelta(minutes=10)
    ) == []

    # Reminder after interval
    events = scheduler.due_events(
        now=first + timedelta(minutes=15)
    )

    assert len(events) == 1
    assert events[0].escalation == "remind"

def test_multiple_reminders_are_generated_every_interval():
    sensors = make_sensors()
    scheduler = ReminderScheduler(
        sensors,
        reminder_interval_min=5,
    )
    scheduler.due_events(

        now=datetime(2026, 6, 30, 8, 0)
    )
    events = scheduler.due_events(

        now=datetime(2026, 6, 30, 8, 5)
    )
    assert events[0].escalation == "remind"
    events = scheduler.due_events(
        now=datetime(2026, 6, 30, 8, 10)
    )
    assert events[0].escalation == "remind"

def test_alert_generated_once_after_threshold():
    sensors = make_sensors()
    scheduler = ReminderScheduler(sensors, alert_after_min=30)

    first_alert = scheduler.due_events(now=datetime(2026, 6, 30, 8, 35))
    second_alert = scheduler.due_events(now=datetime(2026, 6, 30, 8, 36))

    assert first_alert[0].escalation == "alert_caregiver"
    assert second_alert == []


def test_taken_dose_is_not_overdue():
    sensors = make_sensors()
    sensors.compartments[0].taken_today = True
    scheduler = ReminderScheduler(sensors)

    assert scheduler.due_events(now=datetime(2026, 6, 30, 9, 0)) == []
