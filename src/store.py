"""
store.py - local adherence event memory for SmartMedBox.

The box should not forget every decision after it speaks or sends an alert.
This module records structured medication events in a small SQLite database so
a caregiver dashboard or report can read the adherence history later.

Privacy choice: store the derived event and spoken message, not the raw camera
image. The image is only needed transiently for intake verification.
"""

import os
import sqlite3
from contextlib import closing
from datetime import date, datetime
from typing import Dict, List, Optional

try:
    from .config import Config
except ImportError:
    from config import Config


DEFAULT_DB_PATH = Config.DB_PATH


class AdherenceStore:
    """Small SQLite wrapper for medication adherence events."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._setup()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _setup(self) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts              TEXT    NOT NULL,
                    compartment     INTEGER,
                    label           TEXT,
                    scheduled_hour  INTEGER,
                    action          TEXT,
                    message         TEXT,
                    notified        INTEGER DEFAULT 0,
                    minutes_overdue INTEGER DEFAULT 0
                )
                """
            )
            conn.commit()

    def log_event(
        self,
        compartment: int,
        action: str,
        message: str = "",
        label: str = "",
        scheduled_hour: Optional[int] = None,
        notified: bool = False,
        minutes_overdue: int = 0,
    ) -> None:
        """Record one Sense -> Reason -> Act cycle."""
        with closing(self._connect()) as conn:
            conn.execute(
                """
                INSERT INTO events
                    (ts, compartment, label, scheduled_hour,
                     action, message, notified, minutes_overdue)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now().isoformat(timespec="seconds"),
                    compartment,
                    label,
                    scheduled_hour,
                    action,
                    message,
                    1 if notified else 0,
                    minutes_overdue,
                ),
            )
            conn.commit()

    def recent_events(self, limit: int = 50) -> List[Dict]:
        """Return the most recent events, newest first."""
        with closing(self._connect()) as conn:
            rows = conn.execute(
                "SELECT * FROM events ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def events_today(self) -> List[Dict]:
        """Return today's events, oldest first."""
        today = date.today().isoformat()
        with closing(self._connect()) as conn:
            rows = conn.execute(
                "SELECT * FROM events WHERE ts LIKE ? ORDER BY id ASC",
                (f"{today}%",),
            ).fetchall()
        return [dict(row) for row in rows]

    def summary_today(self) -> Dict[str, int]:
        """Count today's events by the categories caregivers care about."""
        rows = self.events_today()
        summary = {
            "taken": 0,
            "late": 0,
            "missed": 0,
            "double": 0,
            "alerts": 0,
            "total": len(rows),
        }

        for row in rows:
            action = (row["action"] or "").lower()
            if action in ("taken", "confirm_taken"):
                summary["taken"] += 1
            elif action in ("late", "remind"):
                summary["late"] += 1
            elif action in ("missed", "alert_caregiver"):
                summary["missed"] += 1
            elif action in ("double", "warn_double"):
                summary["double"] += 1

            if row["notified"]:
                summary["alerts"] += 1

        return summary


if __name__ == "__main__":
    store = AdherenceStore()

    store.log_event(
        0,
        action="confirm_taken",
        label="Morning",
        scheduled_hour=8,
        message="Great, your morning dose is confirmed.",
    )
    store.log_event(
        1,
        action="remind",
        label="Noon",
        scheduled_hour=12,
        minutes_overdue=10,
        message="Gentle reminder: it is time for your noon pill.",
    )
    store.log_event(
        1,
        action="alert_caregiver",
        label="Noon",
        scheduled_hour=12,
        notified=True,
        minutes_overdue=35,
        message="Noon dose still not taken; caregiver notified.",
    )

    print("Today's summary:")
    for key, value in store.summary_today().items():
        print(f"  {key:8}: {value}")

    print("\nMost recent events:")
    for event in store.recent_events(limit=5):
        alerted = " (caregiver alerted)" if event["notified"] else ""
        print(
            f"  [{event['ts']}] {event['label']:8} "
            f"{event['action']}{alerted}"
        )

    print(f"\nDatabase file: {os.path.abspath(store.db_path)}")
