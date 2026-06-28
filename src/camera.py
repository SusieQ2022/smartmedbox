"""
camera.py — Camera capture & visual intake confirmation (part of SENSE).

This module captures an image when the user is asked to confirm they have
taken their medication, then passes it to the LLM vision model to verify
that the pill was actually taken (e.g. the user shows an empty hand / mouth).

This is the key feature that distinguishes SmartMedBox from existing products:
weight sensors only tell us the pill is *gone* — the camera confirms it was
actually *taken*.
"""

import base64
import os
import time
from typing import Optional

from src.config import Config


class Camera:
    """
    Captures images for visual medication-intake confirmation.

    In real mode it uses the Raspberry Pi Camera (picamera2). In mock mode it
    returns a placeholder image path so the pipeline can be tested on a laptop.
    """

    def __init__(self):
        self.mock = Config.is_mock()
        self._cam = None
        if not self.mock:
            self._init_camera()

    def _init_camera(self) -> None:
        """Initialise the Raspberry Pi camera (real mode only)."""
        from picamera2 import Picamera2  # lazy import — Pi only
        self._cam = Picamera2()
        self._cam.configure(self._cam.create_still_configuration())
        self._cam.start()
        time.sleep(1)  # allow sensor to warm up

    def capture(self, save_dir: str = "captures") -> str:
        """
        Capture a still image and return its file path.

        In mock mode this returns a bundled sample image instead.
        """
        if self.mock:
            # Return a placeholder shipped in assets/ for development.
            return os.path.join("assets", "sample_confirmation.jpg")

        os.makedirs(save_dir, exist_ok=True)
        path = os.path.join(save_dir, f"confirm_{int(time.time())}.jpg")
        self._cam.capture_file(path)
        return path

    @staticmethod
    def encode_base64(image_path: str) -> Optional[str]:
        """Encode an image as base64 for sending to the vision API."""
        if not os.path.exists(image_path):
            return None
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
