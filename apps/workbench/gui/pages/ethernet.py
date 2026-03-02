"""Ethernet configuration page: IP, gateway, DNS, DHCP/Static toggle."""

import subprocess

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib


def _run_cmd(cmd):
    """Run a shell command and return stdout."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"


class EthernetPage(Gtk.Box):
    """Ethernet configuration with DHCP/Static IP management."""

    IFACE = "eth0"

    def __init__(self, on_back=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._on_back = on_back
        self._con_name = None  # NetworkManager connection name

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
        title.set_markup('<span size="18000" weight="bold">Ethernet</span>')
        title.set_hexpand(True)
        header.pack_start(title, True, True, 0)

        refresh_btn = Gtk.Button(label="Refresh")
        refresh_btn.connect("clicked", lambda w: self.refresh())
        header.pack_start(refresh_btn, False, False, 0)

        self.pack_start(header, False, False, 0)
        self.pack_start(Gtk.Separator(), False, False, 0)

        # Scrollable content
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.set_vexpand(True)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        content.set_margin_start(16)
        content.set_margin_end(16)
        content.set_margin_top(12)
        content.set_margin_bottom(16)

        # ── Link status ──
        self.link_label = Gtk.Label()
        self.link_label.set_halign(Gtk.Align.START)
        content.pack_start(self.link_label, False, False, 0)

        self.mac_label = Gtk.Label()
        self.mac_label.set_halign(Gtk.Align.START)
        content.pack_start(self.mac_label, False, False, 0)

        self.speed_label = Gtk.Label()
        self.speed_label.set_halign(Gtk.Align.START)
        content.pack_start(self.speed_label, False, False, 0)

        content.pack_start(Gtk.Separator(), False, False, 4)

        # ── Current IP info (read-only display) ──
        current_title = Gtk.Label()
        current_title.set_markup(
            '<span size="14000" weight="bold">Current Configuration</span>'
        )
        current_title.set_halign(Gtk.Align.START)
        content.pack_start(current_title, False, False, 0)

        info_grid = Gtk.Grid()
        info_grid.set_column_spacing(12)
        info_grid.set_row_spacing(4)

        info_fields = ["IP Address:", "Subnet:", "Gateway:", "DNS:", "Method:"]
        self.info_labels = {}
        for i, text in enumerate(info_fields):
            lbl = Gtk.Label(label=text)
            lbl.set_halign(Gtk.Align.START)
            lbl.get_style_context().add_class("section-title")
            info_grid.attach(lbl, 0, i, 1, 1)

            val = Gtk.Label(label="--")
            val.set_halign(Gtk.Align.START)
            val.set_selectable(True)
            info_grid.attach(val, 1, i, 1, 1)
            self.info_labels[text] = val

        content.pack_start(info_grid, False, False, 0)

        content.pack_start(Gtk.Separator(), False, False, 8)

        # ── Configuration section ──
        config_title = Gtk.Label()
        config_title.set_markup(
            '<span size="14000" weight="bold">Configure</span>'
        )
        config_title.set_halign(Gtk.Align.START)
        content.pack_start(config_title, False, False, 0)

        # DHCP / Static toggle
        method_box = Gtk.Box(spacing=12)
        method_box.set_margin_top(4)

        method_lbl = Gtk.Label()
        method_lbl.set_markup('<span size="12000">Mode:</span>')
        method_box.pack_start(method_lbl, False, False, 0)

        self.dhcp_radio = Gtk.RadioButton.new_with_label(None, "DHCP")
        self.dhcp_radio.connect("toggled", self._on_method_toggled)
        method_box.pack_start(self.dhcp_radio, False, False, 0)

        self.static_radio = Gtk.RadioButton.new_with_label_from_widget(
            self.dhcp_radio, "Static"
        )
        method_box.pack_start(self.static_radio, False, False, 0)

        content.pack_start(method_box, False, False, 0)

        # Static IP fields
        self.static_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.static_box.set_margin_top(8)

        self.ip_entry = self._make_field(self.static_box, "IP Address", "192.168.0.100")
        self.mask_entry = self._make_field(self.static_box, "Subnet Mask (CIDR)", "24")
        self.gw_entry = self._make_field(self.static_box, "Gateway", "192.168.0.1")
        self.dns_entry = self._make_field(self.static_box, "DNS Server", "8.8.8.8")

        content.pack_start(self.static_box, False, False, 0)

        # Apply button
        btn_box = Gtk.Box(spacing=8)
        btn_box.set_margin_top(12)

        apply_btn = Gtk.Button(label="Apply")
        apply_btn.get_style_context().add_class("suggested-action")
        apply_btn.set_size_request(120, 42)
        apply_btn.connect("clicked", self._on_apply)
        btn_box.pack_start(apply_btn, False, False, 0)

        self.status_msg = Gtk.Label()
        self.status_msg.set_halign(Gtk.Align.START)
        btn_box.pack_start(self.status_msg, True, True, 0)

        content.pack_start(btn_box, False, False, 0)

        sw.add(content)
        self.pack_start(sw, True, True, 0)

        # Initial state: DHCP selected, static fields hidden
        self.static_box.set_no_show_all(True)
        self._on_method_toggled(self.dhcp_radio)

    def _make_field(self, parent, label_text, placeholder):
        """Create a labeled entry field and return the entry widget."""
        lbl = Gtk.Label()
        lbl.set_markup(f'<span size="10000" foreground="#a0a0a0">{label_text}</span>')
        lbl.set_halign(Gtk.Align.START)
        parent.pack_start(lbl, False, False, 0)

        entry = Gtk.Entry()
        entry.set_placeholder_text(placeholder)
        parent.pack_start(entry, False, False, 0)
        return entry

    def _go_back(self, widget):
        if self._on_back:
            self._on_back()

    def _on_method_toggled(self, widget):
        """Show/hide static fields based on selected mode."""
        is_static = self.static_radio.get_active()
        if is_static:
            self.static_box.set_no_show_all(False)
            self.static_box.show_all()
            self.static_box.set_visible(True)
        else:
            self.static_box.set_visible(False)
            self.static_box.set_no_show_all(True)

    def _find_connection_name(self):
        """Find the NetworkManager connection profile for eth0."""
        # First try active connections
        raw = _run_cmd(
            f"nmcli -t -f NAME,DEVICE con show | grep {self.IFACE}"
        )
        for line in raw.splitlines():
            parts = line.split(":")
            if len(parts) >= 2 and parts[1].strip() == self.IFACE:
                return parts[0].strip()
        # Fallback: look for any ethernet connection
        raw = _run_cmd("nmcli -t -f NAME,TYPE con show")
        for line in raw.splitlines():
            parts = line.split(":")
            if len(parts) >= 2 and "ethernet" in parts[1]:
                return parts[0].strip()
        return None

    def refresh(self):
        """Read current ethernet status and configuration."""
        self.status_msg.set_text("")

        # Find connection name
        self._con_name = self._find_connection_name()

        # Link status
        dev_state = _run_cmd(
            f"nmcli -t -f DEVICE,STATE,CONNECTION dev status | grep {self.IFACE}"
        )
        if dev_state:
            parts = dev_state.split(":")
            state = parts[1] if len(parts) >= 2 else "unknown"
            connected = state == "connected"
            if connected:
                self.link_label.set_markup(
                    '<span size="13000" foreground="#2ecc71">'
                    'Link: Connected</span>'
                )
            elif "unavailable" in state:
                self.link_label.set_markup(
                    '<span size="13000" foreground="#e74c3c">'
                    'Link: No cable</span>'
                )
            else:
                self.link_label.set_markup(
                    f'<span size="13000" foreground="#f39c12">'
                    f'Link: {state}</span>'
                )
        else:
            self.link_label.set_markup(
                '<span size="13000" foreground="#e74c3c">'
                'Link: Interface not found</span>'
            )

        # MAC address
        mac = _run_cmd(f"cat /sys/class/net/{self.IFACE}/address 2>/dev/null")
        self.mac_label.set_markup(
            f'<span size="10000" foreground="#888888">MAC: {mac or "N/A"}</span>'
        )

        # Link speed
        speed = _run_cmd(f"cat /sys/class/net/{self.IFACE}/speed 2>/dev/null")
        if speed and speed.isdigit() and int(speed) > 0:
            self.speed_label.set_markup(
                f'<span size="10000" foreground="#888888">'
                f'Speed: {speed} Mbps</span>'
            )
        else:
            self.speed_label.set_markup(
                '<span size="10000" foreground="#888888">Speed: --</span>'
            )

        # Read current config from NetworkManager
        if self._con_name:
            raw = _run_cmd(
                f"nmcli -t -f ipv4.method,ipv4.addresses,ipv4.gateway,ipv4.dns "
                f'con show "{self._con_name}"'
            )
            config = {}
            for line in raw.splitlines():
                key, _, val = line.partition(":")
                config[key.strip()] = val.strip()

            method = config.get("ipv4.method", "auto")
            addresses = config.get("ipv4.addresses", "")
            gateway = config.get("ipv4.gateway", "")
            dns = config.get("ipv4.dns", "")

            self.info_labels["Method:"].set_text(
                "DHCP" if method == "auto" else "Static"
            )

            # For DHCP, get the actual assigned IP from device
            if method == "auto":
                actual_ip = _run_cmd(
                    f"nmcli -t -f IP4.ADDRESS dev show {self.IFACE} "
                    "2>/dev/null | head -1"
                )
                if actual_ip:
                    actual_ip = actual_ip.split(":")[-1].strip()
                actual_gw = _run_cmd(
                    f"nmcli -t -f IP4.GATEWAY dev show {self.IFACE} "
                    "2>/dev/null | head -1"
                )
                if actual_gw:
                    actual_gw = actual_gw.split(":")[-1].strip()
                actual_dns = _run_cmd(
                    f"nmcli -t -f IP4.DNS dev show {self.IFACE} "
                    "2>/dev/null | head -1"
                )
                if actual_dns:
                    actual_dns = actual_dns.split(":")[-1].strip()

                ip_str = actual_ip or "--"
                if "/" in ip_str:
                    ip_part, cidr = ip_str.rsplit("/", 1)
                    self.info_labels["IP Address:"].set_text(ip_part)
                    self.info_labels["Subnet:"].set_text(f"/{cidr}")
                else:
                    self.info_labels["IP Address:"].set_text(ip_str)
                    self.info_labels["Subnet:"].set_text("--")
                self.info_labels["Gateway:"].set_text(actual_gw or "--")
                self.info_labels["DNS:"].set_text(actual_dns or "--")

                # Set radio to DHCP
                self.dhcp_radio.set_active(True)
            else:
                # Static config
                if addresses and "/" in addresses:
                    ip_part, cidr = addresses.rsplit("/", 1)
                    self.info_labels["IP Address:"].set_text(ip_part)
                    self.info_labels["Subnet:"].set_text(f"/{cidr}")
                    # Pre-fill edit fields
                    self.ip_entry.set_text(ip_part)
                    self.mask_entry.set_text(cidr)
                else:
                    self.info_labels["IP Address:"].set_text(addresses or "--")
                    self.info_labels["Subnet:"].set_text("--")

                self.info_labels["Gateway:"].set_text(gateway or "--")
                self.info_labels["DNS:"].set_text(dns or "--")

                # Pre-fill edit fields
                if gateway:
                    self.gw_entry.set_text(gateway)
                if dns:
                    self.dns_entry.set_text(dns)

                # Set radio to Static
                self.static_radio.set_active(True)
        else:
            for val in self.info_labels.values():
                val.set_text("--")
            self.info_labels["Method:"].set_text("No connection profile")

    def _on_apply(self, widget):
        """Apply the configuration via nmcli."""
        if not self._con_name:
            self._con_name = self._find_connection_name()
            if not self._con_name:
                self.status_msg.set_markup(
                    '<span foreground="#e74c3c">No connection profile found</span>'
                )
                return

        con = self._con_name

        if self.dhcp_radio.get_active():
            # Switch to DHCP
            result = _run_cmd(f'nmcli con mod "{con}" ipv4.method auto '
                              f'ipv4.addresses "" ipv4.gateway "" ipv4.dns ""')
            if "Error" in result:
                self.status_msg.set_markup(
                    f'<span foreground="#e74c3c">{GLib.markup_escape_text(result)}</span>'
                )
                return
        else:
            # Switch to Static
            ip = self.ip_entry.get_text().strip()
            mask = self.mask_entry.get_text().strip()
            gw = self.gw_entry.get_text().strip()
            dns = self.dns_entry.get_text().strip()

            if not ip or not mask:
                self.status_msg.set_markup(
                    '<span foreground="#e74c3c">IP and subnet mask required</span>'
                )
                return

            addr = f"{ip}/{mask}"
            cmd = f'nmcli con mod "{con}" ipv4.method manual ipv4.addresses "{addr}"'
            if gw:
                cmd += f' ipv4.gateway "{gw}"'
            if dns:
                cmd += f' ipv4.dns "{dns}"'

            result = _run_cmd(cmd)
            if "Error" in result:
                self.status_msg.set_markup(
                    f'<span foreground="#e74c3c">{GLib.markup_escape_text(result)}</span>'
                )
                return

        # Bring connection up to apply changes
        up_result = _run_cmd(f'nmcli con up "{con}"')
        if "Error" in up_result and "not available" not in up_result.lower():
            self.status_msg.set_markup(
                f'<span foreground="#f39c12">Saved. '
                f'{GLib.markup_escape_text(up_result)}</span>'
            )
        else:
            self.status_msg.set_markup(
                '<span foreground="#2ecc71">Applied successfully</span>'
            )

        # Refresh display
        self.refresh()
