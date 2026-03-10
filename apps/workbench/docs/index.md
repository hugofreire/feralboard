# FeralBoard Workbench

Consolidated development environment for FeralBoard — firmware, serial library, E2E tests, and GTK3 GUI.

## Overview

The FeralBoard Workbench is a single self-contained project that brings together everything needed to develop, test, and interact with the FeralBoard (ATmega4809 microcontroller):

- **Firmware** — source code, build, and flash tooling
- **Python Library** — serial comms, CRC-8, protocol constants, GPIO client
- **E2E Tests** — end-to-end tests using a raspi-gpio auxiliary device
- **GTK3 GUI** — interactive application for output control and input monitoring

## Project Structure

```
feralboard-workbench/
├── firmware/        ATmega4809 source + build/flash script
├── lib/             Python library modules
├── tests/           E2E tests (outputs + inputs)
├── gui/             GTK3 application (pages, widgets, serial bridge)
├── scripts/         Shell helpers (run, screenshot, send)
├── .venv/           Project virtualenv with system GTK packages visible
├── docs/            Documentation (you are here)
├── mkdocs.yml       MkDocs configuration
├── setup.sh         Dependency installer
└── requirements.txt Python dependencies
```

## Quick Start

```bash
# Install system dependencies
sudo bash setup.sh

# Build and flash firmware
sudo bash ../../scripts/firmware/flash.sh

# Launch the GUI
bash scripts/run.sh

# Run E2E tests
bash scripts/python.sh tests/test_outputs_e2e.py
bash scripts/python.sh tests/test_inputs_e2e.py
```

## Key Specs

| Parameter | Value |
|-----------|-------|
| MCU | ATmega4809 (MegaCoreX) |
| Serial Port | `/dev/ttyAMA0` @ 9600 baud |
| TX Frame | 11 bytes (outputs + command + CRC8) |
| RX Frame | 41 bytes (echo + inputs + temps + errors + CRC8) |
| Flash Port | `/dev/ttyAMA3` via serialUPDI |
| GUI Display | 480x819 portrait (Wayland/Sway) |
| GPIO Tester | 192.168.0.142:5555 (TCP API) |

## I/O Summary

- **DI0–DI7** — 8 digital inputs (RX byte 4, bits 0–7)
- **DO0–DO11** — 12 digital outputs (TX bytes 0, 2, 3)

See the [I/O Naming](firmware/io-naming.md) page for the full mapping table.
