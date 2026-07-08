"""
voice.py - text-to-speech output for the ACT stage.

In mock mode this prints the spoken message. In real mode it uses the offline
pyttsx3 engine so the box can speak through its speaker.
"""

try:
    from .config import Config
except ImportError:
    from config import Config


class Voice:
    """Handles spoken output to the user."""

    def __init__(self):
        self.mock = Config.is_mock()
        self._engine = None
        if not self.mock:
            self._init_engine()

    def _init_engine(self) -> None:
        import pyttsx3

        self._engine = pyttsx3.init()
        self._engine.setProperty("rate", 150)
        self._engine.setProperty("volume", 1.0)

    def speak(self, text: str) -> None:
        """Speak the given text aloud, or print it in mock mode."""
        if not text:
            return
        if self.mock:
            print(f"[SmartMedBox says]: {text}")
            return
        self._engine.say(text)
        self._engine.runAndWait()
