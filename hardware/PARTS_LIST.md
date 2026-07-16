# Hardware Parts List (Bill of Materials)

Components used in the SmartMedBox prototype. **Status** reflects what was
already available in the lab versus what was ordered.

---

## Core components

| # | Component | Qty | Purpose | Status |
|---|-----------|-----|---------|--------|
| 1 | Raspberry Pi Zero 2 W | 1 | Main controller | Have |
| 2 | Magnetic reed switch (module) | 4 | Compartment open/close detection — the primary sensor | Ordered by supervisor |
| 3 | Raspberry Pi Camera Module v2 | 1 | Visual intake verification | Order |
| 4 | HC-SR501 PIR motion sensor | 1 | Optional: detect user presence | Have |
| 5 | Small speaker (3 W, 8 Ω) | 1 | Voice output | Order |
| 6 | PAM8403 mini amplifier module | 1 | Drives the speaker | Order |
| 7 | Microphone module (MAX9814) | 1 | Optional: future voice input | Order |
| 8 | OLED display (128×64, I2C, SSD1306) | 1 | Large-text visual prompts | Have |
| 9 | Green LEDs | 4 | Per-compartment "OK" status | Order |
| 10 | Red LEDs | 4 | Per-compartment "due / missed" status | Order |
| 11 | 220 Ω resistors | 8 | LED current limiting | Have |
| 12 | Tactile push buttons | 4 | Manual confirm / snooze | Order |
| 13 | 4-compartment pill organizer box | 1 | Enclosure | Order |

## Power, prototyping & consumables

| # | Component | Qty | Purpose | Status |
|---|-----------|-----|---------|--------|
| 14 | MicroSD card (32 GB) | 1 | OS + application storage | Have |
| 15 | Micro USB power supply (5 V 2.5 A) | 1 | Power | Have |
| 16 | Breadboard + jumper wires (F-F, M-F) | 1 set | Prototyping | Have |
| 17 | Assorted resistor kit | 1 | Spares | Have |
| 18 | Heat shrink tubing / electrical tape / mounting pads | 1 set | Insulating joints, securing wires, mounting components in the box | Order |

**Estimated prototype cost: ~€90.**

---

## Dropped: weight sensing

The original concept placed the pill box on 1–2 load cells and inferred pill
removal from weight change. This was **dropped** for two reasons:

1. No sufficiently sensitive, reliably sourceable load cell was found, and the
   supervisor advised narrowing the project's scope.
2. More fundamentally, a weight drop only proves a pill *left the box* — not
   that it was *taken*. The reed switch + camera approach answers the question
   that actually matters.

The HX711 amplifier and load cell are therefore **not part of the build**.

---

## Component links (reference)

| Component | Link |
|-----------|------|
| Magnetic reed switch module | https://amzn.eu/d/0cyvKbSd |
| HC-SR501 PIR motion sensor | https://www.az-delivery.de/en/products/hc-sr501-bewegungsmelder |
| Raspberry Pi Camera Module v2 | https://www.raspberrypi.com/products/camera-module-v2/ |
| 3 W 8 Ω speaker | https://www.amazon.de/s?k=3w+8ohm+speaker |
| PAM8403 mini amplifier | https://www.amazon.de/s?k=PAM8403 |
| MAX9814 microphone module | https://www.amazon.de/s?k=MAX9814 |
| OLED display 128×64 I2C (SSD1306) | https://www.az-delivery.de/en/products/0-96zolldisplay |
| LEDs (red / green) | https://www.amazon.de/s?k=5mm+led+kit |
| 220 Ω resistors | https://www.amazon.de/s?k=220+ohm+resistor |
| Tactile push buttons | https://www.amazon.de/s?k=tactile+push+button+switch |
| MicroSD card 32 GB | https://www.amazon.de/s?k=32gb+microsd+card |
| 5 V 2.5 A micro USB power supply | https://www.amazon.de/s?k=5v+2.5a+micro+usb+power+supply |
| Breadboard + jumper wires | https://www.amazon.de/s?k=breadboard+jumper+wire+kit |
| Assorted resistor kit | https://www.amazon.de/s?k=resistor+kit |
| Heat shrink tubing / electrical tape | https://www.amazon.de/s?k=heat+shrink+tubing |
| 4-compartment pill organizer box | https://amzn.eu/d/0cFSgsuD |

---

## Clarifications

**Magnetic reed switch** — the magnetic sensor that detects whether a
compartment lid is open or closed. A magnet on the lid, the switch on the body;
each open/close registers an event. This is the primary trigger for the
verification flow. Currently wired to **GPIO 17**.

**Push buttons ("actual electronic buttons")** — standard tactile momentary
push-button switches (the small 4-pin breadboard type), as opposed to any
decorative buttons on the pill box itself.

**Heat shrink tubing / tape / mounting pads** — used to insulate soldered
joints, bundle loose wires, and mount the boards, camera and speaker securely
inside the enclosure.
