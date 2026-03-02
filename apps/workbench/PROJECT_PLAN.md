# Feralboard Workbench — Consolidated Project Plan

## Objective

Create `/home/pi/apps/feralboard-workbench/` — a single self-contained repo that consolidates:

- **Firmware source** + build/flash tooling (from `feralboard-sdk/firmware/`)
- **Python serial library** (extracted from `program-firmware-arduino-uno/board_tester.py`)
- **E2E test infrastructure** (from `program-firmware-arduino-uno/test_*.py`)
- **raspi-gpio integration** (GPIO API client for auxiliary RPi at 192.168.0.142:5555)
- **GTK3 Python GUI** (based on `python-gui/` patterns) for interactive FeralBoard I/O testing

---

## Directory Structure

```
feralboard-workbench/
├── firmware/                        # ATmega4809 firmware (copy from feralboard-sdk)
│   ├── src/                         # Arduino source tree (the inner src/)
│   │   ├── core/
│   │   │   ├── Communication.cpp/h
│   │   │   ├── InputManager.cpp/h
│   │   │   └── OutputManager.cpp/h
│   │   ├── subsystems/
│   │   │   └── Safety.cpp/h
│   │   ├── feralboard.ino
│   │   └── ... (remaining firmware files)
│   ├── build-and-flash.sh           # Build + flash script (copy from feralboard-sdk)
│   ├── IO_NAMING.md                 # DI/DO naming reference
│   ├── HARDWARE_SPEC.md             # Hardware specification
│   └── PIN_MAP.md                   # Pin mapping
│
├── lib/                             # Python library modules
│   ├── __init__.py
│   ├── serial_comm.py               # SerialCommunicator class (extracted from board_tester.py)
│   ├── crc8.py                      # CRC-8 lookup table + calc (extracted from board_tester.py)
│   ├── protocol.py                  # TX/RX buffer constants, command IDs, frame definitions
│   ├── gpio_client.py               # raspi-gpio TCP client (extracted from test_outputs_e2e.py)
│   └── io_map.py                    # DI0-DI7 / DO0-DO11 channel definitions and bit mappings
│
├── tests/                           # E2E and unit tests
│   ├── test_outputs_e2e.py          # Output echo + GPIO verification (adapted)
│   ├── test_inputs_e2e.py           # Input GPIO drive + RX verification (adapted)
│   └── conftest.py                  # Shared fixtures (serial port, gpio client)
│
├── gui/                             # GTK3 application
│   ├── app.py                       # Main WorkbenchWindow (Gtk.ApplicationWindow + Gtk.Stack)
│   ├── serial_bridge.py             # GLib.timeout_add bridge between serial thread and GTK
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── home.py                  # Home/status page (connection status, board info)
│   │   ├── outputs.py               # 12 output toggles (DO0-DO11) with echo feedback
│   │   ├── inputs.py                # 8 input indicators (DI0-DI7) with live state
│   │   └── tests.py                 # E2E test runner page (run tests, show results)
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── toggle_card.py           # Reusable DO toggle widget (label + switch + echo LED)
│   │   ├── input_card.py            # Reusable DI indicator widget (label + status dot)
│   │   └── header_bar.py            # Custom header bar with serial port selector
│   ├── ipc.py                       # Unix socket IPC server (/tmp/feralboard-workbench.sock)
│   └── style.css                    # GTK CSS theme (dark, matching python-gui patterns)
│
├── scripts/
│   ├── run.sh                       # Launch GUI with Wayland env vars (from python-gui/run.sh)
│   ├── screenshot.sh                # grim screenshot helper
│   └── send.sh                      # socat IPC command sender
│
├── docs/
│   ├── SERIAL_PROTOCOL.md           # Serial frame format reference (copy from feralboard-sdk)
│   ├── RASPI_GPIO_API.md            # raspi-gpio TCP API documentation (new)
│   └── GETTING_STARTED.md           # Setup and usage guide (new)
│
├── requirements.txt                 # Python dependencies (PyGObject, pyserial)
├── setup.sh                         # One-shot dependency installer
└── CLAUDE.md                        # Claude Code onboarding for this project
```

---

## File Sources — What to Copy vs Create

### Copy and Flatten (from `feralboard-sdk/firmware/`)

| Source | Destination | Notes |
|--------|-------------|-------|
| `feralboard-sdk/firmware/src/src/` (entire inner tree) | `firmware/src/` | Flatten the double-`src` into single `src/` |
| `feralboard-sdk/firmware/src/build-and-flash.sh` | `firmware/build-and-flash.sh` | Update paths for new layout |
| `feralboard-sdk/firmware/IO_NAMING.md` | `firmware/IO_NAMING.md` | Direct copy |
| `feralboard-sdk/firmware/src/HARDWARE_SPEC.md` | `firmware/HARDWARE_SPEC.md` | Direct copy |
| `feralboard-sdk/firmware/src/PIN_MAP.md` | `firmware/PIN_MAP.md` | Direct copy |
| `feralboard-sdk/SERIAL_PROTOCOL.md` | `docs/SERIAL_PROTOCOL.md` | Direct copy |

### Extract and Refactor (from `program-firmware-arduino-uno/board_tester.py`)

The 1264-line `board_tester.py` gets split into focused modules:

| New File | Extracted From | Content |
|----------|---------------|---------|
| `lib/crc8.py` | `board_tester.py` lines 1-50 | `CRC8_TABLE`, `calculate_crc8()` |
| `lib/protocol.py` | `board_tester.py` constants section | `TX_SIZE=11`, `RX_SIZE=41`, command IDs, byte offsets, bit masks |
| `lib/serial_comm.py` | `board_tester.py` `SerialCommunicator` class | Threaded TX/RX loop (250ms), thread-safe lock, output control methods |
| `lib/io_map.py` | New, based on `IO_NAMING.md` | Channel definitions: `OUTPUTS = [("DO0", 0, 0), ...]`, `INPUTS = [("DI0", 4, 0), ...]` |
| `lib/gpio_client.py` | `test_outputs_e2e.py` GPIO functions | `GpioClient` class wrapping TCP socket to 192.168.0.142:5555 |

### Adapt (from `program-firmware-arduino-uno/test_*.py`)

| Source | Destination | Changes |
|--------|-------------|---------|
| `test_outputs_e2e.py` | `tests/test_outputs_e2e.py` | Import from `lib/`, use `conftest.py` fixtures |
| `test_inputs_e2e.py` | `tests/test_inputs_e2e.py` | Import from `lib/`, use `conftest.py` fixtures |

### Copy Shell Scripts (from `python-gui/`)

| Source | Destination | Changes |
|--------|-------------|---------|
| `python-gui/run.sh` | `scripts/run.sh` | Update python path to `gui/app.py` |
| `python-gui/screenshot.sh` | `scripts/screenshot.sh` | Direct copy |
| `python-gui/send.sh` | `scripts/send.sh` | Update socket path |
| `python-gui/setup.sh` | `setup.sh` | Add `pyserial` to deps |

### Create New

| File | Description |
|------|-------------|
| `gui/app.py` | Main window: `Gtk.ApplicationWindow` + `Gtk.Stack` with 4 pages, dark theme, fullscreen |
| `gui/serial_bridge.py` | Polls `SerialCommunicator` via `GLib.timeout_add(100)`, emits signals on state change |
| `gui/pages/home.py` | Connection status, serial port selector, board info (firmware mode, error byte) |
| `gui/pages/outputs.py` | 12 `ToggleCard` widgets in a grid, click to toggle DO, echo feedback from RX |
| `gui/pages/inputs.py` | 8 `InputCard` widgets showing live DI0-DI7 state from RX byte 4 |
| `gui/pages/tests.py` | Button to run E2E tests (subprocess), scrollable log output |
| `gui/widgets/toggle_card.py` | `Gtk.Box` with label ("DO0"), `Gtk.Switch`, and echo indicator LED |
| `gui/widgets/input_card.py` | `Gtk.Box` with label ("DI0") and colored status circle (green=ON, gray=OFF) |
| `gui/widgets/header_bar.py` | `Gtk.HeaderBar` with page navigation buttons and serial port combo |
| `gui/ipc.py` | Unix socket server at `/tmp/feralboard-workbench.sock` (from python-gui pattern) |
| `gui/style.css` | Dark theme CSS for cards, toggles, indicators |
| `tests/conftest.py` | Shared pytest fixtures: `serial_port`, `gpio_client`, `communicator` |
| `docs/RASPI_GPIO_API.md` | Document the raspi-gpio TCP API (host, port, commands, responses) |
| `docs/GETTING_STARTED.md` | Setup guide: deps, firmware build/flash, running GUI, running tests |
| `CLAUDE.md` | Claude Code context file for the new project |
| `requirements.txt` | `PyGObject`, `pyserial` |

---

## GUI Architecture

### Window Layout (480x819 portrait)

```
┌──────────────────────────┐
│  Header Bar              │
│  [Home][Outputs][Inputs] │
│  [Tests]   [port: ▾]    │
├──────────────────────────┤
│                          │
│   Gtk.Stack              │
│   (active page content)  │
│                          │
│                          │
│                          │
│                          │
│                          │
└──────────────────────────┘
```

### Pages

**Home Page**
- Serial port selector (auto-detect `/dev/ttyAMA*`)
- Connect/Disconnect button
- Connection status indicator
- Board info: factory mode, error byte value, last RX timestamp

**Outputs Page**
- 3-column grid of 12 `ToggleCard` widgets (DO0-DO11)
- Each card: channel label, ON/OFF switch, echo indicator
- Switch toggle → sets bit in TX buffer → serial sends → RX echo confirms
- Echo indicator: green when TX bit matches RX bit, red on mismatch

**Inputs Page**
- 2-column grid of 8 `InputCard` widgets (DI0-DI7)
- Each card: channel label, colored circle (green=HIGH, gray=LOW)
- Auto-updates from RX byte 4 via serial bridge
- Optional: byte value display in hex

**Tests Page**
- "Run Output E2E" button → subprocess `python3 tests/test_outputs_e2e.py`
- "Run Input E2E" button → subprocess `python3 tests/test_inputs_e2e.py`
- Scrollable `Gtk.TextView` log showing test output in real-time
- Pass/fail summary at bottom

### Serial Bridge Pattern

```python
# gui/serial_bridge.py
class SerialBridge:
    def __init__(self, communicator: SerialCommunicator):
        self.comm = communicator
        self._last_rx = None
        GLib.timeout_add(100, self._poll)  # 10Hz GUI update

    def _poll(self):
        with self.comm.lock:
            rx = self.comm.rxBuffer.copy()
        if rx != self._last_rx:
            self._last_rx = rx
            self.on_state_changed(rx)  # callback to update GUI
        return True  # keep polling

    def set_output(self, channel_index, bit_offset, value):
        with self.comm.lock:
            # set/clear bit in TX buffer
            ...
```

---

## Key Technical Decisions

1. **Serial baud rate**: 9600 (matches firmware UART1 and board_tester.py, despite SERIAL_PROTOCOL.md saying 115200)
2. **Serial port**: Auto-detect, default `/dev/ttyAMA3` on Pi 5
3. **GUI framework**: GTK3 + PyGObject (matches python-gui base, works on Wayland/Sway)
4. **Thread safety**: `SerialCommunicator` runs in background thread, GUI polls via `GLib.timeout_add`
5. **IPC**: Unix socket at `/tmp/feralboard-workbench.sock` for remote control and screenshot automation
6. **raspi-gpio**: TCP client to 192.168.0.142:5555 (only used by E2E tests, not by GUI)
7. **Firmware build**: `sudo bash firmware/build-and-flash.sh` from project root

---

## raspi-gpio API Reference

The auxiliary Raspberry Pi at `192.168.0.142:5555` exposes a TCP socket GPIO API:

- **Set pin mode**: send `MODE <pin> OUTPUT\n` or `MODE <pin> INPUT\n`
- **Write pin**: send `WRITE <pin> HIGH\n` or `WRITE <pin> LOW\n`
- **Read pin**: send `READ <pin>\n`, receive JSON with pin state
- **Read all**: send `READ_ALL\n`, receive JSON with all pin states

Known GPIO-to-DI mappings:
- GPIO 15 → DI0
- GPIO 18 → DI1
- GPIO 17 → DI2, DI3

Known GPIO-to-DO mappings (from test_outputs_e2e.py output verification):
- Documented per-output in the E2E test file

---

## Implementation Phases

### Phase 1: Scaffold and Copy
- Create directory structure
- Copy firmware files (flatten double-src)
- Copy shell scripts
- Create `requirements.txt`, `setup.sh`, `CLAUDE.md`

### Phase 2: Extract Python Library
- Split `board_tester.py` into `lib/crc8.py`, `lib/protocol.py`, `lib/serial_comm.py`
- Create `lib/io_map.py` from IO_NAMING.md
- Extract `lib/gpio_client.py` from test files

### Phase 3: Adapt E2E Tests
- Port `test_outputs_e2e.py` and `test_inputs_e2e.py` to use `lib/` imports
- Create `tests/conftest.py` with shared fixtures
- Verify tests still pass

### Phase 4: Build GUI Shell
- Create `gui/app.py` with `Gtk.ApplicationWindow`, `Gtk.Stack`, dark theme
- Create `gui/serial_bridge.py`
- Create header bar with page navigation
- Create `gui/ipc.py` socket server
- Create `scripts/run.sh`

### Phase 5: Outputs Page
- Create `gui/widgets/toggle_card.py`
- Create `gui/pages/outputs.py` with 12 toggle cards
- Wire switches to TX buffer via serial bridge
- Show echo feedback from RX

### Phase 6: Inputs Page
- Create `gui/widgets/input_card.py`
- Create `gui/pages/inputs.py` with 8 input indicators
- Wire to RX byte 4 via serial bridge

### Phase 7: Home and Tests Pages
- Create `gui/pages/home.py` with serial port selector and status
- Create `gui/pages/tests.py` with subprocess test runner

### Phase 8: Documentation
- Write `docs/RASPI_GPIO_API.md`
- Write `docs/GETTING_STARTED.md`
- Update `firmware/build-and-flash.sh` paths for new layout
