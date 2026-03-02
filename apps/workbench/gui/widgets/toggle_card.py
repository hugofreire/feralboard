"""Reusable DO toggle widget: label + switch + echo LED indicator."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class ToggleCard(Gtk.Box):
    """A card for a digital output: channel label, ON/OFF switch, echo indicator."""

    def __init__(self, channel_name: str, on_toggle=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.get_style_context().add_class("toggle-card")
        self.set_margin_start(4)
        self.set_margin_end(4)
        self.set_margin_top(4)
        self.set_margin_bottom(4)

        self.channel_name = channel_name
        self._on_toggle = on_toggle
        self._programmatic = False

        # Channel label
        self.label = Gtk.Label(label=channel_name)
        self.label.set_markup(
            f'<span weight="bold" size="12000">{channel_name}</span>'
        )
        self.pack_start(self.label, False, False, 0)

        # Switch
        self.switch = Gtk.Switch()
        self.switch.set_halign(Gtk.Align.CENTER)
        self.switch.connect("state-set", self._on_state_set)
        self.pack_start(self.switch, False, False, 4)

        # Echo indicator
        self.echo_label = Gtk.Label()
        self.echo_label.set_markup(
            '<span size="9000" foreground="#555555">echo: --</span>'
        )
        self.pack_start(self.echo_label, False, False, 0)

        self.show_all()

    def _on_state_set(self, switch, state):
        if self._programmatic:
            return False
        if self._on_toggle:
            self._on_toggle(self.channel_name, state)
        return False

    def set_active(self, active: bool):
        """Programmatically set the switch state without triggering callback."""
        self._programmatic = True
        self.switch.set_state(active)
        self.switch.set_active(active)
        self._programmatic = False

    def set_echo(self, tx_on: bool, rx_on: bool):
        """Update echo indicator: green=match, red=mismatch, gray=off."""
        if not tx_on and not rx_on:
            self.echo_label.set_markup(
                '<span size="9000" foreground="#555555">echo: OFF</span>'
            )
            ctx = self.get_style_context()
            ctx.remove_class("toggle-card-on")
        elif tx_on and rx_on:
            self.echo_label.set_markup(
                '<span size="9000" foreground="#2ecc71">echo: ON</span>'
            )
            ctx = self.get_style_context()
            ctx.add_class("toggle-card-on")
        else:
            self.echo_label.set_markup(
                '<span size="9000" foreground="#e74c3c">echo: MISMATCH</span>'
            )
            ctx = self.get_style_context()
            ctx.add_class("toggle-card-on")
