"""
test_llm_engine.py

Integration test for the SmartMedBox multimodal reasoning engine.

This test loads a sample image and evaluates the LLM under the three
scheduler escalation levels:

    • due
    • remind
    • alert_caregiver

The same image is reused while only the scheduler context changes,
demonstrating that the scheduler controls the escalation and the LLM
generates the appropriate response.

Run:

    python tests/test_llm_engine.py
"""

import base64
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.llm_engine import LLMEngine


def separator():
    print("\n" + "=" * 70)


def load_image(path: Path) -> str:
    """Load an image and return it as a Base64 string."""

    if not path.exists():
        raise FileNotFoundError(path)

    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def print_result(context, result):
    print("Context")

    for key, value in context.items():
        print(f"  {key:<18}: {value}")

    print("\nLLM Response")

    print(f"  Message             : {result.message}")
    print(f"  Visual confirmation : {result.visually_confirmed}")
    print(f"  Confidence          : {result.confidence:.2f}")
    print(f"  Explanation         : {result.explanation}")

    separator()


def main():


    # ---------------------------------------------------------
    # Create LLM
    # ---------------------------------------------------------

    engine = LLMEngine()

    # ---------------------------------------------------------
    # Test scenarios
    # ---------------------------------------------------------

    scenarios = [

        {
            "escalation": "due",
            "compartment": 1,
            "label": "Vitamin D",
            "minutes_overdue": 0,
        },

        {
            "escalation": "remind",
            "compartment": 1,
            "label": "Vitamin D",
            "minutes_overdue": 10,
        },

        {
            "escalation": "alert_caregiver",
            "compartment": 1,
            "label": "Vitamin D",
            "minutes_overdue": 35,
        },

    ]

    # ---------------------------------------------------------
    # Run scenarios
    # ---------------------------------------------------------

    # for context in scenarios:

    #     result = engine.generate_reminder(
    #         context=context,
    #     )
    #     print_result(context, result)
        
    open_compartment_scenario = [ 
    {
        "compartment": 1,
        "open_count": 1,
        "label": "Vitamin D"
    },
        {
        "compartment": 1,
        "open_count": 1,
        "label": "Vitamin D"
    }
    ]
    # ---------------------------------------------------------
    # Load sample image
    # ---------------------------------------------------------

    image_path = PROJECT_ROOT / "assets" / "sample_intake.jpeg"
    image_b64 = load_image(image_path)

    print("\nUsing image:")
    print(image_path)
    
    result = engine.verify_intake(
        context=open_compartment_scenario[0],
        image_b64=image_b64,
    )
    print_result(open_compartment_scenario[0], result)
    
        # ---------------------------------------------------------
    # Load sample image
    # ---------------------------------------------------------

    image_path = PROJECT_ROOT / "assets" / "sample_not_intake.jpeg"
    image_b64 = load_image(image_path)
    
    result = engine.verify_intake(
        context=open_compartment_scenario[1],
        image_b64=image_b64,
    )
    print_result(open_compartment_scenario[1], result)

if __name__ == "__main__":
    main()