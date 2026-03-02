"""Custom header bar with page navigation buttons and serial port selector."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import glob


class WorkbenchHeaderBar(Gtk.HeaderBar):
    """Header bar with nav buttons and serial port combo box."""

    def __init__(self, on_navigate=None, on_port_changed=None):
        super().__init__()
        self.set_show_close_button(False)
        self.set_title("FeralBoard Workbench")

        self._on_navigate = on_navigate
        self._on_port_changed = on_port_changed

        # Navigation buttons
        nav_box = Gtk.Box(spacing=4)

        self.nav_buttons = {}
        nav_pages = [
            ("Home", "home"),
            ("Outputs", "outputs"),
            ("Inputs", "inputs"),
            ("Tests", "tests"),
            ("WiFi", "wifi"),
            ("Eth", "ethernet"),
            ("Sys", "system"),
            ("Apps", "apps"),
            ("RFID", "rfid"),
        ]
        for label, page_key in nav_pages:
            btn = Gtk.ToggleButton(label=label)
            btn.connect("toggled", self._on_nav_toggled, page_key)
            nav_box.pack_start(btn, False, False, 0)
            self.nav_buttons[page_key] = btn

        self.pack_start(nav_box)

        # Serial port combo
        self.port_combo = Gtk.ComboBoxText()
        self.port_combo.set_size_request(140, -1)
        self.port_combo.connect("changed", self._on_port_combo_changed)
        self.pack_end(self.port_combo)

        self.refresh_ports()
        self.set_active_page("home")

    def _on_nav_toggled(self, button, page_name):
        if button.get_active():
            # Deactivate other nav buttons
            for name, btn in self.nav_buttons.items():
                if name != page_name:
                    btn.handler_block_by_func(self._on_nav_toggled)
                    btn.set_active(False)
                    btn.handler_unblock_by_func(self._on_nav_toggled)
            if self._on_navigate:
                self._on_navigate(page_name)

    def set_active_page(self, page_name: str):
        """Programmatically set the active page button."""
        for name, btn in self.nav_buttons.items():
            btn.handler_block_by_func(self._on_nav_toggled)
            btn.set_active(name == page_name)
            btn.handler_unblock_by_func(self._on_nav_toggled)

    def _on_port_combo_changed(self, combo):
        port = combo.get_active_text()
        if port and self._on_port_changed:
            self._on_port_changed(port)

    def refresh_ports(self):
        """Re-scan available serial ports and populate the combo box."""
        self.port_combo.remove_all()
        ports = sorted(glob.glob("/dev/ttyAMA*"))
        for port in ports:
            self.port_combo.append_text(port)
        # Default to /dev/ttyAMA0 (serial comms) or first available
        for i, port in enumerate(ports):
            if "ttyAMA0" in port:
                self.port_combo.set_active(i)
                return
        if ports:
            self.port_combo.set_active(0)

    def get_selected_port(self) -> str:
        return self.port_combo.get_active_text() or ""
