# Installation Guide

Two setups are covered:

1. **Development / demo mode** — runs on any laptop, no hardware needed.
2. **Hardware mode** — runs on a Raspberry Pi Zero 2 W with the real sensors.

---

## 1. Development mode (laptop)

### Prerequisites
- Python 3.11 or newer
- Git

### Setup

```bash
git clone https://github.com/<your-org>/smartmedbox.git
cd smartmedbox

python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
```

Edit `.env`:

| Variable | Notes |
|----------|-------|
| `KICONNECT_API_KEY` | University Ki:connect key. Optional — without it, reminders fall back to deterministic messages, but vision verification is unavailable. |
| `KICONNECT_BASE_URL` | Ki:connect endpoint. |
| `LLM_MODEL` | Model name (e.g. the Mistral model exposed by Ki:connect). |
| `HARDWARE_MODE` | Keep `mock` on a laptop. |
| `CAREGIVER_PHONE`, `TWILIO_*` | Optional — leave blank to log alerts to the console instead of sending SMS. |

### Run the interactive demo

```bash
python src/main.py
```

| Command | Effect |
|---------|--------|
| `due` | Initial reminder |
| `remind` | Repeated reminder |
| `alert` | Caregiver alert |
| `open` | Simulate opening the box → capture → intake verification |
| `refill` | Reset today's medication |
| `quit` | Exit |

### Run the automated demo

```bash
python src/simulator.py
```

Plays the full scenario end to end without any typing — ideal for rehearsing or
presenting.

### Run the tests

```bash
python -m pytest tests/ -v
```

---

## 2. Hardware mode (Raspberry Pi)

### Prerequisites
- Raspberry Pi Zero 2 W with Raspberry Pi OS (Bookworm or newer)
- Components wired per [`hardware/WIRING.md`](../hardware/WIRING.md) — reed switch on **GPIO 17**
- Network access (Ki:connect API)

### Setup

```bash
sudo apt update && sudo apt install -y python3-venv python3-pip libportaudio2

git clone https://github.com/<your-org>/smartmedbox.git
cd smartmedbox

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
nano .env
# Set KICONNECT_API_KEY and change HARDWARE_MODE=real
```

Enable the camera interface:

```bash
sudo raspi-config      # Interface Options → Camera → Enable
```

Run:

```bash
python src/main.py
```

The Pi now polls the reed switch and the medication schedule continuously.

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
| `KICONNECT_API_KEY is not set` warning | Add the key to `.env`, or ignore it to use the offline reminder fallback (vision will be unavailable). |
| `ModuleNotFoundError: RPi` on a laptop | Expected — hardware packages are skipped in mock mode. Keep `HARDWARE_MODE=mock`. |
| Reed switch never triggers | Check it is on **GPIO 17** and GND, and that the magnet actually separates when the lid opens. |
| Camera not detected | Enable it via `sudo raspi-config` → Interface Options → Camera. |
| No sound on the Pi | Ensure `libportaudio2` is installed and the speaker/amplifier is the default audio output. |
| Vision never confirms intake | Check lighting, and make sure the user follows the spoken prompt and holds the pill visibly before the capture. |
| Pi won't join a network | The Pi Zero 2 W only supports **2.4 GHz** Wi-Fi. Set phone hotspots to 2.4 GHz and avoid spaces/special characters in the SSID. |
