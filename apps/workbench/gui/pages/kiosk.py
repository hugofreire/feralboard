"""Kiosk lock screen: shows app content, long-press title to unlock."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib


class KioskPage(Gtk.Box):
    """Kiosk lock screen with long-press unlock on title."""

    def __init__(self, on_unlock=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.get_style_context().add_class("kiosk-page")
        self._on_unlock = on_unlock
        self._press_timer = None

        # Title with long-press detection
        event_box = Gtk.EventBox()
        event_box.add_events(
            gi.repository.Gdk.EventMask.BUTTON_PRESS_MASK
            | gi.repository.Gdk.EventMask.BUTTON_RELEASE_MASK
        )
        event_box.connect("button-press-event", self._on_press)
        event_box.connect("button-release-event", self._on_release)

        title = Gtk.Label()
        title.set_markup(
            '<span size="20000" weight="bold" foreground="white">'
            'Ecr\u00e3 Principal</span>'
        )
        title.set_margin_top(24)
        title.set_margin_bottom(12)
        event_box.add(title)
        self.pack_start(event_box, False, False, 0)

        # Greeting centered vertically
        self.greeting_label = Gtk.Label()
        self.greeting_label.set_markup(
            '<span size="24000" foreground="white">Ol\u00e1 Mundo!</span>'
        )
        self.greeting_label.set_vexpand(True)
        self.greeting_label.set_valign(Gtk.Align.CENTER)
        self.pack_start(self.greeting_label, True, True, 0)

    def set_greeting(self, text):
        """Update the center greeting text."""
        self.greeting_label.set_markup(
            f'<span size="24000" foreground="white">{text}</span>'
        )

    def _on_press(self, widget, event):
        if event.button == 1:
            self._cancel_timer()
            self._press_timer = GLib.timeout_add(2000, self._timer_fired)
        return False

    def _on_release(self, widget, event):
        if event.button == 1:
            self._cancel_timer()
        return False

    def _timer_fired(self):
        self._press_timer = None
        if self._on_unlock:
            self._on_unlock()
        return False

    def _cancel_timer(self):
        if self._press_timer is not None:
            GLib.source_remove(self._press_timer)
            self._press_timer = None
