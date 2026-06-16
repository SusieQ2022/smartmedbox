"""
main.py — SmartMedBox entry point.

Orchestrates the full Embodied AI loop:

    SENSE   -> read sensors (weight, open count) + camera
    REASON  -> LLM decides the appropriate action and message
    ACT     -> speak to the user + alert caregiver if needed

Run with `python src/main.py`. In the default 'mock' hardware mode this runs
on any laptop and lets you simulate medication events interactively, which is
ideal for development and for rehearsing the live demo.
"""

import time

from config import Config
from sensors import SensorArray
from camera import Camera
from llm_engine import LLMEngine, Decision
from voice import Voice
from notifier import Notifier


class SmartMedBox:
    """Top-level controller wiring together all subsystems."""

    def __init__(self):
        Config.validate()
        self.sensors = SensorArray()
        self.camera = Camera()
        self.llm = LLMEngine()
        self.voice = Voice()
        self.notifier = Notifier()

    def handle_compartment(self, index: int, minutes_overdue: int = 0) -> Decision:
        """
        Run one full Sense -> Reason -> Act cycle for a single compartment.
        Returns the Decision taken (useful for tests and logging).
        """
        state = self.sensors.compartments[index]

        # ── SENSE ──
        context = {
            "compartment": index,
            "is_empty": state.is_empty,
            "open_count": state.open_count,
            "minutes_overdue": minutes_overdue,
        }

        # If the dose appears gone, visually confirm it was actually taken.
        if state.is_empty:
            image_path = self.camera.capture()
            image_b64 = Camera.encode_base64(image_path)
            confirmed = self.llm.confirm_intake(image_b64)
            context["visually_confirmed"] = confirmed

        # ── REASON ──
        decision = self.llm.reason(context)

        # ── ACT ──
        self.voice.speak(decision.message)
        if decision.notify_caregiver:
            self.notifier.alert(decision.message)

        return decision

    def run_interactive(self) -> None:
        """
        Simple interactive loop for development / demo in mock mode.

        Lets you type a compartment number to simulate the user taking a pill,
        then watch the full Sense -> Reason -> Act response play out.
        """
        print("=" * 56)
        print(" SmartMedBox — interactive demo (mock mode)")
        print("=" * 56)
        print("Commands:")
        print("  take <n>     simulate taking the dose in compartment n")
        print("  double <n>   simulate opening compartment n twice")
        print("  overdue <n>  simulate compartment n being 35 min overdue")
        print("  refill <n>   reset compartment n")
        print("  quit         exit")
        print("-" * 56)

        while True:
            try:
                cmd = input("> ").strip().lower().split()
            except (EOFError, KeyboardInterrupt):
                break
            if not cmd:
                continue
            if cmd[0] == "quit":
                break

            if len(cmd) == 2 and cmd[1].isdigit():
                n = int(cmd[1])
                if n not in self.sensors.compartments:
                    print(f"  No compartment {n}.")
                    continue

                if cmd[0] == "take":
                    self.sensors.simulate_pill_removed(n)
                    self.handle_compartment(n)
                elif cmd[0] == "double":
                    self.sensors.simulate_pill_removed(n)
                    self.sensors.simulate_pill_removed(n)
                    self.handle_compartment(n)
                elif cmd[0] == "overdue":
                    self.handle_compartment(n, minutes_overdue=35)
                elif cmd[0] == "refill":
                    self.sensors.simulate_refill(n)
                    print(f"  Compartment {n} refilled.")
                else:
                    print("  Unknown command.")
            else:
                print("  Usage: take|double|overdue|refill <compartment-number>")

        print("Goodbye — stay healthy!")


def main() -> None:
    box = SmartMedBox()
    if Config.is_mock():
        box.run_interactive()
    else:
        # On real hardware this would be a continuous polling loop driven by
        # the medication schedule. Kept minimal here for clarity.
        print("[main] Running on hardware. Starting monitoring loop...")
        while True:
            box.sensors.poll()
            time.sleep(2)


if __name__ == "__main__":
    main()
