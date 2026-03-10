"""Tests page: E2E test runner with scrollable log output."""

import os
import subprocess
import sys
import threading

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))


class TestsPage(Gtk.Box):
    """Page to run E2E tests and display their output."""

    def __init__(self, on_back=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.set_margin_start(8)
        self.set_margin_end(8)
        self.set_margin_top(8)

        self._process = None
        self._on_back = on_back

        # Title row with back button
        title_row = Gtk.Box(spacing=8)
        title_row.set_margin_start(4)
        back_btn = Gtk.Button(label="\u2190")
        back_btn.set_size_request(36, 36)
        back_btn.connect("clicked", lambda w: self._on_back() if self._on_back else None)
        title_row.pack_start(back_btn, False, False, 0)
        title = Gtk.Label()
        title.set_markup('<span size="16000" weight="bold">E2E Tests</span>')
        title.set_valign(Gtk.Align.CENTER)
        title_row.pack_start(title, False, False, 0)
        self.pack_start(title_row, False, False, 0)

        # Button row
        btn_box = Gtk.Box(spacing=8)
        btn_box.set_margin_start(8)

        self.output_btn = Gtk.Button(label="Run Output Test")
        self.output_btn.connect("clicked", self._on_run_outputs)
        btn_box.pack_start(self.output_btn, False, False, 0)

        self.input_btn = Gtk.Button(label="Run Input Test")
        self.input_btn.connect("clicked", self._on_run_inputs)
        btn_box.pack_start(self.input_btn, False, False, 0)

        self.clear_btn = Gtk.Button(label="Clear Log")
        self.clear_btn.connect("clicked", self._on_clear)
        btn_box.pack_start(self.clear_btn, False, False, 0)

        self.pack_start(btn_box, False, False, 0)

        # Status label
        self.status_label = Gtk.Label()
        self.status_label.set_markup(
            '<span size="11000" foreground="#888888">Ready</span>'
        )
        self.status_label.set_halign(Gtk.Align.START)
        self.status_label.set_margin_start(8)
        self.pack_start(self.status_label, False, False, 0)

        # Scrolled text view for test output
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sw.set_vexpand(True)

        self.text_view = Gtk.TextView()
        self.text_view.set_editable(False)
        self.text_view.set_cursor_visible(False)
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.text_view.set_monospace(True)
        self.text_buffer = self.text_view.get_buffer()

        sw.add(self.text_view)
        self.pack_start(sw, True, True, 0)

        self.show_all()

    def _set_buttons_sensitive(self, sensitive: bool):
        self.output_btn.set_sensitive(sensitive)
        self.input_btn.set_sensitive(sensitive)

    def _on_run_outputs(self, widget):
        script = os.path.join(PROJECT_ROOT, "tests", "test_outputs_e2e.py")
        self._run_test(script, "Output E2E Test")

    def _on_run_inputs(self, widget):
        script = os.path.join(PROJECT_ROOT, "tests", "test_inputs_e2e.py")
        self._run_test(script, "Input E2E Test")

    def _on_clear(self, widget):
        self.text_buffer.set_text("")
        self.status_label.set_markup(
            '<span size="11000" foreground="#888888">Ready</span>'
        )

    def _run_test(self, script_path: str, test_name: str):
        if self._process is not None:
            return

        self._set_buttons_sensitive(False)
        self.text_buffer.set_text("")
        self.status_label.set_markup(
            f'<span size="11000" foreground="#f39c12">Running: {test_name}...</span>'
        )

        thread = threading.Thread(
            target=self._run_subprocess, args=(script_path, test_name), daemon=True
        )
        thread.start()

    def _run_subprocess(self, script_path: str, test_name: str):
        try:
            self._process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=PROJECT_ROOT,
            )

            for line in self._process.stdout:
                GLib.idle_add(self._append_line, line)

            self._process.wait()
            rc = self._process.returncode
            self._process = None

            if rc == 0:
                GLib.idle_add(
                    self.status_label.set_markup,
                    f'<span size="11000" foreground="#2ecc71">{test_name}: PASSED</span>',
                )
            else:
                GLib.idle_add(
                    self.status_label.set_markup,
                    f'<span size="11000" foreground="#e74c3c">{test_name}: FAILED (exit {rc})</span>',
                )
        except Exception as e:
            self._process = None
            GLib.idle_add(
                self.status_label.set_markup,
                f'<span size="11000" foreground="#e74c3c">Error: {e}</span>',
            )

        GLib.idle_add(self._set_buttons_sensitive, True)

    def _append_line(self, line: str):
        end_iter = self.text_buffer.get_end_iter()
        self.text_buffer.insert(end_iter, line)
        # Auto-scroll to bottom
        mark = self.text_buffer.get_insert()
        self.text_view.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)
