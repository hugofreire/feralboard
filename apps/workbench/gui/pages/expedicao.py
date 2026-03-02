"""Expedição kiosk app: RFID inventory validation with traffic-light UI."""

import json
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.request

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib, Pango
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from lib.rfid_reader import RfidReader

ENV_PATH = os.path.join(
    os.path.dirname(__file__), "../../kiosk_apps/expedicao/.env"
)


def _load_env(path):
    try:
        with open(path, "r", encoding="utf-8") as env_file:
            for raw_line in env_file:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())
    except OSError:
        pass


_load_env(ENV_PATH)

READER_HOST = os.getenv("READER_HOST", "192.168.50.2")
READER_PORT = int(os.getenv("READER_PORT", "5084"))
ITEMS_API_BASE = os.getenv("ITEMS_API_BASE", "http://192.168.0.213:3001/api/items")
ITEMS_API_TIMEOUT = float(os.getenv("ITEMS_API_TIMEOUT", "5"))
ITEMS_DOCK = os.getenv("ITEMS_DOCK", "").strip()

# Emoji constants
CIRCLE_BLACK = "\u26ab"
CIRCLE_RED = "\U0001f534"
CIRCLE_YELLOW = "\U0001f7e1"
CIRCLE_GREEN = "\U0001f7e2"

# DI bit positions in RX byte 4
DI0_BIT = 0
DI1_BIT = 1


class ExpedicaoPage(Gtk.Box):
    """RFID inventory validation page with traffic-light status."""

    def __init__(self, on_unlock=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.get_style_context().add_class("kiosk-page")
        self._on_unlock = on_unlock
        self._press_timer = None

        # Traffic light state: "off", "red", "yellow", "green"
        self._light_state = "off"

        # Scan finished flag: stays True until DI leaves yellow
        self._scan_finished = False

        # RFID reader
        self._reader = RfidReader(host=READER_HOST, port=READER_PORT)
        self._reader.reduced_power = False
        self._reader.on_tag_read = self._on_tag_read
        self._reader.on_status_change = self._on_status_change
        self._reader.on_log = self._on_reader_log

        # Order data
        self._order_id = ""
        self._dock_number = ""
        self._expected_items = []  # [{"name": str, "epc": str, "matched": bool}]
        self._unknown_tags = []  # [{"epc": str}]
        self._items_loading = False

        # Widget refs
        self._light_labels = {}
        self._item_rows = {}  # epc -> {"box", "indicator", "name_label"}
        self._items_container = None
        self._order_header = None
        self._rfid_status = None
        self._board_status = None
        self._rfid_last_error = None
        self._rfid_state = "disconnected"
        self._rfid_state_since = None
        self._rfid_retrying = False
        self._rfid_watchdog_timer = GLib.timeout_add(1000, self._on_rfid_watchdog)

        self._last_rx_time = None
        self._last_di0 = None
        self._last_di1 = None
        self._last_debug_di = None
        self._board_timer = None

        self._debug_line_count = 0
        self._log_path = os.path.join(
            os.path.dirname(__file__), "../../kiosk_apps/expedicao/expedicao.log"
        )

        self._build_ui()
        self._board_timer = GLib.timeout_add(1000, self._on_board_timer)

    def _build_ui(self):
        # ── Title with long-press ──
        event_box = Gtk.EventBox()
        event_box.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK
        )
        event_box.connect("button-press-event", self._on_press)
        event_box.connect("button-release-event", self._on_release)

        self._title_label = Gtk.Label()
        self._title_label.set_markup(
            '<span size="20000" weight="bold" foreground="white">'
            'Expedi\u00e7\u00e3o</span>'
        )
        self._title_label.set_margin_top(16)
        self._title_label.set_margin_bottom(4)
        event_box.add(self._title_label)
        self.pack_start(event_box, False, False, 0)

        # ── Traffic light row (clickable shortcuts) ──
        light_box = Gtk.Box(spacing=12)
        light_box.set_halign(Gtk.Align.CENTER)
        light_box.set_margin_top(8)
        light_box.set_margin_bottom(4)

        for color in ("red", "yellow", "green"):
            btn = Gtk.Button()
            btn.set_relief(Gtk.ReliefStyle.NONE)
            btn.get_style_context().add_class("expedicao-light")
            lbl = Gtk.Label()
            lbl.set_markup(f'<span size="40000">{CIRCLE_BLACK}</span>')
            btn.add(lbl)
            btn.connect("clicked", self._on_light_clicked, color)
            light_box.pack_start(btn, False, False, 8)
            self._light_labels[color] = lbl

        self.pack_start(light_box, False, False, 0)

        # ── FeralBoard status ──
        self._board_status = Gtk.Label()
        self._board_status.set_markup(
            '<span size="9000" foreground="#555555">FeralBoard: waiting for data</span>'
        )
        self._board_status.set_halign(Gtk.Align.CENTER)
        self._board_status.set_margin_bottom(2)
        self.pack_start(self._board_status, False, False, 0)

        # ── RFID status ──
        self._rfid_status = Gtk.Label()
        self._rfid_status.set_markup(
            '<span size="9000" foreground="#555555">'
            'RFID: waiting for DI0+DI1 (yellow)</span>'
        )
        self._rfid_status.set_halign(Gtk.Align.CENTER)
        self._rfid_status.set_margin_bottom(4)
        self.pack_start(self._rfid_status, False, False, 0)

        self.pack_start(Gtk.Separator(), False, False, 4)

        # ── Order header ──
        self._order_header = Gtk.Label()
        self._order_header.set_halign(Gtk.Align.START)
        self._order_header.set_margin_start(16)
        self._order_header.set_margin_top(8)
        self._order_header.set_margin_bottom(4)
        self.pack_start(self._order_header, False, False, 0)

        # ── Scrollable item list ──
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.set_vexpand(True)

        self._items_container = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=4
        )
        self._items_container.set_margin_start(16)
        self._items_container.set_margin_end(16)
        self._items_container.set_margin_top(4)
        self._items_container.set_margin_bottom(16)

        sw.add(self._items_container)
        self.pack_start(sw, True, True, 0)

        self.pack_start(Gtk.Separator(), False, False, 4)

        # ── Debug log (footer) ──
        debug_frame = Gtk.Frame()
        debug_frame.set_shadow_type(Gtk.ShadowType.IN)
        debug_frame.set_margin_start(16)
        debug_frame.set_margin_end(16)
        debug_frame.set_margin_bottom(8)
        debug_scroller = Gtk.ScrolledWindow()
        debug_scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        debug_scroller.set_min_content_height(160)
        debug_scroller.set_vexpand(False)
        debug_scroller.set_hexpand(True)
        self._debug_scroller = debug_scroller
        self._debug_list = Gtk.ListBox()
        self._debug_list.set_selection_mode(Gtk.SelectionMode.NONE)
        debug_scroller.add(self._debug_list)
        debug_frame.add(debug_scroller)
        self.pack_start(debug_frame, False, False, 0)

    # ── Public API ──

    def load_app(self, app_info):
        """Load order data from app manifest (list shown only when yellow)."""
        self._stop_rfid()
        self._set_light("off")
        self._scan_finished = False
        self._last_rx_time = None
        self._last_di0 = None
        self._last_di1 = None
        self._board_status.set_markup(
            '<span size="9000" foreground="#555555">'
            'FeralBoard: waiting for data</span>'
        )
        self._rfid_status.set_markup(
            '<span size="9000" foreground="#555555">'
            'RFID: waiting for DI0+DI1 (yellow)</span>'
        )
        if self._board_timer is None:
            self._board_timer = GLib.timeout_add(1000, self._on_board_timer)
        if self._rfid_watchdog_timer is None:
            self._rfid_watchdog_timer = GLib.timeout_add(1000, self._on_rfid_watchdog)

        app_name = app_info.get("name", "Expedição")
        self._title_label.set_markup(
            f'<span size="20000" weight="bold" foreground="white">'
            f'{escape(app_name)}</span>'
        )

        order = app_info.get("order", {})
        self._order_id = order.get("id", "")
        self._dock_number = order.get("dock_number", "")

        raw_items = order.get("inventory_check", {}).get("items", [])
        self._expected_items = [
            {"name": item["name"], "epc": item["epc"].upper(), "matched": False}
            for item in raw_items
        ]
        self._unknown_tags = []
        self._fetch_items_async()

        self._order_header.set_markup("")
        self._clear_item_list()
        for child in self._debug_list.get_children():
            self._debug_list.remove(child)
        self._debug_line_count = 0
        self._last_debug_di = None
        try:
            with open(self._log_path, "a", encoding="utf-8") as log_file:
                log_file.write("\n--- App loaded ---\n")
        except OSError:
            pass
        self._append_debug("App loaded")

    def refresh(self):
        pass

    def cleanup(self):
        """Stop RFID reader."""
        self._stop_rfid()
        if self._board_timer is not None:
            GLib.source_remove(self._board_timer)
            self._board_timer = None
        if self._rfid_watchdog_timer is not None:
            GLib.source_remove(self._rfid_watchdog_timer)
            self._rfid_watchdog_timer = None

    def update_from_rx(self, rx_buffer):
        """Drive traffic light state from DI0/DI1 digital inputs."""
        input_byte = rx_buffer[4]
        di0 = (input_byte >> DI0_BIT) & 1 == 1
        di1 = (input_byte >> DI1_BIT) & 1 == 1

        self._last_rx_time = time.monotonic()
        self._last_di0 = di0
        self._last_di1 = di1
        self._set_board_status(True, di0, di1)
        if self._last_debug_di != (di0, di1):
            self._last_debug_di = (di0, di1)
            self._append_debug(f"DI update: DI0={int(di0)} DI1={int(di1)}")

        if not di0:
            desired = "off"
        elif not di1:
            desired = "red"
        else:
            desired = "yellow"

        if desired == self._light_state:
            return

        # After scan completes (green/red), hold state while DI says yellow.
        # Only a DI change away from yellow clears the flag for a new cycle.
        if self._scan_finished:
            if desired == "yellow":
                return
            self._scan_finished = False

        self._transition_to(desired)

    def _set_board_status(self, connected, di0=None, di1=None):
        if connected:
            di0_text = "ON" if di0 else "OFF"
            di1_text = "ON" if di1 else "OFF"
            self._board_status.set_markup(
                '<span size="9000" foreground="#2ecc71">'
                f'FeralBoard: connected (DI0={di0_text}, DI1={di1_text})'
                '</span>'
            )
        else:
            self._board_status.set_markup(
                '<span size="9000" foreground="#e74c3c">'
                'FeralBoard: disconnected</span>'
            )

    def _on_board_timer(self):
        if self._last_rx_time is None:
            self._board_status.set_markup(
                '<span size="9000" foreground="#555555">'
                'FeralBoard: waiting for data</span>'
            )
            return True

        if time.monotonic() - self._last_rx_time > 2.0:
            self._set_board_status(False)
        return True

    def _append_debug(self, message):
        timestamp = time.strftime("%H:%M:%S")
        line = f"[{timestamp}] {message}"
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        label = Gtk.Label(label=line)
        label.set_xalign(0)
        label.set_line_wrap(True)
        label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        label.override_font(Pango.FontDescription("monospace 9"))
        row.set_margin_start(8)
        row.set_margin_end(8)
        row.set_margin_top(2)
        row.set_margin_bottom(2)
        row.pack_start(label, True, True, 0)
        self._debug_list.add(row)

        try:
            with open(self._log_path, "a", encoding="utf-8") as log_file:
                log_file.write(line + "\n")
        except OSError:
            pass

        self._debug_line_count += 1
        if self._debug_line_count > 200:
            first = self._debug_list.get_row_at_index(0)
            if first is not None:
                self._debug_list.remove(first)
                self._debug_line_count -= 1

        self._debug_list.show_all()
        GLib.idle_add(self._scroll_debug_to_bottom)

    def _scroll_debug_to_bottom(self):
        if not self._debug_scroller:
            return False
        adj = self._debug_scroller.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())
        return False

    # ── State transitions ──

    def _transition_to(self, new_state):
        """Handle state transition with side effects."""
        old_state = self._light_state

        if new_state == old_state:
            return

        self._append_debug(f"Traffic light -> {new_state}")

        # Leaving yellow — stop RFID
        if old_state == "yellow":
            self._stop_rfid()

        # Entering off — hide list
        if new_state == "off":
            self._set_light("off")
            self._order_header.set_markup("")
            self._clear_item_list()
            self._rfid_status.set_markup(
                '<span size="9000" foreground="#555555">'
                'RFID: waiting for DI0+DI1 (yellow)</span>'
            )

        # Entering red (from DI, not from scan)
        elif new_state == "red":
            self._set_light("red")
            self._order_header.set_markup("")
            self._clear_item_list()
            self._rfid_status.set_markup(
                '<span size="9000" foreground="#555555">'
                'RFID: waiting for DI0+DI1 (yellow)</span>'
            )

        # Entering yellow — show list, start RFID
        elif new_state == "yellow":
            self._set_light("yellow")
            self._reset_matches()
            self._show_order_header()
            self._rebuild_item_list()
            self._start_rfid()

    def _show_order_header(self):
        self._order_header.set_markup(
            f'<span size="13000" weight="bold" foreground="#a0a0a0">'
            f'Order: {self._order_id}  |  Dock {self._dock_number}</span>'
        )

    def _get_dock_slug(self):
        if ITEMS_DOCK:
            return ITEMS_DOCK
        if self._dock_number:
            digits = "".join(ch for ch in self._dock_number if ch.isdigit())
            if digits:
                return f"dock{int(digits)}"
        return "dock1"

    def _fetch_items_async(self):
        if not ITEMS_API_BASE or self._items_loading:
            return
        self._items_loading = True
        dock_slug = self._get_dock_slug()
        self._append_debug(f"Fetching items from API ({dock_slug})")
        threading.Thread(
            target=self._fetch_items_from_api, args=(dock_slug,), daemon=True
        ).start()

    def _fetch_items_from_api(self, dock_slug):
        url = f"{ITEMS_API_BASE.rstrip('/')}/{dock_slug}"
        try:
            with urllib.request.urlopen(url, timeout=ITEMS_API_TIMEOUT) as response:
                payload = response.read().decode("utf-8")
                items = json.loads(payload)
        except Exception as exc:
            GLib.idle_add(self._on_items_fetch_failed, str(exc))
            return

        GLib.idle_add(self._on_items_loaded, items, dock_slug)

    def _on_items_loaded(self, items, dock_slug):
        self._items_loading = False
        if not isinstance(items, list):
            self._append_debug("API returned unexpected data")
            return

        self._expected_items = [
            {
                "name": item.get("name", "Unnamed"),
                "epc": str(item.get("epc", "")).upper(),
                "matched": False,
            }
            for item in items
            if item.get("epc")
        ]
        self._unknown_tags = []
        self._append_debug(
            f"Loaded {len(self._expected_items)} items from API ({dock_slug})"
        )
        if self._light_state == "yellow":
            self._rebuild_item_list()
        return False

    def _on_items_fetch_failed(self, message):
        self._items_loading = False
        self._append_debug(f"Item fetch failed: {message}")
        return False

    # ── Traffic light display ──

    def _set_light(self, color):
        self._light_state = color
        emoji_map = {
            "red": (CIRCLE_RED, CIRCLE_BLACK, CIRCLE_BLACK),
            "yellow": (CIRCLE_BLACK, CIRCLE_YELLOW, CIRCLE_BLACK),
            "green": (CIRCLE_BLACK, CIRCLE_BLACK, CIRCLE_GREEN),
            "off": (CIRCLE_BLACK, CIRCLE_BLACK, CIRCLE_BLACK),
        }
        emojis = emoji_map.get(color, (CIRCLE_BLACK, CIRCLE_BLACK, CIRCLE_BLACK))
        for lbl_color, emoji in zip(("red", "yellow", "green"), emojis):
            self._light_labels[lbl_color].set_markup(
                f'<span size="40000">{emoji}</span>'
            )

    def _on_light_clicked(self, button, color):
        """Shortcut: click a traffic light to force that state transition."""
        if color == self._light_state:
            # Clicking same color → go to off
            self._scan_finished = False
            self._transition_to("off")
        else:
            self._scan_finished = False
            self._transition_to(color)

    def _reset_matches(self):
        for item in self._expected_items:
            item["matched"] = False
        self._unknown_tags.clear()
        self._scan_finished = False

    # ── Item list ──

    def _clear_item_list(self):
        for child in self._items_container.get_children():
            self._items_container.remove(child)
        self._item_rows.clear()

    def _rebuild_item_list(self):
        self._clear_item_list()

        for item in self._expected_items:
            row = self._make_item_row(
                item["name"], item["epc"], matched=item["matched"], is_unknown=False
            )
            self._items_container.pack_start(row["box"], False, False, 0)
            self._item_rows[item["epc"]] = row

        for tag in self._unknown_tags:
            row = self._make_item_row(
                "Unknown Tag", tag["epc"], matched=False, is_unknown=True
            )
            self._items_container.pack_start(row["box"], False, False, 0)
            self._item_rows[tag["epc"]] = row

        self._items_container.show_all()

    def _make_item_row(self, name, epc, matched, is_unknown):
        box = Gtk.Box(spacing=8)
        box.get_style_context().add_class("expedicao-item-row")
        if is_unknown:
            box.get_style_context().add_class("expedicao-item-unknown")
        elif matched:
            box.get_style_context().add_class("expedicao-item-matched")
        box.set_margin_top(2)
        box.set_margin_bottom(2)

        indicator = Gtk.Label()
        if is_unknown:
            indicator.set_markup(f'<span size="16000">{CIRCLE_RED}</span>')
        elif matched:
            indicator.set_markup(f'<span size="16000">{CIRCLE_GREEN}</span>')
        else:
            indicator.set_markup(f'<span size="16000">{CIRCLE_BLACK}</span>')
        indicator.set_valign(Gtk.Align.CENTER)
        box.pack_start(indicator, False, False, 4)

        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        name_label = Gtk.Label()
        name_label.set_markup(
            f'<span size="11000" foreground="white">{escape(name)}</span>'
        )
        name_label.set_halign(Gtk.Align.START)
        name_label.set_line_wrap(True)
        text_box.pack_start(name_label, False, False, 0)

        epc_label = Gtk.Label()
        epc_label.set_markup(
            f'<span size="7000" foreground="#555555"'
            f' font_family="monospace">{epc}</span>'
        )
        epc_label.set_halign(Gtk.Align.START)
        text_box.pack_start(epc_label, False, False, 0)

        box.pack_start(text_box, True, True, 0)

        return {"box": box, "indicator": indicator, "name_label": name_label}

    def _update_item_row(self, epc, matched):
        row = self._item_rows.get(epc)
        if not row:
            return
        if matched:
            row["indicator"].set_markup(f'<span size="16000">{CIRCLE_GREEN}</span>')
            row["box"].get_style_context().add_class("expedicao-item-matched")

    # ── RFID ──

    def _start_rfid(self):
        """Check network reachability, then connect to RFID reader."""
        self._rfid_last_error = None
        self._rfid_retrying = False
        self._append_debug("RFID: starting network check")
        self._rfid_status.set_markup(
            '<span size="9000" foreground="#f39c12">RFID: checking network...</span>'
        )
        threading.Thread(
            target=self._check_network_and_connect, daemon=True
        ).start()

    def _check_network_and_connect(self):
        """Background thread: ping + TCP port check, then connect if OK."""
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "2", READER_HOST],
                capture_output=True, text=True, timeout=5,
            )
            ping_ok = result.returncode == 0
        except Exception:
            ping_ok = False

        if not ping_ok:
            GLib.idle_add(self._on_network_check_failed, "unreachable")
            return

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((READER_HOST, READER_PORT))
            s.close()
        except Exception:
            GLib.idle_add(self._on_network_check_failed, "port closed")
            return

        GLib.idle_add(self._on_network_check_ok)

    def _on_network_check_failed(self, reason):
        if self._light_state != "yellow":
            return
        if reason == "port closed":
            self._rfid_last_error = "reader not ready (LLRP port closed)"
            self._append_debug("RFID network check failed: LLRP port closed")
            self._rfid_status.set_markup(
                '<span size="9000" foreground="#e74c3c">'
                'RFID: reader not ready (LLRP port closed)</span>'
            )
        else:
            self._rfid_last_error = "reader unreachable"
            self._append_debug("RFID network check failed: unreachable")
            self._rfid_status.set_markup(
                '<span size="9000" foreground="#e74c3c">'
                'RFID: reader unreachable</span>'
            )

    def _on_network_check_ok(self):
        if self._light_state != "yellow":
            return
        self._append_debug("RFID network check OK, connecting")
        self._reader.reset_stats()
        self._reader.connect()

    def _stop_rfid(self):
        if self._reader.state == "inventorying":
            self._reader.stop_inventory()
        self._reader.disconnect()

    def _on_tag_read(self, tag):
        GLib.idle_add(self._process_tag, tag.epc)

    def _process_tag(self, epc):
        epc_upper = epc.upper()

        for item in self._expected_items:
            if item["epc"] == epc_upper:
                if not item["matched"]:
                    item["matched"] = True
                    self._update_item_row(epc_upper, matched=True)
                    self._check_completion()
                return

        # Already tracked as unknown?
        for tag in self._unknown_tags:
            if tag["epc"] == epc_upper:
                return

        # New unknown tag
        self._unknown_tags.append({"epc": epc_upper})
        row = self._make_item_row("Unknown Tag", epc_upper, False, is_unknown=True)
        self._items_container.pack_start(row["box"], False, False, 0)
        self._item_rows[epc_upper] = row
        row["box"].show_all()

        self._scan_finished = True
        self._set_light("red")

    def _check_completion(self):
        if self._unknown_tags:
            return
        if self._expected_items and all(
            item["matched"] for item in self._expected_items
        ):
            self._scan_finished = True
            self._set_light("green")
            self._stop_rfid()

    def _on_status_change(self, state):
        GLib.idle_add(self._update_rfid_status, state)

    def _on_reader_log(self, msg):
        GLib.idle_add(self._handle_reader_log, msg)

    def _handle_reader_log(self, msg):
        if any(key in msg for key in ("Connection failed", "Connection lost",
                                      "Setup failed", "Send error")):
            self._rfid_last_error = msg
            self._append_debug(f"RFID error: {msg}")
            if self._light_state == "yellow" and self._reader.state == "disconnected":
                self._rfid_status.set_markup(
                    '<span size="9000" foreground="#e74c3c">'
                    f'RFID: {escape(msg)}</span>'
                )

    def _update_rfid_status(self, state):
        self._rfid_state = state
        self._rfid_state_since = time.monotonic()
        if state in ("ready", "inventorying"):
            self._rfid_retrying = False
        self._append_debug(f"RFID state -> {state}")

        colors = {
            "disconnected": "#555555",
            "connecting": "#f39c12",
            "setup": "#f39c12",
            "ready": "#2ecc71",
            "starting": "#f39c12",
            "inventorying": "#2ecc71",
            "stopping": "#f39c12",
        }
        color = colors.get(state, "#555555")

        if state == "disconnected" and self._light_state == "green":
            self._rfid_status.set_markup(
                '<span size="9000" foreground="#2ecc71">RFID: scan complete</span>'
            )
        elif state == "disconnected" and self._light_state == "red":
            self._rfid_status.set_markup(
                '<span size="9000" foreground="#e74c3c">RFID: unknown tag detected</span>'
            )
        elif state == "disconnected" and self._light_state == "yellow":
            if self._rfid_last_error:
                self._rfid_status.set_markup(
                    '<span size="9000" foreground="#e74c3c">'
                    f'RFID: {escape(self._rfid_last_error)}</span>'
                )
            else:
                self._rfid_status.set_markup(
                    '<span size="9000" foreground="#e74c3c">RFID: disconnected</span>'
                )
        else:
            self._rfid_status.set_markup(
                f'<span size="9000" foreground="{color}">RFID: {state}</span>'
            )

        if state == "ready" and self._light_state == "yellow":
            self._reader.start_inventory()

    def _on_rfid_watchdog(self):
        if self._light_state != "yellow":
            return True
        if self._rfid_state in ("connecting", "setup"):
            if (self._rfid_state_since is not None
                    and time.monotonic() - self._rfid_state_since > 8.0
                    and not self._rfid_retrying):
                self._rfid_last_error = f"{self._rfid_state} timeout"
                self._append_debug(f"RFID watchdog: {self._rfid_last_error}")
                self._rfid_status.set_markup(
                    '<span size="9000" foreground="#e74c3c">'
                    f'RFID: {escape(self._rfid_last_error)}, retrying</span>'
                )
                self._rfid_retrying = True
                self._reader.disconnect()
                GLib.timeout_add(1000, self._retry_rfid)
        return True

    def _retry_rfid(self):
        if self._light_state != "yellow":
            self._rfid_retrying = False
            return False
        self._append_debug("RFID: retrying connection")
        self._start_rfid()
        return False

    # ── Long-press unlock ──

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
