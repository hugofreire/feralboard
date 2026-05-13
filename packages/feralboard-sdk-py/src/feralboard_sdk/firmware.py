"""Firmware HEX deployment helpers for FeralBoard OEM integrations."""

from __future__ import annotations

from dataclasses import dataclass
import glob
import os
from pathlib import Path
import shutil
import subprocess
from typing import Callable


AVRDUDE_PART = "m4809"
AVRDUDE_PROGRAMMER = "serialupdi"
AVRDUDE_BAUDRATE = 115200
PI_MODEL_PATH = "/proc/device-tree/model"


class FirmwareDeploymentError(RuntimeError):
    """Raised when firmware deployment cannot complete."""


class HexValidationError(ValueError):
    """Raised when a HEX file is missing or not valid Intel HEX."""


@dataclass(frozen=True)
class FirmwareDeploymentResult:
    """Result metadata for a firmware deployment attempt."""

    hex_path: str
    port: str
    commands: tuple[tuple[str, ...], ...]
    dry_run: bool


def validate_intel_hex(hex_path: str | os.PathLike[str]) -> Path:
    """Validate that a file is basic Intel HEX with data and EOF records."""
    path = Path(hex_path).expanduser().resolve()
    if not path.is_file():
        raise HexValidationError(f"HEX file does not exist: {path}")

    saw_data = False
    saw_eof = False

    with path.open("r", encoding="ascii") as hex_file:
        for line_number, raw_line in enumerate(hex_file, start=1):
            line = raw_line.strip()
            if not line:
                continue
            if not line.startswith(":"):
                raise HexValidationError(f"Line {line_number} is not an Intel HEX record")
            payload = line[1:]
            if len(payload) < 10 or len(payload) % 2:
                raise HexValidationError(f"Line {line_number} has an invalid record length")
            try:
                record = bytes.fromhex(payload)
            except ValueError as exc:
                raise HexValidationError(f"Line {line_number} contains non-hex data") from exc

            data_len = record[0]
            record_type = record[3]
            expected_len = 5 + data_len
            if len(record) != expected_len:
                raise HexValidationError(f"Line {line_number} length byte does not match data")
            if sum(record) & 0xFF:
                raise HexValidationError(f"Line {line_number} checksum is invalid")
            if record_type == 0x00 and data_len > 0:
                saw_data = True
            elif record_type == 0x01:
                saw_eof = True

    if not saw_data:
        raise HexValidationError("HEX file has no data records")
    if not saw_eof:
        raise HexValidationError("HEX file has no EOF record")
    return path


def detect_default_updi_port() -> str:
    """Return the likely serialUPDI port for local Raspberry Pi flashing."""
    default_port = "/dev/ttyAMA4"
    try:
        model = Path(PI_MODEL_PATH).read_text(encoding="utf-8", errors="ignore")
        if "Raspberry Pi 5" in model:
            default_port = "/dev/ttyAMA3"
    except OSError:
        pass

    if os.path.exists(default_port):
        return default_port

    candidates = [
        port for port in glob.glob("/dev/ttyAMA*")
        if not port.endswith("ttyAMA0")
    ]
    if candidates:
        return sorted(candidates)[-1]
    return default_port


def _resolve_avrdude(avrdude: str | None) -> str:
    if avrdude:
        return avrdude
    if os.path.exists("/usr/local/bin/avrdude"):
        return "/usr/local/bin/avrdude"
    return shutil.which("avrdude") or "avrdude"


class FirmwareDeployer:
    """Deploy a release HEX file to FeralBoard via serialUPDI."""

    def __init__(
        self,
        *,
        avrdude: str | None = None,
        runner: Callable[..., subprocess.CompletedProcess] | None = None,
    ):
        self.avrdude = _resolve_avrdude(avrdude)
        self.runner = runner or subprocess.run

    def build_commands(
        self,
        hex_path: str | os.PathLike[str],
        *,
        port: str | None = None,
    ) -> tuple[tuple[str, ...], ...]:
        """Build the avrdude command sequence for a validated HEX file."""
        resolved_hex = validate_intel_hex(hex_path)
        resolved_port = port or detect_default_updi_port()
        base = (
            self.avrdude,
            "-p", AVRDUDE_PART,
            "-c", AVRDUDE_PROGRAMMER,
            "-P", resolved_port,
            "-b", str(AVRDUDE_BAUDRATE),
        )
        return (
            base + ("-U", "fuse5:w:0xC1:m"),
            base + ("-e", "-U", f"flash:w:{resolved_hex}:i"),
            base + (
                "-U", "fuse0:w:0x00:m",
                "-U", "fuse1:w:0xF4:m",
                "-U", "fuse2:w:0x02:m",
                "-U", "fuse5:w:0xC9:m",
                "-U", "fuse6:w:0x06:m",
                "-U", "fuse7:w:0x00:m",
                "-U", "fuse8:w:0x00:m",
            ),
        )

    def deploy_hex(
        self,
        hex_path: str | os.PathLike[str],
        *,
        port: str | None = None,
        dry_run: bool = False,
        timeout: float | None = None,
    ) -> FirmwareDeploymentResult:
        """Deploy a HEX file or return the command sequence in dry-run mode."""
        resolved_hex = validate_intel_hex(hex_path)
        resolved_port = port or detect_default_updi_port()
        commands = self.build_commands(resolved_hex, port=resolved_port)

        if not dry_run:
            for command in commands:
                try:
                    self.runner(
                        list(command),
                        check=True,
                        text=True,
                        capture_output=True,
                        timeout=timeout,
                    )
                except subprocess.CalledProcessError as exc:
                    raise FirmwareDeploymentError(
                        f"Firmware deployment command failed: {' '.join(command)}\n"
                        f"{exc.stderr or exc.stdout or exc}"
                    ) from exc
                except OSError as exc:
                    raise FirmwareDeploymentError(
                        f"Could not execute firmware deployment command: {command[0]}"
                    ) from exc

        return FirmwareDeploymentResult(
            hex_path=str(resolved_hex),
            port=resolved_port,
            commands=commands,
            dry_run=dry_run,
        )


def deploy_firmware_hex(
    hex_path: str | os.PathLike[str],
    *,
    port: str | None = None,
    dry_run: bool = False,
    avrdude: str | None = None,
    timeout: float | None = None,
) -> FirmwareDeploymentResult:
    """Convenience wrapper for FirmwareDeployer.deploy_hex()."""
    deployer = FirmwareDeployer(avrdude=avrdude)
    return deployer.deploy_hex(hex_path, port=port, dry_run=dry_run, timeout=timeout)
