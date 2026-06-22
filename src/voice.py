"""
voice.py — Text-to-speech output (part of the ACT stage).

Speaks the LLM-generated message aloud through the box's speaker. Uses the
offline pyttsx3 engine by default (works without internet); in mock mode it
simply prints the spoken text to the console for development.
"""

from config import Config


class Voice:
    """Handles spoken output to the user."""

    def __init__(self):
        self.mock = Config.is_mock()
        self._engine = None
        if not self.mock:
            self._init_engine()

    def _init_engine(self) -> None:
        """Initialise the offline TTS engine (real mode only)."""
        import pyttsx3
        self._engine = pyttsx3.init()
        self._engine.setProperty("rate", 150)   # slower, clearer for elderly users
        self._engine.setProperty("volume", 1.0)

    def speak(self, text: str) -> None:
        """Speak the given text aloud (or print it in mock mode)."""
        if not text:
            return
        if self.mock:
            print(f"🔊 [SmartMedBox says]: {text}")
            return
        self._engine.say(text)
        self._engine.runAndWait()
