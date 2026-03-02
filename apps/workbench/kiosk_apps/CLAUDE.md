# Kiosk App Development Guide

You are a coding agent editing a kiosk app for the FeralBoard system. This guide tells you everything you need to know about the app architecture, available APIs, and constraints.

## Your Scope

When working on a kiosk app, you should ONLY modify:
- `kiosk_apps/<app_slug>/app.json` — the app manifest
- `kiosk_apps/<app_slug>/.env` — per-app environment variables
- `gui/pages/<app_slug>.py` — the GTK page (for custom page apps)

Do NOT modify core framework files unless explicitly asked:
- `gui/app.py` — main window (loads your page dynamically, no changes needed)
- `gui/pages/kiosk.py` — default kiosk lock screen
- `lib/*` — serial, RFID, protocol libraries (use them, don't change them)

## App Types

### Greeting App (simple)
Just an `app.json` with a `greeting` field. Displays text on the kiosk lock screen.
```json
{
    "name": "Hello World",
    "description": "A simple greeting app",
    "greeting": "Welcome!"
}
```

### Custom Page App (dynamic)
Has a `page` field that maps to `gui/pages/<page>.py`. The framework loads it dynamically via importlib.
```json
{
    "name": "My App",
    "description": "Does something cool",
    "page": "my-app"
}
```

## Page Class Contract

Your page class MUST follow this contract exactly:

```python
class MyAppPage(Gtk.Box):
    def __init__(self, on_unlock=None):
        """
        - Must call super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        - Must store on_unlock callback for long-press unlock
        - Build your UI here
        """

    def load_app(self, app_info):
        """
        Called when the app is selected. Receives the full app.json dict.
        Use this to configure your page from the manifest data.
        """

    def cleanup(self):
        """
        Called when navigating away. MUST stop all:
        - GLib timers (GLib.source_remove)
        - Background threads
        - Network connections (RFID reader, sockets)
        - Serial subscriptions
        """

    def update_from_rx(self, rx_buffer):
        """
        Optional. Called every ~500ms with the latest serial RX frame (41 bytes)
        when this page is visible and serial is connected.

        RX buffer layout:
        - bytes 0-3: echo of TX
        - byte 4: digital inputs (DI0-DI7, bit-mapped)
        - bytes 5-8: analog/temp data
        - remaining: errors, CRC

        Example: read DI0
            di0 = (rx_buffer[4] >> 0) & 1 == 1
        """
```

**Class naming**: The slug `my-app` maps to class `MyAppPage` (each hyphen/underscore segment capitalized + "Page").

**Long-press unlock**: Every kiosk page should include a long-press (2 second) handler on the title that calls `self._on_unlock()`. This is how operators exit the kiosk screen. See the boilerplate template for the pattern.

## Available Libraries

### Serial Communication (`lib/serial_comm.py`)
```python
from lib.serial_comm import SerialCommunicator
# Don't create your own — the framework manages the serial connection.
# Use update_from_rx() to receive data, or access via the bridge.
```

### RFID Reader (`lib/rfid_reader.py`)
```python
from lib.rfid_reader import RfidReader
reader = RfidReader(host="192.168.50.2", port=5084)
reader.reduced_power = True
reader.on_tag_read = lambda tag: print(tag.epc)
reader.on_status_change = lambda state: print(state)
reader.connect()       # async, triggers on_status_change
reader.start_inventory()
reader.stop_inventory()
reader.disconnect()
```

### Protocol Constants (`lib/protocol.py`)
```python
from lib.protocol import CMD_FACTORY_MODE
# I/O mapping constants, command bytes, etc.
```

### GPIO Client (`lib/gpio_client.py`)
```python
from lib.gpio_client import GpioClient
gpio = GpioClient("192.168.0.142", 5555)
gpio.read("17")
gpio.write("17", 1)
```

## I/O Reference

- **DI0-DI7**: Digital inputs (RX byte 4, bits 0-7)
- **DO0-DO11**: Digital outputs (TX bytes 0, 2, 3)
- **Serial port**: `/dev/ttyAMA0` at 9600 baud

## GTK3 Patterns

### Display constraints
- Screen: 480x819 portrait, dark theme
- Use Pango markup for text (not CSS):
  ```python
  label.set_markup('<span size="14000" foreground="white">Hello</span>')
  ```
- Use `Gtk.Box` with `VERTICAL` orientation for layouts
- Use `Gtk.ScrolledWindow` for scrollable content
- Set margins with `set_margin_start()`, `set_margin_end()`, `set_margin_top()`, `set_margin_bottom()`

### Thread safety
GTK is NOT thread-safe. Always use `GLib.idle_add()` to update UI from background threads:
```python
import threading
def background_work():
    result = do_something()
    GLib.idle_add(update_label, result)
threading.Thread(target=background_work, daemon=True).start()
```

### Timers
```python
timer_id = GLib.timeout_add(1000, my_callback)  # 1 second, returns True to repeat
GLib.source_remove(timer_id)  # cancel
```

## Environment Variables

Per-app `.env` files are in `kiosk_apps/<slug>/.env`. Read them in your page:
```python
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "../../kiosk_apps/<slug>/.env"))
READER_HOST = os.getenv("READER_HOST", "192.168.50.2")
```

Or read them directly in `load_app()` from the app directory.

## Testing Your App

After making changes, the developer will restart the GUI:
```bash
pkill -f "python3.*gui/app.py"
bash scripts/run.sh &
```

Then navigate to Apps > select your app to test it.

To take a screenshot: `bash scripts/screenshot.sh`

## Example: Expedição App

See `gui/pages/expedicao.py` for a complete, production custom page app. It demonstrates:
- RFID reader integration with network checks
- Traffic light state machine driven by digital inputs (DI0/DI1)
- Dynamic item list with match indicators
- Proper cleanup of RFID connections
- Thread-safe UI updates via GLib.idle_add
