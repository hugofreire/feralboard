"""Inputs page: 8 input indicators for DI0-DI7 with live state."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from lib.io_map import INPUTS, INPUT_LEGACY_NAMES
from gui.widgets.input_card import InputCard


class InputsPage(Gtk.Box):
    """Page with 8 InputCard widgets showing live DI0-DI7 state."""

    def __init__(self, on_back=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.set_margin_start(8)
        self.set_margin_end(8)
        self.set_margin_top(8)

        self._on_back = on_back

        # Title row with back button
        title_row = Gtk.Box(spacing=8)
        title_row.set_margin_start(4)
        back_btn = Gtk.Button(label="\u2190")
        back_btn.set_size_request(36, 36)
        back_btn.connect("clicked", lambda w: self._on_back() if self._on_back else None)
        title_row.pack_start(back_btn, False, False, 0)
        title = Gtk.Label()
        title.set_markup('<span size="16000" weight="bold">Digital Inputs</span>')
        title.set_valign(Gtk.Align.CENTER)
        title_row.pack_start(title, False, False, 0)
        self.pack_start(title_row, False, False, 0)

        # Raw byte display
        self.byte_label = Gtk.Label()
        self.byte_label.set_markup(
            '<span size="11000" foreground="#888888">Byte 4: -- (--------)</span>'
        )
        self.byte_label.set_halign(Gtk.Align.START)
        self.byte_label.set_margin_start(8)
        self.pack_start(self.byte_label, False, False, 0)

        # Scrolled container
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.set_vexpand(True)

        # 2-column grid
        self.grid = Gtk.Grid()
        self.grid.set_column_spacing(8)
        self.grid.set_row_spacing(8)
        self.grid.set_column_homogeneous(True)
        self.grid.set_margin_start(4)
        self.grid.set_margin_end(4)

        self.cards = {}
        for i, (name, rx_byte, bit_idx) in enumerate(INPUTS):
            legacy = INPUT_LEGACY_NAMES.get(name, "")
            display_name = f"{name} - {legacy}" if legacy else name
            card = InputCard(display_name)
            col = i % 2
            row = i // 2
            self.grid.attach(card, col, row, 1, 1)
            self.cards[name] = card

        sw.add(self.grid)
        self.pack_start(sw, True, True, 0)

        self.show_all()

    def update_from_rx(self, rx_buffer: bytes):
        """Update input indicators from RX buffer."""
        input_byte = rx_buffer[4]
        self.byte_label.set_markup(
            f'<span size="11000" foreground="#888888">'
            f'Byte 4: 0x{input_byte:02X} ({input_byte:08b})</span>'
        )
        for name, rx_byte, bit_idx in INPUTS:
            card = self.cards[name]
            high = (rx_buffer[rx_byte] >> bit_idx) & 1 == 1
            card.set_state(high)
