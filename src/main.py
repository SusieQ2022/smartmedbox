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
from llm_engine import LLMEngine, ReasoningResult
from voice import Voice
from notifier import Notifier
from store import AdherenceStore
from scheduler import ReminderScheduler, ScheduleEvent
from datetime import date, datetime


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

    def process_scheduler_event(self, event: ScheduleEvent) -> None:
        """
        Handle a scheduled medication reminder.
        """

        context = {
            "label": event.label,
            "minutes_overdue": event.minutes_overdue,
            "escalation": event.escalation,
        }

        result = self.llm.generate_reminder(context)

        self.voice.speak(result.message or "")

        if event.escalation == "alert_caregiver":
            self.notifier.alert(result.message or "")

        self.store.log_event(
        compartment=event.compartment,
        action=event.escalation,
        message=result.message or "",
        label=event.label,
        scheduled_hour=self.sensors.compartments[event.compartment].scheduled_hour,
        notified=(event.escalation == "alert_caregiver"),
        minutes_overdue=event.minutes_overdue,
    )

    def process_compartment_open(
        self,
        compartment: int,
    ) -> None:
        """
        Handle a user opening a medication compartment.
        Workflow:
            Reed switch
                ↓
            Capture image
                ↓
            Verify intake with LLM
                ↓
            Mark dose completed (if confirmed)
                ↓
            Log event
    """
        state = self.sensors.compartments[compartment]

        # ----------------------------------------------------------
        # Capture image
        # ----------------------------------------------------------

        image_path = self.camera.capture()
        image_b64 = Camera.encode_base64(image_path)

        if image_b64 is None:
            print("[camera] Failed to capture image.")
            return

        # ----------------------------------------------------------
        # Vision verification
        # ----------------------------------------------------------

        context = {
            "compartment": compartment,
            "label": state.label,
            "open_count": state.open_count,
        }
        result = self.llm.verify_intake(
            context=context,
            image_b64=image_b64,
        )

        # ----------------------------------------------------------
        # Medication confirmed
        # ----------------------------------------------------------

        if result.visually_confirmed:
            self.scheduler.mark_completed(compartment)
            state.taken_today = True
            self.voice.speak(
                result.message or ""
            )

            self.store.log_event(

                compartment=compartment,
                action="confirmed",
                message=result.message or "",
                label=state.label,
                scheduled_hour=state.scheduled_hour,

            )

        # ----------------------------------------------------------
        # Medication NOT confirmed
        # ----------------------------------------------------------

        else:
            self.voice.speak(
                result.message or ""
            )
            self.store.log_event(
                compartment=compartment,
                action="verification_failed",
                message=result.message or "",
                label=state.label,
                scheduled_hour=state.scheduled_hour,
            )

        # ----------------------------------------------------------
        # Debug output
        # ----------------------------------------------------------

        print("\n----------- Vision Result -----------")
        print(f"Confirmed   : {result.visually_confirmed}")
        print(f"Confidence  : {result.confidence:.2f}")
        print(f"Explanation : {result.explanation}")
        print("-------------------------------------\n")
    
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

                self.process_compartment_open(compartment)


            elif cmd[0] == "double":

                self.sensors.simulate_open(compartment)

                self.sensors.simulate_open(compartment)

                self.process_compartment_open(compartment)
                
            elif cmd[0] == "due":

                self.process_scheduler_event(
                    event =  ScheduleEvent(
                        compartment=compartment,
                        label=self.sensors.compartments[compartment].label,
                        minutes_overdue=0,
                        escalation="due",

                ))
                
            elif cmd[0] == "remind":

                self.process_scheduler_event(
                    event =  ScheduleEvent(
                        compartment=compartment,
                        label=self.sensors.compartments[compartment].label,
                        minutes_overdue=10,
                        escalation="remind",

                ))    
                    
            elif cmd[0] == "overdue":

                self.process_scheduler_event(
                    event =  ScheduleEvent(
                        compartment=compartment,
                        label=self.sensors.compartments[compartment].label,
                        minutes_overdue=35,
                        escalation="alert_caregiver",

                ))

            elif cmd[0] == "refill":

                self.sensors.simulate_refill(compartment)

                print(f"Compartment {compartment} refilled.")

                continue

            else:

                print("Unknown command.")

                continue

            # ----------------------------------------------------------
            # Display LLM decision: already logged internally
            # ----------------------------------------------------------


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

            opened = self.sensors.poll()

            for event in self.scheduler.due_events():
                self.process_scheduler_event(event)
                
            for compartment in opened:
                self.process_compartment_open(compartment)

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
