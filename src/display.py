"""
display.py - OLED display output for SmartMedBox.
"""

class OLEDDisplay:
    def __init__(self):
        try:
            import board
            import busio
            from PIL import Image, ImageDraw
            import adafruit_ssd1306

            self.Image = Image
            self.ImageDraw = ImageDraw

            i2c = busio.I2C(board.SCL, board.SDA)
            self.oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)
            self.available = True
            self.clear()
        except Exception as e:
            print(f"[display] OLED unavailable: {e}")
            self.available = False

    def clear(self):
        if not self.available:
            return
        self.oled.fill(0)
        self.oled.show()

    def show_message(self, line1="", line2="", line3=""):
        if not self.available:
            return

        image = self.Image.new("1", (128, 64))
        draw = self.ImageDraw.Draw(image)

        draw.text((0, 0), str(line1)[:21], fill=255)
        draw.text((0, 20), str(line2)[:21], fill=255)
        draw.text((0, 40), str(line3)[:21], fill=255)

        self.oled.image(image)
        self.oled.show()
