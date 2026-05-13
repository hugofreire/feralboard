"""Device identity helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import socket

from ._system import CommandResult, Runner, command_output, run_command


@dataclass(frozen=True)
class DeviceIdentity:
    """Stable device identity information."""

    hostname: str
    device_name: str | None
    serial_number: str | None


def _read_cpu_serial() -> str | None:
    try:
        for line in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
            if line.lower().startswith("serial"):
                _, value = line.split(":", 1)
                return value.strip() or None
    except OSError:
        return None
    return None


def get_device_identity(*, runner: Runner | None = None) -> DeviceIdentity:
    """Read hostname, pretty device name, and hardware serial."""
    hostname = socket.gethostname()
    pretty = command_output(
        ["hostnamectl", "--pretty"],
        runner=runner,
    ) or None
    return DeviceIdentity(
        hostname=hostname,
        device_name=pretty,
        serial_number=_read_cpu_serial(),
    )


def set_hostname(
    hostname: str,
    *,
    dry_run: bool = False,
    runner: Runner | None = None,
) -> CommandResult:
    """Set the static system hostname."""
    return run_command(
        ["hostnamectl", "set-hostname", hostname],
        dry_run=dry_run,
        runner=runner,
    )


def set_device_name(
    device_name: str,
    *,
    dry_run: bool = False,
    runner: Runner | None = None,
) -> CommandResult:
    """Set the pretty device name shown in host management tools."""
    return run_command(
        ["hostnamectl", "--pretty", "set-hostname", device_name],
        dry_run=dry_run,
        runner=runner,
    )
