from dotenv import load_dotenv
import os
from picamera2 import Picamera2
from openai import OpenAI
import base64

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

picam = Picamera2()
picam.start()

picam.capture_file("image.jpg")

#schedule taking picture every hour
schedule.every().hour.do(capture_and_process)

while True:
    schedule.run_pending()
    time.sleep(1)

with open("image.jpg", "rb") as f:
    image = base64.b64encode(f.read()).decode()

response = client.responses.create(
    model="gpt-4.1-mini",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": (
                        "Verify whether in the photo, a person has taken a pill out and put it in their mouth. "
                        "Answer ONLY with YES or NO."
                    )
                },
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{image_base64}"
                }
            ]
        }
    ]
)

print(response.output_text)
