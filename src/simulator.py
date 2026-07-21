"""
simulator.py — Automated demo for SmartMedBox (new scheduler + vision architecture).

Plays through a scripted medication scenario hands-free, for the live demo:

  1. Dose becomes due          → friendly reminder
  2. Still not taken           → repeated reminder
  3. Overdue > 30 min          → caregiver alert
  4. Intake verification       → confirmed / not confirmed (vision)

The reminder line runs in deterministic rule-based mode so the escalation
messages are stable and predictable. The vision line tries the live LLM and
falls back to a simulated result if the model is unavailable, so the demo
never breaks.

Run:
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
try:
    from .llm_engine import LLMEngine, ReasoningResult
    from .store import (
        ACTION_ALERT_CAREGIVER,
        ACTION_CONFIRMED,
        ACTION_VERIFICATION_FAILED,
        AdherenceStore,
    )
except ImportError:
    from llm_engine import LLMEngine, ReasoningResult
    from store import (
        ACTION_ALERT_CAREGIVER,
        ACTION_CONFIRMED,
        ACTION_VERIFICATION_FAILED,
        AdherenceStore,
    )


PAUSE = 2.0


def _print(title: str, context: dict, result) -> None:
    print("\n" + "=" * 62)
    print(f" SCENE: {title}")
    print("=" * 62)
    print(" Context:")
    for k, v in context.items():
        print(f"   {k:<16}: {v}")
    print(" Response:")
    print(f"   Message            : {result.message}")
    print(f"   Visually confirmed : {result.visually_confirmed}")
    print(f"   Confidence         : {result.confidence:.2f}")
    if result.explanation:
        print(f"   Explanation        : {result.explanation}")
    print("=" * 62)


def run_demo(
    use_live_vision: bool = True,
    store: AdherenceStore | None = None,
    pause_seconds: float = PAUSE,
) -> None:
    """
    Run the full automated demo.

    Parameters
    ----------
    use_live_vision:
        If True, the intake-verification scenes call the live LLM vision model.
        If it is unavailable, they fall back to a simulated result so the demo
        still completes.
    store:
        Event store used by the caregiver dashboard. Defaults to the same
        configured SQLite database as main.py.
    pause_seconds:
        Delay between scenes. Tests set this to zero.
    """
    store = store or AdherenceStore()
    engine = LLMEngine()

    print("\n" + "#" * 62)
    print("#  SmartMedBox — Automated Demo")
    print("#  Scheduler drives escalation · LLM generates the message")
    print("#" * 62)

    # ── Reminder line: force deterministic messages ──
    reminder_engine = LLMEngine()
    reminder_engine.client = None  # rule-based, stable output

    reminder_scenes = [
        ("08:00 — Dose becomes due",
         {"escalation": "due", "compartment": 0, "label": "Vitamin D", "minutes_overdue": 0}),
        ("08:15 — Still not taken, gentle reminder",
         {"escalation": "remind", "compartment": 0, "label": "Vitamin D", "minutes_overdue": 15}),
        ("08:35 — Overdue, caregiver alerted",
         {"escalation": "alert_caregiver", "compartment": 0, "label": "Vitamin D", "minutes_overdue": 35}),
    ]

    for title, ctx in reminder_scenes:
        result = reminder_engine.generate_reminder(context=ctx)
        _print(title, ctx, result)
        store.log_event(
            compartment=ctx["compartment"],
            action=ctx["escalation"],
            message=result.message or "",
            label=ctx["label"],
            scheduled_hour=8,
            notified=(ctx["escalation"] == ACTION_ALERT_CAREGIVER),
            minutes_overdue=ctx["minutes_overdue"],
        )
        time.sleep(pause_seconds)

    # ── Vision line: intake verification ──
    _run_vision(engine, use_live_vision, store, pause_seconds)

    print("\n" + "#" * 62)
    print("#  Demo complete.")
    print(f"#  Dashboard events: {store.db_path}")
    print("#" * 62 + "\n")


def _run_vision(
    engine: LLMEngine,
    use_live: bool,
    store: AdherenceStore,
    pause_seconds: float,
) -> None:
    """Demonstrate intake verification for a 'taken' and a 'not taken' image."""
    import base64
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[1]
    cases = [
        ("Intake verification — pill taken", "sample_intake.jpeg", True),
        ("Intake verification — pill NOT taken", "sample_not_intake.jpeg", False),
    ]

    for title, filename, simulated_confirmed in cases:
        ctx = {"compartment": 0, "open_count": 1, "label": "Vitamin D"}
        image_path = project_root / "assets" / filename

        result = None
        if use_live and engine.client is not None and image_path.exists():
            try:
                with open(image_path, "rb") as f:
                    image_b64 = base64.b64encode(f.read()).decode("utf-8")
                result = engine.verify_intake(context=ctx, image_b64=image_b64)
            except Exception as exc:
                print(f"[vision] live call failed, using simulated result: {exc}")

        # Fallback: simulated vision result so the demo never breaks.
        if result is None:
            result = ReasoningResult(
                message=("Great, I've confirmed you took your medication!"
                         if simulated_confirmed
                         else "I couldn't confirm your medication. Please try again."),
                visually_confirmed=simulated_confirmed,
                confidence=0.95,
                explanation="Simulated vision result (demo fallback).",
            )

        _print(title, ctx, result)
        store.log_event(
            compartment=ctx["compartment"],
            action=(
                ACTION_CONFIRMED
                if result.visually_confirmed
                else ACTION_VERIFICATION_FAILED
            ),
            message=result.message or "",
            label=ctx["label"],
            scheduled_hour=8,
        )
        time.sleep(pause_seconds)


if __name__ == "__main__":
    run_demo()
