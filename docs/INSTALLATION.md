# Installation Guide

SmartMedBox runs in two modes:

- **Mock mode** — runs on any laptop, no hardware required. Ideal for
  development, testing, and demonstrating the software.
- **Hardware mode** — runs on a Raspberry Pi Zero W with the real sensors.

The mode is controlled by `HARDWARE_MODE` in your `.env` file (`mock` or `real`).

---

## 1. Mock mode (laptop — no hardware)

### Prerequisites
- Python 3.11 or newer
- Git

### Setup

```bash
git clone https://github.com/SusieQ2022/smartmedbox.git
cd smartmedbox

python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
```

Edit `.env`:

| Variable | Notes |
|----------|-------|
| `KICONNECT_API_KEY` | University Ki:connect key. Needed for **live vision verification**. Without it, reminders still work via a deterministic fallback, but intake verification is unavailable. |
| `KICONNECT_BASE_URL` | Ki:connect endpoint (default already set). |
| `LLM_MODEL` | Model name (defaults to the confirmed Ki:connect Mistral model). |
| `HARDWARE_MODE` | Keep `mock` on a laptop. |
| `SMARTMEDBOX_DB` | Path to the SQLite database (default `smartmedbox.db`). |
| `CAREGIVER_PHONE`, `TWILIO_*` | Optional — leave blank to log alerts to the console instead of sending SMS. |

### Run

```bash
# Interactive demo
python src/main.py
```

| Command | Effect |
|---------|--------|
| `due` | Send the initial reminder |
| `remind` | Send a repeated reminder |
| `alert` | Trigger the caregiver alert |
| `open` | Simulate opening the box → capture → intake verification |
| `refill` | Reset today's medication |
| `quit` | Exit |

```bash
# Automated end-to-end demo (no typing — good for rehearsing / presenting)
python src/simulator.py

# Run the test suite (21 tests, all offline)
python -m pytest tests/ -v
```

### Caregiver dashboard

The dashboard is a standalone web view of the adherence event log. It works
**independently of the hardware** — it simply reads the SQLite database written
by `main.py` or `simulator.py`, so it runs in mock mode on a laptop too.

**Step 1 — generate some events** (in one terminal):

```bash
python src/simulator.py          # writes the demo scenario to the database
# or run python src/main.py and use the due / open / alert commands
```

**Step 2 — start the dashboard** (in a second terminal):

```bash
python src/dashboard.py --host 0.0.0.0 --port 8000
```

**Step 3 — open it in a browser:**

- On the same computer: `http://localhost:8000`
- From a phone on the same Wi-Fi: `http://<your-computer-ip>:8000`

The page auto-refreshes every 10 seconds and shows:

- **Summary metrics** at the top — Taken, Late, Missed, Unverified, Alerts.
- **An event table** — each row is one logged event with its timestamp, dose,
  outcome (Due / Reminder / Caregiver alert / Confirmed / Unverified), how
  overdue it was, whether the caregiver was alerted, and the spoken message.

> **Important — shared database:** `dashboard.py` and whatever writes the events
> (`main.py` / `simulator.py`) must point at the **same** `SMARTMEDBOX_DB` path,
> or the dashboard will show an empty page. Running everything from the
> repository root uses the same default (`smartmedbox.db`) automatically; on the
> Pi, set `SMARTMEDBOX_DB` to an absolute path in `.env`.
>
> Privacy note: only structured decisions are stored and served — raw camera
> images are never saved or shown.

---

## 2. Hardware mode (Raspberry Pi Zero W)

### Prerequisites
- Raspberry Pi Zero W with Raspberry Pi OS (Bookworm or newer)
- Components wired per [`../hardware/WIRING.md`](../hardware/WIRING.md) — reed switch on **GPIO 17**
- Network access (for the Ki:connect API)

### Setup

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip libportaudio2 python3-picamera2

git clone https://github.com/<your-org>/smartmedbox.git
cd smartmedbox

python3 -m venv venv --system-site-packages
source venv/bin/activate
pip install -r requirements.txt
```

> `--system-site-packages` lets the virtual environment see `picamera2`, which
> is installed system-wide on Raspberry Pi OS.

### Configure

```bash
cp .env.example .env
nano .env
```

Set the following for hardware mode:

| Variable | Value |
|----------|-------|
| `HARDWARE_MODE` | `real` |
| `KICONNECT_API_KEY` | your active Ki:connect key |
| `SMARTMEDBOX_DB` | an **absolute** path (e.g. `/home/pi/smartmedbox/smartmedbox.db`) so `main.py` and `dashboard.py` share one database |

Enable the camera interface once:

```bash
sudo raspi-config      # Interface Options → Camera → Enable → reboot
```

### Run

```bash
python src/main.py
```

The Pi now continuously polls the reed switch (GPIO 17) and the medication
schedule. Opening the box triggers: spoken prompt → wait → camera capture →
vision verification → spoken result → event logged.

In a second terminal, start the dashboard:

```bash
python src/dashboard.py --host 0.0.0.0 --port 8000
```

### Start on boot (optional)

```bash
sudo nano /etc/systemd/system/smartmedbox.service
```

```ini
[Unit]
Description=SmartMedBox
After=network-online.target

[Service]
ExecStart=/home/pi/smartmedbox/venv/bin/python /home/pi/smartmedbox/src/main.py
WorkingDirectory=/home/pi/smartmedbox
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable smartmedbox
sudo systemctl start smartmedbox
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'RPi'` (or `luma`, `picamera2`) on a laptop | You're in `HARDWARE_MODE=real` without the hardware. Set `HARDWARE_MODE=mock` in `.env`. |
| `KICONNECT_API_KEY is not set` warning | Add the key to `.env`. Reminders still work offline; vision verification needs the key. |
| `403 API key temporarily disabled` | Log in at https://chat.kiconnect.nrw to reactivate the key. |
| Reed switch never triggers | Check it's on **GPIO 17** and GND, and that the magnet actually separates when the lid opens. |
| Camera not detected | Enable it via `sudo raspi-config` → Interface Options → Camera, then reboot. |
| No sound on the Pi | Ensure `libportaudio2` is installed and the speaker/amplifier is the default audio output. |
| Vision never confirms intake | Check lighting, and make sure the user follows the spoken prompt and holds the pill visibly before capture. |
| Dashboard is empty | Confirm `main.py`/`simulator.py` and `dashboard.py` point at the same `SMARTMEDBOX_DB` path. |
| Pi won't join Wi-Fi | The Pi Zero 2 W only supports **2.4 GHz** Wi-Fi. Set phone hotspots to 2.4 GHz and avoid spaces/special characters in the SSID. |