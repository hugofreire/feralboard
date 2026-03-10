#!/usr/bin/env python3
"""FeralBoard Workbench — GTK3 app for interactive FeralBoard I/O testing."""

import importlib
import json
import os
import subprocess
import sys
import time
import glob

# Ensure lib/ is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("WAYLAND_DISPLAY", "wayland-1")
os.environ.setdefault("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

from lib.serial_comm import SerialCommunicator
from lib.protocol import CMD_FACTORY_MODE
from gui.serial_bridge import SerialBridge
from gui.pages.home import HomePage
from gui.pages.outputs import OutputsPage
from gui.pages.inputs import InputsPage
from gui.pages.tests import TestsPage
from gui.pages.builder_portal import BuilderPortalPage
from gui.pages.wifi import WifiPage
from gui.pages.ethernet import EthernetPage
from gui.pages.system import SystemPage
from gui.pages.kiosk import KioskPage
from gui.pages.pin import PinPage
from gui.pages.apps import AppsPage
from gui.pages.rfid import RfidPage
from gui.ipc import IpcServer


class ClampBox(Gtk.Box):
    """Box that clamps its allocation width to a maximum value."""

    def __init__(self, max_width, **kwargs):
        super().__init__(**kwargs)
        self._max_width = max_width

    def do_size_allocate(self, allocation):
        allocation.width = min(allocation.width, self._max_width)
        Gtk.Box.do_size_allocate(self, allocation)


class WorkbenchWindow(Gtk.Window):
    """Main application window with Gtk.Stack page navigation."""

    def __init__(self):
        super().__init__(title="FeralBoard Workbench")
        self.set_border_width(0)

        # Query actual Sway output size (GTK3 mishandles fractional scaling)
        self._display_w, self._display_h = self._get_sway_output_size()
        self.fullscreen()

        # Dark theme
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme", True)

        # Load CSS
        css_path = os.path.join(os.path.dirname(__file__), "style.css")
        if os.path.exists(css_path):
            css = Gtk.CssProvider()
            css.load_from_path(css_path)
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(), css,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

        # Serial state
        self.comm = None
        self.bridge = None

        # No window decorations (header packed as regular widget)
        self.set_decorated(False)

        # Main layout — clamp width to actual display
        # (GTK3 fullscreen allocates wrong width with fractional Wayland scaling)
        main_box = ClampBox(self._display_w,
                            orientation=Gtk.Orientation.VERTICAL)

        # Stack for pages
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(200)

        # Build pages
        self.home_page = HomePage(
            on_connect=self._connect,
            on_disconnect=self._disconnect,
            on_factory_mode=self._send_factory_mode,
            on_navigate=self.navigate_to,
            on_lock=lambda: self.navigate_to("kiosk"),
        )
        go_home = lambda: self.navigate_to("home")
        self.outputs_page = OutputsPage(on_toggle=self._on_output_toggle, on_back=go_home)
        self.inputs_page = InputsPage(on_back=go_home)
        self.tests_page = TestsPage(on_back=go_home)
        self.builder_portal_page = BuilderPortalPage(on_back=go_home)
        self.wifi_page = WifiPage(on_back=go_home)
        self.ethernet_page = EthernetPage(on_back=go_home)
        self.system_page = SystemPage(on_back=go_home)
        self.kiosk_page = KioskPage(on_unlock=lambda: self.navigate_to("pin"))
        self.pin_page = PinPage(
            on_success=lambda: self.navigate_to("home"),
            on_back=lambda: self.navigate_to("kiosk"),
        )
        self.apps_page = AppsPage(
            on_back=go_home,
            on_app_selected=self._on_app_selected,
        )
        self.rfid_page = RfidPage(on_back=go_home)

        # Dynamic kiosk app page (loaded on demand via _on_app_selected)
        self._dynamic_page = None
        self._dynamic_page_name = None

        self.stack.add_named(self.home_page, "home")
        self.stack.add_named(self.outputs_page, "outputs")
        self.stack.add_named(self.inputs_page, "inputs")
        self.stack.add_named(self.tests_page, "tests")
        self.stack.add_named(self.builder_portal_page, "builder-portal")
        self.stack.add_named(self.wifi_page, "wifi")
        self.stack.add_named(self.ethernet_page, "ethernet")
        self.stack.add_named(self.system_page, "system")
        self.stack.add_named(self.kiosk_page, "kiosk")
        self.stack.add_named(self.pin_page, "pin")
        self.stack.add_named(self.apps_page, "apps")
        self.stack.add_named(self.rfid_page, "rfid")

        main_box.pack_start(self.stack, True, True, 0)
        self.add(main_box)

        # Keyboard
        self.connect("key-press-event", self._on_key_press)
        self.connect("destroy", self._on_destroy)

        # Stats update timer
        self._stats_timer = GLib.timeout_add(500, self._update_stats)

        # IPC server
        self.ipc = IpcServer(self)
        self.ipc.start()

    @staticmethod
    def _get_sway_output_size():
        """Query Sway for the focused output's logical size."""
        try:
            out = subprocess.check_output(
                ["swaymsg", "-t", "get_outputs"], timeout=2
            )
            for output in json.loads(out):
                if output.get("focused"):
                    rect = output["rect"]
                    return rect["width"], rect["height"]
        except Exception:
            pass
        return 480, 819  # fallback

    def navigate_to(self, page_name: str):
        """Switch to a page by name."""
        current = self.stack.get_visible_child_name()
        if current == "rfid" and page_name != "rfid":
            self.rfid_page.cleanup()
        if (self._dynamic_page
                and current == self._dynamic_page_name
                and page_name != self._dynamic_page_name):
            self._dynamic_page.cleanup()
        self.stack.set_visible_child_name(page_name)
        if page_name == "wifi":
            self.wifi_page.refresh()
        elif page_name == "builder-portal":
            self.builder_portal_page.refresh()
        elif page_name == "ethernet":
            self.ethernet_page.refresh()
        elif page_name == "system":
            self.system_page.refresh()
        elif page_name == "apps":
            self.apps_page.refresh()
        elif page_name == "rfid":
            self.rfid_page.refresh()
        elif page_name == "pin":
            self.pin_page.reset()

    def _on_app_selected(self, app_info):
        """Handle app selection from apps page."""
        page_name = app_info.get("page")
        if page_name:
            self._load_dynamic_page(page_name, app_info)
        else:
            self.kiosk_page.set_greeting(
                app_info.get("greeting", app_info.get("name", ""))
            )
            self.navigate_to("kiosk")

    def _load_dynamic_page(self, page_name, app_info):
        """Dynamically import, instantiate, and show a kiosk app page."""
        if self._dynamic_page and self._dynamic_page_name != page_name:
            self._cleanup_dynamic_page()

        if not self._dynamic_page:
            try:
                module = importlib.import_module(f"gui.pages.{page_name}")
            except ImportError as e:
                print(f"Failed to import gui.pages.{page_name}: {e}")
                return
            class_name = page_name.capitalize() + "Page"
            page_class = getattr(module, class_name, None)
            if page_class is None:
                print(f"gui.pages.{page_name} has no class {class_name}")
                return
            self._dynamic_page = page_class(
                on_unlock=lambda: self.navigate_to("home"),
            )
            self._dynamic_page_name = page_name
            self.stack.add_named(self._dynamic_page, page_name)
            self._dynamic_page.show_all()

        self._dynamic_page.load_app(app_info)
        self.navigate_to(page_name)

    def _cleanup_dynamic_page(self):
        """Clean up and remove the current dynamic page from the stack."""
        if self._dynamic_page:
            if hasattr(self._dynamic_page, "cleanup"):
                self._dynamic_page.cleanup()
            self.stack.remove(self._dynamic_page)
            self._dynamic_page.destroy()
            self._dynamic_page = None
            self._dynamic_page_name = None

    @staticmethod
    def _get_default_serial_port() -> str:
        ports = sorted(glob.glob("/dev/ttyAMA*"))
        for port in ports:
            if port.endswith("ttyAMA0"):
                return port
        return ports[0] if ports else ""

    def _connect(self):
        """Open serial port and start communication."""
        port = self._get_default_serial_port()
        if not port:
            return

        if self.comm:
            self._disconnect()

        self.comm = SerialCommunicator(port)
        if not self.comm.open():
            self.comm = None
            return

        self.comm.start()
        self.bridge = SerialBridge(self.comm)
        self.bridge.on_state_changed(self._on_rx_update)
        self.bridge.start()
        self.home_page.set_connected(True)

    def _disconnect(self):
        """Stop communication and close serial port."""
        if self.bridge:
            self.bridge.stop()
            self.bridge = None
        if self.comm:
            self.comm.clear_all_outputs()
            time.sleep(0.3)
            self.comm.stop()
            self.comm.close()
            self.comm = None
        self.home_page.set_connected(False)

    def _send_factory_mode(self):
        """Send factory mode command."""
        if self.bridge:
            self.bridge.send_command(CMD_FACTORY_MODE)

    def _on_output_toggle(self, channel_name, state):
        """Handle output toggle from the outputs page."""
        if not self.bridge:
            return
        if channel_name is None:
            # Clear all
            self.bridge.clear_all_outputs()
        else:
            self.bridge.set_output(channel_name, state)

    def _on_rx_update(self, rx_buffer: bytes):
        """Called by SerialBridge when RX state changes."""
        self.home_page.update_from_rx(rx_buffer)
        self.outputs_page.update_from_rx(rx_buffer)
        self.inputs_page.update_from_rx(rx_buffer)
        if (self._dynamic_page
                and hasattr(self._dynamic_page, "update_from_rx")
                and self.stack.get_visible_child_name() == self._dynamic_page_name):
            self._dynamic_page.update_from_rx(rx_buffer)

    def _update_stats(self):
        """Periodic stats update for the home page."""
        if self.comm:
            tx, rx, errors = self.comm.get_stats()
            self.home_page.update_stats(tx, rx, errors)
        return True

    def _on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self._on_destroy(widget)
            Gtk.main_quit()
            return True
        return False

    def _on_destroy(self, widget):
        self._disconnect()
        self.rfid_page.cleanup()
        self._cleanup_dynamic_page()
        IpcServer.cleanup()


def main():
    win = WorkbenchWindow()
    win.show_all()

    # Check for a default kiosk app to load on startup
    default_app_file = os.path.join(os.path.dirname(__file__), "..", ".default_app")
    if os.path.exists(default_app_file):
        try:
            slug = open(default_app_file).read().strip()
            manifest_path = os.path.join(
                os.path.dirname(__file__), "..", "kiosk_apps", slug, "app.json"
            )
            if slug and os.path.exists(manifest_path):
                app_info = json.load(open(manifest_path))
                win._on_app_selected(app_info)
            else:
                win.navigate_to("kiosk")
        except Exception as e:
            print(f"Failed to load default app: {e}")
            win.navigate_to("kiosk")
    else:
        win.navigate_to("kiosk")

    # Auto-connect to the default serial port on startup (after GTK loop starts)
    GLib.idle_add(win._connect)

    try:
        Gtk.main()
    except KeyboardInterrupt:
        pass
    finally:
        win._on_destroy(win)


if __name__ == "__main__":
    main()
