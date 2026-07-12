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


# Seconds to pause between scenes so the audience can read each result.
PAUSE = 2.0


def _print_decision(scene: str, decision) -> None:
    """Pretty-print the outcome of one scenario."""
    print("\n" + "=" * 60)
    print(f" SCENE: {scene}")
    print("=" * 60)
    print(f"Action     : {decision.action}")
    print(f"Message    : {decision.message}")
    print(f"Confidence : {decision.confidence:.2f}")
    print(f"Caregiver  : {decision.notify_caregiver}")
    print("=" * 60)


def run_demo(deterministic: bool = True) -> None:
    """
    Run the full automated demo scenario.

    When `deterministic` is True, the demo forces the rule-based reasoning
    path so that safety-critical behaviours (double-take warning, caregiver
    alert) are shown reliably and predictably, independent of live LLM
    variability. Set to False to demo the live LLM instead.
    """
    box = SmartMedBox()

    if deterministic:
        # Force the deterministic rule-based path for a predictable demo.
        box.llm.client = None

    print("\n" + "#" * 60)
    print("#  SmartMedBox — Automated Daily Demo")
    print("#  A day in the life of an elderly patient")
    print("#" * 60)

    # ── Scene 1: Morning dose taken on time ──
    # Patient opens compartment 0 and takes the morning pill.
    box.sensors.simulate_pill_removed(0)
    decision = box.process_medication_event(0)
    _print_decision("08:00 — Morning dose taken on time", decision)
    time.sleep(PAUSE)

    # ── Scene 2: Noon dose missed — gentle reminder ──
    # Compartment 1 not opened yet, and it is slightly overdue.
    decision = box.process_medication_event(1, minutes_overdue=10)
    _print_decision("12:10 — Noon dose overdue, gentle reminder", decision)
    time.sleep(PAUSE)

    # ── Scene 3: Noon dose still missed — caregiver alerted ──
    # Same compartment, now well past the threshold.
    decision = box.process_medication_event(1, minutes_overdue=35)
    _print_decision("12:35 — Still not taken, caregiver alerted", decision)
    time.sleep(PAUSE)

    # ── Scene 4: Evening dose — accidental double-take ──
    # Patient opens compartment 2 twice, risking a double dose.
    box.sensors.simulate_open(2)
    box.sensors.simulate_open(2)
    decision = box.process_medication_event(2)
    _print_decision("18:00 — Evening dose opened twice, double-take warning",
                    decision)
    time.sleep(PAUSE)

    print("\n" + "#" * 60)
    print("#  Demo complete — all core behaviours shown.")
    print("#" * 60 + "\n")


if __name__ == "__main__":
    run_demo()