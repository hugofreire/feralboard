"""Home page: friendly main screen with large navigation buttons and board status."""

import struct

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from lib.protocol import (
    RX_MAIN_TEMP_OFFSET, RX_PCB_TEMP, RX_ERROR_FLAGS, RX_MODE_STATE,
    bytes_to_float, get_door_state,
    DOOR_STATE_UNKNOWN, DOOR_STATE_OPEN, DOOR_STATE_INTERMEDIATE, DOOR_STATE_CLOSED,
    CMD_FACTORY_MODE,
)


DOOR_STATE_NAMES = {
    DOOR_STATE_UNKNOWN: "UNKNOWN",
    DOOR_STATE_OPEN: "OPEN",
    DOOR_STATE_INTERMEDIATE: "INTERMEDIATE",
    DOOR_STATE_CLOSED: "CLOSED",
}


class HomePage(Gtk.Box):
    """Home page with friendly navigation and board status."""

    def __init__(self, on_connect=None, on_disconnect=None, on_factory_mode=None,
                 on_navigate=None, on_lock=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect
        self._on_factory_mode = on_factory_mode
        self._on_navigate = on_navigate
        self._on_lock = on_lock

        # Scrollable so content fits on small screens
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.set_vexpand(True)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # ── Title area ──
        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        title_box.set_valign(Gtk.Align.CENTER)
        title_box.set_margin_top(24)
        title_box.set_margin_bottom(12)

        title = Gtk.Label()
        title.set_markup(
            '<span size="26000" weight="bold" foreground="white">'
            'FeralBoard</span>'
        )
        title_box.pack_start(title, False, False, 0)

        subtitle = Gtk.Label()
        subtitle.set_markup(
            '<span size="12000" foreground="#888888">Workbench</span>'
        )
        title_box.pack_start(subtitle, False, False, 0)

        content.pack_start(title_box, False, False, 0)

        # ── Connection status ──
        status_row = Gtk.Box(spacing=8)
        status_row.set_halign(Gtk.Align.CENTER)
        status_row.set_margin_bottom(8)

        self.status_label = Gtk.Label()
        self.status_label.set_markup(
            '<span size="12000" foreground="#e74c3c">Disconnected</span>'
        )
        status_row.pack_start(self.status_label, False, False, 0)

        content.pack_start(status_row, False, False, 0)

        # ── Connect / Disconnect / Factory buttons ──
        ctrl_box = Gtk.Box(spacing=8)
        ctrl_box.set_halign(Gtk.Align.CENTER)
        ctrl_box.set_margin_bottom(16)

        self.connect_btn = Gtk.Button(label="Connect")
        self.connect_btn.get_style_context().add_class("suggested-action")
        self.connect_btn.connect("clicked", self._on_connect_clicked)
        ctrl_box.pack_start(self.connect_btn, False, False, 0)

        self.disconnect_btn = Gtk.Button(label="Disconnect")
        self.disconnect_btn.set_sensitive(False)
        self.disconnect_btn.connect("clicked", self._on_disconnect_clicked)
        ctrl_box.pack_start(self.disconnect_btn, False, False, 0)

        self.factory_btn = Gtk.Button(label="Factory")
        self.factory_btn.set_sensitive(False)
        self.factory_btn.connect("clicked", self._on_factory_clicked)
        ctrl_box.pack_start(self.factory_btn, False, False, 0)

        lock_btn = Gtk.Button(label="Lock")
        lock_btn.get_style_context().add_class("destructive-action")
        lock_btn.connect("clicked", lambda w: self._on_lock() if self._on_lock else None)
        ctrl_box.pack_start(lock_btn, False, False, 0)

        content.pack_start(ctrl_box, False, False, 0)

        content.pack_start(Gtk.Separator(), False, False, 0)

        # ── Navigation grid — 2 columns of big buttons ──
        nav_grid = Gtk.Grid()
        nav_grid.set_row_spacing(12)
        nav_grid.set_column_spacing(12)
        nav_grid.set_margin_start(16)
        nav_grid.set_margin_end(16)
        nav_grid.set_margin_top(16)
        nav_grid.set_margin_bottom(16)
        nav_grid.set_column_homogeneous(True)

        nav_items = [
            ("outputs", "Outputs", "DO0-DO11", "preferences-desktop-peripherals-symbolic"),
            ("inputs", "Inputs", "DI0-DI7", "view-list-symbolic"),
            ("tests", "Tests", "E2E", "system-run-symbolic"),
            ("wifi", "WiFi", "Networks", "network-wireless-symbolic"),
            ("ethernet", "Ethernet", "IP Config", "network-wired-symbolic"),
            ("system", "System", "Monitor", "utilities-system-monitor-symbolic"),
            ("apps", "Apps", "Kiosk Apps", "application-x-executable-symbolic"),
            ("rfid", "RFID", "FX9600", "network-transmit-receive-symbolic"),
        ]

        for i, (page, label, desc, icon) in enumerate(nav_items):
            btn = self._make_nav_button(page, label, desc, icon)
            row = i // 2
            col = i % 2
            nav_grid.attach(btn, col, row, 1, 1)

        content.pack_start(nav_grid, False, False, 0)

        content.pack_start(Gtk.Separator(), False, False, 0)

        # ── Board status section ──
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        info_box.set_margin_start(16)
        info_box.set_margin_end(16)
        info_box.set_margin_top(8)
        info_box.set_margin_bottom(16)

        info_title = Gtk.Label()
        info_title.set_markup(
            '<span size="13000" weight="bold" foreground="#a0a0a0">'
            'Board Status</span>'
        )
        info_title.set_halign(Gtk.Align.START)
        info_box.pack_start(info_title, False, False, 0)

        grid = Gtk.Grid()
        grid.set_column_spacing(16)
        grid.set_row_spacing(4)

        labels = [
            "Main Temperature:",
            "PCB Temperature:",
            "Door State:",
            "Error Byte:",
            "Factory Mode:",
            "TX Count:",
            "RX Count:",
            "Errors:",
        ]
        self.value_labels = {}
        for i, text in enumerate(labels):
            lbl = Gtk.Label(label=text)
            lbl.set_halign(Gtk.Align.START)
            lbl.get_style_context().add_class("section-title")
            grid.attach(lbl, 0, i, 1, 1)

            val = Gtk.Label(label="--")
            val.set_halign(Gtk.Align.START)
            grid.attach(val, 1, i, 1, 1)
            self.value_labels[text] = val

        info_box.pack_start(grid, False, False, 0)
        content.pack_start(info_box, False, False, 0)

        sw.add(content)
        self.pack_start(sw, True, True, 0)

    def _make_nav_button(self, page_name, label_text, description, icon_name):
        """Create a large navigation button with icon and description."""
        btn = Gtk.Button()
        btn.get_style_context().add_class("nav-card")
        btn.set_size_request(-1, 90)
        btn.connect("clicked", lambda w: self._navigate(page_name))

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        vbox.set_valign(Gtk.Align.CENTER)

        # Icon row
        hbox = Gtk.Box(spacing=8)
        hbox.set_halign(Gtk.Align.CENTER)

        try:
            icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)
            hbox.pack_start(icon, False, False, 0)
        except Exception:
            pass

        name_lbl = Gtk.Label()
        name_lbl.set_markup(
            f'<span size="14000" weight="bold">{label_text}</span>'
        )
        hbox.pack_start(name_lbl, False, False, 0)

        vbox.pack_start(hbox, False, False, 0)

        # Description
        desc_lbl = Gtk.Label()
        desc_lbl.set_markup(
            f'<span size="9000" foreground="#a78bfa">{description}</span>'
        )
        vbox.pack_start(desc_lbl, False, False, 0)

        btn.add(vbox)
        return btn

    def _navigate(self, page_name):
        if self._on_navigate:
            self._on_navigate(page_name)

    def _on_connect_clicked(self, widget):
        if self._on_connect:
            self._on_connect()

    def _on_disconnect_clicked(self, widget):
        if self._on_disconnect:
            self._on_disconnect()

    def _on_factory_clicked(self, widget):
        if self._on_factory_mode:
            self._on_factory_mode()

    def set_connected(self, connected: bool):
        if connected:
            self.status_label.set_markup(
                '<span size="12000" foreground="#2ecc71">Connected</span>'
            )
            self.connect_btn.set_sensitive(False)
            self.disconnect_btn.set_sensitive(True)
            self.factory_btn.set_sensitive(True)
        else:
            self.status_label.set_markup(
                '<span size="12000" foreground="#e74c3c">Disconnected</span>'
            )
            self.connect_btn.set_sensitive(True)
            self.disconnect_btn.set_sensitive(False)
            self.factory_btn.set_sensitive(False)
            for val in self.value_labels.values():
                val.set_text("--")

    def update_from_rx(self, rx_buffer: bytes):
        """Update board info from RX buffer."""
        main_temp = bytes_to_float(rx_buffer, RX_MAIN_TEMP_OFFSET)
        pcb_temp = rx_buffer[RX_PCB_TEMP]
        error_byte = rx_buffer[RX_ERROR_FLAGS]
        door = get_door_state(rx_buffer)
        factory = (rx_buffer[RX_MODE_STATE] >> 0) & 1

        self.value_labels["Main Temperature:"].set_text(f"{main_temp:.1f} C")
        self.value_labels["PCB Temperature:"].set_text(f"{pcb_temp} C")
        self.value_labels["Door State:"].set_text(DOOR_STATE_NAMES.get(door, "?"))
        self.value_labels["Error Byte:"].set_text(
            f"0x{error_byte:02X} ({error_byte:08b})"
        )
        self.value_labels["Factory Mode:"].set_text("ON" if factory else "OFF")

    def update_stats(self, tx_count: int, rx_count: int, errors: int):
        self.value_labels["TX Count:"].set_text(str(tx_count))
        self.value_labels["RX Count:"].set_text(str(rx_count))
        self.value_labels["Errors:"].set_text(str(errors))
