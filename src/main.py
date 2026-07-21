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

import textwrap

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from PIL import ImageFont
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

class OLEDDisplay:
    """Controls the SH1106 OLED display at I2C address 0x3C."""

    def __init__(self) -> None:
        self.device = None
        self.font = None

        try:
            serial = i2c(
                port=1,
                address=0x3C,
            )

            self.device = sh1106(serial)
            self.font = ImageFont.load_default()

            self.show_message(
                "SmartMedBox",
                "Starting...",
            )

            print("[display] OLED initialized.")

        except Exception as error:
            print(f"[display] OLED initialization failed: {error}")
            self.device = None

    def show_message(self, *messages: str) -> None:
        """Display wrapped text on the OLED."""

        if self.device is None:
            print("[display]", " | ".join(messages))
            return

        lines: list[str] = []

        for message in messages:
            wrapped = textwrap.wrap(
                str(message),
                width=20,
            )

            lines.extend(wrapped or [""])

        try:
            with canvas(self.device) as draw:
                y_position = 0

                for line in lines[:6]:
                    draw.text(
                        (0, y_position),
                        line,
                        font=self.font,
                        fill="white",
                    )

                    y_position += 10

        except Exception as error:
            print(f"[display] Message failed: {error}")

    def clear(self) -> None:
        """Clear the OLED."""

        if self.device is not None:
            try:
                self.device.clear()
            except Exception:
                pass


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
        self.display = OLEDDisplay()
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

        medication = self.scheduler.medication_for(event.compartment, event.scheduled_hour)

        self.store.log_event(
            compartment=event.compartment,
            action=event.escalation,
            message=result.message or "",
            label=medication.label,
            scheduled_hour=medication.scheduled_hour,
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
        medication = self.scheduler.medication_for(compartment) 
        

        # Ask the user to present the pill
        self.voice.speak(
            "Please hold the pill near your mouth. I will check in five seconds."
        )
        
        self.display.show_message(
            "Medicine box opened",
            "Please take medicine",
            "Photo in 10 seconds",
        )

        # Give the user time to take the pill out
        time.sleep(20)
    
        # ----------------------------------------------------------
        # Capture image
        # ----------------------------------------------------------
        
        image_path = self.camera.capture()
        print(f"[camera] Photo captured: {image_path}")
        #image_b64 = Camera.encode_base64(image_path)

        if image_b64 is None:
            print("[camera] Failed to capture image.")
            return

        # ----------------------------------------------------------
        # Vision verification
        # ----------------------------------------------------------

        #context = {
            #"compartment": compartment,
            #"label": medication.label,
            #"open_count": state.open_count,
        #}
        #result = self.llm.verify_intake(
            #context=context,
            #image_b64=image_b64,
        #)

        # ----------------------------------------------------------
        # Medication confirmed
        # ----------------------------------------------------------

        #if result.visually_confirmed:
            #self.scheduler.mark_completed(compartment,medication.scheduled_hour)
            #self.display = OLEDDisplay()
            #state.taken_today = True
            #self.voice.speak(
                #result.message or ""
            #)

            #self.store.log_event(

                #compartment=compartment,
                #action="confirmed",
                #message=result.message or "",
                #label=medication.label,
                #scheduled_hour=medication.scheduled_hour,

            #)

        # ----------------------------------------------------------
        # Medication NOT confirmed
        # ----------------------------------------------------------

        #else:
            #self.voice.speak(
                #result.message or ""
            #)
            #self.store.log_event(
                #compartment=compartment,
                #action="verification_failed",
                #message=result.message or "",
                #label=medication.label,
                #scheduled_hour=medication.scheduled_hour,
            #)

        # ----------------------------------------------------------
        # Temporary validation solution
        # ----------------------------------------------------------
        
        self.scheduler.mark_completed(
            compartment,
            medication.scheduled_hour,
        )

        state.taken_today = True

        confirmation_message = "Medicine finally taken."

        self.voice.speak(confirmation_message)

        self.display.show_message(
            "Medicine finally taken",
            "Successfully recorded",
        )

        self.store.log_event(
            compartment=compartment,
            action="confirmed",
            message=confirmation_message,
            label=medication.label,
            scheduled_hour=medication.scheduled_hour,
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
            due
            remind
            alert
            open
            refill
            quit
        """

        compartment = 0
        medication = self.scheduler.medication_for(compartment)
        
        print("=" * 60)
        print(" SmartMedBox — Interactive Demo")
        print("=" * 60)

        print("Commands:")
        print("  due      Send initial reminder")
        print("  remind   Send repeated reminder")
        print("  alert    Trigger caregiver alert")
        print("  open     Simulate opening the medication box")
        print("  refill   Reset today's medication")
        print("  quit")
        print("-" * 60)

        while True:
            try:
                command = input("> ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if not command:
                continue

            if command == "quit":
                break

            elif command == "open":
                self.sensors.simulate_open(compartment)
                self.process_compartment_open(compartment)

            elif command == "due":
                self.process_scheduler_event(
                    ScheduleEvent(
                        compartment=compartment,
                        label=medication.label,
                        scheduled_hour=medication.scheduled_hour,
                        minutes_overdue=0,
                        escalation="due",
                    )
                )

            elif command == "remind":
                self.process_scheduler_event(
                    ScheduleEvent(
                        compartment=compartment,
                        label=medication.label,
                        scheduled_hour=medication.scheduled_hour,
                        minutes_overdue=10,
                        escalation="remind",
                    )
                )

            elif command == "alert":
                self.process_scheduler_event(
                    ScheduleEvent(
                        compartment=compartment,
                        label=medication.label,
                        scheduled_hour=medication.scheduled_hour,
                        minutes_overdue=35,
                        escalation="alert_caregiver",
                    )
                )

            elif command == "refill":
                self.sensors.simulate_refill(compartment)
                print("Medication compartment reset.")

            else:
                print("Unknown command.")
                print("Available commands: due, remind, alert, open, refill, quit")

        print("Goodbye — stay healthy!")

    # ------------------------------------------------------------------
    # Hardware Mode
    # ------------------------------------------------------------------

    def run(self) -> None:
        print("[main] Running on Raspberry Pi...")
        print("[main] Waiting for the medicine box to open.")

        try:
           while True:
              opened = self.sensors.poll()

              if opened:
                print(f"[DEBUG] Opened compartments: {opened}")
  
              for event in self.scheduler.due_events():
                self.process_scheduler_event(event)

              for compartment in opened:
                self.process_compartment_open(compartment)
 
              time.sleep(0.2)

        except KeyboardInterrupt:
           print("\n[main] Stopping SmartMedBox...")

        finally:
           self.sensors.cleanup()


    # ----------------------------------------------------------------------
    # Entry Point
    # ----------------------------------------------------------------------



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
