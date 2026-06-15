<div align="center">

# 💊 SmartMedBox

### AI-Powered Verified Medication Adherence System

*An Embodied AI project — Sense → Reason → Act*

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-Zero%202%20W-C51A4A.svg)](https://www.raspberrypi.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Emerging Electronic Business ·  M.Sc. · University of Cologne**

</div>

---

## 📖 Overview

SmartMedBox is a sensor-enhanced medication box that **verifies whether medication was actually taken** — not just whether a reminder was triggered. It addresses a critical real-world problem: elderly and chronic patients frequently miss or accidentally double-take their medication, a leading cause of preventable hospitalisation.

Unlike existing smart pill boxes that only beep or send notifications, SmartMedBox combines **weight sensing**, **camera-based visual confirmation**, and an **LLM-powered conversational voice assistant** to close the loop between *reminding* and *confirming intake*.

### The Embodied AI Loop

| Stage | Component | Function |
|-------|-----------|----------|
| **SENSE** | Weight sensors (HX711 + load cells) per compartment + camera | Detect exact pill removal; capture visual confirmation |
| **REASON** | LLM (GPT-4o) | Determine: dose missed? taken? double-taken? caregiver alert needed? |
| **ACT** | Speaker + caregiver notification | Conversational voice reminder; real-time family alert |

---

## ✨ Key Features

- **Verified intake** — weight sensors detect removal; camera + GPT-4o Vision confirms the pill was actually taken, solving the core flaw of existing products.
- **Empathetic LLM voice companion** — natural, context-aware spoken reminders instead of generic beeping; multilingual support.
- **Double-take detection** — flags when a compartment is opened more than once, preventing accidental overdose.
- **Caregiver integration** — real-time adherence confirmation and alerts sent to family or care staff.
- **Habit learning** — adapts reminder timing to the user's actual medication patterns.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        SmartMedBox                            │
│                                                               │
│   ┌──────────┐     ┌──────────────┐     ┌────────────────┐   │
│   │  SENSE   │────▶│    REASON    │────▶│      ACT       │   │
│   │          │     │              │     │                │   │
│   │ Weight   │     │  LLM Engine  │     │  Voice (TTS)   │   │
│   │ Camera   │     │  (GPT-4o)    │     │  Caregiver     │   │
│   │ Reed sw. │     │  Vision API  │     │  Notification  │   │
│   └──────────┘     └──────────────┘     └────────────────┘   │
│         │                  │                     │           │
│         └──────────────────┴─────────────────────┘           │
│                     Raspberry Pi Zero 2 W                     │
└─────────────────────────────────────────────────────────────┘
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for a detailed breakdown.

---

## 🚀 Installation

> Full step-by-step setup is in [`docs/INSTALLATION.md`](docs/INSTALLATION.md).

### Quick start

```bash
# 1. Clone the repository
git clone https://github.com/<your-org>/smartmedbox.git
cd smartmedbox

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate          # On Raspberry Pi / Linux / macOS

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your API key and settings
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 5. Run
python src/main.py
```

---

## 📁 Repository Structure

```
smartmedbox/
├── src/                  # Application source code
│   ├── main.py           # Entry point — orchestrates the Sense→Reason→Act loop
│   ├── sensors.py        # Weight, reed switch & motion sensor interface
│   ├── camera.py         # Camera capture + visual confirmation
│   ├── llm_engine.py     # LLM reasoning & conversational logic
│   ├── voice.py          # Text-to-speech output
│   ├── notifier.py       # Caregiver notification (SMS / push)
│   └── config.py         # Configuration loader
├── hardware/             # Wiring diagrams, parts list, enclosure files
├── docs/                 # Architecture, installation, individual contributions
├── tests/                # Unit tests
├── assets/               # Images, demo media
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🛠️ Hardware

See [`hardware/PARTS_LIST.md`](hardware/PARTS_LIST.md) for the full bill of materials and [`hardware/WIRING.md`](hardware/WIRING.md) for wiring instructions.

**Core components:** Raspberry Pi Zero 2 W · HX711 load cells (×4) · Pi Camera Module v2 · Reed switches · Speaker · Microphone · OLED display.

---

## 👥 Team & Individual Contributions

This project is graded individually. Each member contributed across hardware, code, report, and presentation. See [`docs/CONTRIBUTIONS.md`](docs/CONTRIBUTIONS.md) for the detailed breakdown of individual work packages.

| Member | Primary Work Package |
|--------|---------------------|
| [Name 1] | Hardware integration & sensor interface |
| [Name 2] | LLM reasoning engine & prompt engineering |
| [Name 3] | Camera & visual confirmation module |
| [Name 4] | Voice output & caregiver notification |
| [Name 5] | Business model, report & presentation lead |

*(Replace with actual names and finalise once work packages are confirmed.)*

---

## 📄 Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Installation Guide](docs/INSTALLATION.md)
- [Hardware Parts List](hardware/PARTS_LIST.md)
- [Individual Contributions](docs/CONTRIBUTIONS.md)

---

## 📜 License

This project is released under the MIT License — see [`LICENSE`](LICENSE).

---

<div align="center">
<sub>Built for the Emerging Electronic Business course · University of Cologne · 2025/26</sub>
</div>
