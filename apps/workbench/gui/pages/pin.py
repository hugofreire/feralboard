"""PIN entry page: numeric keypad for unlocking admin area."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Pango


CORRECT_PIN = "9127"


class PinPage(Gtk.Box):
    """PIN entry page with numeric keypad."""

    def __init__(self, on_success=None, on_back=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.get_style_context().add_class("pin-page")
        self._on_success = on_success
        self._on_back = on_back
        self._entered = ""
        self._error_timer = None

        # Title
        title = Gtk.Label()
        title.set_markup(
            '<span size="20000" weight="bold" foreground="white">'
            'Enter PIN</span>'
        )
        title.set_margin_top(40)
        title.set_margin_bottom(20)
        self.pack_start(title, False, False, 0)

        # PIN display
        self.pin_display = Gtk.Label()
        self.pin_display.set_margin_bottom(8)
        self.pack_start(self.pin_display, False, False, 0)
        self._update_display()

        # Error label
        self.error_label = Gtk.Label()
        self.error_label.set_markup(
            '<span size="12000" foreground="#e74c3c">Incorrect PIN</span>'
        )
        self.error_label.set_no_show_all(True)
        self.error_label.set_visible(False)
        self.error_label.set_margin_bottom(12)
        self.pack_start(self.error_label, False, False, 0)

        # Keypad grid
        keypad = Gtk.Grid()
        keypad.set_row_spacing(10)
        keypad.set_column_spacing(10)
        keypad.set_halign(Gtk.Align.CENTER)
        keypad.set_margin_top(10)
        keypad.set_margin_bottom(20)

        keys = [
            ("1", 0, 0), ("2", 0, 1), ("3", 0, 2),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2),
            ("7", 2, 0), ("8", 2, 1), ("9", 2, 2),
            ("\u2190", 3, 0), ("0", 3, 1), ("OK", 3, 2),
        ]

        for label, row, col in keys:
            btn = Gtk.Button(label=label)
            btn.set_size_request(90, 70)
            btn.get_style_context().add_class("pin-key")
            if label == "\u2190":
                btn.get_style_context().add_class("pin-key-back")
                btn.connect("clicked", self._on_backspace)
            elif label == "OK":
                btn.get_style_context().add_class("pin-key-ok")
                btn.connect("clicked", self._on_submit)
            else:
                btn.connect("clicked", self._on_digit, label)
            keypad.attach(btn, col, row, 1, 1)

        self.pack_start(keypad, False, False, 0)

        # Cancel button
        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.set_halign(Gtk.Align.CENTER)
        cancel_btn.connect("clicked", self._on_cancel)
        self.pack_start(cancel_btn, False, False, 0)

    def reset(self):
        """Clear entered digits and hide error."""
        self._entered = ""
        self.error_label.set_visible(False)
        if self._error_timer:
            GLib.source_remove(self._error_timer)
            self._error_timer = None
        self._update_display()

    def _update_display(self):
        filled = len(self._entered)
        dots = "\u25cf" * filled + "_" * (4 - filled)
        self.pin_display.set_markup(
            f'<span size="32000" foreground="white" letter_spacing="12000">'
            f'{dots}</span>'
        )

    def _on_digit(self, widget, digit):
        if len(self._entered) < 4:
            self._entered += digit
            self._update_display()

    def _on_backspace(self, widget):
        if self._entered:
            self._entered = self._entered[:-1]
            self._update_display()

    def _on_submit(self, widget):
        if self._entered == CORRECT_PIN:
            if self._on_success:
                self._on_success()
        else:
            self.error_label.set_visible(True)
            self._entered = ""
            self._update_display()
            if self._error_timer:
                GLib.source_remove(self._error_timer)
            self._error_timer = GLib.timeout_add(2000, self._hide_error)

    def _hide_error(self):
        self.error_label.set_visible(False)
        self._error_timer = None
        return False

    def _on_cancel(self, widget):
        if self._on_back:
            self._on_back()
