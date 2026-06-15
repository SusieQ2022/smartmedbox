# Hardware Parts List (Bill of Materials)

Bill of materials for the SmartMedBox prototype. The **Status** column reflects
what is already available in the lab versus what needs to be ordered, based on
the team's component review.

> **Note on the weight sensor:** After review, the load-cell-based weighing
> approach is currently **on hold**. A suitable, sufficiently sensitive scale
> could not be sourced reliably, and the supervisor advised narrowing the
> project's scope to focus on the core verified-intake loop (reed switch +
> camera + LLM) rather than weighing. The load cell and HX711 are kept in the
> list as **optional**, should we revisit weighing later.

---

## Core components

| # | Component | Qty | Purpose | Status |
|---|-----------|-----|---------|--------|
| 1 | Raspberry Pi Zero 2 W | 1 | Main controller | Have |
| 2 | Raspberry Pi Camera Module v2 | 1 | Visual intake confirmation | Order |
| 3 | Magnetic Reed Switch (module) | 4 | Compartment open/close detection | Ordered by supervisor |
| 4 | HC-SR501 PIR Motion Sensor | 1 | Detect user presence (proactive greeting) | Have |
| 5 | Small Speaker (3 W, 8 Ω) | 1 | Voice output | Order |
| 6 | PAM8403 Mini Amplifier Module | 1 | Drives the speaker from the Pi | Order |
| 7 | Microphone Module (MAX9814) | 1 | Voice dialogue input | Order |
| 8 | OLED Display (128×64, I2C, SSD1306) | 1 | Large-text visual prompts | Have (likely) |
| 9 | Green LEDs | 4 | Per-compartment "OK" status | Order |
| 10 | Red LEDs | 4 | Per-compartment "due / missed" status | Order |
| 11 | 220 Ω Resistors | 8 | Current limiting for LEDs | Have |
| 12 | Tactile Push Buttons | 4 | Manual confirm / snooze input | Order |
| 13 | 4-Compartment Pill Organizer Box | 1 | Housing | Order |

## Power, prototyping & consumables

| # | Component | Qty | Purpose | Status |
|---|-----------|-----|---------|--------|
| 14 | MicroSD Card (32 GB) | 1 | OS + application storage | Have |
| 15 | Micro USB Power Supply (5 V 2.5 A) | 1 | Power | Have |
| 16 | Breadboard + Jumper Wires (F-F and M-F) | 1 set | Prototyping wiring | Have |
| 17 | Assorted Resistor Kit | 1 | Spare resistors for prototyping | Have |
| 18 | Heat Shrink Tubing / Electrical Tape / Mounting Pads | 1 set | Insulating solder joints, securing wires, mounting sensors in the box | Order |

## Optional — weight sensing (on hold)

| # | Component | Qty | Purpose | Status |
|---|-----------|-----|---------|--------|
| 19 | HX711 Load Cell Amplifier | 1–2 | Read load cell(s) | Optional |
| 20 | Load Cell (100 g, e.g. SparkFun TAL221) | 1–2 | Measure total box weight | Optional |

---

## Component links (reference)

| Component | Link |
|-----------|------|
| HX711 Load Cell Amplifier | https://www.az-delivery.de/en/products/hx711-load-cell-amplifier |
| HX711 (alt.) | https://amzn.eu/d/09gGtB2q |
| Load Cell (100 g) | https://eckstein-shop.de/SparkFunMiniLoadCell-100g2CStraightBarTAL221EN |
| Load Cell (alt.) | https://amzn.eu/d/03NWwoA5 |
| Magnetic Reed Switch Module | https://amzn.eu/d/0cyvKbSd |
| HC-SR501 PIR Motion Sensor | https://www.az-delivery.de/en/products/hc-sr501-bewegungsmelder |
| PIR Motion Sensor (alt.) | https://amzn.eu/d/0837LtCk |
| Raspberry Pi Camera Module v2 | https://www.raspberrypi.com/products/camera-module-v2/ |
| 3 W 8 Ω Speaker | https://www.amazon.de/s?k=3w+8ohm+speaker |
| PAM8403 Mini Amplifier | https://www.amazon.de/s?k=PAM8403 |
| MAX9814 Microphone Module | https://www.amazon.de/s?k=MAX9814 |
| OLED Display 128×64 I2C (SSD1306) | https://www.az-delivery.de/en/products/0-96zolldisplay |
| LEDs (Red / Green) | https://www.amazon.de/s?k=5mm+led+kit |
| 220 Ω Resistors | https://www.amazon.de/s?k=220+ohm+resistor |
| Tactile Push Buttons | https://www.amazon.de/s?k=tactile+push+button+switch |
| MicroSD Card 32 GB | https://www.amazon.de/s?k=32gb+microsd+card |
| 5 V 2.5 A Micro USB Power Supply | https://www.amazon.de/s?k=5v+2.5a+micro+usb+power+supply |
| Breadboard + Jumper Wires | https://www.amazon.de/s?k=breadboard+jumper+wire+kit |
| Assorted Resistor Kit | https://www.amazon.de/s?k=resistor+kit |
| Heat Shrink Tubing / Electrical Tape | https://www.amazon.de/s?k=heat+shrink+tubing |
| 4-Compartment Pill Organizer Box | https://amzn.eu/d/0cFSgsuD |

---

## Clarifications on specific components

**Magnetic reed switches** — Yes, these are the magnetic sensors used to detect
whether a compartment lid is opened or closed. A small magnet sits on the lid;
the reed switch on the body registers each open/close event. These are the
primary trigger for the "compartment accessed" signal.

**Push buttons ("actual electronic buttons")** — This refers to standard
tactile push-button switches (the small 4-pin momentary buttons used on
breadboards), as opposed to the painted/decorative buttons on a physical pill
box. They let the user manually confirm a dose or snooze a reminder.

**Heat shrink tubing / electrical tape / mounting pads** — Used to insulate
soldered joints, bundle and secure loose wires inside the enclosure, and mount
the sensors, camera, and boards neatly inside the pill box so nothing rattles
loose during the demo.

**Weight sensing approach (on hold)** — The original idea was to place the pill
box on 1–2 load cells measuring total weight continuously; when a reed switch
detects an opening, the system compares weight before and after to infer pill
removal. A 100 g load cell would give the needed sensitivity. However, since a
reliable scale could not be sourced and the supervisor recommended narrowing
scope, the current prototype relies on **reed switch + camera + LLM** for
verified intake instead of weighing.

---

> Components already in the lab are marked "Have". Confirm availability with the
> supervisor before ordering anything marked "Order".