# Getting Started

## Prerequisites

- Raspberry Pi 5 running Sway/Wayland
- FeralBoard (ATmega4809) connected via UART to `/dev/ttyAMA0`
- raspi-gpio auxiliary Pi at 192.168.0.142 (for E2E tests only)

## Installation

```bash
cd /home/pi/apps/feralboard-workbench
sudo bash setup.sh
```

This installs: python3, PyGObject, GTK3, pyserial, grim, socat.

## Firmware Build & Flash

```bash
# Full pipeline: install deps + compile + flash
sudo bash firmware/build-and-flash.sh

# Build only (no flash)
sudo bash firmware/build-and-flash.sh --build-only

# Flash only (existing hex)
sudo bash firmware/build-and-flash.sh --flash-only
```

| Parameter | Value |
|-----------|-------|
| Board | ATmega4809 via MegaCoreX |
| Flash port | `/dev/ttyAMA3` (Pi 5) via serialUPDI |
| Build output | `firmware/src/cli-build/Feralboard_v1.2.7.ino.hex` |

## Running the GUI

```bash
# From SSH (sets Wayland env vars automatically)
bash scripts/run.sh

# Or directly with env vars
export WAYLAND_DISPLAY=wayland-1 XDG_RUNTIME_DIR=/run/user/1000
python3 gui/app.py
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
python3 tests/test_outputs_e2e.py

# Input test: raspi-gpio GPIO -> FeralBoard verification
python3 tests/test_inputs_e2e.py

# With custom options
python3 tests/test_outputs_e2e.py --port /dev/ttyAMA0 --gpio-host 192.168.0.142

# Via pytest
pytest tests/ --port /dev/ttyAMA0
```

## Serial Ports

| Port | Baud | Purpose |
|------|------|---------|
| `/dev/ttyAMA0` | 9600 | Command I/O (TX 11 bytes, RX 41 bytes) |
| `/dev/ttyAMA3` | 115200 | Firmware flashing (serialUPDI) |

See the [Serial Protocol](api/serial-protocol.md) page for the full frame format.
