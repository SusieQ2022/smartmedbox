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

    def __init__(self, num_compartments: int | None = None):
        self.num_compartments = num_compartments or Config.NUM_COMPARTMENTS
        self.mock = Config.is_mock()
        self.compartments: Dict[int, CompartmentState] = {}
        self._init_compartments()

        if not self.mock:
            self._init_hardware()

    def _init_compartments(self) -> None:
        """Create one hardware state object per compartment."""

        for index in range(self.num_compartments):
            self.compartments[index] = CompartmentState(index=index)

    def _init_hardware(self) -> None:
        """Initialise Raspberry Pi GPIO and reed switch."""

        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)

        self._gpio = GPIO

        # Single reed switch connected to GPIO17
        self._reed_pin = 17

        GPIO.setup(
            self._reed_pin,
            GPIO.IN,
            pull_up_down=GPIO.PUD_UP,
        )

        GPIO.add_event_detect(
            self._reed_pin,
            GPIO.FALLING,
            callback=self._reed_callback,
            bouncetime=300,
        )


    def _reed_callback(self, channel: int) -> None:
        """Called whenever the reed switch is triggered."""
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
        opened = []
        for index, state in self.compartments.items():
            # Detect a NEW opening event
            if state.open_count > state.last_processed_open_count:
                opened.append(index)
                # Mark this opening as processed
                state.last_processed_open_count = state.open_count

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

