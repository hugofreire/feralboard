"""Read-only diagnostics snapshot for FeralBoard devices."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import glob
import json
import os
from pathlib import Path
import shutil

from ._system import Runner, command_output
from .identity import DeviceIdentity, get_device_identity
from .network import InterfaceStatus, get_interface_status
from .services import ServiceStatus, get_service_status
from .vpn import VpnStatus, get_vpn_status


@dataclass(frozen=True)
class SerialPortStatus:
    """Serial device presence and basic ownership hint."""

    port: str
    exists: bool
    candidates: tuple[str, ...]


@dataclass(frozen=True)
class DiskStatus:
    """Disk usage for one mount point."""

    path: str
    total_bytes: int
    used_bytes: int
    free_bytes: int


@dataclass(frozen=True)
class HealthSnapshot:
    """One-call support snapshot for a FeralBoard device."""

    identity: DeviceIdentity
    serial_port: SerialPortStatus
    firmware_version: str | None
    ip_addresses: tuple[str, ...]
    interfaces: tuple[InterfaceStatus, ...]
    disk: DiskStatus
    cpu_temp_c: float | None
    services: tuple[ServiceStatus, ...]
    vpn: VpnStatus | None

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def _read_cpu_temp() -> float | None:
    for path in glob.glob("/sys/class/thermal/thermal_zone*/temp"):
        try:
            raw = Path(path).read_text(encoding="utf-8").strip()
            return int(raw) / 1000.0
        except (OSError, ValueError):
            continue
    return None


def _read_firmware_version(path: str | None) -> str | None:
    if not path:
        return None
    try:
        value = Path(path).read_text(encoding="utf-8").strip()
        return value or None
    except OSError:
        return None


def _ip_addresses(*, runner: Runner | None = None) -> tuple[str, ...]:
    raw = command_output(["hostname", "-I"], runner=runner)
    return tuple(part for part in raw.split() if part)


def collect_health_snapshot(
    *,
    serial_port: str = "/dev/ttyAMA0",
    interfaces: tuple[str, ...] = ("eth0", "wlan0"),
    services: tuple[str, ...] = ("vpn", "mqtt", "postgres"),
    firmware_version_path: str | None = None,
    runner: Runner | None = None,
) -> HealthSnapshot:
    """Collect read-only diagnostic information for support."""
    disk_usage = shutil.disk_usage("/")
    return HealthSnapshot(
        identity=get_device_identity(runner=runner),
        serial_port=SerialPortStatus(
            port=serial_port,
            exists=os.path.exists(serial_port),
            candidates=tuple(sorted(glob.glob("/dev/ttyAMA*") + glob.glob("/dev/ttyUSB*"))),
        ),
        firmware_version=_read_firmware_version(firmware_version_path),
        ip_addresses=_ip_addresses(runner=runner),
        interfaces=tuple(
            get_interface_status(interface, runner=runner)
            for interface in interfaces
        ),
        disk=DiskStatus(
            path="/",
            total_bytes=disk_usage.total,
            used_bytes=disk_usage.used,
            free_bytes=disk_usage.free,
        ),
        cpu_temp_c=_read_cpu_temp(),
        services=tuple(
            get_service_status(service, runner=runner)
            for service in services
        ),
        vpn=get_vpn_status(runner=runner) if "vpn" in services else None,
    )
