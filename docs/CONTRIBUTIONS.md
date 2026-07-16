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
| [Name 1] | [@handle] | Hardware assembly & sensor integration |
| [Name 2] | [@Ppkhanh] | LLM engine, vision verification, prompt engineering |
| [Name 3] | [@Waqar] | Scheduler, SQLite store, caregiver dashboard |
| [Name 4] | [@SusieQ2022] | Demo simulator, tests, documentation |
| [Name 5] | [@handle] | Integration, business model, presentation |

*(Replace placeholders with real names and confirm handles.)*

## Contribution matrix

| Member | Hardware | Code | Report | Presentation |
|--------|----------|------|--------|--------------|
| **[Name 1]** | Lead: wiring speaker, camera, display & reed switch; enclosure assembly | Hardware testing & GPIO validation | Hardware section | Demo operation |
| **[Name 2]** | Support | Lead: `llm_engine.py`, vision intake verification, Ki:connect integration, scheduler/LLM refactor, `main.py` | Reasoning / AI section | AI explanation |
| **[Name 3]** | Support | Lead: `scheduler.py`, `store.py`, `dashboard.py`, caregiver pipeline | Data & escalation section | Business / market |
| **[Name 4]** | Support | Lead: `simulator.py`, test suite, medication schedule logic, documentation | Lead: documentation & report | Technology section |
| **[Name 5]** | Enclosure | Integration & testing support | Lead: business model | Presentation lead |

## Detailed deliverables

### [Name 1] — Hardware
- Wired and tested all physical components: reed switch (GPIO 17), Pi Camera v2, speaker + PAM8403 amplifier, OLED display.
- Validated hardware integration end-to-end on the Raspberry Pi.
- Assembled components into the pill-box enclosure.

### [Name 2] — AI & reasoning
- Integrated the university's Ki:connect API (Mistral) as the reasoning backend.
- Built `verify_intake()` — multimodal vision verification of medication intake.
- Refactored the engine so the scheduler owns escalation and the LLM only phrases messages.
- Restructured `main.py` around the two-line architecture; added the pre-capture prompt + delay.

### [Name 3] — Data & scheduling
- Built `scheduler.py`: fixed medication schedule, overdue calculation, three-level escalation.
- Built `store.py` (SQLite adherence log) and `dashboard.py` (caregiver view).
- Implemented the caregiver notification pipeline.

### [Name 4] — Simulator, tests & docs
- Built `simulator.py` — automated hands-free demo of the full escalation and verification flow, with a deterministic mode so safety-critical behaviour demos reliably.
- Wrote the test suite; fixed fallback tests that were accidentally calling the live LLM, and a syntax error that broke the whole suite.
- Implemented the original medication schedule and overdue calculation (later migrated into `scheduler.py`).
- Wrote and maintained project documentation: README, architecture, installation, contributing, hardware docs.
- Produced the project proposal presentation.

### [Name 5] — Integration & business
- Business Model Canvas, market analysis and financial plan.
- Presentation coordination and delivery.

## Verifying contributions in Git

```bash
git shortlog -sne            # commit count per author
git log --author="Name"      # one member's commits
git log --oneline --graph    # full branch/merge history
```

## Notes

- Update this file as responsibilities evolve.
- Keep commit authorship accurate — it is the primary evidence of who did what.
