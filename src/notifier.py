"""
notifier.py — Caregiver notification (part of the ACT stage).

Sends an SMS alert to a registered caregiver when the system detects a missed
dose or a possible double-dose. Uses Twilio in real mode; in mock mode it logs
the notification to the console so the flow can be tested without credentials.
"""

from config import Config


class Notifier:
    """Sends alerts to caregivers."""

    def __init__(self):
        self.mock = Config.is_mock() or not Config.TWILIO_ACCOUNT_SID
        self._client = None
        if not self.mock:
            from twilio.rest import Client
            self._client = Client(Config.TWILIO_ACCOUNT_SID,
                                  Config.TWILIO_AUTH_TOKEN)

    def alert(self, message: str) -> None:
        """Send a caregiver alert with the given message."""
        if not Config.CAREGIVER_PHONE:
            print("[notifier] No caregiver phone configured; skipping alert.")
            return
        if self.mock:
            print(f"📲 [Caregiver alert -> {Config.CAREGIVER_PHONE}]: {message}")
            return
        self._client.messages.create(
            body=f"SmartMedBox: {message}",
            from_=Config.TWILIO_FROM_NUMBER,
            to=Config.CAREGIVER_PHONE,
        )
