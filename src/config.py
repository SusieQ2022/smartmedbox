"""
config.py — Centralised configuration loader for SmartMedBox.

Loads settings from environment variables (.env file) with sensible defaults.
Keeping all configuration in one place makes the rest of the codebase clean
and avoids scattering os.getenv() calls everywhere.
"""

import os

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv() -> None:
        """Allow mock mode to run before optional dependencies are installed."""
        return None

# Load variables from a .env file in the project root, if present.
load_dotenv()


class Config:
    """Application-wide configuration, populated from environment variables."""

    # ── LLM / OpenAI ──
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o")
    VISION_MODEL: str = os.getenv("VISION_MODEL", "gpt-4o")
    KICONNECT_API_KEY: str = os.getenv("KICONNECT_API_KEY", "")
    KICONNECT_BASE_URL: str = os.getenv(
        "KICONNECT_BASE_URL",
        "https://chat.kiconnect.nrw/api/v1",
    )

    # ── Caregiver notification (optional) ──
    CAREGIVER_PHONE: str = os.getenv("CAREGIVER_PHONE", "")
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_FROM_NUMBER: str = os.getenv("TWILIO_FROM_NUMBER", "")

    # ── Device behaviour ──
    NUM_COMPARTMENTS: int = int(os.getenv("NUM_COMPARTMENTS", "4"))
    LANGUAGE: str = os.getenv("LANGUAGE", "en")
    REMINDER_INTERVAL_MIN: int = int(os.getenv("REMINDER_INTERVAL_MIN", "15"))
    DB_PATH: str = os.getenv("SMARTMEDBOX_DB", "smartmedbox.db")
    SMARTMEDBOX_DB: str = DB_PATH

    # ── Hardware mode ──
    # 'real'  -> use Raspberry Pi GPIO / camera
    # 'mock'  -> simulate hardware so the app runs on a laptop for development
    HARDWARE_MODE: str = os.getenv("HARDWARE_MODE", "mock").lower()

    @classmethod
    def is_mock(cls) -> bool:
        """Return True when running without real hardware (development mode)."""
        return cls.HARDWARE_MODE != "real"

    @classmethod
    def validate(cls) -> None:
        """Warn early if critical configuration is missing."""
        if not (cls.KICONNECT_API_KEY or cls.OPENAI_API_KEY):
            print("[config] WARNING: no LLM API key is set. "
                  "LLM reasoning will fall back to a rule-based stub.")
