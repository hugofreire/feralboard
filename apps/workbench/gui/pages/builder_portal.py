"""Builder Portal page: show reachable pi-web URLs for this device."""

import socket
import subprocess
from urllib.error import URLError
from urllib.request import urlopen

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib


def _run_cmd(cmd: str) -> str:
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return (result.stdout or result.stderr).strip()
    except Exception as exc:
        return f"Error: {exc}"


def _port_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=1.0):
            return True
    except OSError:
        return False


def _http_ok(url: str) -> bool:
    try:
        with urlopen(url, timeout=1.5) as response:
            content_type = response.headers.get("Content-Type", "")
            return response.status < 400 and "text/html" in content_type
    except (OSError, URLError, ValueError):
        return False


class BuilderPortalPage(Gtk.Box):
    """Show local-network URLs for the pi-web Builder Portal."""

    def __init__(self, on_back=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._on_back = on_back

        header = Gtk.Box(spacing=8)
        header.set_margin_top(10)
        header.set_margin_bottom(10)
        header.set_margin_start(10)
        header.set_margin_end(10)

        back_btn = Gtk.Button(label="< Back")
        back_btn.connect("clicked", self._go_back)
        header.pack_start(back_btn, False, False, 0)

        title = Gtk.Label()
        title.set_markup('<span size="18000" weight="bold">Builder Portal</span>')
        title.set_hexpand(True)
        header.pack_start(title, True, True, 0)

        refresh_btn = Gtk.Button(label="Refresh")
        refresh_btn.connect("clicked", lambda _w: self.refresh())
        header.pack_start(refresh_btn, False, False, 0)

        self.pack_start(header, False, False, 0)
        self.pack_start(Gtk.Separator(), False, False, 0)

        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        info_box.set_margin_start(16)
        info_box.set_margin_end(16)
        info_box.set_margin_top(12)
        info_box.set_margin_bottom(12)

        self.status_label = Gtk.Label()
        self.status_label.set_halign(Gtk.Align.START)
        self.status_label.set_line_wrap(True)
        info_box.pack_start(self.status_label, False, False, 0)

        self.hint_label = Gtk.Label()
        self.hint_label.set_halign(Gtk.Align.START)
        self.hint_label.set_line_wrap(True)
        self.hint_label.set_markup(
            '<span size="10000" foreground="#888888">'
            'Use these URLs from a laptop or phone on the same network.</span>'
        )
        info_box.pack_start(self.hint_label, False, False, 0)

        self.pack_start(info_box, False, False, 0)
        self.pack_start(Gtk.Separator(), False, False, 0)

        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.set_vexpand(True)

        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        sw.add(self.listbox)
        self.pack_start(sw, True, True, 0)

    def _go_back(self, _widget):
        if self._on_back:
            self._on_back()

    def refresh(self):
        hostname = (_run_cmd("hostname") or "feralboard").splitlines()[0].strip()
        addresses = self._collect_addresses(hostname)

        dev_open = _port_open("127.0.0.1", 5173)
        api_open = _port_open("127.0.0.1", 3001)
        dev_html = _http_ok("http://127.0.0.1:5173")
        api_html = _http_ok("http://127.0.0.1:3001")

        status_bits = []
        status_bits.append(
            "Portal UI on :5173" if dev_html else ("Vite dev server detected on :5173" if dev_open else "No UI detected on :5173")
        )
        status_bits.append(
            "HTML available on :3001" if api_html else ("API server detected on :3001" if api_open else "No server detected on :3001")
        )
        status_color = "#2ecc71" if (dev_open or api_open) else "#e74c3c"
        self.status_label.set_markup(
            f'<span size="12000" foreground="{status_color}">'
            f'{" | ".join(GLib.markup_escape_text(bit) for bit in status_bits)}</span>'
        )

        for child in self.listbox.get_children():
            self.listbox.remove(child)

        if not addresses:
            row = Gtk.ListBoxRow()
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            box.set_border_width(12)
            label = Gtk.Label()
            label.set_halign(Gtk.Align.START)
            label.set_markup(
                '<span foreground="#e74c3c">No active network addresses found.</span>'
            )
            box.pack_start(label, False, False, 0)
            row.add(box)
            self.listbox.add(row)
            self.listbox.show_all()
            return

        for label, host in addresses:
            self._add_host_rows(label, host, dev_open, dev_html, api_open, api_html)

        self.listbox.show_all()

    def _collect_addresses(self, hostname: str):
        addresses = [("This device", "localhost"), ("mDNS", f"{hostname}.local"), ("Hostname", hostname)]
        raw = _run_cmd("ip -o -4 addr show up scope global")
        seen = {host for _label, host in addresses}
        for line in raw.splitlines():
            parts = line.split()
            if len(parts) < 4:
                continue
            iface = parts[1]
            ip = parts[3].split("/")[0]
            if ip.startswith("127.") or ip in seen:
                continue
            seen.add(ip)
            label = {
                "wlan0": "WiFi",
                "eth0": "Ethernet",
            }.get(iface, iface)
            addresses.append((label, ip))
        return addresses

    def _add_host_rows(self, label: str, host: str, dev_open: bool, dev_html: bool, api_open: bool, api_html: bool):
        rows = []
        if dev_open:
            rows.append((
                "Builder Portal",
                f"http://{host}:5173",
                "#2ecc71" if dev_html else "#f39c12",
                "Open this first when the Vite dev server is running." if dev_html else "Port is open, but HTML was not confirmed.",
            ))
        if api_open:
            rows.append((
                "Server / fallback",
                f"http://{host}:3001",
                "#2ecc71" if api_html else "#888888",
                "May serve the portal directly when PI_WEB_SERVE_DIST=1." if api_html else "API server port is reachable.",
            ))

        if not rows:
            rows.append((
                "Unavailable",
                f"http://{host}:5173",
                "#e74c3c",
                "No Builder Portal process detected on this device.",
            ))

        for title, url, color, hint in rows:
            row = Gtk.ListBoxRow()
            wrapper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
            wrapper.set_border_width(12)

            host_label = Gtk.Label()
            host_label.set_halign(Gtk.Align.START)
            host_label.set_markup(
                f'<span size="12000" weight="bold">{GLib.markup_escape_text(label)}'
                f' <span foreground="#888888">({GLib.markup_escape_text(title)})</span></span>'
            )
            wrapper.pack_start(host_label, False, False, 0)

            url_label = Gtk.Label()
            url_label.set_halign(Gtk.Align.START)
            url_label.set_selectable(True)
            url_label.set_line_wrap(True)
            url_label.set_markup(
                f'<span size="11000" foreground="{color}">{GLib.markup_escape_text(url)}</span>'
            )
            wrapper.pack_start(url_label, False, False, 0)

            hint_label = Gtk.Label()
            hint_label.set_halign(Gtk.Align.START)
            hint_label.set_line_wrap(True)
            hint_label.set_markup(
                f'<span size="9500" foreground="#888888">{GLib.markup_escape_text(hint)}</span>'
            )
            wrapper.pack_start(hint_label, False, False, 0)

            row.add(wrapper)
            self.listbox.add(row)
