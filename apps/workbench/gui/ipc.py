"""Unix socket IPC server for remote control of the workbench GUI."""

import os
import socket
import threading

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

SOCK_PATH = "/tmp/feralboard-workbench.sock"


class IpcServer:
    """Unix socket server for remote commands."""

    def __init__(self, app_window):
        self.app = app_window
        self._thread = None

    def start(self):
        self._thread = threading.Thread(target=self._listen, daemon=True)
        self._thread.start()

    def _listen(self):
        if os.path.exists(SOCK_PATH):
            os.remove(SOCK_PATH)

        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(SOCK_PATH)
        os.chmod(SOCK_PATH, 0o777)
        server.listen(5)
        print(f"IPC listening on {SOCK_PATH}")

        while True:
            conn, _ = server.accept()
            try:
                data = conn.recv(4096).decode().strip()
                response = self._handle(data)
                conn.sendall(response.encode())
            except Exception as e:
                conn.sendall(f"ERROR: {e}\n".encode())
            finally:
                conn.close()

    def _handle(self, data: str) -> str:
        parts = data.split()
        if not parts:
            return "ERROR: empty command\n"

        cmd = parts[0].lower()

        if cmd == "navigate" and len(parts) >= 2:
            page = parts[1].lower()
            static_pages = ("home", "outputs", "inputs", "tests", "wifi", "ethernet", "system", "kiosk", "pin", "apps", "rfid")
            if page in static_pages or page == self.app._dynamic_page_name:
                GLib.idle_add(self.app.navigate_to, page)
                return f"OK: navigated to {page}\n"
            return f"ERROR: unknown page '{page}'\n"

        elif cmd == "page":
            name = self.app.stack.get_visible_child_name()
            return f"OK: {name}\n"

        elif cmd == "size":
            alloc = self.app.get_allocation()
            return f"OK: {alloc.width} {alloc.height}\n"

        elif cmd == "screenshot":
            return "OK: use scripts/screenshot.sh instead\n"

        elif cmd == "click" and len(parts) == 3:
            try:
                x, y = int(float(parts[1])), int(float(parts[2]))
            except ValueError:
                return "ERROR: click X Y requires numeric coordinates\n"
            GLib.idle_add(self._simulate_click_at, x, y)
            return f"OK: click at ({x}, {y})\n"

        elif cmd == "widgets":
            lines = []
            self._list_widgets(self.app, lines)
            if not lines:
                return "OK: no interactive widgets visible\n"
            return "OK:\n" + "\n".join(lines) + "\n"

        elif cmd == "lock":
            GLib.idle_add(self.app.navigate_to, "kiosk")
            return "OK: locked\n"

        elif cmd == "unlock":
            GLib.idle_add(self.app.navigate_to, "pin")
            return "OK: showing PIN page\n"

        elif cmd == "help":
            return (
                "Commands:\n"
                "  navigate <page>  - switch page (static + loaded dynamic pages)\n"
                "  click X Y - simulate click at pixel coordinates\n"
                "  widgets    - list visible buttons/switches with coordinates\n"
                "  connect    - open serial connection\n"
                "  disconnect - close serial connection\n"
                "  toggle <DOx> <on|off>  - toggle output channel\n"
                "  lock       - go to kiosk lock screen\n"
                "  unlock     - go to PIN entry page\n"
                "  page       - get current page name\n"
                "  size       - get window size\n"
                "  help       - show this\n"
            )

        elif cmd == "connect":
            GLib.idle_add(self.app._connect)
            return "OK: connect requested\n"

        elif cmd == "disconnect":
            GLib.idle_add(self.app._disconnect)
            return "OK: disconnect requested\n"

        elif cmd == "run-test" and len(parts) >= 2:
            test = parts[1].lower()
            tp = self.app.tests_page
            if test in ("outputs", "output"):
                GLib.idle_add(tp._on_run_outputs, None)
                return "OK: running output test\n"
            elif test in ("inputs", "input"):
                GLib.idle_add(tp._on_run_inputs, None)
                return "OK: running input test\n"
            return f"ERROR: unknown test '{test}'. Use outputs or inputs\n"

        elif cmd == "toggle" and len(parts) >= 3:
            channel = parts[1].upper()
            state = parts[2].lower() in ("on", "1", "true")
            card = self.app.outputs_page.cards.get(channel)
            if not card:
                return f"ERROR: unknown channel '{channel}'\n"
            GLib.idle_add(self._do_toggle, channel, card, state)
            return f"OK: {channel} {'ON' if state else 'OFF'}\n"

        return f"ERROR: unknown '{data}'. Try 'help'\n"

    def _list_widgets(self, widget, lines, depth=0):
        """Collect all visible interactive widgets with their positions."""
        if not widget.get_visible():
            return
        if isinstance(widget, (Gtk.Button, Gtk.Switch, Gtk.ToggleButton)):
            alloc = widget.get_allocation()
            toplevel = widget.get_toplevel()
            result = widget.translate_coordinates(toplevel, 0, 0)
            if result is not None:
                tx, ty = result
                cx = tx + alloc.width // 2
                cy = ty + alloc.height // 2
                label = ""
                if isinstance(widget, (Gtk.Button, Gtk.ToggleButton)):
                    label = widget.get_label() or ""
                    if not label:
                        child = widget.get_child()
                        if child:
                            label = self._get_widget_text(child)
                kind = type(widget).__name__
                lines.append(
                    f"  {kind} '{label}' center=({cx},{cy}) "
                    f"rect=({tx},{ty},{alloc.width},{alloc.height})"
                )
        # Recurse into all containers (Button is also a Container/Bin)
        if isinstance(widget, Gtk.Container):
            for child in widget.get_children():
                self._list_widgets(child, lines, depth + 1)

    @staticmethod
    def _get_widget_text(widget):
        """Extract text from a widget tree (labels inside buttons)."""
        if isinstance(widget, Gtk.Label):
            return widget.get_text() or widget.get_label() or ""
        if isinstance(widget, Gtk.Container):
            for child in widget.get_children():
                text = IpcServer._get_widget_text(child)
                if text:
                    return text
        return ""

    def _do_toggle(self, channel, card, state):
        card.set_active(state)
        self.app._on_output_toggle(channel, state)

    def _simulate_click_at(self, x, y):
        """Find the widget at (x, y) and activate it if it's a button/switch."""
        widget = self._find_widget_at(self.app, x, y)
        if widget and isinstance(widget, (Gtk.RadioButton, Gtk.ToggleButton)):
            # Radio/toggle buttons need set_active to properly trigger toggled signal
            widget.set_active(not widget.get_active())
            label = widget.get_label() or "unlabeled"
            print(f"Toggled {type(widget).__name__} at ({x}, {y}): {label}")
        elif widget and isinstance(widget, Gtk.Button):
            widget.clicked()
            label = widget.get_label() or "unlabeled"
            print(f"Clicked button at ({x}, {y}): {label}")
        elif widget and isinstance(widget, Gtk.Switch):
            widget.set_active(not widget.get_active())
            widget.emit("state-set", widget.get_active())
            print(f"Toggled switch at ({x}, {y})")
        else:
            name = type(widget).__name__ if widget else "None"
            print(f"Click at ({x}, {y}): no interactive widget (got {name})")

    def _widget_contains_point(self, widget, x, y):
        """Check if toplevel point (x, y) is within widget bounds."""
        toplevel = widget.get_toplevel()
        # Translate (x,y) from toplevel coords to widget-local coords
        result = toplevel.translate_coordinates(widget, x, y)
        if result is None:
            return False
        local_x, local_y = result
        alloc = widget.get_allocation()
        return 0 <= local_x <= alloc.width and 0 <= local_y <= alloc.height

    def _find_widget_at(self, widget, x, y):
        """Recursively find the deepest visible interactive widget at screen (x, y)."""
        if not widget.get_visible() or not widget.get_mapped():
            return None

        # Check if point is within this widget's bounds
        if widget != self.app:  # skip bounds check for toplevel
            if not self._widget_contains_point(widget, x, y):
                return None

        # Recurse into children (deepest match wins)
        best = None
        if isinstance(widget, Gtk.Container):
            for child in widget.get_children():
                result = self._find_widget_at(child, x, y)
                if result and isinstance(result, (Gtk.Button, Gtk.Switch)):
                    best = result

        if best:
            return best

        # Return self if interactive and point is within
        if isinstance(widget, (Gtk.Button, Gtk.Switch)):
            return widget

        return None

    @staticmethod
    def cleanup():
        if os.path.exists(SOCK_PATH):
            os.remove(SOCK_PATH)
