"""
sensors.py — Hardware sensing layer (the SENSE stage).

Provides a unified interface to the weight sensors, reed switches and motion
sensor. On a Raspberry Pi it talks to real GPIO hardware; in mock mode it
simulates readings so the full application can be developed and demonstrated
on a laptop without any hardware attached.
"""

from dataclasses import dataclass
from typing import Dict

from config import Config
import time
import RPi.GPIO as GPIO


@dataclass
class CompartmentState:
    """Represents the current state of a single pill compartment."""
    index: int
    open_count: int = 0
    last_processed_open_count: int = 0
    taken_today: bool = False  # whether this dose was already taken today



class SensorArray:
    """
    Manages all sensing hardware for the medication box.

    In real mode this reads from HX711 load-cell amplifiers and GPIO reed
    switches. In mock mode it generates plausible fake readings.
    """

    def __init__(self, num_compartments: int = 1) -> None:
        self.num_compartments = num_compartments or Config.NUM_COMPARTMENTS
        self.mock = Config.is_mock()
        self.compartments: Dict[int, CompartmentState] = {}

        # Physical pin 11 = BCM GPIO17
        self._reed_pin = 17

        self._init_compartments()

        if not self.mock:
            self._init_hardware()

    def _init_compartments(self) -> None:
        """Create one hardware state object per compartment."""

        for index in range(self.num_compartments):
            self.compartments[index] = CompartmentState(index=index)

    def _init_hardware(self) -> None:
        """Initialize the reed switch GPIO safely."""

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        # Configure reed-switch pin as an input.
        # PUD_UP means the pin is HIGH when the switch is open
        # and LOW when the magnet closes the switch.
        GPIO.setup(
            self._reed_pin,
            GPIO.IN,
            pull_up_down=GPIO.PUD_UP,
        )

        initial_state = GPIO.input(self._reed_pin)

        print(
            f"[sensors] Initial GPIO17 state: {initial_state} "
            f"({'open' if initial_state == 1 else 'closed'})"
        )

        # Remove any old detector left on this pin.
        try:
           GPIO.remove_event_detect(self._reed_pin)
        except (RuntimeError, ValueError):
           pass

        # Small delay allows the GPIO state to settle.
        time.sleep(0.2)

        try:
           GPIO.add_event_detect(
               self._reed_pin,
               GPIO.RISING,
               callback=self._reed_callback,
               bouncetime=300,
           )

           print(
               f"[sensors] Reed-switch monitoring enabled "
               f"on GPIO {self._reed_pin}."
           )
        except RuntimeError as error:
           print(f"[sensors] Failed to initialize reed switch: {error}")
           raise

    def _reed_callback(self, channel: int) -> None:
        """Called whenever the reed switch is triggered."""
        print(f"[sensors] Reed switch opened on GPIO {channel}")
        self.compartments[0].open_count += 1
    
    def poll(self) -> list[int]:
        """
        Poll the reed switches and return compartments that have been
        opened since the previous poll.

        Returns
        -------
        list[int]
            Indices of compartments with a newly detected opening event.
        """
        opened: list[int] = []
        for index, state in self.compartments.items():
            # Detect a NEW opening event
            if state.open_count > state.last_processed_open_count:
                # Mark this opening as processed
                state.last_processed_open_count = state.open_count
                opened.append(index)

        return opened


    # ── Mock helpers (used by the simulator / tests only) ──

    def simulate_open(self, index: int) -> None:
        """Pretend the user opened a compartment lid."""
        if index in self.compartments:
            self.compartments[index].open_count += 1

    def simulate_pill_removed(self, index: int) -> None:
        """Pretend the user removed the dose from a compartment."""
        if index in self.compartments:
            self.compartments[index].open_count += 1

    def simulate_refill(self, index: int) -> None:
        """Reset a compartment back to a full dose."""
        if index in self.compartments:
            self.compartments[index].open_count = 0

    def cleanup(self) -> None:
        """Release GPIO resources."""

        if self.mock:
            return

        try:
            GPIO.remove_event_detect(self._reed_pin)
        except Exception:
            pass

        try:
            GPIO.cleanup()
        except Exception:
            pass

        print("[sensors] GPIO cleaned up.")
