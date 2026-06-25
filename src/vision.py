"""
vision.py — Visual medication confirmation using OpenAI Vision.

This module sends a captured image to an OpenAI vision model and asks it
whether the user appears to have taken their medication.

The model returns ONLY JSON, making it easy to parse programmatically.

Expected output:

{
    "pill_taken": true
}

or

{
    "pill_taken": false
}
"""

import json
import os

from openai import OpenAI

from camera import Camera


class VisionVerifier:

    PROMPT = """
You are assisting a smart medication reminder system.

Look at the image and determine whether the person appears to have taken
or is clearly taking a pill.

Base your decision ONLY on what is visible.

Return ONLY valid JSON.

{
    "pill_taken": true
}

or

{
    "pill_taken": false
}
"""

    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

    def verify(self, image_path: str) -> bool:
        """
        Sends an image to OpenAI Vision.

        Returns:
            True  -> pill appears taken
            False -> pill not confirmed
        """

        image = Camera.encode_base64(image_path)

        if image is None:
            raise FileNotFoundError(image_path)

        response = self.client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": self.PROMPT
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{image}"
                        }
                    ]
                }
            ]
        )

        output = response.output_text.strip()

        try:
            result = json.loads(output)
            return bool(result["pill_taken"])

        except Exception as e:
            raise RuntimeError(
                f"Could not parse LLM response:\n{output}"
            ) from e
