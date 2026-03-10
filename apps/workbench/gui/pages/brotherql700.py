"""brother ql-700 kiosk app."""

import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

ENV_PATH = os.path.join(
    os.path.dirname(__file__), "../../kiosk_apps/brother-ql-700/.env"
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

WORKBENCH_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
WORKBENCH_BROTHER_QL = os.path.join(WORKBENCH_ROOT, "scripts", "brother_ql.sh")


def _resolve_brother_ql_bin():
    override = os.getenv("BROTHER_QL_BIN", "").strip()
    candidates = [
        override,
        WORKBENCH_BROTHER_QL,
        shutil.which("brother_ql") or "",
        "/home/pi/.local/bin/brother_ql",
    ]
    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            return candidate
    return override or WORKBENCH_BROTHER_QL

PRINT_CMD_TEMPLATE = os.getenv("PRINT_CMD_TEMPLATE", "")
PRINT_TIMEOUT = float(os.getenv("PRINT_TIMEOUT", "15"))
DEFAULT_COPIES = int(os.getenv("DEFAULT_COPIES", "1"))
MAX_COPIES = int(os.getenv("MAX_COPIES", "50"))
LABEL_DESC = os.getenv("LABEL_DESC", "12mm x 30.48mm (1/2\" x 100')")
PRINTER_DESC = os.getenv("PRINTER_DESC", "USB")
BROTHER_QL_BIN = _resolve_brother_ql_bin()
PRINTER_PATH = os.getenv("PRINTER_PATH", "/dev/usb/lp0")
PRINT_BACKEND = os.getenv("PRINT_BACKEND", "linux_kernel")
PRINTER_MODEL = os.getenv("PRINTER_MODEL", "QL-700")
LABEL_TYPE = os.getenv("LABEL_TYPE", "12")
LABEL_WIDTH_MM = float(os.getenv("LABEL_WIDTH_MM", "12"))
LABEL_HEIGHT_MM = float(os.getenv("LABEL_HEIGHT_MM", "30.48"))
LABEL_DPI = int(os.getenv("LABEL_DPI", "300"))
CODE39_HORIZONTAL = os.getenv("CODE39_HORIZONTAL", "true").lower() in ("1", "true", "yes")

CIRCLE_GREEN = "\U0001f7e2"
CIRCLE_RED = "\U0001f534"


class Brotherql700Page(Gtk.Box):
    """brother ql-700 — custom kiosk page."""

    def __init__(self, on_unlock=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.get_style_context().add_class("kiosk-page")
        self._on_unlock = on_unlock
        self._press_timer = None

        self._title_label = None
        self._status_label = None
        self._printer_icon = None
        self._printer_status = None
        self._text_entry = None
        self._code39_switch = None
        self._copies_spin = None
        self._print_btn = None

        self._build_ui()

    def _build_ui(self):
        # Title with long-press to unlock
        event_box = Gtk.EventBox()
        event_box.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK
        )
        event_box.connect("button-press-event", self._on_press)
        event_box.connect("button-release-event", self._on_release)

        self._title_label = Gtk.Label()
        self._title_label.set_markup(
            '<span size="20000" weight="bold" foreground="white">'
            'brother ql-700</span>'
        )
        self._title_label.set_margin_top(16)
        self._title_label.set_margin_bottom(8)
        event_box.add(self._title_label)
        self.pack_start(event_box, False, False, 0)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content.set_margin_start(24)
        content.set_margin_end(24)
        content.set_margin_top(16)
        content.set_margin_bottom(24)

        desc = Gtk.Label()
        desc.set_halign(Gtk.Align.START)
        desc.set_markup(
            f'<span size="11000" foreground="#8b949e">'
            f'Printer: {PRINTER_DESC} | Label: {LABEL_DESC}</span>'
        )
        content.pack_start(desc, False, False, 0)

        printer_row = Gtk.Box(spacing=8)
        printer_row.set_margin_bottom(6)

        self._printer_icon = Gtk.Label()
        self._printer_icon.set_markup(f'<span size="14000">{CIRCLE_RED}</span>')
        printer_row.pack_start(self._printer_icon, False, False, 0)

        self._printer_status = Gtk.Label()
        self._printer_status.set_halign(Gtk.Align.START)
        self._printer_status.set_markup(
            '<span size="11000" foreground="#8b949e">Impressora: a verificar...</span>'
        )
        printer_row.pack_start(self._printer_status, False, False, 0)

        content.pack_start(printer_row, False, False, 0)

        text_label = Gtk.Label()
        text_label.set_halign(Gtk.Align.START)
        text_label.set_markup(
            '<span size="12000" foreground="#a0a0a0">Texto da etiqueta</span>'
        )
        content.pack_start(text_label, False, False, 0)

        self._text_entry = Gtk.Entry()
        self._text_entry.set_placeholder_text("Digite o texto...")
        self._text_entry.set_margin_bottom(6)
        content.pack_start(self._text_entry, False, False, 0)

        mode_row = Gtk.Box(spacing=10)
        mode_row.set_margin_bottom(6)

        mode_label = Gtk.Label()
        mode_label.set_halign(Gtk.Align.START)
        mode_label.set_markup(
            '<span size="12000" foreground="#a0a0a0">Modo</span>'
        )
        mode_row.pack_start(mode_label, False, False, 0)

        mode_text = Gtk.Label()
        mode_text.set_halign(Gtk.Align.START)
        mode_text.set_markup(
            '<span size="11000" foreground="#8b949e">Texto</span>'
        )
        mode_row.pack_start(mode_text, False, False, 0)

        self._code39_switch = Gtk.Switch()
        self._code39_switch.set_active(False)
        mode_row.pack_start(self._code39_switch, False, False, 0)

        mode_barcode = Gtk.Label()
        mode_barcode.set_halign(Gtk.Align.START)
        mode_barcode.set_markup(
            '<span size="11000" foreground="#8b949e">Code39</span>'
        )
        mode_row.pack_start(mode_barcode, False, False, 0)

        content.pack_start(mode_row, False, False, 0)

        copies_row = Gtk.Box(spacing=10)
        copies_row.set_margin_bottom(8)

        copies_label = Gtk.Label()
        copies_label.set_halign(Gtk.Align.START)
        copies_label.set_markup(
            '<span size="12000" foreground="#a0a0a0">Quantidade</span>'
        )
        copies_row.pack_start(copies_label, False, False, 0)

        adjustment = Gtk.Adjustment(
            value=max(DEFAULT_COPIES, 1),
            lower=1,
            upper=max(MAX_COPIES, 1),
            step_increment=1,
            page_increment=5,
        )
        self._copies_spin = Gtk.SpinButton()
        self._copies_spin.set_adjustment(adjustment)
        self._copies_spin.set_digits(0)
        self._copies_spin.set_numeric(True)
        self._copies_spin.set_margin_start(8)
        copies_row.pack_start(self._copies_spin, False, False, 0)

        content.pack_start(copies_row, False, False, 0)

        self._print_btn = Gtk.Button(label="Imprimir")
        self._print_btn.get_style_context().add_class("suggested-action")
        self._print_btn.connect("clicked", self._on_print_clicked)
        content.pack_start(self._print_btn, False, False, 0)

        self._status_label = Gtk.Label()
        self._status_label.set_halign(Gtk.Align.START)
        self._status_label.set_margin_top(10)
        self._set_status("Pronto para imprimir.", "#8b949e")
        content.pack_start(self._status_label, False, False, 0)

        self.pack_start(content, True, True, 0)

    def load_app(self, app_info):
        app_name = app_info.get("name", "brother ql-700")
        self._title_label.set_markup(
            f'<span size="20000" weight="bold" foreground="white">'
            f'{app_name}</span>'
        )
        self._set_status("Pronto para imprimir.", "#8b949e")
        self._refresh_printer_status()

    def cleanup(self):
        pass

    def update_from_rx(self, rx_buffer):
        pass

    def _build_label_image(self, text, code39=False):
        try:
            from PIL import Image, ImageDraw, ImageFont
        except Exception as exc:
            raise RuntimeError("Pillow não instalado") from exc

        width_px = max(1, int((LABEL_WIDTH_MM / 25.4) * LABEL_DPI))
        height_px = max(1, int((LABEL_HEIGHT_MM / 25.4) * LABEL_DPI))
        image = Image.new("RGB", (width_px, height_px), "white")
        draw = ImageDraw.Draw(image)

        if code39:
            if CODE39_HORIZONTAL:
                barcode_image = Image.new("RGB", (height_px, width_px), "white")
                barcode_draw = ImageDraw.Draw(barcode_image)
                self._draw_code39(barcode_draw, text, height_px, width_px)
                barcode_image = barcode_image.rotate(90, expand=True)
                image = Image.new("RGB", (width_px, height_px), "white")
                image.paste(barcode_image, (0, 0))
            else:
                self._draw_code39(draw, text, width_px, height_px)
            fd, path = tempfile.mkstemp(prefix="brother_ql_label_", suffix=".png")
            os.close(fd)
            image.save(path)
            return path

        def text_width(value, font):
            bbox = draw.textbbox((0, 0), value, font=font)
            return bbox[2] - bbox[0]

        def wrap_text(value, font, max_width):
            words = value.split()
            if not words:
                return [value]
            lines = []
            line = ""
            for word in words:
                test = f"{line} {word}".strip()
                if text_width(test, font) <= max_width:
                    line = test
                else:
                    if line:
                        lines.append(line)
                    line = word
            if line:
                lines.append(line)

            if any(text_width(item, font) > max_width for item in lines):
                lines = []
                current = ""
                for ch in value:
                    test = current + ch
                    if text_width(test, font) <= max_width or not current:
                        current = test
                    else:
                        lines.append(current)
                        current = ch
                if current:
                    lines.append(current)
            return lines

        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        best_font = ImageFont.load_default()
        best_lines = [text]
        for size in range(32, 11, -2):
            try:
                font = ImageFont.truetype(font_path, size)
            except Exception:
                font = ImageFont.load_default()
            lines = wrap_text(text, font, width_px - 10)
            line_height = font.getbbox("Ag")[3] - font.getbbox("Ag")[1]
            total_height = len(lines) * line_height + max(len(lines) - 1, 0) * 4
            if total_height <= height_px - 10:
                best_font = font
                best_lines = lines
                break

        line_height = best_font.getbbox("Ag")[3] - best_font.getbbox("Ag")[1]
        total_height = len(best_lines) * line_height + max(len(best_lines) - 1, 0) * 4
        y = (height_px - total_height) // 2

        for line in best_lines:
            line_width = text_width(line, best_font)
            x = max((width_px - line_width) // 2, 0)
            draw.text((x, y), line, font=best_font, fill="black")
            y += line_height + 4

        fd, path = tempfile.mkstemp(prefix="brother_ql_label_", suffix=".png")
        os.close(fd)
        image.save(path)
        return path

    def _draw_code39(self, draw, text, width_px, height_px):
        patterns = {
            "0": "nnnwwnwnn",
            "1": "wnnwnnnnw",
            "2": "nnwwnnnnw",
            "3": "wnwwnnnnn",
            "4": "nnnwwnnnw",
            "5": "wnnwwnnnn",
            "6": "nnwwwnnnn",
            "7": "nnnwnnwnw",
            "8": "wnnwnnwnn",
            "9": "nnwwnnwnn",
            "A": "wnnnnwnnw",
            "B": "nnwnnwnnw",
            "C": "wnwnnwnnn",
            "D": "nnnnwwnnw",
            "E": "wnnnwwnnn",
            "F": "nnwnwwnnn",
            "G": "nnnnnwwnw",
            "H": "wnnnnwwnn",
            "I": "nnwnnwwnn",
            "J": "nnnnwwwnn",
            "K": "wnnnnnnww",
            "L": "nnwnnnnww",
            "M": "wnwnnnnwn",
            "N": "nnnnwnnww",
            "O": "wnnnwnnwn",
            "P": "nnwnwnnwn",
            "Q": "nnnnnnwww",
            "R": "wnnnnnwwn",
            "S": "nnwnnnwwn",
            "T": "nnnnwnwwn",
            "U": "wwnnnnnnw",
            "V": "nwwnnnnnw",
            "W": "wwwnnnnnn",
            "X": "nwnnwnnnw",
            "Y": "wwnnwnnnn",
            "Z": "nwwnwnnnn",
            "-": "nwnnnnwnw",
            ".": "wwnnnnwnn",
            " ": "nwwnnnwnn",
            "$": "nwnwnwnnn",
            "/": "nwnwnnnwn",
            "+": "nwnnnwnwn",
            "%": "nnnwnwnwn",
            "*": "nwnnwnwnn",
        }

        content = text.strip().upper()
        if not content:
            raise RuntimeError("Texto vazio")
        for ch in content:
            if ch not in patterns:
                raise RuntimeError(f"Caractere inválido: {ch}")

        encoded = f"*{content}*"
        modules = []
        for index, ch in enumerate(encoded):
            pattern = patterns[ch]
            for i, symbol in enumerate(pattern):
                width = 3 if symbol == "w" else 1
                is_bar = i % 2 == 0
                modules.append((is_bar, width))
            if index != len(encoded) - 1:
                modules.append((False, 1))  # inter-character gap

        total_units = sum(width for _is_bar, width in modules)
        if total_units <= 0:
            return

        scale = max(1, int((width_px - 20) / total_units))
        x = max((width_px - total_units * scale) // 2, 0)
        y = 6
        bar_height = max(height_px - 12, 1)

        for is_bar, width in modules:
            w_px = width * scale
            if is_bar:
                draw.rectangle([x, y, x + w_px - 1, y + bar_height], fill="black")
            x += w_px

    def _refresh_printer_status(self):
        if not self._printer_status:
            return
        self._printer_status.set_markup(
            '<span size="11000" foreground="#8b949e">Impressora: a verificar...</span>'
        )
        self._printer_icon.set_markup(f'<span size="14000">{CIRCLE_RED}</span>')
        threading.Thread(target=self._check_printer_status, daemon=True).start()

    def _check_printer_status(self):
        connected = False
        detail = "USB indisponível"
        printer_present = False
        try:
            if os.path.exists(PRINTER_PATH):
                printer_present = True
                detail = PRINTER_PATH
            else:
                result = subprocess.run(
                    ["lsusb"], capture_output=True, text=True, timeout=3
                )
                if result.returncode == 0 and "Brother" in result.stdout:
                    printer_present = True
                    detail = "Brother USB"
        except Exception as exc:
            detail = str(exc)

        cmd_present = bool(shutil.which(BROTHER_QL_BIN) or os.path.exists(BROTHER_QL_BIN))
        if printer_present and os.path.exists(PRINTER_PATH):
            if not os.access(PRINTER_PATH, os.R_OK | os.W_OK):
                detail = "sem permissao em /dev/usb/lp0"
                printer_present = False

        if printer_present and cmd_present:
            connected = True
        elif printer_present and not cmd_present:
            detail = "brother_ql ausente"

        GLib.idle_add(self._set_printer_status, connected, detail)

    def _set_printer_status(self, connected, detail):
        if not self._printer_status:
            return False
        if connected:
            self._printer_icon.set_markup(f'<span size="14000">{CIRCLE_GREEN}</span>')
            self._printer_status.set_markup(
                f'<span size="11000" foreground="#2ecc71">'
                f'Impressora: conectada ({detail})</span>'
            )
        else:
            self._printer_icon.set_markup(f'<span size="14000">{CIRCLE_RED}</span>')
            self._printer_status.set_markup(
                f'<span size="11000" foreground="#e74c3c">'
                f'Impressora: desligada ({detail})</span>'
            )
        return False

    def _on_print_clicked(self, _widget):
        text = (self._text_entry.get_text() or "").strip()
        copies = int(self._copies_spin.get_value())
        code39 = bool(self._code39_switch and self._code39_switch.get_active())

        if not text:
            self._set_status("Introduza o texto da etiqueta.", "#e74c3c")
            return
        if copies < 1:
            self._set_status("Quantidade inválida.", "#e74c3c")
            return
        if not os.path.exists(BROTHER_QL_BIN):
            self._set_status("brother_ql não encontrado.", "#e74c3c")
            return

        self._print_btn.set_sensitive(False)
        self._set_status("A imprimir...", "#f39c12")
        threading.Thread(
            target=self._run_print_job, args=(text, copies, code39), daemon=True
        ).start()

    def _run_print_job(self, text, copies, code39):
        image_path = None
        try:
            image_path = self._build_label_image(text, code39=code39)
            cmd_template = PRINT_CMD_TEMPLATE
            if not cmd_template:
                cmd_template = (
                    f"{BROTHER_QL_BIN} -b {PRINT_BACKEND} -m {PRINTER_MODEL} "
                    f"-p {PRINTER_PATH} print -l {LABEL_TYPE} {{image}}"
                )
            for _ in range(copies):
                cmd = cmd_template.format(image=shlex.quote(image_path))
                args = shlex.split(cmd)
                result = subprocess.run(
                    args, capture_output=True, text=True, timeout=PRINT_TIMEOUT
                )
                if result.returncode != 0:
                    stderr = (result.stderr or result.stdout or "").strip()
                    raise RuntimeError(stderr or "Print failed")
        except Exception as exc:
            GLib.idle_add(
                self._on_print_failed,
                f"Erro ao imprimir: {exc}",
            )
            return
        finally:
            if image_path:
                try:
                    os.remove(image_path)
                except OSError:
                    pass

        GLib.idle_add(self._on_print_success, copies)

    def _on_print_success(self, copies):
        self._print_btn.set_sensitive(True)
        self._set_status(f"Impressão concluída ({copies}x).", "#2ecc71")
        return False

    def _on_print_failed(self, message):
        self._print_btn.set_sensitive(True)
        self._set_status(message, "#e74c3c")
        return False

    def _set_status(self, message, color):
        if self._status_label:
            self._status_label.set_markup(
                f'<span size="11000" foreground="{color}">{message}</span>'
            )

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
