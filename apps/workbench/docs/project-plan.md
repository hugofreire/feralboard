# Project Plan

## Objective

Create a single self-contained project that consolidates:

- **Firmware source** + build/flash tooling (from `feralboard-sdk/firmware/`)
- **Python serial library** (extracted from `program-firmware-arduino-uno/board_tester.py`)
- **E2E test infrastructure** (from `program-firmware-arduino-uno/test_*.py`)
- **raspi-gpio integration** (GPIO API client for auxiliary RPi at 192.168.0.142:5555)
- **GTK3 Python GUI** (based on `python-gui/` patterns) for interactive FeralBoard I/O testing

---

## Directory Structure

```
feralboard-workbench/
├── firmware/                        # ATmega4809 firmware
│   ├── src/                         # Arduino source tree
│   │   ├── core/                    # Communication, InputManager, OutputManager
│   │   ├── subsystems/              # Safety, Buzzer, DoorLock
│   │   ├── config/                  # Config, Definitions
│   │   ├── utils/                   # Logger, Utils
│   │   └── Feralboard_v1.2.7.ino   # Main sketch
│   └── build-and-flash.sh          # Build + flash script
│
├── lib/                             # Python library modules
│   ├── serial_comm.py               # SerialCommunicator class
│   ├── crc8.py                      # CRC-8 lookup table + calc
│   ├── protocol.py                  # TX/RX constants, command IDs
│   ├── gpio_client.py               # raspi-gpio TCP client
│   └── io_map.py                    # DI/DO channel definitions
│
├── tests/                           # E2E tests
│   ├── test_outputs_e2e.py          # Output echo + GPIO verification
│   ├── test_inputs_e2e.py           # Input GPIO drive + RX verification
│   └── conftest.py                  # Shared pytest fixtures
│
├── gui/                             # GTK3 application
│   ├── app.py                       # Main WorkbenchWindow
│   ├── serial_bridge.py             # GLib bridge to serial thread
│   ├── ipc.py                       # Unix socket server
│   ├── style.css                    # Dark theme CSS
│   ├── pages/                       # Home, Outputs, Inputs, Tests
│   └── widgets/                     # ToggleCard, InputCard, HeaderBar
│
├── scripts/                         # Shell helpers
│   ├── run.sh                       # Launch GUI on Wayland
│   ├── screenshot.sh                # grim screenshot
│   └── send.sh                      # socat IPC sender
│
├── docs/                            # Documentation (MkDocs)
├── mkdocs.yml                       # MkDocs configuration
├── setup.sh                         # Dependency installer
└── requirements.txt                 # Python dependencies
```

---

## File Sources

### Copied and Flattened

| Source | Destination |
|--------|-------------|
| `feralboard-sdk/firmware/src/src/` | `firmware/src/` (flattened double-`src`) |
| `feralboard-sdk/firmware/src/build-and-flash.sh` | `firmware/build-and-flash.sh` (paths updated) |
| `feralboard-sdk/SERIAL_PROTOCOL.md` | `docs/api/serial-protocol.md` |
| `feralboard-sdk/firmware/IO_NAMING.md` | `docs/firmware/io-naming.md` |

### Extracted from `board_tester.py` (1264 lines → 5 modules)

| Module | Content |
|--------|---------|
| `lib/crc8.py` | CRC-8 lookup table, `calculate_crc8()`, `verify_crc8()` |
| `lib/protocol.py` | Buffer sizes, byte offsets, command IDs, helpers |
| `lib/serial_comm.py` | `SerialCommunicator` class (threaded TX/RX loop) |
| `lib/io_map.py` | `OUTPUTS`, `INPUTS` channel definitions |
| `lib/gpio_client.py` | `GpioClient` TCP socket wrapper |

### Adapted

| Source | Destination |
|--------|-------------|
| `test_outputs_e2e.py` | `tests/test_outputs_e2e.py` (imports from `lib/`) |
| `test_inputs_e2e.py` | `tests/test_inputs_e2e.py` (imports from `lib/`) |
| `python-gui/run.sh` | `scripts/run.sh` (updated path) |

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
└──────────────────────────┘
```

### Pages

| Page | Description |
|------|-------------|
| **Home** | Serial port selector, connect/disconnect, board status (temps, errors, door state, factory mode) |
| **Outputs** | 3-column grid of 12 `ToggleCard` widgets (DO0–DO11) with echo feedback |
| **Inputs** | 2-column grid of 8 `InputCard` widgets (DI0–DI7) with live state |
| **Tests** | E2E test runner with scrollable log output |

### Serial Bridge Pattern

```python
class SerialBridge:
    def __init__(self, communicator):
        self.comm = communicator
        self._last_rx = None
        GLib.timeout_add(100, self._poll)  # 10Hz GUI update

    def _poll(self):
        rx_buffer, valid = self.comm.get_rx_buffer()
        if valid and rx_buffer != self._last_rx:
            self._last_rx = rx_buffer
            for cb in self._callbacks:
                cb(rx_buffer)
        return True
```

---

## Technical Decisions

| Decision | Value | Reason |
|----------|-------|--------|
| Serial baud rate | 9600 | Matches firmware UART1 and `board_tester.py` |
| Serial port | Auto-detect, default `/dev/ttyAMA3` | Pi 5 standard |
| GUI framework | GTK3 + PyGObject | Works on Wayland/Sway, matches existing patterns |
| Thread safety | Background thread + `GLib.timeout_add` | Non-blocking GUI updates |
| IPC | Unix socket `/tmp/feralboard-workbench.sock` | Remote control + screenshots |
| raspi-gpio | TCP to 192.168.0.142:5555 | E2E tests only, not GUI |

---

## Implementation Phases

All phases have been completed:

- [x] **Phase 1**: Scaffold and copy firmware + scripts
- [x] **Phase 2**: Extract Python library (5 modules from board_tester.py)
- [x] **Phase 3**: Adapt E2E tests to use `lib/` imports
- [x] **Phase 4**: Build GTK GUI shell with serial bridge
- [x] **Phase 5**: Outputs page (12 toggle cards)
- [x] **Phase 6**: Inputs page (8 input indicators)
- [x] **Phase 7**: Home and Tests pages
- [x] **Phase 8**: Documentation (MkDocs with shadcn theme)
