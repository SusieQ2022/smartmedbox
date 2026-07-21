"""
simulator.py — Automated end-to-end demo for SmartMedBox.

Plays through a realistic "day in the life" medication scenario, triggering
each core behaviour of the system in sequence so the full Sense → Reason → Act
loop can be demonstrated hands-free. Ideal for the live demo: no need to type
commands one by one.

Run with:

    python src/simulator.py
"""

from __future__ import annotations

import time

from main import SmartMedBox
from scheduler import ScheduleEvent


# Seconds to pause between scenes so the audience can read each result.
PAUSE = 3.0


def _scene_header(title: str) -> None:
    """Print a visible scene separator."""
    print("\n" + "=" * 60)
    print(f"  SCENE: {title}")
    print("=" * 60)


def run_demo(deterministic: bool = True) -> None:
    """
    Run the full automated demo scenario.

    When `deterministic` is True, the demo forces the rule-based reasoning
    path so that safety-critical behaviours (caregiver alert) are shown
    reliably and predictably, independent of live LLM variability.
    Set to False to demo the live LLM instead.
    """
    box = SmartMedBox()

    if deterministic:
        # Force the deterministic rule-based path for a predictable demo.
        box.llm.client = None

    print("\n" + "#" * 60)
    print("#  SmartMedBox — Automated Daily Demo")
    print("#  A day in the life of an elderly patient")
    print("#" * 60)

    # ── Scene 1: Morning dose due — friendly first reminder ──
    _scene_header("08:00 — Morning dose due, friendly reminder")
    box.process_scheduler_event(
        ScheduleEvent(
            compartment=0,
            label="Vitamin D",
            scheduled_hour=8,
            minutes_overdue=0,
            escalation="due",
        )
    )
    time.sleep(PAUSE)

    # ── Scene 2: Morning dose still not taken — repeated reminder ──
    _scene_header("08:10 — Morning dose overdue, repeated reminder")
    box.process_scheduler_event(
        ScheduleEvent(
            compartment=0,
            label="Vitamin D",
            scheduled_hour=8,
            minutes_overdue=10,
            escalation="remind",
        )
    )
    time.sleep(PAUSE)

    # ── Scene 3: Morning dose well overdue — caregiver alerted ──
    _scene_header("08:35 — Still not taken, caregiver alerted")
    box.process_scheduler_event(
        ScheduleEvent(
            compartment=0,
            label="Vitamin D",
            scheduled_hour=8,
            minutes_overdue=35,
            escalation="alert_caregiver",
        )
    )
    time.sleep(PAUSE)

    # ── Scene 4: Patient opens the box — vision verification ──
    _scene_header("08:40 — Patient opens the box, verifying intake")
    box.sensors.simulate_open(0)
    box.process_compartment_open(0)
    time.sleep(PAUSE)

    print("\n" + "#" * 60)
    print("#  Demo complete — all core behaviours shown.")
    print("#" * 60 + "\n")


if __name__ == "__main__":
    run_demo()