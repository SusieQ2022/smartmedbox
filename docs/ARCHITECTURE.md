# Architecture

SmartMedBox follows the **Embodied AI loop**: every action flows through three
stages — Sense, Reason, Act — coordinated by a single controller running on a
Raspberry Pi Zero 2 W.

## High-level flow

```
   ┌──────────────────────── SmartMedBox controller (main.py) ────────────────────────┐
   │                                                                                   │
   │   SENSE                      REASON                       ACT                      │
   │   ┌─────────────┐            ┌──────────────┐             ┌────────────────────┐   │
   │   │ sensors.py  │            │ llm_engine.py│             │ voice.py           │   │
   │   │  weight     │───state───▶│  GPT-4o      │───decision─▶│  speaks reminder   │   │
   │   │  reed switch│            │  reasoning   │             │                    │   │
   │   ├─────────────┤            │              │             ├────────────────────┤   │
   │   │ camera.py   │───image───▶│  GPT-4o      │             │ notifier.py        │   │
   │   │  capture    │            │  Vision      │             │  caregiver alert   │   │
   │   └─────────────┘            └──────────────┘             └────────────────────┘   │
   │                                                                                   │
   └───────────────────────────────────────────────────────────────────────────────────┘
```

## Module responsibilities

| Module | Stage | Responsibility |
|--------|-------|----------------|
| `config.py` | — | Loads all settings from `.env`; defines mock vs. real mode. |
| `sensors.py` | SENSE | Reads weight per compartment and tracks open counts. |
| `camera.py` | SENSE | Captures a confirmation image and encodes it for the vision model. |
| `llm_engine.py` | REASON | Decides the action and crafts the spoken message; vision-confirms intake. Falls back to deterministic rules offline. |
| `voice.py` | ACT | Speaks the message via offline TTS. |
| `notifier.py` | ACT | Sends caregiver SMS alerts via Twilio. |
| `main.py` | — | Wires everything together and runs the loop. |

## Design decisions

**Mock mode.** Every hardware-touching module has a `mock` path that activates
when `HARDWARE_MODE=mock`. This lets the entire system run on a laptop, which
makes development, testing, and demo rehearsal possible without the physical box.

**Graceful degradation.** If the LLM API is unavailable (no key, or network
failure), `llm_engine.py` falls back to a clear rule-based decision function.
The system stays fully functional offline — important for a medical device.

**Separation of Sense / Reason / Act.** Each stage is an independent module
with a narrow interface. This keeps the code testable (the reasoning logic is
unit-tested in isolation) and maps directly onto the course's Embodied AI
paradigm.

**Verified intake.** The combination of weight sensing (`sensors.py`) and
camera confirmation (`camera.py` + vision in `llm_engine.py`) is the core
innovation: the system confirms a pill was *taken*, not merely *removed*.

## Data flow per cycle

1. `main.handle_compartment()` reads the compartment state from `sensors`.
2. If the dose appears gone, `camera` captures an image and `llm_engine`
   visually confirms intake.
3. `llm_engine.reason()` returns a structured `Decision`.
4. `voice` speaks the message; if flagged, `notifier` alerts the caregiver.
