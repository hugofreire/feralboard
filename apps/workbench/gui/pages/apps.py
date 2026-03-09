"""Apps listing page: discover and select kiosk apps."""

import json
import os

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


APPS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "kiosk_apps")


class AppsPage(Gtk.Box):
    """Apps listing page with cards for each kiosk app."""

    def __init__(self, on_back=None, on_app_selected=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._on_back = on_back
        self._on_app_selected = on_app_selected

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
        title.set_markup('<span size="18000" weight="bold">Apps</span>')
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

        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(12)
        self.grid.set_column_spacing(12)
        self.grid.set_margin_start(16)
        self.grid.set_margin_end(16)
        self.grid.set_margin_top(16)
        self.grid.set_margin_bottom(16)
        self.grid.set_column_homogeneous(True)

        sw.add(self.grid)
        self.pack_start(sw, True, True, 0)

    def refresh(self):
        """Rescan kiosk_apps/ and rebuild the grid."""
        for child in self.grid.get_children():
            self.grid.remove(child)

        apps = self._discover_apps()
        for i, app_info in enumerate(apps):
            btn = self._make_app_card(app_info)
            row = i // 2
            col = i % 2
            self.grid.attach(btn, col, row, 1, 1)

        self.grid.show_all()

    def _discover_apps(self):
        """Scan kiosk_apps/ for subdirs with app.json."""
        apps = []
        apps_dir = os.path.abspath(APPS_DIR)
        if not os.path.isdir(apps_dir):
            return apps
        for entry in sorted(os.listdir(apps_dir)):
            manifest = os.path.join(apps_dir, entry, "app.json")
            if os.path.isfile(manifest):
                try:
                    with open(manifest) as f:
                        info = json.load(f)
                    info.setdefault("name", entry)
                    info.setdefault("description", "")
                    info.setdefault("greeting", info["name"])
                    info["_dir"] = entry
                    apps.append(info)
                except Exception:
                    pass
        return apps

    def _make_app_card(self, app_info):
        """Create a nav-card style button for an app."""
        btn = Gtk.Button()
        btn.get_style_context().add_class("nav-card")
        btn.set_size_request(-1, 90)
        btn.connect("clicked", lambda w: self._select_app(app_info))

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        vbox.set_valign(Gtk.Align.CENTER)

        name_lbl = Gtk.Label()
        name_lbl.set_markup(
            f'<span size="14000" weight="bold">{app_info["name"]}</span>'
        )
        vbox.pack_start(name_lbl, False, False, 0)

        desc_lbl = Gtk.Label()
        desc_lbl.set_markup(
            f'<span size="9000" foreground="#a78bfa">{app_info["description"]}</span>'
        )
        vbox.pack_start(desc_lbl, False, False, 0)

        btn.add(vbox)
        return btn

    def _select_app(self, app_info):
        if self._on_app_selected:
            self._on_app_selected(app_info)

    def _go_back(self, widget):
        if self._on_back:
            self._on_back()
