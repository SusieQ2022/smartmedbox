# Architecture

SmartMedBox follows the **Embodied AI loop** — Sense → Reason → Act — running on a
single Raspberry Pi Zero 2 W. The system is organised around **two independent
lines** that meet in the Act stage.

## The two lines

### 1. Reminder line (time-driven, deterministic)

```
scheduler.py            llm_engine.py           voice.py / notifier.py
┌────────────┐          ┌──────────────┐        ┌─────────────────┐
│ fixed      │ escalat. │ generate_    │ text   │ speak message   │
│ schedule   │─────────▶│  reminder()  │───────▶│ alert caregiver │
│ + timing   │  due |   │              │        │ log to store    │
└────────────┘  remind| └──────────────┘        └─────────────────┘
                alert_caregiver
```

The **scheduler decides the action**; the LLM only phrases it. This separation is
deliberate — see [Design decisions](#design-decisions).

### 2. Verification line (event-driven, vision-based)

```
sensors.py        camera.py              llm_engine.py         voice / store
┌──────────┐      ┌───────────────┐      ┌──────────────┐      ┌───────────┐
│ reed     │ open │ prompt user   │ img  │ verify_      │ bool │ confirm / │
│ switch   │─────▶│ wait 5s       │─────▶│  intake()    │─────▶│ retry     │
│ GPIO 17  │      │ capture       │      │  (multimodal)│      │ + log     │
└──────────┘      └───────────────┘      └──────────────┘      └───────────┘
```

When intake is visually confirmed, the dose is marked complete in the scheduler,
which stops any further reminders for that dose today.

## Module responsibilities

| Module | Stage | Responsibility |
|--------|-------|----------------|
| `config.py` | — | Loads settings from `.env`; defines mock vs. real hardware mode. |
| `sensors.py` | SENSE | Reed switch interface on GPIO 17 (interrupt-driven); `poll()` returns newly opened compartments. Provides mock helpers for laptop development. |
| `camera.py` | SENSE | Captures an image after the user prompt and encodes it for the vision model. |
| `scheduler.py` | REASON | Holds the fixed medication schedule; computes overdue minutes and the escalation level (`due` / `remind` / `alert_caregiver`); tracks completed doses. |
| `llm_engine.py` | REASON | `generate_reminder()` phrases a message for a given escalation level; `verify_intake()` performs multimodal vision verification. Falls back to deterministic messages when the API is unavailable. |
| `voice.py` | ACT | Speaks messages via text-to-speech. |
| `notifier.py` | ACT | Sends caregiver alerts. |
| `store.py` | ACT | Logs every event to SQLite (adherence history). |
| `dashboard.py` | — | Renders caregiver-facing summaries from the store. |
| `simulator.py` | — | Automated end-to-end demo of both lines. |
| `main.py` | — | Wires everything together; interactive mock mode and hardware loop. |

## Escalation logic

Managed entirely by `scheduler.py`, keyed on `(date, compartment, scheduled_hour)`:

| Level | Trigger | Action |
|-------|---------|--------|
| `due` | Dose is overdue and no reminder sent yet today | First friendly reminder |
| `remind` | `reminder_interval_min` elapsed since the last reminder | Repeated, slightly more urgent reminder |
| `alert_caregiver` | Overdue ≥ 30 min, fired once per dose | Caregiver notification |

A dose marked complete via `mark_completed()` produces no further events that day.

## Data flow per cycle (hardware mode)

1. `main.run()` polls `sensors.poll()` for newly opened compartments.
2. `scheduler.due_events()` yields any doses needing a reminder → `process_scheduler_event()` phrases and speaks it, alerting the caregiver if escalated.
3. For each opened compartment → `process_compartment_open()`: prompt the user, wait, capture, verify with the vision model, mark complete if confirmed.
4. Every event is logged to SQLite.

## Design decisions

**Scheduler decides, LLM phrases.**
Early testing showed the live model would sometimes return `remind` for a dose
overdue by 45 minutes, silently skipping the caregiver alert. Safety-critical
timing must not depend on model variability, so escalation moved entirely into
the scheduler. The LLM's role is what it is genuinely good at: warm, natural,
multilingual phrasing.

**Delay before capture.**
Capturing at the instant the box opens would only ever photograph the lid being
lifted — never the intake itself. The system therefore prompts the user aloud,
waits, and only then captures, so the image can actually show the pill reaching
the mouth.

**Weight sensing dropped.**
The original concept placed the box on load cells to infer pill removal from
weight change. No sufficiently sensitive, reliably sourceable load cell was
available, and the supervisor advised narrowing scope. Weight was removed in
favour of reed switch + camera — which also solves a problem weighing never
could: a weight drop proves a pill *left the box*, not that it was *taken*.

**Graceful degradation.**
Without an API key, `generate_reminder()` returns deterministic messages, so the
reminder flow stays fully functional offline. Vision verification requires the
model and reports honestly when unavailable rather than assuming a dose was taken.

**Mock mode.**
Every hardware-touching module has a mock path (`HARDWARE_MODE=mock`), letting
the whole system run on a laptop for development, testing and demo rehearsal.

## Known limitations

- One reed switch is wired (GPIO 17), mapped to compartment 0; additional compartments need one pin each.
- Vision verification depends on adequate lighting and the user following the spoken prompt.
- Double-dose detection is not implemented — reliably distinguishing "opened twice" from "took a second pill" needs intake state, not just open count.
- Caregiver alerts are SMS-only.
