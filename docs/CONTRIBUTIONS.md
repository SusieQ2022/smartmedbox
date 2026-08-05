# Individual Contributions

> This project is graded **individually**. Every member contributed across all
> four aspects (hardware, code, report, presentation); the tables below record
> each member's **primary** work package and concrete deliverables.
>
> The Git history is the primary evidence — each member committed their own work
> under their own account.

## Contribution matrix

| Member | Hardware | Code | Report | Presentation |
|--------|----------|------|--------|--------------|
| **Shuzhen Liu** | Support | Repo setup & scaffolding; `simulator.py`; full test suite; mock-mode restoration (dual mock/hardware support); medication scheduling logic | Lead: all documentation & first draft of the report; Sections 1, 2, 8 | Lead: first-version decks for all three presentations; Technology section |
| **Angela Yunjie Feng** | Lead: enclosure design & build (drilling, soldering), sensor co-wiring (reed switch, camera, OLED), Pi environment setup (SD card flashing, SSH, venv, Git deployment) | Lead: display module rewrite (Luma library), sensor code updates, dependency fixes (`requirements.txt`), boot-stage logging, end-to-end integration for demo | Sections 3.1 & 3.5 | Live demo troubleshooting & hardware fault resolution |
| **Maheen Muhammad Sohail** | Hardware construction and integration: Built and assembled the SmartMedBox prototype using the Raspberry Pi Zero W, reed switch, camera, speaker and amplifier, OLED display, breadboard, enclosure, and associated wiring. Tested the physical connections and supported troubleshooting of the camera, GPIO components, audio output, power, and network connectivity. | Deployment and end-to-end integration: Prepared and configured the microSD card and Raspberry Pi environment, deployed and synchronised the Git repository, installed the required dependencies, and launched the application and dashboard services. Integrated and tested the complete workflow from compartment opening and timed image capture to multimodal AI verification, voice feedback, SQLite logging, and caregiver-dashboard updates. The contribution focused on deployment, configuration, troubleshooting, and system integration rather than primary development of the core software modules. | Technical report authorship: Authored Sections 3.2 Architecture, 3.3 Technology Stack and Third-Party Tools, and 3.4 Key Challenges and How We Solved Them. Added and formatted the architecture figure, dashboard screenshot, hardware photograph, tables, captions, and prompt appendix references. Also contributed to shortening, proofreading, formatting, consistency checking, and final report revisions. | Presentation development and live demonstration: Developed and refined the Value Proposition, Customer Segments, Channels, Customer Relationships, Key Challenges and Limitations, Conclusion, and Next Steps sections. Improved slide structure and visual consistency, prepared speaking scripts and demonstration material, and presented the working SmartMedBox and caregiver dashboard during the final live demonstration. |
| **[Name 3]** | Support | Lead: `scheduler.py`, `store.py`, `dashboard.py`, caregiver pipeline | Data & escalation section | Business / market |
| **[Name 4]** | Enclosure | Integration & testing support | Lead: business model | Presentation lead |

## Detailed deliverables

### Shuzhen Liu — Software development, Repository architecture, simulator & testing, mock-mode restoration, documentation
- Set up the initial repository and project scaffolding (structure, config, base modules, git setup).
- Built `simulator.py`: automated hands-free demo of the full escalation and
  verification flow, with a deterministic mode so safety-critical behaviours
  (caregiver alert) demo reliably without live LLM variability; rewrote it after
  the scheduler/LLM refactor to match the new two-line architecture.
- Wrote and maintained the test suite; fixed fallback tests that were accidentally
  calling the live LLM instead of the rule-based path; fixed a syntax error that
  broke the entire suite; cleaned up and updated tests after the architecture
  refactor (removed tests for deleted APIs, updated scheduler tests to match new
  behaviour): 21 tests passing.
- Implemented the original medication schedule and overdue calculation in
  `sensors.py` (later migrated into `scheduler.py` during the refactor).
- Restored mock mode after hardware integration broke laptop execution: moved
  `RPi.GPIO`, `luma` and `picamera2` imports to lazy hardware-only paths so the
  full application runs on any laptop without a Raspberry Pi attached.
- Wrote and maintained all project documentation: `README.md`, `ARCHITECTURE.md`,
  `INSTALLATION.md` (mock + hardware modes, dashboard usage), `CONTRIBUTING.md`,
  `WIRING.md`, `PARTS_LIST.md`, `CONTRIBUTIONS.md`.
- Produced the first-version slide decks for the proposal presentation, business
  plan presentation and final presentation, then distributed sections to teammates
  to adapt their own parts.
- Presentation: technology section (architecture + stack).
- Final Report: authored the first draft; Sections 1, 2 and 8.
- Hardware: support.

### Maheen Muhammad Sohail - Detailed Contribution
- Hardware and prototype integration: Built and tested the SmartMedBox hardware using the Raspberry Pi Zero W, reed switch, camera, speaker and amplifier, OLED display, breadboard, enclosure, and wiring.
- Raspberry Pi and Git deployment: Prepared the microSD card, configured the Raspberry Pi environment, installed the required dependencies, and deployed and synchronised the team’s Git repository on the device.
- Dashboard and system integration: Brought the complete sensor-to-dashboard workflow into operation, including image capture, multimodal AI verification, voice feedback, SQLite event logging, and caregiver-dashboard updates.
- Testing, troubleshooting, and demonstration: Tested confirmed and unverified intake scenarios, resolved hardware, camera, audio, database, network, and dashboard-access issues, and prepared the working prototype for the final live demonstration.
- Technical report: Authored Sections 3.2 Architecture, 3.3 Technology Stack and Third-Party Tools, and 3.4 Key Challenges and How We Solved Them. Also contributed figures, tables, captions, prompt appendices, formatting, proofreading, and chapter shortening.
- Presentation and project showcase: Developed and refined the value proposition, customer segments, channels, customer relationships, challenges, limitations, conclusion, and future roadmap. Prepared speaking scripts, demonstration material, videos, dashboard recordings, photographs, and social-media content.

### Angela Yunjie Feng — Hardware
- Co-wired all sensor components to the Raspberry Pi Zero 2 W, including the reed switch (GPIO 17), camera module, and OLED display
- Solely designed and assembled the physical enclosure: selected a clear box to protect the camera and screen inside, drilled mounting holes for the speaker and microphone, and soldered the reed switch into position
- Assembled all hardware components into the final integrated prototype
- Flashed the microSD card and established the SSH connection via terminal
- Created the Python virtual environment and ensured all packages from requirements.txt installed correctly within the venv
- Connected the device to the team's Git repository
- Rewrote the display module by integrating the Luma screen library
- Updated sensor connection code for hardware compatibility
- Resolved dependency issues across the codebase, including adding the required packages to requirements.txt
- Added console-level loading indicators for each boot stage to support systematic testing
- Carried out the end-to-end integration that brought the full prototype to a runnable state ahead of the demonstration
- Authored Section 3.1 (Product Concept and Application Scenarios) and Section 3.5 (Defensibility)
- Diagnosed and resolved hardware failures during the live demonstration by verifying physical connections and restarting the system to restore functionality

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
