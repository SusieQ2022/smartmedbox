"""
sensors.py — Hardware sensing layer (the SENSE stage).

Provides a unified interface to the weight sensors, reed switches and motion
sensor. On a Raspberry Pi it talks to real GPIO hardware; in mock mode it
simulates readings so the full application can be developed and demonstrated
on a laptop without any hardware attached.
"""

import random
import time
from dataclasses import dataclass, field
from typing import Dict

from config import Config


@dataclass
class CompartmentState:
    """Represents the current state of a single pill compartment."""
    index: int
    weight_g: float
    baseline_g: float
    open_count: int = 0
    label: str = ""            # e.g. "Morning", "Noon", "Evening", "Night"
    scheduled_hour: int = 8    # hour of day (0-23) this dose should be taken
    taken_today: bool = False  # whether this dose was already taken today

    @property
    def is_empty(self) -> bool:
        """A compartment is 'empty' when its weight drops well below baseline."""
        return self.weight_g < (self.baseline_g * 0.4)


class SensorArray:
    """
    Manages all sensing hardware for the medication box.

    In real mode this reads from HX711 load-cell amplifiers and GPIO reed
    switches. In mock mode it generates plausible fake readings.
    """

    def __init__(self, num_compartments: int = None):
        self.num_compartments = num_compartments or Config.NUM_COMPARTMENTS
        self.mock = Config.is_mock()
        self.compartments: Dict[int, CompartmentState] = {}
        self._init_compartments()

        if not self.mock:
            self._init_hardware()

    def _init_compartments(self) -> None:
        """Set up each compartment with a baseline weight and a daily schedule."""
        # Default daily medication schedule: one dose per time-of-day slot.
        # (label, scheduled_hour) — extended/truncated to fit num_compartments.
        schedule = [
            ("Morning", 8),    # 08:00
            ("Noon", 12),      # 12:00
            ("Evening", 18),   # 18:00
            ("Night", 22),     # 22:00
        ]
        for i in range(self.num_compartments):
            label, hour = schedule[i % len(schedule)]
            # Baseline ~5g represents a typical full daily dose of pills.
            self.compartments[i] = CompartmentState(
                index=i,
                weight_g=5.0,
                baseline_g=5.0,
                label=label,
                scheduled_hour=hour,
            )

    def _init_hardware(self) -> None:
        """Initialise real GPIO + HX711 hardware (Raspberry Pi only)."""
        # Imported lazily so the module still imports on a laptop.
        import RPi.GPIO as GPIO  # noqa: F401
        from hx711 import HX711  # noqa: F401

        GPIO.setmode(GPIO.BCM)
        # NOTE: pin assignments are documented in hardware/WIRING.md
        self._hx = {}  # would hold one HX711 instance per compartment
        # Real initialisation omitted here for brevity; see WIRING.md.

    def read_weight(self, index: int) -> float:
        """Read the current weight (grams) of a given compartment."""
        if self.mock:
            # Simulate small sensor noise around the stored value.
            state = self.compartments[index]
            return max(0.0, state.weight_g + random.uniform(-0.05, 0.05))
        # Real mode: read from the corresponding HX711 amplifier.
        # return self._hx[index].get_weight_mean()
        raise NotImplementedError("Real HX711 read configured per-device.")

    def poll(self) -> Dict[int, CompartmentState]:
        """
        Read all compartments and return their current state.

        This is the main method the application loop calls each cycle.
        """
        for i, state in self.compartments.items():
            state.weight_g = self.read_weight(i)
        return self.compartments

    def minutes_overdue(self, index: int, now=None) -> int:
        """
        Calculate how many minutes overdue a compartment's dose is.
        Compares the current time against the compartment's scheduled hour.
        Returns 0 if the dose is not yet due or has already been taken today.
        """
        from datetime import datetime

        state = self.compartments[index]
        if state.taken_today:
            return 0

        now = now or datetime.now()
        # Scheduled time today, at the compartment's scheduled hour (on the hour).
        scheduled = now.replace(
            hour=state.scheduled_hour, minute=0, second=0, microsecond=0
        )
        delta_minutes = int((now - scheduled).total_seconds() / 60)
        # Only positive values count as "overdue"; negative means not due yet.
        return max(0, delta_minutes)

    # ── Mock helpers (used by the simulator / tests only) ──

    def simulate_open(self, index: int) -> None:
        """Pretend the user opened a compartment lid."""
        if index in self.compartments:
            self.compartments[index].open_count += 1

    def simulate_pill_removed(self, index: int) -> None:
        """Pretend the user removed the dose from a compartment."""
        if index in self.compartments:
            self.compartments[index].weight_g = 0.2
            self.compartments[index].open_count += 1

    def simulate_refill(self, index: int) -> None:
        """Reset a compartment back to a full dose."""
        if index in self.compartments:
            self.compartments[index].weight_g = 5.0
            self.compartments[index].open_count = 0


if __name__ == "__main__":
    # Quick manual smoke-test of the sensor layer in mock mode.
    arr = SensorArray()
    print("Initial state:")
    for idx, st in arr.poll().items():
        print(f"  Compartment {idx}: {st.weight_g:.2f}g  empty={st.is_empty}")

    print("\nSimulating pill removal from compartment 0...")
    arr.simulate_pill_removed(0)
    for idx, st in arr.poll().items():
        print(f"  Compartment {idx}: {st.weight_g:.2f}g  empty={st.is_empty}")
