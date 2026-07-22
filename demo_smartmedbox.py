import subprocess
import time
from pathlib import Path

from src.display import OLEDDisplay
from src.camera import Camera
from src.voice import Voice

display = OLEDDisplay()
camera = Camera()
voice = Voice()

display.show_message("SmartMedBox", "Demo Ready", "Open box")
voice.mock = False

input("Press Enter when reed switch / box is opened...")

display.show_message("SmartMedBox", "Box Opened", "Capturing...")
image_path = camera.capture()
print("Captured image:", image_path)

display.show_message("SmartMedBox", "AI Checking", "Please wait")
time.sleep(1)

message = "Please take your medicine."
display.show_message("SmartMedBox", "Reminder", "Take medicine")
voice.speak(message)

print("Recording microphone for 5 seconds...")
display.show_message("SmartMedBox", "Listening", "Speak now")

subprocess.run([
    "arecord", "-D", "plughw:1,0",
    "-f", "S32_LE",
    "-r", "48000",
    "-c", "1",
    "-d", "5",
    "demo_voice.wav"
])

display.show_message("SmartMedBox", "Demo Done", "Thank you")
print("Voice saved as demo_voice.wav")
print("Demo complete.")
