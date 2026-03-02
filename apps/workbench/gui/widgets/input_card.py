"""Reusable DI indicator widget: label + colored status dot."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class InputCard(Gtk.Box):
    """A card for a digital input: channel label and colored status circle."""

    def __init__(self, channel_name: str):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.get_style_context().add_class("input-card")
        self.set_margin_start(2)
        self.set_margin_end(2)
        self.set_margin_top(2)
        self.set_margin_bottom(2)

        self.channel_name = channel_name

        # Status dot
        self.dot = Gtk.Label()
        self.dot.set_markup(
            '<span size="18000" foreground="#555555">\u25CF</span>'
        )
        self.dot.set_valign(Gtk.Align.CENTER)
        self.pack_start(self.dot, False, False, 4)

        # Info column
        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
        info.set_valign(Gtk.Align.CENTER)

        self.label = Gtk.Label()
        self.label.set_markup(
            f'<span weight="bold" size="10000">{channel_name}</span>'
        )
        self.label.set_halign(Gtk.Align.START)
        self.label.set_ellipsize(3)  # PANGO_ELLIPSIZE_END
        info.pack_start(self.label, False, False, 0)

        self.state_label = Gtk.Label()
        self.state_label.set_markup(
            '<span size="10000" foreground="#888888">--</span>'
        )
        self.state_label.set_halign(Gtk.Align.START)
        info.pack_start(self.state_label, False, False, 0)

        self.pack_start(info, True, True, 0)

        # Bit value display
        self.bit_label = Gtk.Label()
        self.bit_label.set_markup(
            '<span size="11000" foreground="#888888">-</span>'
        )
        self.bit_label.set_valign(Gtk.Align.CENTER)
        self.pack_end(self.bit_label, False, False, 8)

        self.show_all()

    def set_state(self, high: bool):
        """Update the indicator: green dot for HIGH, gray for LOW."""
        if high:
            self.dot.set_markup(
                '<span size="18000" foreground="#2ecc71">\u25CF</span>'
            )
            self.state_label.set_markup(
                '<span size="10000" foreground="#2ecc71">HIGH</span>'
            )
            self.bit_label.set_markup(
                '<span size="11000" foreground="#2ecc71">1</span>'
            )
        else:
            self.dot.set_markup(
                '<span size="18000" foreground="#555555">\u25CF</span>'
            )
            self.state_label.set_markup(
                '<span size="10000" foreground="#888888">LOW</span>'
            )
            self.bit_label.set_markup(
                '<span size="11000" foreground="#888888">0</span>'
            )
