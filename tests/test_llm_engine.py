"""
test_llm_engine.py

Integration test for the SmartMedBox reasoning engine.

This test loads a sample image from the assets directory,
creates mock sensor data, and sends BOTH to the multimodal
LLM. The returned decision is printed in a readable format.

Run:

    python tests/test_llm_engine.py
"""

from camera import Camera
from llm_engine import LLMEngine


def print_separator():

    print("\n" + "=" * 60)


def main():

    # ---------------------------------------------------------
    # Load sample image
    # ---------------------------------------------------------

    image_path = "assets/sample_intake.jpg"

    image_b64 = Camera.encode_base64(image_path)

    if image_b64 is None:

        raise FileNotFoundError(
            f"Could not load image: {image_path}"
        )

    # ---------------------------------------------------------
    # Mock sensor data
    # ---------------------------------------------------------

    context = {

        "compartment": 1,

        "scheduled": True,

        "open_count": 1,

        "minutes_overdue": 0,

    }

    # ---------------------------------------------------------
    # Run LLM
    # ---------------------------------------------------------

    engine = LLMEngine()

    decision = engine.reason(

        context=context,

        image_b64=image_b64,

    )

    # ---------------------------------------------------------
    # Display results
    # ---------------------------------------------------------

    print_separator()

    print("SMARTMEDBOX MULTIMODAL LLM TEST")

    print_separator()

    print("\nImage")

    print(f"  {image_path}")

    print("\nSensor Context")

    for key, value in context.items():

        print(f"  {key:<20}: {value}")

    print_separator()

    print("LLM Decision")

    print_separator()

    print(f"Action              : {decision.action}")

    print(f"Message             : {decision.message}")

    print(f"Confidence          : {decision.confidence:.2f}")

    print(f"Notify caregiver    : {decision.notify_caregiver}")

    print_separator()


if __name__ == "__main__":

    main()
