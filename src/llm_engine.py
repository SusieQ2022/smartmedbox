"""
llm_engine.py — LLM reasoning core (the REASON stage).

This is the "brain" of SmartMedBox. It takes the current sensor state and,
where relevant, a confirmation image, and decides what the system should do:
remind the user, confirm intake, warn about a possible double-dose, or alert
a caregiver. It also generates the natural-language message that the voice
module will speak.

If no API key is configured, it falls back to a deterministic rule-based stub
so the application still runs end-to-end during development.
"""

import json
from dataclasses import dataclass
from typing import Optional

from config import Config


@dataclass
class Decision:
    """The structured output of the reasoning step."""
    action: str          # one of: remind | confirm_taken | warn_double | alert_caregiver | idle
    message: str         # natural-language text to speak to the user
    confidence: float    # 0.0–1.0
    notify_caregiver: bool = False


# System prompt that defines the assistant's role and required output format.
SYSTEM_PROMPT = """You are SmartMedBox, an empathetic medication assistant for
elderly and chronic patients. Given the current state of a pill box, decide the
single most appropriate action and craft a short, warm, spoken message.

Always respond with ONLY a JSON object of the form:
{"action": "...", "message": "...", "confidence": 0.0, "notify_caregiver": false}

Valid actions: remind, confirm_taken, warn_double, alert_caregiver, idle.
Keep the message under 30 words, conversational, and never clinical or alarming.
"""


class LLMEngine:
    """Wraps the OpenAI client and exposes high-level reasoning methods."""

    def __init__(self):
        self.model = Config.LLM_MODEL
        self.vision_model = Config.VISION_MODEL
        self._client = None
        if Config.OPENAI_API_KEY:
            from openai import OpenAI
            self._client = OpenAI(api_key=Config.OPENAI_API_KEY)

    # ── Public API ──

    def reason(self, context: dict) -> Decision:
        """
        Decide what to do given the current context.

        `context` typically contains: compartment index, whether it is empty,
        how many times it was opened, the scheduled time, and elapsed minutes.
        """
        if self._client is None:
            return self._rule_based_fallback(context)

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": json.dumps(context)},
                ],
                temperature=0.4,
                max_tokens=150,
            )
            raw = response.choices[0].message.content.strip()
            return self._parse(raw)
        except Exception as exc:  # network / API failure — stay functional
            print(f"[llm] API error, using fallback: {exc}")
            return self._rule_based_fallback(context)

    def confirm_intake(self, image_b64: Optional[str]) -> bool:
        """
        Use the vision model to confirm the pill was actually taken.

        Returns True if intake is visually confirmed. Falls back to True in
        mock/dev mode so the demo flow completes.
        """
        if self._client is None or image_b64 is None:
            return True  # development fallback

        try:
            response = self._client.chat.completions.create(
                model=self.vision_model,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text":
                            "Has the person taken their medication? "
                            "Answer strictly 'yes' or 'no'."},
                        {"type": "image_url", "image_url":
                            {"url": f"data:image/jpeg;base64,{image_b64}"}},
                    ],
                }],
                max_tokens=5,
            )
            answer = response.choices[0].message.content.strip().lower()
            return answer.startswith("yes")
        except Exception as exc:
            print(f"[llm] vision error, assuming confirmed: {exc}")
            return True

    # ── Internal helpers ──

    def _parse(self, raw: str) -> Decision:
        """Parse the JSON returned by the model into a Decision."""
        # Strip code fences if the model added them.
        raw = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw)
        return Decision(
            action=data.get("action", "idle"),
            message=data.get("message", ""),
            confidence=float(data.get("confidence", 0.5)),
            notify_caregiver=bool(data.get("notify_caregiver", False)),
        )

    def _rule_based_fallback(self, context: dict) -> Decision:
        """
        Deterministic logic used when no LLM is available.

        Keeps the system fully functional offline and serves as a clear,
        readable specification of the intended behaviour.
        """
        opened = context.get("open_count", 0)
        is_empty = context.get("is_empty", False)
        overdue = context.get("minutes_overdue", 0)

        if opened >= 2:
            return Decision(
                action="warn_double",
                message="It looks like this compartment was opened twice. "
                        "Did you already take your pill? Let's make sure first.",
                confidence=0.9,
                notify_caregiver=True,
            )
        if is_empty:
            return Decision(
                action="confirm_taken",
                message="Great — that's your dose taken. Have a lovely day!",
                confidence=0.85,
            )
        if overdue >= 30:
            return Decision(
                action="alert_caregiver",
                message="You still haven't taken your medication. "
                        "I'll let your family know so they can check in.",
                confidence=0.8,
                notify_caregiver=True,
            )
        if overdue > 0:
            return Decision(
                action="remind",
                message="Just a gentle reminder — it's time for your "
                        "medication. Shall I remind you again shortly?",
                confidence=0.8,
            )
        return Decision(action="idle", message="", confidence=1.0)
