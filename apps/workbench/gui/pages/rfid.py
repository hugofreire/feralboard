"""RFID debug page: connect to FX9600 reader, run inventory, view tag reads."""

import socket
import subprocess
import threading

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Pango

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from lib.rfid_reader import RfidReader

READER_HOST = "192.168.50.2"
READER_PORT = 5084


class RfidPage(Gtk.Box):
    """RFID debug page for FX9600 reader."""

    def __init__(self, on_back=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._on_back = on_back
        self._reader = RfidReader(host=READER_HOST, port=READER_PORT)
        self._reader.on_tag_read = self._on_tag_read
        self._reader.on_status_change = self._on_status_change
        self._reader.on_log = self._on_log
        self._stats_timer = None
        self._log_line_count = 0
        self._verbose = False
        # Track tag lines: EPC -> (Gtk.TextMark, cumulative_count)
        self._tag_lines = {}

        # ── Header ──
        header = Gtk.Box(spacing=8)
        header.set_margin_top(10)
        header.set_margin_bottom(10)
        header.set_margin_start(10)
        header.set_margin_end(10)

        back_btn = Gtk.Button(label="< Back")
        back_btn.connect("clicked", lambda w: self._on_back() if self._on_back else None)
        header.pack_start(back_btn, False, False, 0)

        title = Gtk.Label()
        title.set_markup('<span size="18000" weight="bold">RFID Debug</span>')
        title.set_hexpand(True)
        header.pack_start(title, True, True, 0)

        refresh_btn = Gtk.Button(label="Refresh")
        refresh_btn.connect("clicked", lambda w: self.refresh())
        header.pack_start(refresh_btn, False, False, 0)

        self.pack_start(header, False, False, 0)
        self.pack_start(Gtk.Separator(), False, False, 0)

        # ── Scrollable content ──
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.set_vexpand(True)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        content.set_margin_start(16)
        content.set_margin_end(16)
        content.set_margin_top(12)
        content.set_margin_bottom(16)

        # ── Status ──
        self.status_label = Gtk.Label()
        self.status_label.set_halign(Gtk.Align.START)
        self._update_status_label("disconnected")
        content.pack_start(self.status_label, False, False, 0)

        self.addr_label = Gtk.Label()
        self.addr_label.set_markup(
            f'<span size="10000" foreground="#888888">'
            f'Reader: {READER_HOST}:{READER_PORT}</span>'
        )
        self.addr_label.set_halign(Gtk.Align.START)
        content.pack_start(self.addr_label, False, False, 0)

        # ── Network check ──
        self.net_label = Gtk.Label()
        self.net_label.set_halign(Gtk.Align.START)
        self.net_label.set_markup(
            '<span size="10000" foreground="#888888">Network: press Refresh to check</span>'
        )
        content.pack_start(self.net_label, False, False, 0)

        content.pack_start(Gtk.Separator(), False, False, 4)

        # ── Control buttons ──
        ctrl_box = Gtk.Box(spacing=8)
        ctrl_box.set_margin_top(4)
        ctrl_box.set_margin_bottom(4)

        self.connect_btn = Gtk.Button(label="Connect")
        self.connect_btn.get_style_context().add_class("suggested-action")
        self.connect_btn.connect("clicked", self._on_connect)
        ctrl_box.pack_start(self.connect_btn, False, False, 0)

        self.disconnect_btn = Gtk.Button(label="Disconnect")
        self.disconnect_btn.set_sensitive(False)
        self.disconnect_btn.connect("clicked", self._on_disconnect)
        ctrl_box.pack_start(self.disconnect_btn, False, False, 0)

        self.start_btn = Gtk.Button(label="Start")
        self.start_btn.set_sensitive(False)
        self.start_btn.connect("clicked", self._on_start)
        ctrl_box.pack_start(self.start_btn, False, False, 0)

        self.stop_btn = Gtk.Button(label="Stop")
        self.stop_btn.set_sensitive(False)
        self.stop_btn.connect("clicked", self._on_stop)
        ctrl_box.pack_start(self.stop_btn, False, False, 0)

        content.pack_start(ctrl_box, False, False, 0)

        # ── Stats ──
        stats_box = Gtk.Box(spacing=16)
        stats_box.set_margin_top(4)

        self.unique_label = Gtk.Label(label="Unique: 0")
        self.unique_label.set_halign(Gtk.Align.START)
        stats_box.pack_start(self.unique_label, False, False, 0)

        self.rate_label = Gtk.Label(label="Rate: 0.0/s")
        self.rate_label.set_halign(Gtk.Align.START)
        stats_box.pack_start(self.rate_label, False, False, 0)

        self.total_label = Gtk.Label(label="Total: 0")
        self.total_label.set_halign(Gtk.Align.START)
        stats_box.pack_start(self.total_label, False, False, 0)

        content.pack_start(stats_box, False, False, 0)

        # ── Log controls: verbose toggle + clear ──
        log_ctrl_box = Gtk.Box(spacing=12)
        log_ctrl_box.set_margin_top(4)

        clear_btn = Gtk.Button(label="Clear Log")
        clear_btn.connect("clicked", self._on_clear_log)
        log_ctrl_box.pack_start(clear_btn, False, False, 0)

        verbose_box = Gtk.Box(spacing=6)
        verbose_box.set_valign(Gtk.Align.CENTER)
        verbose_label = Gtk.Label(label="Verbose")
        verbose_box.pack_start(verbose_label, False, False, 0)
        self.verbose_switch = Gtk.Switch()
        self.verbose_switch.set_active(False)
        self.verbose_switch.connect("state-set", self._on_verbose_toggled)
        verbose_box.pack_start(self.verbose_switch, False, False, 0)
        log_ctrl_box.pack_start(verbose_box, False, False, 0)

        power_box = Gtk.Box(spacing=6)
        power_box.set_valign(Gtk.Align.CENTER)
        power_label = Gtk.Label(label="-50% Power")
        power_box.pack_start(power_label, False, False, 0)
        self.power_switch = Gtk.Switch()
        self.power_switch.set_active(False)
        self.power_switch.connect("state-set", self._on_power_toggled)
        power_box.pack_start(self.power_switch, False, False, 0)
        log_ctrl_box.pack_start(power_box, False, False, 0)

        content.pack_start(log_ctrl_box, False, False, 4)

        # ── Log view ──
        self.log_buffer = Gtk.TextBuffer()
        self.log_view = Gtk.TextView(buffer=self.log_buffer)
        self.log_view.set_editable(False)
        self.log_view.set_cursor_visible(False)
        self.log_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.log_view.override_font(Pango.FontDescription("monospace 9"))

        log_sw = Gtk.ScrolledWindow()
        log_sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        log_sw.set_min_content_height(250)
        log_sw.set_vexpand(True)
        log_sw.add(self.log_view)

        log_frame = Gtk.Frame()
        log_frame.add(log_sw)
        content.pack_start(log_frame, True, True, 0)

        sw.add(content)
        self.pack_start(sw, True, True, 0)

    def refresh(self):
        """Check network reachability in background thread."""
        self.net_label.set_markup(
            '<span size="10000" foreground="#f39c12">Network: checking...</span>'
        )
        threading.Thread(target=self._check_network, daemon=True).start()

    def cleanup(self):
        """Disconnect reader on app destroy."""
        if self._stats_timer:
            GLib.source_remove(self._stats_timer)
            self._stats_timer = None
        self._reader.disconnect()

    def _check_network(self):
        """Ping reader and check LLRP port (runs in background thread)."""
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "2", READER_HOST],
                capture_output=True, text=True, timeout=5,
            )
            ping_ok = result.returncode == 0
        except Exception:
            ping_ok = False

        # Only check LLRP port if not already connected (avoid interference)
        port_ok = False
        if ping_ok and self._reader.state == "disconnected":
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                s.connect((READER_HOST, READER_PORT))
                s.close()
                port_ok = True
            except Exception:
                pass
        elif ping_ok:
            port_ok = True  # Assume port OK since we're already connected

        if ping_ok and port_ok:
            markup = '<span size="10000" foreground="#2ecc71">Network: reachable, LLRP port open</span>'
        elif ping_ok:
            markup = '<span size="10000" foreground="#f39c12">Network: reachable, LLRP port closed</span>'
        else:
            markup = '<span size="10000" foreground="#e74c3c">Network: unreachable</span>'

        GLib.idle_add(self.net_label.set_markup, markup)

    def _update_status_label(self, state):
        colors = {
            "disconnected": "#e74c3c",
            "connecting": "#f39c12",
            "setup": "#f39c12",
            "ready": "#2ecc71",
            "starting": "#f39c12",
            "inventorying": "#2ecc71",
            "stopping": "#f39c12",
        }
        color = colors.get(state, "#888888")
        display = state.replace("_", " ").title()
        self.status_label.set_markup(
            f'<span size="13000" foreground="{color}">Status: {display}</span>'
        )

    def _update_buttons(self, state):
        self.connect_btn.set_sensitive(state == "disconnected")
        self.disconnect_btn.set_sensitive(state != "disconnected")
        self.start_btn.set_sensitive(state == "ready")
        self.stop_btn.set_sensitive(state == "inventorying")

    def _append_log(self, text):
        """Append text to log buffer, capping at 500 lines."""
        end = self.log_buffer.get_end_iter()
        self.log_buffer.insert(end, text + "\n")
        self._log_line_count += 1

        if self._log_line_count > 500:
            start = self.log_buffer.get_start_iter()
            line2 = self.log_buffer.get_iter_at_line(1)
            self.log_buffer.delete(start, line2)
            self._log_line_count -= 1

        end = self.log_buffer.get_end_iter()
        self.log_view.scroll_to_iter(end, 0.0, False, 0, 0)

    def _update_tag_line(self, tag):
        """Update existing tag line in-place or append a new one."""
        epc = tag.epc

        if epc in self._tag_lines:
            mark, count = self._tag_lines[epc]
            count += max(tag.seen_count, 1)
            self._tag_lines[epc] = (mark, count)

            # Replace the line content at the mark
            start = self.log_buffer.get_iter_at_mark(mark)
            end = start.copy()
            end.forward_to_line_end()
            self.log_buffer.delete(start, end)
            start = self.log_buffer.get_iter_at_mark(mark)
            self.log_buffer.insert(start, self._format_tag(epc, count, tag.rssi, tag.antenna))
        else:
            # Append new line with a mark so we can find it later
            end = self.log_buffer.get_end_iter()
            mark = self.log_buffer.create_mark(None, end, True)
            count = max(tag.seen_count, 1)
            self.log_buffer.insert(end, self._format_tag(epc, count, tag.rssi, tag.antenna) + "\n")
            self._tag_lines[epc] = (mark, count)
            self._log_line_count += 1

        # Auto-scroll
        end = self.log_buffer.get_end_iter()
        self.log_view.scroll_to_iter(end, 0.0, False, 0, 0)

    @staticmethod
    def _format_tag(epc, count, rssi, antenna):
        return f"{count:>5}x  {epc}  RSSI={rssi}  Ant={antenna}"

    # ── Reader callbacks (fired from reader thread — marshal to GTK) ──

    def _on_tag_read(self, tag):
        if self._verbose:
            line = self._format_tag(tag.epc, tag.seen_count, tag.rssi, tag.antenna)
            GLib.idle_add(self._append_log, line)
        else:
            GLib.idle_add(self._update_tag_line, tag)

    def _on_status_change(self, state):
        GLib.idle_add(self._on_state_changed_ui, state)

    def _on_state_changed_ui(self, state):
        self._update_status_label(state)
        self._update_buttons(state)
        if state == "inventorying" and not self._stats_timer:
            self._stats_timer = GLib.timeout_add(500, self._update_stats)
        elif state in ("disconnected", "ready") and self._stats_timer:
            GLib.source_remove(self._stats_timer)
            self._stats_timer = None
            self._update_stats()  # Final update

    def _on_log(self, msg):
        GLib.idle_add(self._append_log, msg)

    # ── Button handlers ──

    def _on_connect(self, widget):
        self._reader.reset_stats()
        self._reader.connect()

    def _on_disconnect(self, widget):
        self._reader.disconnect()

    def _on_start(self, widget):
        self._reader.start_inventory()

    def _on_stop(self, widget):
        self._reader.stop_inventory()

    def _on_verbose_toggled(self, switch, state):
        self._verbose = state
        # Clear log when switching modes to avoid mixed formats
        self.log_buffer.set_text("")
        self._log_line_count = 0
        self._tag_lines.clear()

    def _on_power_toggled(self, switch, state):
        self._reader.reduced_power = state
        mode = "reduced (15 dBm)" if state else "full (30 dBm)"
        self._append_log(f"TX power set to {mode} — reconnect to apply")

    def _on_clear_log(self, widget):
        self.log_buffer.set_text("")
        self._log_line_count = 0
        self._tag_lines.clear()
        self._reader.reset_stats()
        self._update_stats()

    def _update_stats(self):
        total, unique, rate = self._reader.get_stats()
        self.unique_label.set_text(f"Unique: {unique}")
        self.rate_label.set_text(f"Rate: {rate:.1f}/s")
        self.total_label.set_text(f"Total: {total}")
        return True
