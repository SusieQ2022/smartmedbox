"""
scheduler.py - fixed medication reminder and escalation engine.

This module decides when a scheduled dose needs attention. It also provides a mock medication schedule for direct testing purposes.
"""


from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, List, Optional, Set, Tuple

try:
    from .config import Config
    from .sensors import SensorArray
except ImportError:
    from config import Config
    from sensors import SensorArray


@dataclass
class MedicationSchedule:
    """One scheduled medication dose."""

    compartment: int
    label: str
    scheduled_hour: int


@dataclass
class ScheduleEvent:
    """A medication event that should be processed."""

    compartment: int
    label: str
    scheduled_hour: int
    minutes_overdue: int
    escalation: str


MEDICATION_SCHEDULE = [
    MedicationSchedule(
        compartment=0,
        label="Vitamin D",
        scheduled_hour=8,
    ),
    MedicationSchedule(
        compartment=1,
        label="Vitamin D",
        scheduled_hour=14,
    ),
]


class ReminderScheduler:
    """Generate reminder and escalation events from a fixed medication schedule."""

    def __init__(
        self,
        sensors: SensorArray,
        reminder_interval_min: int = Config.REMINDER_INTERVAL_MIN,
        alert_after_min: int = 30,
        schedule: list[MedicationSchedule] | None = None,
    ):
        self.sensors = sensors
        self.schedule = schedule or MEDICATION_SCHEDULE

        self.reminder_interval_min = reminder_interval_min
        self.alert_after_min = alert_after_min

        # key = (date, compartment, scheduled_hour)
        self._last_reminded: Dict[Tuple[date, int, int], datetime] = {}
        self._alerted: Set[Tuple[date, int, int]] = set()
        self._completed: Set[Tuple[date, int, int]] = set()

    def due_events(self, now: Optional[datetime] = None) -> List[ScheduleEvent]:
        """Return medication doses requiring reminders."""

        now = now or datetime.now()
        today = now.date()

        events: List[ScheduleEvent] = []

        for medication in self.schedule:

            scheduled = now.replace(
                hour=medication.scheduled_hour,
                minute=0,
                second=0,
                microsecond=0,
            )

            minutes_overdue = max(
                0,
                int((now - scheduled).total_seconds() / 60),
            )

            if minutes_overdue <= 0:
                continue

            key = (
                today,
                medication.compartment,
                medication.scheduled_hour,
            )

            if key in self._completed:
                continue

            escalation = self._escalation_for(
                key,
                minutes_overdue,
                now,
            )

            if escalation is None:
                continue

            events.append(
                ScheduleEvent(
                    compartment=medication.compartment,
                    label=medication.label,
                    scheduled_hour=medication.scheduled_hour,
                    minutes_overdue=minutes_overdue,
                    escalation=escalation,
                )
            )

            self._last_reminded[key] = now

            if escalation == "alert_caregiver":
                self._alerted.add(key)

        return events

    def _escalation_for(
        self,
        key: Tuple[date, int, int],
        minutes_overdue: int,
        now: datetime,
    ) -> Optional[str]:
        """Determine reminder escalation."""

        if minutes_overdue >= self.alert_after_min and key not in self._alerted:
            return "alert_caregiver"

        last = self._last_reminded.get(key)

        if last is None:
            return "due"

        elapsed = (now - last).total_seconds() / 60

        if elapsed >= self.reminder_interval_min:
            return "remind"

        return None

    def medication_for(
        self,
        compartment: int,
        scheduled_hour: int | None = None,
    ) -> MedicationSchedule:
        """
        Return the medication assigned to a compartment.

        If multiple doses share a compartment, scheduled_hour disambiguates.
        """

        if scheduled_hour is None:
            return next(
                med
                for med in self.schedule
                if med.compartment == compartment
            )

        return next(
            med
            for med in self.schedule
            if med.compartment == compartment
            and med.scheduled_hour == scheduled_hour
        )

    def mark_completed(
        self,
        compartment: int,
        scheduled_hour: int,
        when: Optional[datetime] = None,
    ) -> None:
        """Mark a scheduled dose as completed."""

        when = when or datetime.now()

        key = (
            when.date(),
            compartment,
            scheduled_hour,
        )

        self._completed.add(key)
        self._last_reminded.pop(key, None)
        self._alerted.discard(key)