# Installation Guide

This guide covers two setups:

1. **Development mode** — run SmartMedBox on any laptop (no hardware), using a
   simulated sensor layer. Ideal for coding, testing, and rehearsing the demo.
2. **Hardware mode** — run on a Raspberry Pi Zero 2 W with real sensors.

---

## 1. Development Mode (laptop)

### Prerequisites
- Python 3.11 or newer
- Git

### Steps

```bash
# Clone the repository
git clone https://github.com/SusieQ2022/smartmedbox.git
cd smartmedbox

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install dependencies (hardware-only packages are skipped automatically)
pip install -r requirements.txt

# Set up configuration
cp .env.example .env
# Open .env and set OPENAI_API_KEY (optional — without it, a rule-based
# fallback is used so the app still runs end-to-end).
# Leave HARDWARE_MODE=mock for laptop development.

# Run the interactive demo
python src/main.py
```

You will get an interactive prompt. Try:

```
take 0       # simulate taking the dose in compartment 0
double 1     # simulate opening compartment 1 twice (double-take warning)
overdue 2    # simulate compartment 2 being overdue (caregiver alert)
quit
```

### Running the tests

```bash
python -m pytest tests/ -v
```

---

## 2. Hardware Mode (Raspberry Pi)

### Prerequisites
- Raspberry Pi Zero 2 W with Raspberry Pi OS (Bookworm or newer)
- Components wired per [`hardware/WIRING.md`](../hardware/WIRING.md)
- Internet connection (for the LLM API)

### Steps

```bash
# On the Raspberry Pi:
sudo apt update && sudo apt install -y python3-venv python3-pip libportaudio2

git clone https://github.com/<your-org>/smartmedbox.git
cd smartmedbox

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
nano .env
# Set OPENAI_API_KEY and change HARDWARE_MODE=real
# Optionally add Twilio credentials for caregiver SMS alerts.

# Run
python src/main.py
```

### Running on boot (optional)

To start SmartMedBox automatically when the Pi powers on, create a systemd
service:

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
| `OPENAI_API_KEY is not set` warning | Add your key to `.env`, or ignore it to use the offline rule-based fallback. |
| `ModuleNotFoundError: RPi` on laptop | Expected — hardware packages are skipped in mock mode. Keep `HARDWARE_MODE=mock`. |
| No sound on the Pi | Check `libportaudio2` is installed and the speaker is selected as the default audio output. |
| Camera not detected | Enable the camera interface with `sudo raspi-config` → Interface Options → Camera. |
