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

try:
    from .config import Config
except ImportError:  # Allows importing as a script-level module in src/.
    from config import Config

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Result returned by the reasoning engine
# ----------------------------------------------------------------------

@dataclass
class ReasoningResult:
    message: str | None = None
    visually_confirmed: bool | None = None
    confidence: float = 1.0
    explanation: str = ""


# ----------------------------------------------------------------------
# System Prompt
# ----------------------------------------------------------------------

REMINDER_PROMPT = """
You are an empathetic medication assistant (SmartMedBox) for elderly users.

The medication schedule has already been determined by the scheduler.

Generate a short spoken reminder.

Return ONLY JSON.

{
    "message":"...",
    "visually_confirmed": none,
    "confidence":0.95,
    "explanation": none
}

Guidelines:
- The scheduler already determines the escalation level. Never change it.
- The escalation level will be one of:
    • due: the medication is due now. Generate a friendly initial reminder.
    • remind: the medication has not yet been taken. Generate a slightly more urgent reminder while remaining supportive.
    • alert: the medication has been overdue for more than 30 minutes. Generate a message informing the user that their caregiver will be notified.
- Never recommend medical decisions.
"""

VISION_SYSTEM_PROMPT = """
You are an empathetic medication assistant (SmartMedBox) for elderly users.

Your only task is determining whether the user has taken their medication.

You receive one photograph captured immediately after the medication compartment was opened.

Return ONLY JSON.

{   "message":"...",
    "visually_confirmed": true,
    "confidence": 0.94,
    "explanation": "..."
}

Guidelines:
- Determine whether there is clear visual evidence that the user has just taken or is placing a pill into their mouth.
- If the image is ambiguous or unclear, do NOT assume the medication has been taken. Set "visually_confirmed" to false.
- Keep confirming messages short. Be warm, supportive, and easy for elderly users to understand.
- Explanation should be a short summary of the reasoning behind the decision, including all relevant context from the sensors and image analysis.
"""

# ----------------------------------------------------------------------
# LLM Engine
# ----------------------------------------------------------------------

class LLMEngine:

    def __init__(self):

        self.model = Config.LLM_MODEL
        self.client = None

        if Config.KICONNECT_API_KEY:
            from openai import OpenAI

            self.client = OpenAI(
                api_key=Config.KICONNECT_API_KEY,
                base_url=Config.KICONNECT_BASE_URL,
            )

    # ------------------------------------------------------------------

    def generate_reminder(
    self,
    context: dict,
) -> ReasoningResult:
        """
        Generate a reminder message from scheduler context.

        The scheduler already determines the escalation level
        (due, remind, alert_caregiver). This method only produces
        an empathetic spoken message.
        """

        if self.client is None:
            return self._rule_based_fallback(context)

        try:

            # ----------------------------------------------------------
            # Build text-only prompt
            # ----------------------------------------------------------

            user_content = (
                "Current SmartMedBox reminder context:\n\n"
                + json.dumps(context, indent=2)
            )

            # ----------------------------------------------------------
            # Call GPT
            # ----------------------------------------------------------

            response = self.client.chat.completions.create(

                model=self.model,

                messages=[

                    {
                        "role": "system",
                        "content": REMINDER_PROMPT,
                    },

                    {
                        "role": "user",
                        "content": user_content,
                    },

                ],

                temperature=0.3,

            )

            content = response.choices[0].message.content
            assert content is not None

            logger.debug("Reminder LLM output:\n%s", content)

            return self._parse(content)

        except Exception:

            logger.exception("Reminder generation failed.")

            return self._rule_based_fallback(context)
    # ------------------------------------------------------------------

    def _parse(self, output_text: str) -> ReasoningResult:
        """
        Parse the LLM response into a ReasoningResult.
        Supports both plain JSON and Markdown-wrapped JSON.
        """

        output_text = output_text.strip()

        # Remove Markdown code fences if present
        if output_text.startswith("```"):
            lines = output_text.splitlines()

            # Remove opening ``` or ```json
            lines = lines[1:]

            # Remove closing ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            output_text = "\n".join(lines).strip()

        # Fix Python-style literals that are not valid JSON
        output_text = output_text.replace(": none", ": null")
        output_text = output_text.replace(":none", ": null")
        output_text = output_text.replace(": None", ": null")
        output_text = output_text.replace(": True", ": true")
        output_text = output_text.replace(": False", ": false")

        try:
            payload = json.loads(output_text)
        except json.JSONDecodeError:
            logger.exception("Failed to parse LLM output:\n%s", output_text)
            raise

        return ReasoningResult(
            message=payload.get("message", ""),
            visually_confirmed=bool(payload.get("visually_confirmed", False)),
            confidence=float(payload.get("confidence", 1.0)),
            explanation=payload.get("explanation", ""),
        )

    # ------------------------------------------------------------------

    def _rule_based_fallback(self, context: dict) -> ReasoningResult:
        """
        Fallback used when the OpenAI API is unavailable.

        The scheduler has already determined the escalation level.
        This method simply generates a deterministic message.
        No visual confirmation is possible without the LLM.
        """
        escalation = context.get("escalation", "due")

        if escalation == "due":
            return ReasoningResult(
                message="It's time to take your medication.",
                visually_confirmed=False,
                confidence=1.0,
                explanation="Rule-based fallback: initial reminder."
            )

        if escalation == "remind":
            return ReasoningResult(
                message="Just a gentle reminder that your medication is still waiting.",
                visually_confirmed=False,
                confidence=1.0,
                explanation="Rule-based fallback: repeated reminder."
            )

        if escalation == "alert_caregiver":
            return ReasoningResult(
                message="Your medication is overdue. Your caregiver will be notified.",
                visually_confirmed=False,
                confidence=1.0,
                explanation="Rule-based fallback: caregiver alert."
            )

        return ReasoningResult(
            message="",
            visually_confirmed=False,
            confidence=1.0,
            explanation="Rule-based fallback: no action required."
        )
        

    def verify_intake(
        self,
        context: dict,
        image_b64: str,
    ) -> ReasoningResult:
        """
        Verify whether the user has taken their medication from
        a single image captured after the compartment was opened.

        Returns
        -------
        ReasoningResult
            Structured reasoning result.
        """

        if self.client is None:
            return ReasoningResult(
                message="Couldn't verify medication intake: server unavailable.",
                visually_confirmed=False,
                confidence=1.0,
                explanation="Rule-based fallback: vision unavailable.",
            )

        try:

            user_content = [

                {
                    "type": "text",
                    "text": (
                        "Current SmartMedBox reminder context:\n\n" + json.dumps(context, indent=2)
                    ),
                },

                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_b64}"
                    },
                },

            ]

            response = self.client.chat.completions.create(

                model=self.model,

                messages=[

                    {
                        "role": "system",
                        "content": VISION_SYSTEM_PROMPT,
                    },

                    {
                        "role": "user",
                        "content": user_content,
                    },

                ],

                temperature=0,

            )

            content = response.choices[0].message.content
            assert content is not None

            logger.debug("Vision LLM output:\n%s", content)

            return self._parse(content)

        except Exception:

            logger.exception("Vision verification failed.")

            return ReasoningResult(
                message="Couldn't verify medication intake: server unavailable.",
                visually_confirmed=False,
                confidence=0.0,
                explanation="Vision verification failed.",

            )