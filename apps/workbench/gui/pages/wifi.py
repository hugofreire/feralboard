"""WiFi management page: scan networks, view status, connect."""

import subprocess
import time

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib


def _run_cmd(cmd):
    """Run a shell command and return stdout."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout.strip()
        if result.returncode != 0:
            err = result.stderr.strip()
            return output or err or f"Command failed with exit code {result.returncode}"
        return output
    except Exception as e:
        return f"Error: {e}"


class WifiPage(Gtk.Box):
    """WiFi management page with network scanning and connection."""

    def __init__(self, on_back=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._on_back = on_back
        self.selected_ssid = None

        # Header
        header = Gtk.Box(spacing=8)
        header.set_margin_top(10)
        header.set_margin_bottom(10)
        header.set_margin_start(10)
        header.set_margin_end(10)

        back_btn = Gtk.Button(label="< Back")
        back_btn.connect("clicked", self._go_back)
        header.pack_start(back_btn, False, False, 0)

        title = Gtk.Label()
        title.set_markup('<span size="18000" weight="bold">WiFi</span>')
        title.set_hexpand(True)
        header.pack_start(title, True, True, 0)

        refresh_btn = Gtk.Button(label="Refresh")
        refresh_btn.connect("clicked", lambda w: self.refresh())
        header.pack_start(refresh_btn, False, False, 0)

        self.pack_start(header, False, False, 0)
        self.pack_start(Gtk.Separator(), False, False, 0)

        # Connection status panel
        status_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        status_box.set_margin_start(16)
        status_box.set_margin_end(16)
        status_box.set_margin_top(12)
        status_box.set_margin_bottom(8)

        self.connected_label = Gtk.Label()
        self.connected_label.set_halign(Gtk.Align.START)
        status_box.pack_start(self.connected_label, False, False, 0)

        self.ip_label = Gtk.Label()
        self.ip_label.set_halign(Gtk.Align.START)
        status_box.pack_start(self.ip_label, False, False, 0)

        self.pack_start(status_box, False, False, 0)
        self.pack_start(Gtk.Separator(), False, False, 0)

        # "Available Networks" label
        net_label = Gtk.Label()
        net_label.set_markup(
            '<span size="13000" weight="bold">Available Networks</span>'
        )
        net_label.set_halign(Gtk.Align.START)
        net_label.set_margin_start(16)
        net_label.set_margin_top(8)
        net_label.set_margin_bottom(4)
        self.pack_start(net_label, False, False, 0)

        # Network list (scrollable)
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.set_vexpand(True)

        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        sw.add(self.listbox)
        self.pack_start(sw, True, True, 0)

    def _go_back(self, widget):
        if self._on_back:
            self._on_back()

    def refresh(self):
        """Fetch current connection info and available networks."""
        # Force a fresh scan. NetworkManager requires elevated privileges here
        # on this Pi, so fall back through the allowed variants.
        for cmd in (
            "sudo nmcli dev wifi rescan ifname wlan0",
            "nmcli dev wifi rescan ifname wlan0",
            "sudo nmcli dev wifi rescan",
            "nmcli dev wifi rescan",
        ):
            _run_cmd(cmd)
        time.sleep(1.0)

        # Current connection
        active = _run_cmd("nmcli -t -f NAME,DEVICE con show --active | grep wlan0")
        if active:
            ssid = active.split(":")[0]
            self.connected_label.set_markup(
                f'<span size="13000" foreground="#2ecc71">'
                f'Connected: <b>{GLib.markup_escape_text(ssid)}</b></span>'
            )
        else:
            self.connected_label.set_markup(
                '<span size="13000" foreground="#e74c3c">Not connected</span>'
            )

        # IP address
        ip = _run_cmd("hostname -I")
        ips = ip.split()
        ip_text = ips[0] if ips else "No IP"
        self.ip_label.set_markup(
            f'<span size="11000" foreground="#888888">IP: {ip_text}</span>'
        )

        # Available networks
        for child in self.listbox.get_children():
            self.listbox.remove(child)

        networks_raw = _run_cmd(
            "nmcli -t --escape no -f IN-USE,SSID,SIGNAL,SECURITY dev wifi list ifname wlan0"
        )
        seen = set()
        for line in networks_raw.splitlines():
            parts = line.split(":", 3)
            if len(parts) < 4:
                continue
            in_use = parts[0].strip() == "*"
            ssid = parts[1].strip()
            if not ssid or ssid in seen:
                continue
            seen.add(ssid)

            signal = parts[2].strip()
            security = parts[3].strip()

            row = Gtk.ListBoxRow()
            row.get_style_context().add_class("wifi-row")
            hbox = Gtk.Box(spacing=8)
            hbox.set_border_width(10)
            hbox.set_margin_start(6)
            hbox.set_margin_end(6)

            # Left side: SSID + security
            left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            ssid_label = Gtk.Label()
            prefix = "* " if in_use else ""
            ssid_label.set_markup(
                f'<span size="13000" weight="bold">'
                f'{prefix}{GLib.markup_escape_text(ssid)}</span>'
            )
            ssid_label.set_halign(Gtk.Align.START)
            left.pack_start(ssid_label, False, False, 0)

            sec_label = Gtk.Label()
            sec_label.set_markup(
                f'<span size="9000" foreground="#888888">'
                f'{security if security else "Open"}</span>'
            )
            sec_label.set_halign(Gtk.Align.START)
            left.pack_start(sec_label, False, False, 0)

            hbox.pack_start(left, True, True, 0)

            # Right side: signal + connect button
            right = Gtk.Box(spacing=8)
            right.set_valign(Gtk.Align.CENTER)

            sig_label = Gtk.Label()
            sig_label.set_markup(f'<span size="11000">{signal}%</span>')
            right.pack_start(sig_label, False, False, 0)

            if not in_use:
                conn_btn = Gtk.Button(label="Connect")
                conn_btn.connect(
                    "clicked", self._on_network_connect_clicked, ssid, security
                )
                right.pack_start(conn_btn, False, False, 0)
            else:
                connected_lbl = Gtk.Label()
                connected_lbl.set_markup(
                    '<span foreground="#2ecc71">Connected</span>'
                )
                right.pack_start(connected_lbl, False, False, 0)

            hbox.pack_start(right, False, False, 0)
            row.add(hbox)
            self.listbox.add(row)

        self.listbox.show_all()

    def _on_network_connect_clicked(self, widget, ssid, security):
        """User clicked Connect on a network."""
        if security and security != "--":
            self._show_password_dialog(ssid)
        else:
            self._do_connect_open(ssid)

    def _show_password_dialog(self, ssid):
        """Prompt for a WiFi password in a modal dialog."""
        dialog = Gtk.Dialog(
            title=f"Connect to {ssid}",
            transient_for=self.get_toplevel(),
            modal=True,
        )
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        connect_btn = dialog.add_button("Connect", Gtk.ResponseType.OK)
        connect_btn.get_style_context().add_class("suggested-action")

        content = dialog.get_content_area()
        content.set_spacing(8)
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        content.set_margin_start(12)
        content.set_margin_end(12)

        label = Gtk.Label()
        label.set_halign(Gtk.Align.START)
        label.set_markup(
            f'<span size="12000">Enter password for '
            f'<b>{GLib.markup_escape_text(ssid)}</b></span>'
        )
        content.pack_start(label, False, False, 0)

        password_entry = Gtk.Entry()
        password_entry.set_placeholder_text("Enter password...")
        password_entry.set_visibility(False)
        password_entry.set_activates_default(True)
        content.pack_start(password_entry, False, False, 0)

        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.show_all()
        password_entry.grab_focus()

        response = dialog.run()
        password = password_entry.get_text()
        dialog.destroy()

        if response == Gtk.ResponseType.OK:
            self._do_connect(ssid, password)

    def _do_connect(self, ssid, password):
        """Connect to the selected secured network."""
        result = _run_cmd(
            f"sudo nmcli dev wifi connect '{ssid}' password '{password}' ifname wlan0"
        )
        self._show_result(ssid, result)
        self.refresh()

    def _do_connect_open(self, ssid):
        """Connect to an open network."""
        result = _run_cmd(f"sudo nmcli dev wifi connect '{ssid}' ifname wlan0")
        self._show_result(ssid, result)
        self.refresh()

    def _show_result(self, ssid, message):
        dialog = Gtk.MessageDialog(
            transient_for=self.get_toplevel(),
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=f"WiFi: {ssid}",
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()
