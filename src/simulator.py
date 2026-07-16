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

try:
    from .llm_engine import LLMEngine, ReasoningResult
except ImportError:
    from llm_engine import LLMEngine, ReasoningResult


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


def run_demo(use_live_vision: bool = True) -> None:
    """
    Run the full automated demo.

    Parameters
    ----------
    use_live_vision:
        If True, the intake-verification scenes call the live LLM vision model.
        If it is unavailable, they fall back to a simulated result so the demo
        still completes.
    """
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
         {"escalation": "due", "compartment": 1, "label": "Vitamin D", "minutes_overdue": 0}),
        ("08:15 — Still not taken, gentle reminder",
         {"escalation": "remind", "compartment": 1, "label": "Vitamin D", "minutes_overdue": 15}),
        ("08:35 — Overdue, caregiver alerted",
         {"escalation": "alert_caregiver", "compartment": 1, "label": "Vitamin D", "minutes_overdue": 35}),
    ]

    for title, ctx in reminder_scenes:
        result = reminder_engine.generate_reminder(context=ctx)
        _print(title, ctx, result)
        time.sleep(PAUSE)

    # ── Vision line: intake verification ──
    _run_vision(engine, use_live_vision)

    print("\n" + "#" * 62)
    print("#  Demo complete.")
    print("#" * 62 + "\n")


def _run_vision(engine: LLMEngine, use_live: bool) -> None:
    """Demonstrate intake verification for a 'taken' and a 'not taken' image."""
    import base64
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[1]
    cases = [
        ("Intake verification — pill taken", "sample_intake.jpeg", True),
        ("Intake verification — pill NOT taken", "sample_not_intake.jpeg", False),
    ]

    for title, filename, simulated_confirmed in cases:
        ctx = {"compartment": 1, "open_count": 1, "label": "Vitamin D"}
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
        time.sleep(PAUSE)


if __name__ == "__main__":
    run_demo()