# Wiring Guide

Pin assignments for the Raspberry Pi Zero 2 W. Always power off the Pi before
changing any wiring.

## Magnetic reed switch — the primary sensor

A small magnet sits on the compartment lid; the reed switch sits on the body.
Opening the lid separates them and triggers the switch.

| Signal | Connection |
|--------|------------|
| Reed switch pin 1 | **GPIO 17** (BCM numbering) |
| Reed switch pin 2 | GND |

Configured in software as an input with the Pi's **internal pull-up** enabled,
detecting the **falling edge** with a 300 ms debounce:

```python
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(17, GPIO.FALLING, callback=..., bouncetime=300)
```

No external resistor is needed — the internal pull-up handles it.

> To add more compartments, wire one additional reed switch per compartment to
> its own GPIO pin (e.g. 27, 22, 23) and extend `_init_hardware()` in `sensors.py`.

## Camera

| Component | Connection |
|-----------|------------|
| Pi Camera Module v2 | CSI ribbon connector |

Enable the interface once with `sudo raspi-config` → Interface Options → Camera.

## Audio output

| Component | Connection |
|-----------|------------|
| PAM8403 amplifier VCC | 5 V |
| PAM8403 GND | GND |
| PAM8403 input | Pi audio out (I2S DAC or USB audio adapter) |
| Speaker (3 W, 8 Ω) | PAM8403 output terminals |

## OLED display (I2C)

| Signal | Connection |
|--------|------------|
| SDA | GPIO 2 |
| SCL | GPIO 3 |
| VCC | 3.3 V |
| GND | GND |

## Status LEDs

Each LED goes through a 220 Ω resistor to GND:

| LED | GPIO |
|-----|------|
| Green (dose OK) | GPIO 25 |
| Red (dose due / missed) | GPIO 8 |

## Safety notes

- Use a common ground rail for all components.
- Never exceed 3.3 V on any GPIO input.
- Insulate solder joints with heat-shrink tubing and secure loose wires inside
  the enclosure so nothing shifts during handling.
