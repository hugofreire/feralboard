# Feralboard Workbench

Consolidated repo for FeralBoard development: firmware, serial library, E2E tests, and GTK3 GUI.

## Project Structure

- `firmware/` — ATmega4809 firmware source + build/flash script
- `lib/` — Python library: serial comms, CRC8, protocol constants, GPIO client, I/O map
- `tests/` — E2E tests using raspi-gpio auxiliary device
- `gui/` — GTK3 Python app for interactive FeralBoard I/O testing
- `kiosk_apps/` — Kiosk app manifests (each app = subdirectory with app.json)
- `scripts/` — Shell helpers (run, screenshot, send)
- `docs/` — Serial protocol, raspi-gpio API, getting started

## Quick Start

```bash
# Install dependencies
sudo bash setup.sh

# Build and flash firmware
sudo bash firmware/build-and-flash.sh

# Run the GUI
bash scripts/run.sh

# Run E2E tests
python3 tests/test_outputs_e2e.py
python3 tests/test_inputs_e2e.py
```

## Firmware Build & Flash

- **Build tool**: arduino-cli with MegaCoreX:megaavr:4809
- **Flash tool**: avrdude via serialUPDI on /dev/ttyAMA3 (Pi 5)
- **Script**: `sudo bash firmware/build-and-flash.sh [--build-only | --flash-only]`

## Serial Ports

- `/dev/ttyAMA0` — **Serial comms** (TX/RX with firmware), 9600 baud. GUI and `lib/serial_comm.py` use this.
- `/dev/ttyAMA3` — **serialUPDI** (firmware flashing via avrdude). Only used by `firmware/build-and-flash.sh`.
- **Critical**: The GUI must connect to ttyAMA0. Connecting to ttyAMA3 will only echo TX back (no real firmware response).

## Serial Protocol

- **TX frame**: 11 bytes (outputs + command + CRC8)
- **RX frame**: 41 bytes (echo + inputs + temps + errors + CRC8)
- **CRC-8**: Polynomial 0x07

## I/O Naming Convention

- **DI0-DI7**: Digital inputs (RX byte 4, bits 0-7)
- **DO0-DO11**: Digital outputs (TX bytes 0, 2, 3)
- See `firmware/IO_NAMING.md` for full mapping

## raspi-gpio Auxiliary Device

- **Host**: 192.168.0.142:5555 (TCP GPIO API)
- **Purpose**: E2E test verification — drive inputs, monitor outputs
- **Commands**: `read_all`, `read <pin>`, `write <pin> <0|1>`, `reset_all`

## GUI (Wayland/Sway)

- **Display**: 480x819 portrait (GTK reports 668x819 due to fractional scaling)
- **IPC socket**: /tmp/feralboard-workbench.sock
- **Screenshot**: `bash scripts/screenshot.sh`
- **Send command**: `bash scripts/send.sh navigate outputs`
- **Fractional scaling**: Display is 1024x600 @ 1.25x scale, rotated 270°. GTK3 misreports width — `ClampBox` in `gui/app.py` constrains layout to actual 480px.

### Pages

| Page | File | Description |
|------|------|-------------|
| Kiosk | `gui/pages/kiosk.py` | Lock screen showing app content, long-press title to unlock |
| PIN | `gui/pages/pin.py` | PIN entry keypad (9127) to access admin area |
| Home | `gui/pages/home.py` | Main screen with large nav buttons, connection controls, board status |
| Outputs | `gui/pages/outputs.py` | 12 digital output toggles (DO0–DO11) with echo feedback |
| Inputs | `gui/pages/inputs.py` | 8 digital input indicators (DI0–DI7) |
| Tests | `gui/pages/tests.py` | E2E test runner with live log output |
| WiFi | `gui/pages/wifi.py` | WiFi network scanning, connection status, connect with password (nmcli) |
| Ethernet | `gui/pages/ethernet.py` | Ethernet config: DHCP/Static toggle, IP/subnet/gateway/DNS, apply via nmcli |
| System | `gui/pages/system.py` | System monitor: RAM, swap, disk usage, CPU temp, uptime |
| Apps | `gui/pages/apps.py` | Kiosk app listing from kiosk_apps/ directory |
| RFID | `gui/pages/rfid.py` | FX9600 RFID reader debug: connect, inventory, live tag reads |
| Expedição | `gui/pages/expedicao.py` | RFID inventory validation with traffic lights, DI-driven state machine (dynamic page) |

### IPC Commands

```
navigate <home|outputs|inputs|tests|wifi|ethernet|system|kiosk|pin|apps|rfid>  - switch page
click X Y       - simulate click at GTK coordinates (use `widgets` to find coords)
widgets          - list all visible buttons/switches with GTK coordinates
connect          - open serial connection
disconnect       - close serial connection
toggle <DOx> <on|off>  - toggle output channel
lock             - go to kiosk lock screen
unlock           - go to PIN entry page
run-test <outputs|inputs>  - run E2E test
page             - get current page name
size             - get window size (GTK coords, not screenshot pixels)
help             - show commands
```

### Click Simulation

Screenshot pixels (480x819) differ from GTK coordinates (668x819) due to fractional Wayland scaling. To click UI elements:

1. Use `widgets` command to get GTK coordinates of all buttons/switches
2. Use `click X Y` with those GTK coordinates (not screenshot pixel positions)

```bash
# List all clickable widgets with their GTK coordinates
echo "widgets" | socat - UNIX-CONNECT:/tmp/feralboard-workbench.sock

# Click a widget at its reported center coordinates
echo "click 355 361" | socat - UNIX-CONNECT:/tmp/feralboard-workbench.sock
```

## FX9600 RFID Reader

- **Reader**: Zebra FX9600, connected via Ethernet (direct cable)
- **Network**: Pi `192.168.50.1` (eth0) ↔ FX9600 `192.168.50.2` (DHCP via dnsmasq)
- **Protocol**: LLRP (Low-Level Reader Protocol) on TCP port `5084`
- **LLRP client**: `lib/rfid_reader.py` — raw TCP socket, binary LLRP, threaded
- **GUI page**: `gui/pages/rfid.py` — connect, start/stop inventory, live tag log with dedup
- **Setup script**: `docs/setup-eth-fx9600.sh` (configures eth0 static IP + dnsmasq DHCP)
- **Full guide**: `docs/FX9600-GUIDE.md`
- **Boot time**: FX9600 takes ~2-3 min from power-on; LLRP port opens ~30s after ping works

## Documentation (MkDocs)

- **Theme**: mkdocs-shadcn
- **Serve**: `mkdocs serve -a 0.0.0.0:8000` (accessible at http://192.168.0.148:8000)
- **Build**: `mkdocs build` (outputs to `site/`)
- **Config**: `mkdocs.yml`

## Git & GitHub

- **Repo**: `hugofreire/feralboard-workbench` (private)
- **Branch**: `main`
- **Git auth**: Uses `gh auth setup-git` for HTTPS credential helper
- **Commit identity**: Uses `-c user.name="FeralBoard" -c user.email="dev@feralboard.local"` (no global git config set)

## Wayland/VNC Warnings

- **DO NOT** kill the `wayvnc` process — it provides VNC access to the Pi and is started by sway config (`/etc/sway/config.d/99-custom-config`)
- **DO NOT** leave `grim` processes hanging — hung grim can block wayvnc screen capture and cause grey screen on VNC clients
- If `grim` hangs (screenshot.sh), kill it immediately: `pkill grim`
- If VNC shows grey screen, reboot the Pi as a last resort

## Kiosk Mode

The app boots into a locked kiosk screen. Long-press (2s) on the title to open the PIN page. Enter PIN `9127` to access the admin area (home page). The Lock button on the home page returns to kiosk mode.

### Kiosk App Manifest

Each app is a subdirectory in `kiosk_apps/` containing an `app.json`. Two types:

**Simple greeting app** — displays text on the kiosk lock screen:

```json
{
    "name": "Hello World",
    "description": "A simple greeting app",
    "greeting": "Olá Mundo!"
}
```

**Custom page app** — loads a GTK page dynamically via `importlib`:

```json
{
    "name": "Expedição",
    "description": "RFID inventory validation for shipping",
    "page": "expedicao",
    "order": { ... }
}
```

When `"page"` is present, the app loads `gui/pages/<page>.py` and instantiates `<Page>Page` (e.g. `expedicao` → `gui.pages.expedicao.ExpedicaoPage`). The page class must accept `on_unlock` kwarg and implement:

- `load_app(app_info)` — receive the full `app.json` dict
- `cleanup()` — stop background tasks (RFID, timers, threads)
- `update_from_rx(rx_buffer)` — (optional) receive serial RX data when page is visible

## Iterative Dev Workflow

```bash
# 1. Kill old instances
pkill -f "python3.*gui/app.py"

# 2. Launch in background
bash scripts/run.sh &

# 3. Screenshot and view (kill grim if it hangs!)
bash scripts/screenshot.sh
# Read /home/pi/apps/feralboard-workbench/screen.png

# 4. Send commands
bash scripts/send.sh navigate outputs
bash scripts/send.sh toggle DO0 on
```
