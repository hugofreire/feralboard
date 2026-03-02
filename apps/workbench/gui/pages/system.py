"""System monitoring page: RAM, Swap, Disk, CPU temp, uptime."""

import subprocess

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


def _run_cmd(cmd):
    """Run a shell command and return stdout."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"


def _human_bytes(b):
    for unit in ["B", "KB", "MB", "GB"]:
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"


class SystemPage(Gtk.Box):
    """System monitoring page with RAM, swap, disk, and CPU info."""

    def __init__(self, on_back=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._on_back = on_back

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
        title.set_markup('<span size="18000" weight="bold">System</span>')
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

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content.set_margin_start(16)
        content.set_margin_end(16)
        content.set_margin_top(12)
        content.set_margin_bottom(12)

        # RAM
        ram_title = Gtk.Label()
        ram_title.set_markup('<span size="15000" weight="bold">Memory (RAM)</span>')
        ram_title.set_halign(Gtk.Align.START)
        content.pack_start(ram_title, False, False, 0)

        self.ram_bar = Gtk.LevelBar()
        self.ram_bar.set_min_value(0)
        self.ram_bar.set_max_value(1)
        self.ram_bar.set_size_request(-1, 30)
        content.pack_start(self.ram_bar, False, False, 0)

        self.ram_label = Gtk.Label()
        self.ram_label.set_halign(Gtk.Align.START)
        content.pack_start(self.ram_label, False, False, 0)

        content.pack_start(Gtk.Separator(), False, False, 4)

        # Swap
        swap_title = Gtk.Label()
        swap_title.set_markup('<span size="15000" weight="bold">Swap</span>')
        swap_title.set_halign(Gtk.Align.START)
        content.pack_start(swap_title, False, False, 0)

        self.swap_bar = Gtk.LevelBar()
        self.swap_bar.set_min_value(0)
        self.swap_bar.set_max_value(1)
        self.swap_bar.set_size_request(-1, 30)
        content.pack_start(self.swap_bar, False, False, 0)

        self.swap_label = Gtk.Label()
        self.swap_label.set_halign(Gtk.Align.START)
        content.pack_start(self.swap_label, False, False, 0)

        content.pack_start(Gtk.Separator(), False, False, 4)

        # Disk
        disk_title = Gtk.Label()
        disk_title.set_markup('<span size="15000" weight="bold">Disk Usage</span>')
        disk_title.set_halign(Gtk.Align.START)
        content.pack_start(disk_title, False, False, 0)

        self.disk_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        content.pack_start(self.disk_box, False, False, 0)

        content.pack_start(Gtk.Separator(), False, False, 4)

        # System info
        misc_title = Gtk.Label()
        misc_title.set_markup('<span size="15000" weight="bold">System Info</span>')
        misc_title.set_halign(Gtk.Align.START)
        content.pack_start(misc_title, False, False, 0)

        self.cpu_temp_label = Gtk.Label()
        self.cpu_temp_label.set_halign(Gtk.Align.START)
        content.pack_start(self.cpu_temp_label, False, False, 0)

        self.uptime_label = Gtk.Label()
        self.uptime_label.set_halign(Gtk.Align.START)
        content.pack_start(self.uptime_label, False, False, 0)

        self.hostname_label = Gtk.Label()
        self.hostname_label.set_halign(Gtk.Align.START)
        content.pack_start(self.hostname_label, False, False, 0)

        sw.add(content)
        self.pack_start(sw, True, True, 0)

    def _go_back(self, widget):
        if self._on_back:
            self._on_back()

    def refresh(self):
        """Fetch RAM, swap, disk, CPU temp, uptime."""
        # RAM
        mem_raw = _run_cmd("free -b | grep Mem")
        parts = mem_raw.split()
        if len(parts) >= 3:
            total = int(parts[1])
            used = int(parts[2])
            frac = used / total if total > 0 else 0
            self.ram_bar.set_value(frac)
            self.ram_label.set_markup(
                f'<span size="11000" foreground="#aaaaaa">'
                f'{_human_bytes(used)} / {_human_bytes(total)} '
                f'({int(frac * 100)}%)</span>'
            )

        # Swap
        swap_raw = _run_cmd("free -b | grep Swap")
        parts = swap_raw.split()
        if len(parts) >= 3:
            total = int(parts[1])
            used = int(parts[2])
            frac = used / total if total > 0 else 0
            self.swap_bar.set_value(frac)
            self.swap_label.set_markup(
                f'<span size="11000" foreground="#aaaaaa">'
                f'{_human_bytes(used)} / {_human_bytes(total)} '
                f'({int(frac * 100)}%)</span>'
            )

        # Disk
        for child in self.disk_box.get_children():
            self.disk_box.remove(child)

        disk_raw = _run_cmd("df -h --output=target,size,used,avail,pcent / /boot/firmware")
        lines = disk_raw.strip().splitlines()
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 5:
                mount = parts[0]
                size = parts[1]
                used = parts[2]
                avail = parts[3]
                pcent = parts[4].replace("%", "")

                row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)

                name = Gtk.Label()
                name.set_markup(
                    f'<span size="12000" weight="bold">{mount}</span>'
                )
                name.set_halign(Gtk.Align.START)
                row.pack_start(name, False, False, 0)

                bar = Gtk.LevelBar()
                bar.set_min_value(0)
                bar.set_max_value(1)
                bar.set_value(int(pcent) / 100)
                bar.set_size_request(-1, 20)
                row.pack_start(bar, False, False, 0)

                detail = Gtk.Label()
                detail.set_markup(
                    f'<span size="10000" foreground="#aaaaaa">'
                    f'{used} / {size} ({pcent}%) — {avail} free</span>'
                )
                detail.set_halign(Gtk.Align.START)
                row.pack_start(detail, False, False, 0)

                self.disk_box.pack_start(row, False, False, 0)

        self.disk_box.show_all()

        # CPU temp
        temp_raw = _run_cmd("cat /sys/class/thermal/thermal_zone0/temp")
        try:
            temp_c = int(temp_raw) / 1000
            self.cpu_temp_label.set_markup(
                f'<span size="12000" foreground="#aaaaaa">'
                f'CPU Temp: {temp_c:.1f} °C</span>'
            )
        except ValueError:
            self.cpu_temp_label.set_markup(
                '<span size="12000" foreground="#aaaaaa">CPU Temp: N/A</span>'
            )

        # Uptime
        uptime = _run_cmd("uptime -p")
        self.uptime_label.set_markup(
            f'<span size="12000" foreground="#aaaaaa">{uptime}</span>'
        )

        # Hostname
        hostname = _run_cmd("hostname")
        self.hostname_label.set_markup(
            f'<span size="12000" foreground="#aaaaaa">Host: {hostname}</span>'
        )
