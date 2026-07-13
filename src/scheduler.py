"""
scheduler.py - fixed medication reminder and escalation engine.

This module decides when a scheduled dose needs attention. It does not change
the medication schedule and it does not learn later times from missed doses.
That keeps the prototype explainable and safer: fixed schedule first, then a
clear escalation after a configurable delay.
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
class ScheduleEvent:
    """A dose that should be processed by the SmartMedBox pipeline."""

    compartment: int
    label: str
    minutes_overdue: int
    escalation: str  # due | remind | alert caregiver


class ReminderScheduler:
    """Generate due/overdue medication events from fixed compartment times."""

    def __init__(
        self,
        sensors: SensorArray,
        reminder_interval_min: int = Config.REMINDER_INTERVAL_MIN,
        alert_after_min: int = 30,
    ):
        self.sensors = sensors
        self.reminder_interval_min = reminder_interval_min
        self.alert_after_min = alert_after_min
        self._last_reminded: Dict[Tuple[date, int], datetime] = {}
        self._alerted: Set[Tuple[date, int]] = set()
        self._completed: Set[Tuple[date, int]] = set()

    def due_events(self, now: Optional[datetime] = None) -> List[ScheduleEvent]:
        """
        Return compartments that should trigger a reminder or escalation.

        A dose is processed when it is overdue and either:
        - no reminder has been sent today,
        - the reminder interval elapsed, or
        - it crossed the caregiver-alert threshold for the first time today.
        """
        now = now or datetime.now()
        today = now.date()
        events: List[ScheduleEvent] = []

        for index, state in self.sensors.compartments.items():
            minutes_overdue = self.sensors.minutes_overdue(index, now=now)
            if minutes_overdue <= 0:
                continue

            key = (today, index)
            if key in self._completed:
                continue
            escalation = self._escalation_for(key, minutes_overdue, now)
            if escalation is None:
                continue
            
            events.append(
                ScheduleEvent(
                    compartment=index,
                    label=state.label,
                    minutes_overdue=minutes_overdue,
                    escalation=escalation,
                )
            )

            if escalation == "alert_caregiver":
                self._alerted.add(key)
            self._last_reminded[key] = now

        return events

    def _escalation_for(
    self,
    key: Tuple[date, int],
    minutes_overdue: int,
    now: datetime,
) -> Optional[str]:
        """
        Determine the escalation level for a scheduled dose.

        Escalation levels:

        due
            Initial reminder when the medication first becomes due.

        remind
            Repeated reminder every reminder_interval_min minutes.

        alert_caregiver
            Medication has been overdue for alert_after_min minutes.
            Trigger caregiver notification once.
        """
        # Highest escalation: caregiver alert
        if (
            minutes_overdue >= self.alert_after_min
            and key not in self._alerted
        ):
            return "alert_caregiver"

        last_reminded = self._last_reminded.get(key)

        # First reminder
        if last_reminded is None:
            return "due"

        # Subsequent reminders
        elapsed = (now - last_reminded).total_seconds() / 60

        if elapsed >= self.reminder_interval_min:
            return "remind"

        return None
    
    def mark_completed(
    self,
    compartment: int,
    when: Optional[datetime] = None,
) -> None:
        """
        Mark today's scheduled dose as completed.

        No more reminders will be generated for this
        compartment until the next scheduled day.
        """

        when = when or datetime.now()
        key = (when.date(), compartment)
        self._completed.add(key)
        self._last_reminded.pop(key, None)
        self._alerted.discard(key)
