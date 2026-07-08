"""
notifier.py - caregiver notification for the ACT stage.

Uses Twilio in real mode and console output in mock mode.
"""

try:
    from .config import Config
except ImportError:
    from config import Config


class Notifier:
    """Sends alerts to caregivers."""

    def __init__(self):
        self.mock = Config.is_mock() or not Config.TWILIO_ACCOUNT_SID
        self._client = None
        if not self.mock:
            from twilio.rest import Client

            self._client = Client(
                Config.TWILIO_ACCOUNT_SID,
                Config.TWILIO_AUTH_TOKEN,
            )

    def alert(self, message: str) -> None:
        """Send a caregiver alert with the given message."""
        if not Config.CAREGIVER_PHONE:
            print("[notifier] No caregiver phone configured; skipping alert.")
            return
        if self.mock:
            print(f"[Caregiver alert -> {Config.CAREGIVER_PHONE}]: {message}")
            return
        self._client.messages.create(
            body=f"SmartMedBox: {message}",
            from_=Config.TWILIO_FROM_NUMBER,
            to=Config.CAREGIVER_PHONE,
        )
