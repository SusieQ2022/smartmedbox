"""
vision.py — Visual medication intake verification.

This module analyses an image captured by the Raspberry Pi camera and
determines whether there is clear visual evidence that the user has
just taken (or is taking) their medication.

It is intentionally conservative:
if the image is ambiguous, the medication is NOT confirmed.
"""

import json
from dataclasses import dataclass

from openai import OpenAI

from config import Config


VISION_PROMPT = """
You are assisting a smart medication reminder system.

Your task is ONLY to determine whether there is clear visual evidence
that the person has just taken, or is placing, a pill into their mouth.

If the image is blurry, ambiguous, obstructed,
or you cannot confidently determine this,
return FALSE.

Return ONLY valid JSON.

{
    "pill_taken": true,
    "confidence": 0.93
}

or

{
    "pill_taken": false,
    "confidence": 0.42
}
"""


@dataclass
class VisionResult:
    confirmed: bool
    confidence: float


class VisionVerifier:

    def __init__(self):

        self.model = Config.VISION_MODEL
        self.client = None

        if Config.OPENAI_API_KEY:
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)

    def verify(self, image_b64: str) -> VisionResult:

        if self.client is None or image_b64 is None:
            return VisionResult(False, 0.0)

        try:

            response = self.client.responses.create(

                model=self.model,

                input=[

                    {
                        "role": "user",

                        "content": [

                            {
                                "type": "input_text",
                                "text": VISION_PROMPT
                            },

                            {
                                "type": "input_image",
                                "image_url":
                                    f"data:image/jpeg;base64,{image_b64}"
                            }

                        ]

                    }

                ],

                temperature=0

            )

            raw = response.output_text.strip()

            data = json.loads(raw)

            return VisionResult(

                confirmed=bool(data["pill_taken"]),

                confidence=float(data["confidence"])

            )

        except Exception as exc:

            print(f"[vision] {exc}")

            return VisionResult(False, 0.0)
