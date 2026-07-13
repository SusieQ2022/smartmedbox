"""
main.py — SmartMedBox entry point.

Embodied AI pipeline:

    SENSE
        - Reed switch detects compartment opening
        - Raspberry Pi camera captures an image after interaction

    REASON
        - Multimodal LLM receives:
            * sensor context
            * captured image
          and decides the appropriate action.

    ACT
        - Speak reminder/confirmation
        - Notify caregiver when required

Run with:

    python src/main.py

In mock mode the application runs on any laptop and allows interactive
simulation of medication events.
"""

from __future__ import annotations

import time

from config import Config
from sensors import SensorArray
from camera import Camera
from llm_engine import LLMEngine, Decision
from voice import Voice
from notifier import Notifier
from store import AdherenceStore
from scheduler import ReminderScheduler


class SmartMedBox:
    """
    Main application controller.

    Coordinates the complete Sense → Reason → Act loop.
    """

    def __init__(self):

        Config.validate()

        self.sensors = SensorArray()
        self.camera = Camera()
        self.llm = LLMEngine()
        self.voice = Voice()
        self.notifier = Notifier()
        self.store = AdherenceStore()
        self.scheduler = ReminderScheduler(self.sensors)

    # ------------------------------------------------------------------
    # Sense → Reason → Act
    # ------------------------------------------------------------------

    def process_medication_event(
        self,
        compartment: int,
        minutes_overdue: int = 0,
    ) -> Decision:
        """
        Execute one complete embodied AI cycle.

        Parameters
        ----------
        compartment:
            Medication compartment number.

        minutes_overdue:
            Minutes since the scheduled medication time.
        """

        state = self.sensors.compartments[compartment]

        # --------------------------------------------------------------
        # SENSE
        # --------------------------------------------------------------

        context = {

            "compartment": compartment,

            "scheduled": True,

            "open_count": state.open_count,

            "is_empty": state.is_empty,

            "minutes_overdue": minutes_overdue,

        }

        image_b64 = None

        # Capture an image only after the compartment
        # has been opened.

        if state.open_count > 0:

            image_path = self.camera.capture()

            image_b64 = Camera.encode_base64(image_path)

        # --------------------------------------------------------------
        # REASON
        # --------------------------------------------------------------

        decision = self.llm.generate_reminder(

            context=context,

            image_b64=image_b64,

        )

        # --------------------------------------------------------------
        # ACT
        # --------------------------------------------------------------

        if decision.message:

            self.voice.speak(decision.message)

        if decision.notify_caregiver:

            self.notifier.alert(decision.message)

        if decision.action == "confirm_taken":

            state.taken_today = True

        self.store.log_event(

            compartment=compartment,

            action=decision.action,

            message=decision.message,

            label=state.label,

            scheduled_hour=state.scheduled_hour,

            notified=decision.notify_caregiver,

            minutes_overdue=minutes_overdue,

        )

        return decision

    # ------------------------------------------------------------------
    # Interactive Demo
    # ------------------------------------------------------------------

    def run_interactive(self) -> None:
        """
        Interactive development mode.

        Commands:

            open <n>
            take <n>
            double <n>
            overdue <n>
            refill <n>
            quit
        """

        print("=" * 60)
        print(" SmartMedBox — Interactive Demo")
        print("=" * 60)

        print("Commands:")
        print("  open <n>      Open compartment n")
        print("  take <n>      Simulate removing/taking dose n")
        print("  double <n>    Open compartment n twice")
        print("  overdue <n>   Simulate 35-minute overdue medication")
        print("  refill <n>    Reset compartment")
        print("  quit")
        print("-" * 60)

        while True:

            try:

                cmd = input("> ").strip().lower().split()

            except (EOFError, KeyboardInterrupt):

                print()

                break

            if not cmd:

                continue

            if cmd[0] == "quit":

                break

            if len(cmd) != 2 or not cmd[1].isdigit():

                print("Usage: open|take|double|overdue|refill <compartment>")

                continue

            compartment = int(cmd[1])

            if compartment not in self.sensors.compartments:

                print(f"Compartment {compartment} does not exist.")

                continue

            # ----------------------------------------------------------

            if cmd[0] == "open":

                self.sensors.simulate_open(compartment)

                decision = self.process_medication_event(compartment)

            elif cmd[0] == "take":

                self.sensors.simulate_pill_removed(compartment)

                decision = self.process_medication_event(compartment)

            elif cmd[0] == "double":

                self.sensors.simulate_open(compartment)

                self.sensors.simulate_open(compartment)

                decision = self.process_medication_event(compartment)

            elif cmd[0] == "overdue":

                decision = self.process_medication_event(

                    compartment,

                    minutes_overdue=35,

                )

            elif cmd[0] == "refill":

                self.sensors.simulate_refill(compartment)

                print(f"Compartment {compartment} refilled.")

                continue

            else:

                print("Unknown command.")

                continue

            # ----------------------------------------------------------
            # Display LLM decision
            # ----------------------------------------------------------

            print("\n---------------- Decision ----------------")

            print(f"Action      : {decision.action}")

            print(f"Message     : {decision.message}")

            print(f"Confidence  : {decision.confidence:.2f}")

            print(f"Caregiver   : {decision.notify_caregiver}")

            print("------------------------------------------\n")

        print("Goodbye — stay healthy!")

    # ------------------------------------------------------------------
    # Hardware Mode
    # ------------------------------------------------------------------

    def run(self) -> None:
        """
        Hardware execution loop.

        In the final Raspberry Pi implementation this loop will be driven
        by the medication schedule and reed-switch interrupts.
        """

        print("[main] Running on Raspberry Pi...")

        while True:

            self.sensors.poll()

            for event in self.scheduler.due_events():

                self.process_medication_event(

                    event.compartment,

                    minutes_overdue=event.minutes_overdue,

                )

            time.sleep(2)


# ----------------------------------------------------------------------
# Entry Point
# ----------------------------------------------------------------------

def main() -> None:

    box = SmartMedBox()

    if Config.is_mock():

        box.run_interactive()

    else:

        box.run()


if __name__ == "__main__":

    main()
