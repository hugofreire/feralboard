# Getting Started

## Prerequisites

- Raspberry Pi 5 running Sway/Wayland
- FeralBoard (ATmega4809) connected via UART to `/dev/ttyAMA0`
- raspi-gpio auxiliary Pi at 192.168.0.142 (for E2E tests only)

## Installation

```bash
cd /home/pi/apps/feralboard/apps/workbench
sudo bash setup.sh
```

This installs: python3, `python3-venv`, PyGObject, GTK3, pyserial, grim, socat.
It also creates `.venv/` with `--system-site-packages` and installs Python packages from `requirements.txt`.

## Firmware Build & Flash

```bash
# Full pipeline: install deps + compile + flash
sudo bash ../../scripts/firmware/flash.sh

# Build only (no flash)
bash ../../scripts/firmware/flash.sh --build-only

# Flash only (existing hex)
sudo bash ../../scripts/firmware/flash.sh --flash-only
```

| Parameter | Value |
|-----------|-------|
| Board | ATmega4809 via MegaCoreX |
| Flash port | `/dev/ttyAMA3` (Pi 5) via serialUPDI |
| Build output | `../../hardware/firmware/src/cli-build/Feralboard_v1.2.7.ino.hex` |

## Running the GUI

```bash
# From SSH (sets Wayland env vars automatically)
bash scripts/run.sh

# Or directly with env vars
export WAYLAND_DISPLAY=wayland-1 XDG_RUNTIME_DIR=/run/user/1000
bash scripts/python.sh gui/app.py
```

The GUI opens fullscreen on the Pi's display (480x819 portrait).

### Pages

| Page | Description |
|------|-------------|
| **Home** | Connect/disconnect serial, view board status (temps, errors, door state) |
| **Outputs** | Toggle 12 digital outputs (DO0–DO11) with RX echo feedback |
| **Inputs** | Monitor 8 digital inputs (DI0–DI7) in real-time |
| **Tests** | Run E2E test scripts and view output |

### Remote Control (IPC Socket)

The app exposes a Unix socket at `/tmp/feralboard-workbench.sock` for remote control:

```bash
# Navigate to a page
bash scripts/send.sh navigate outputs

# Get current page
bash scripts/send.sh page

# Get window size
bash scripts/send.sh size
```

### Screenshots

```bash
bash scripts/screenshot.sh
```

## Running E2E Tests

E2E tests require both the FeralBoard (serial) and raspi-gpio (TCP GPIO API) to be connected.

```bash
# Output test: FeralBoard -> raspi-gpio GPIO verification
bash scripts/python.sh tests/test_outputs_e2e.py

# Input test: raspi-gpio GPIO -> FeralBoard verification
bash scripts/python.sh tests/test_inputs_e2e.py

# With custom options
bash scripts/python.sh tests/test_outputs_e2e.py --port /dev/ttyAMA0 --gpio-host 192.168.0.142

# Via pytest
bash scripts/python.sh -m pytest tests/ --port /dev/ttyAMA0
```

## Serial Ports

| Port | Baud | Purpose |
|------|------|---------|
| `/dev/ttyAMA0` | 9600 | Command I/O (TX 11 bytes, RX 41 bytes) |
| `/dev/ttyAMA3` | 115200 | Firmware flashing (serialUPDI) |

See the [Serial Protocol](api/serial-protocol.md) page for the full frame format.
