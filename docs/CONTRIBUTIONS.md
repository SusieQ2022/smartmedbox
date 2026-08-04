# Individual Contributions

> This project is graded **individually**. Every member contributed across all
> four aspects (hardware, code, report, presentation); the tables below record
> each member's **primary** work package and concrete deliverables.
>
> The Git history is the primary evidence — each member committed their own work
> under their own account.

## Work package ownership

| Member | GitHub | Primary focus |
|--------|--------|---------------|
| Shuzhen Liu | [@SusieQ2022] | Demo simulator, tests, documentation |
| [Name 1] | [@handle] | Hardware assembly & sensor integration |
| [Name 2] | [@Ppkhanh] | LLM engine, vision verification, prompt engineering |
| [Name 3] | [@Waqar] | Scheduler, SQLite store, caregiver dashboard |
| [Name 5] | [@handle] | Integration, business model, presentation |

*(Replace placeholders with real names and confirm handles.)*

## Contribution matrix

| Member | Hardware | Code | Report | Presentation |
|--------|----------|------|--------|--------------|
| **Shuzhen Liu** | Support | Lead: `simulator.py`, test suite, mock-mode restoration, medication schedule logic, documentation | Lead: documentation & report | Lead: first-version slides & Technology section |
| **[Name 1]** | Lead: wiring speaker, camera, display & reed switch; enclosure assembly | Hardware testing & GPIO validation | Hardware section | Demo operation |
| **[Name 2]** | Support | Lead: `llm_engine.py`, vision intake verification, Ki:connect integration, scheduler/LLM refactor, `main.py` | Reasoning / AI section | AI explanation |
| **[Name 3]** | Support | Lead: `scheduler.py`, `store.py`, `dashboard.py`, caregiver pipeline | Data & escalation section | Business / market |
| **[Name 4]** | Enclosure | Integration & testing support | Lead: business model | Presentation lead |

## Detailed deliverables

### Shuzhen Liu — Simulator, tests & documentation
- Built `simulator.py` — automated hands-free demo of the full escalation and
  verification flow, with a deterministic mode so safety-critical behaviours
  (caregiver alert) demo reliably without live LLM variability; rewrote it after
  the scheduler/LLM refactor to match the new two-line architecture.
- Wrote and maintained the test suite; fixed fallback tests that were accidentally
  calling the live LLM instead of the rule-based path; fixed a syntax error that
  broke the entire suite; cleaned up and updated tests after the architecture
  refactor (removed tests for deleted APIs, updated scheduler tests to match new
  behaviour) — 21 tests passing.
- Implemented the original medication schedule and overdue calculation in
  `sensors.py` (later migrated into `scheduler.py` during the refactor).
- Restored mock mode after hardware integration broke laptop execution — moved
  `RPi.GPIO`, `luma` and `picamera2` imports to lazy hardware-only paths so the
  full application runs on any laptop without a Raspberry Pi attached.
- Wrote and maintained all project documentation: `README.md`, `ARCHITECTURE.md`,
  `INSTALLATION.md` (mock + hardware modes, dashboard usage), `CONTRIBUTING.md`,
  `WIRING.md`, `PARTS_LIST.md`, `CONTRIBUTIONS.md`.
- Produced the first-version slide decks for the proposal presentation, business
  plan presentation and final presentation, then distributed sections to teammates
  to adapt their own parts.
- Presentation: technology section (architecture + stack).
- Hardware: support.

### [Name 1] — Hardware
- Wired and tested all physical components: reed switch (GPIO 17), Pi Camera v2, speaker + PAM8403 amplifier, OLED display.
- Validated hardware integration end-to-end on the Raspberry Pi.
- Assembled components into the pill-box enclosure.

### [Name 2] — AI & reasoning
- Integrated the university's Ki:connect API (Mistral) as the reasoning backend.
- Built `verify_intake()` — multimodal vision verification of medication intake.
- Refactored the engine so the scheduler owns escalation and the LLM only phrases messages.
- Restructured `main.py` around the two-line architecture; added the pre-capture prompt + delay.

### [Name 4] — Integration & business
- Business Model Canvas
- Presentation coordination and delivery.

### [Waqar Khowaja] — Caregiver data, scheduling safety, Business Model (Market Sizing, Positioning,  Financial Planning)
- Designed and implemented the original `scheduler.py`: fixed medication
  scheduling, overdue calculation and deterministic escalation from `due` to
  `remind` to `alert_caregiver`.
- Built `store.py`, the SQLite adherence-data layer used to record medication
  events, reminders, verification outcomes, overdue duration and caregiver
  alerts. 
- Built the original `dashboard.py`: a lightweight standard-library caregiver
  dashboard showing adherence history, Taken/Late/Missed/Unverified metrics,
  alert status and LLM-generated messages. Added automatic refresh, responsive
  phone layouts and network access from another device on the Pi's local
  network. Maheen later improved and deployed that.
- Integrated and stabilized the caregiver pipeline across `main.py`,
  `config.py`, `store.py`, `dashboard.py` and the simulator. Introduced a shared
  database configuration, aligned the event vocabulary
  (`due`, `remind`, `alert_caregiver`, `confirmed`,
  `verification_failed`) and ensured simulator fallback events also populate
  the dashboard.
- Owned the business-viability analysis: developed the unit economics, pricing
  and revenue model, production-scale cost assumptions and three-year financial
  projection, including the device, consumer subscription and B2B caregiver
  dashboard revenue streams.
- Conducted German care-market sizing and competitor benchmarking, positioning
  SmartMedBox between basic reminder products and expensive
  subscription-locked dispensers. Pressure-tested component, API and scaling
  assumptions against the actual prototype parts list.
- Detailed Financial Planning and three year plan.
- Presentation: financial projections and viability, subscription assumptions and at-scale component costs, key activities and revenue stream.
  


## Verifying contributions in Git

```bash
git shortlog -sne            # commit count per author
git log --author="Name"      # one member's commits
git log --oneline --graph    # full branch/merge history
```

## Notes

- Replace all `[Name X]` and `[@handle]` placeholders with real names before submission.
- Keep commit authorship accurate — it is the primary evidence of who did what.
