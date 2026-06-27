"""
llm_engine.py — LLM reasoning core (REASON stage).

This module is the reasoning engine of SmartMedBox.

It receives structured context from the sensing layer:
    - Reed switch (compartment opened)
    - Vision verification
    - Reminder timing
    - Number of compartment openings

and decides the single best action for the system.

Vision analysis is performed in vision.py.
This module ONLY reasons over the resulting context.
"""

import json
import logging
from dataclasses import dataclass

from config import Config

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Decision returned by the reasoning engine
# ----------------------------------------------------------------------

@dataclass
class Decision:
    action: str
    message: str
    confidence: float
    notify_caregiver: bool = False


# ----------------------------------------------------------------------
# System Prompt
# ----------------------------------------------------------------------

SYSTEM_PROMPT = """
You are an empathetic medication assistant for elderly users.

You receive:
1. Structured sensor data
2. A photograph taken immediately after the medication compartment was opened.

Use BOTH sources of information to decide the most appropriate action.

If an image is provided:
- Determine whether there is clear visual evidence that the user has just taken or is placing a pill into their mouth.
- If the image is ambiguous or unclear, do NOT assume the medication has been taken.

Return ONLY valid JSON.

{
    "action": "...",
    "message": "...",
    "confidence": 0.95,
    "notify_caregiver": false
}

Allowed actions:
- remind
- confirm_taken
- warn_double
- alert_caregiver
- idle

Guidelines:
- Keep messages under 30 words.
- Be supportive and reassuring.
- Never recommend medical decisions.
- Never modify medication schedules.
"""


# ----------------------------------------------------------------------
# LLM Engine
# ----------------------------------------------------------------------

class LLMEngine:

    def __init__(self):

        self.model = Config.LLM_MODEL
        self.client = None

        if Config.OPENAI_API_KEY:
            from openai import OpenAI

            self.client = OpenAI(
                api_key=Config.OPENAI_API_KEY
            )

    # ------------------------------------------------------------------

    def reason(
    self,
    context: dict,
    image_b64: str | None = None,
) -> Decision:
    """
    Decide what SmartMedBox should do.

    Parameters
    ----------
    context:
        Structured sensor context.

    image_b64:
        Base64-encoded image captured after the compartment
        was opened. Can be None if no image was taken.

    Example context:

    {
        "compartment": 1,
        "scheduled": True,
        "open_count": 1,
        "minutes_overdue": 5
    }
    """

    if self.client is None:
        return self._rule_based_fallback(context)

    try:

        # ----------------------------------------------------------
        # Build multimodal user content
        # ----------------------------------------------------------

        user_content = [

            {
                "type": "input_text",
                "text": (
                    "Current SmartMedBox context:\n\n"
                    + json.dumps(context, indent=2)
                ),
            }

        ]

        if image_b64 is not None:

            user_content.append(

                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{image_b64}",
                }

            )

        # ----------------------------------------------------------
        # Call GPT
        # ----------------------------------------------------------

        response = self.client.responses.create(

            model=self.model,

            input=[

                {
                    "role": "system",

                    "content": [

                        {
                            "type": "input_text",

                            "text": SYSTEM_PROMPT,

                        }

                    ],

                },

                {
                    "role": "user",

                    "content": user_content,

                },

            ],

            temperature=0.2,

        )

        return self._parse(response.output_text)

    except Exception:

        logger.exception("LLM reasoning failed.")

        return self._rule_based_fallback(context)

    # ------------------------------------------------------------------

    def _rule_based_fallback(self, context: dict) -> Decision:
        """
        Runs when the API is unavailable.

        Keeps SmartMedBox fully functional offline.
        """

        opened = context.get("open_count", 0)

        overdue = context.get("minutes_overdue", 0)

        vision_confirmed = context.get(
            "vision_confirmed",
            False,
        )

        # --------------------------------------------------------------

        # Possible double dose

        if opened >= 2:

            return Decision(

                action="warn_double",

                message=(
                    "This compartment has already been opened. "
                    "Let's make sure you haven't already taken "
                    "your medication."
                ),

                confidence=0.95,

                notify_caregiver=True,

            )

        # --------------------------------------------------------------

        # Medication confirmed

        if opened >= 1 and vision_confirmed:

            return Decision(

                action="confirm_taken",

                message=(
                    "Great! I've confirmed your medication intake. "
                    "Have a wonderful day!"
                ),

                confidence=0.95,

            )

        # --------------------------------------------------------------

        # Compartment opened but intake NOT confirmed

        if opened >= 1 and not vision_confirmed:

            return Decision(

                action="remind",

                message=(
                    "I couldn't confirm your medication yet. "
                    "Please hold the pill near your mouth "
                    "so I can verify it."
                ),

                confidence=0.80,

            )

        # --------------------------------------------------------------

        # Medication overdue

        if overdue >= 30:

            return Decision(

                action="alert_caregiver",

                message=(
                    "Your medication is still overdue. "
                    "I'll notify your caregiver "
                    "so they can check in."
                ),

                confidence=0.90,

                notify_caregiver=True,

            )

        # --------------------------------------------------------------

        # Gentle reminder

        if overdue > 0:

            return Decision(

                action="remind",

                message=(
                    "It's time to take your medication."
                ),

                confidence=0.80,

            )

        # --------------------------------------------------------------

        return Decision(

            action="idle",

            message="",

            confidence=1.0,

        )
