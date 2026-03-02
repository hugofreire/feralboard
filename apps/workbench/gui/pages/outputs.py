"""Outputs page: 12 toggle cards for DO0-DO11 with echo feedback."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from lib.io_map import OUTPUTS
from gui.widgets.toggle_card import ToggleCard


class OutputsPage(Gtk.Box):
    """Page with 12 ToggleCard widgets in a 3-column grid."""

    def __init__(self, on_toggle=None, on_back=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.set_margin_start(8)
        self.set_margin_end(8)
        self.set_margin_top(8)

        self._on_toggle = on_toggle
        self._on_back = on_back

        # Title row with back button
        title_row = Gtk.Box(spacing=8)
        title_row.set_margin_start(4)
        back_btn = Gtk.Button(label="\u2190")
        back_btn.set_size_request(36, 36)
        back_btn.connect("clicked", lambda w: self._on_back() if self._on_back else None)
        title_row.pack_start(back_btn, False, False, 0)
        title = Gtk.Label()
        title.set_markup('<span size="16000" weight="bold">Digital Outputs</span>')
        title.set_valign(Gtk.Align.CENTER)
        title_row.pack_start(title, False, False, 0)
        self.pack_start(title_row, False, False, 0)

        # Clear all button
        btn_box = Gtk.Box(spacing=8)
        btn_box.set_margin_start(8)
        self.clear_btn = Gtk.Button(label="Clear All")
        self.clear_btn.connect("clicked", self._on_clear_all)
        btn_box.pack_start(self.clear_btn, False, False, 0)
        self.pack_start(btn_box, False, False, 0)

        # Scrolled container for the grid
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.set_vexpand(True)

        # Grid: 3 columns
        self.grid = Gtk.Grid()
        self.grid.set_column_spacing(4)
        self.grid.set_row_spacing(4)
        self.grid.set_column_homogeneous(True)
        self.grid.set_margin_start(4)
        self.grid.set_margin_end(4)

        self.cards = {}
        for i, (name, tx_byte, bit_idx, rx_echo_byte) in enumerate(OUTPUTS):
            card = ToggleCard(name, on_toggle=self._handle_toggle)
            col = i % 3
            row = i // 3
            self.grid.attach(card, col, row, 1, 1)
            self.cards[name] = card

        sw.add(self.grid)
        self.pack_start(sw, True, True, 0)

        self.show_all()

    def _handle_toggle(self, channel_name: str, state: bool):
        if self._on_toggle:
            self._on_toggle(channel_name, state)

    def _on_clear_all(self, widget):
        for card in self.cards.values():
            card.set_active(False)
        if self._on_toggle:
            self._on_toggle(None, False)  # None = clear all

    def update_from_rx(self, rx_buffer: bytes):
        """Update echo indicators from RX buffer."""
        for name, tx_byte, bit_idx, rx_echo_byte in OUTPUTS:
            card = self.cards[name]
            tx_on = card.switch.get_active()
            rx_on = (rx_buffer[rx_echo_byte] >> bit_idx) & 1 == 1
            card.set_echo(tx_on, rx_on)
