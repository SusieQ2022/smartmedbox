<div align="center">

# 💊 SmartMedBox

### AI-Powered Verified Medication Adherence System

*An Embodied AI project — Sense → Reason → Act*

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-Zero%202%20W-C51A4A.svg)](https://www.raspberrypi.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Emerging Electronic Business · Wirtschaftsinformatik M.Sc. · University of Cologne**

</div>

---

## 📖 Overview

SmartMedBox is a sensor-enhanced medication box that **verifies whether medication was actually taken** — not just whether a reminder was triggered. It addresses a real-world problem: elderly and chronic patients frequently miss their medication, a leading cause of preventable hospitalisation.

Existing smart pill boxes only *remind* — they beep or send a notification, but they cannot confirm the pill ever reached the user. SmartMedBox closes that loop by combining a **reed switch**, a **camera**, and a **multimodal LLM** that visually verifies intake and speaks to the user in natural language.

### The Embodied AI Loop

| Stage | Component | Function |
|-------|-----------|----------|
| **SENSE** | Reed switch + Pi camera | Detect the compartment opening; capture an image after a short delay |
| **REASON** | Scheduler + multimodal LLM | Scheduler determines *when* and *how urgently* to act; the LLM verifies intake from the image and phrases the message |
| **ACT** | Speaker + caregiver notifier | Speak a natural reminder or confirmation; alert the caregiver when overdue |

---

## ✨ Key Features

- **Verified intake** — after the box is opened, the system prompts the user, waits, then captures an image. A multimodal LLM confirms whether the pill was actually taken, and explains its reasoning.
- **Deterministic escalation** — a fixed-schedule scheduler drives a clear three-level escalation (`due` → `remind` → `alert_caregiver`). Safety-critical timing never depends on model variability.
- **Empathetic voice** — the LLM generates warm, natural spoken messages instead of a generic beep; the scheduler decides the action, the LLM only phrases it.
- **Caregiver integration** — when a dose stays overdue past the threshold, the caregiver is notified once.
- **Adherence history** — every event is logged to SQLite and surfaced through a caregiver dashboard.
- **Runs without hardware** — a full mock mode lets the entire system run on a laptop for development and demos.

---

## 🏗️ Architecture

```
┌──────────────────────── SmartMedBox (main.py) ────────────────────────┐
│                                                                        │
│   REMINDER LINE                          VERIFICATION LINE             │
│   ┌──────────────┐                       ┌──────────────┐              │
│   │ scheduler.py │                       │ sensors.py   │              │
│   │  fixed times │                       │  reed switch │              │
│   │  escalation  │                       └──────┬───────┘              │
│   └──────┬───────┘                              │ opened               │
│          │ due | remind | alert_caregiver       ▼                      │
│          ▼                               ┌──────────────┐              │
│   ┌──────────────┐                       │ camera.py    │              │
│   │ llm_engine   │                       │  prompt+wait │              │
│   │ generate_    │                       │  capture     │              │
│   │  reminder()  │                       └──────┬───────┘              │
│   └──────┬───────┘                              ▼                      │
│          │                               ┌──────────────┐              │
│          │                               │ llm_engine   │              │
│          │                               │ verify_      │              │
│          │                               │  intake()    │              │
│          │                               └──────┬───────┘              │
│          └───────────────┬──────────────────────┘                      │
│                          ▼                                             │
│              ┌───────────────────────┐                                 │
│              │ voice · notifier      │  ACT                            │
│              │ store (SQLite)        │  + log every event              │
│              └───────────────────────┘                                 │
└────────────────────────────────────────────────────────────────────────┘
                        Raspberry Pi Zero 2 W
```

Two independent lines: the **reminder line** is time-driven and deterministic; the **verification line** is event-driven and vision-based. See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for details.

---

## 🚀 Installation

> Full setup instructions: [`docs/INSTALLATION.md`](docs/INSTALLATION.md)

### Quick start (laptop, no hardware needed)

```bash
git clone https://github.com/<your-org>/smartmedbox.git
cd smartmedbox

python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Add your KICONNECT_API_KEY (optional — without it a rule-based
# fallback keeps the reminder flow fully functional offline).
# Keep HARDWARE_MODE=mock to run on a laptop.

python src/main.py
```

### Interactive commands

| Command | Effect |
|---------|--------|
| `due` | Send the initial reminder |
| `remind` | Send a repeated reminder |
| `alert` | Trigger the caregiver alert |
| `open` | Simulate opening the box → image capture → intake verification |
| `refill` | Reset today's medication |
| `quit` | Exit |

### Automated demo

```bash
python src/simulator.py
```

Plays the full scenario hands-free: escalation from `due` → `remind` → `alert_caregiver`, followed by intake verification on a "taken" and a "not taken" image.

### Tests

```bash
python -m pytest tests/ -v
```

---

## 📁 Repository Structure

```
smartmedbox/
├── src/
│   ├── main.py           # Entry point — orchestrates Sense → Reason → Act
│   ├── sensors.py        # Reed switch interface (GPIO 17) + mock helpers
│   ├── scheduler.py      # Fixed medication schedule & escalation engine
│   ├── camera.py         # Image capture + base64 encoding
│   ├── llm_engine.py     # Reminder phrasing + vision intake verification
│   ├── voice.py          # Text-to-speech output
│   ├── notifier.py       # Caregiver notification
│   ├── store.py          # SQLite adherence event store
│   ├── dashboard.py      # Caregiver dashboard rendering
│   ├── simulator.py      # Automated end-to-end demo
│   └── config.py         # Configuration loader
├── hardware/             # Parts list & wiring guide
├── docs/                 # Architecture, installation, contributions
├── tests/                # Automated tests
├── assets/               # Sample images for vision verification
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🛠️ Hardware

See [`hardware/PARTS_LIST.md`](hardware/PARTS_LIST.md) for the bill of materials and [`hardware/WIRING.md`](hardware/WIRING.md) for wiring.

**Core components:** Raspberry Pi Zero 2 W · Magnetic reed switch (GPIO 17) · Pi Camera Module v2 · Speaker + PAM8403 amplifier · OLED display · Status LEDs.

> **Note:** the project originally explored load-cell weight sensing. This was dropped in favour of a focused reed-switch + camera approach — see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md#design-decisions).

---

## 👥 Team & Individual Contributions

This project is graded individually. Every member contributed across hardware, code, report and presentation — see [`docs/CONTRIBUTIONS.md`](docs/CONTRIBUTIONS.md) for the detailed breakdown of work packages.

| Member | Primary Work Package |
|--------|---------------------|
| [Name 1] | Hardware assembly & sensor wiring |
| [Name 2] | LLM engine, vision verification & prompt engineering |
| [Name 3] | Scheduler, SQLite store & caregiver dashboard |
| [Name 4] | Demo simulator, tests & documentation |
| [Name 5] | Integration, business model & presentation |

*(Replace placeholders with actual names.)*

---

## 📄 Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Installation Guide](docs/INSTALLATION.md)
- [Hardware Parts List](hardware/PARTS_LIST.md)
- [Wiring Guide](hardware/WIRING.md)
- [Individual Contributions](docs/CONTRIBUTIONS.md)
- [Contributing Guide](CONTRIBUTING.md)

---

## 📜 License

Released under the MIT License — see [`LICENSE`](LICENSE).

---

<div align="center">
<sub>Built for the Emerging Electronic Business course · University of Cologne · 2025/26</sub>
</div>
