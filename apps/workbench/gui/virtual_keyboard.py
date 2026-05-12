"""Helpers for launching an on-screen keyboard for text inputs."""

import os
import shlex
import shutil
import subprocess

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk


class VirtualKeyboardManager:
    """Launch a single keyboard process while text inputs are focused."""

    _ENV_KEYS = ("FERALBOARD_OSK_CMD", "VIRTUAL_KEYBOARD_CMD", "OSK_CMD")
    _CANDIDATES = (
        "wvkbd-mobintl",
        "wvkbd",
        "squeekboard",
        "onboard",
        "matchbox-keyboard",
    )

    def __init__(self):
        self._proc = None
        self._hide_timer = None
        self._command = self._resolve_command()

    def attach(self, widget):
        """Show keyboard while the widget has focus."""
        widget.connect("focus-in-event", self._on_focus_in)
        widget.connect("focus-out-event", self._on_focus_out)
        widget.connect("destroy", self._on_widget_destroy)
        return widget

    def show(self):
        """Start the keyboard process if available and not already running."""
        self._cancel_hide()
        if not self._command:
            return
        if self._proc and self._proc.poll() is None:
            return
        try:
            self._proc = subprocess.Popen(self._command)
        except Exception:
            self._proc = None

    def hide(self):
        """Stop the keyboard process if it was started by the GUI."""
        self._cancel_hide()
        proc = self._proc
        self._proc = None
        if not proc or proc.poll() is not None:
            return
        try:
            proc.terminate()
            proc.wait(timeout=1)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

    def _resolve_command(self):
        for env_key in self._ENV_KEYS:
            raw = os.getenv(env_key, "").strip()
            if raw:
                return shlex.split(raw)
        for candidate in self._CANDIDATES:
            path = shutil.which(candidate)
            if path:
                return [path]
        return None

    def _cancel_hide(self):
        if self._hide_timer:
            GLib.source_remove(self._hide_timer)
            self._hide_timer = None

    def _on_focus_in(self, widget, event):
        self.show()
        return False

    def _on_focus_out(self, widget, event):
        self._cancel_hide()
        self._hide_timer = GLib.timeout_add(150, self._hide_if_no_text_focus)
        return False

    def _on_widget_destroy(self, widget):
        self._cancel_hide()

    def _hide_if_no_text_focus(self):
        self._hide_timer = None
        for window in Gtk.Window.list_toplevels():
            if not isinstance(window, Gtk.Window):
                continue
            focus = window.get_focus()
            if isinstance(focus, (Gtk.Entry, Gtk.SpinButton)):
                return False
        self.hide()
        return False


keyboard_manager = VirtualKeyboardManager()


def attach_virtual_keyboard(widget):
    """Attach keyboard focus handlers to a text input widget."""
    return keyboard_manager.attach(widget)
