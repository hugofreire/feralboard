"""OpenVPN profile installation and service helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil

from ._system import CommandResult, Runner, command_output, run_command


OPENVPN_CLIENT_DIR = "/etc/openvpn/client"


@dataclass(frozen=True)
class VpnStatus:
    """OpenVPN client service status."""

    profile_name: str
    unit: str
    active_state: str | None
    sub_state: str | None


def _validate_profile_name(profile_name: str):
    if not profile_name.replace("-", "").replace("_", "").isalnum():
        raise ValueError("OpenVPN profile name must be alphanumeric, '-' or '_'")


def _unit(profile_name: str) -> str:
    _validate_profile_name(profile_name)
    return f"openvpn-client@{profile_name}"


def install_openvpn_profile(
    profile_path: str,
    *,
    profile_name: str = "client",
    dry_run: bool = False,
    runner: Runner | None = None,
) -> list[CommandResult]:
    """Install an OpenVPN client profile and enable its service."""
    _validate_profile_name(profile_name)
    source = Path(profile_path).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"OpenVPN profile does not exist: {source}")

    target = Path(OPENVPN_CLIENT_DIR) / f"{profile_name}.conf"
    copy_command = ("copy-file", str(source), str(target))
    results: list[CommandResult] = []
    if dry_run:
        results.append(CommandResult(copy_command, None, "", "", dry_run=True))
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        target.chmod(0o600)
        results.append(CommandResult(copy_command, 0, "", ""))

    results.append(
        run_command(
            ["systemctl", "enable", _unit(profile_name)],
            dry_run=dry_run,
            runner=runner,
        )
    )
    return results


def enable_vpn(
    profile_name: str = "client",
    *,
    dry_run: bool = False,
    runner: Runner | None = None,
) -> CommandResult:
    return run_command(
        ["systemctl", "enable", "--now", _unit(profile_name)],
        dry_run=dry_run,
        runner=runner,
    )


def disable_vpn(
    profile_name: str = "client",
    *,
    dry_run: bool = False,
    runner: Runner | None = None,
) -> CommandResult:
    return run_command(
        ["systemctl", "disable", "--now", _unit(profile_name)],
        dry_run=dry_run,
        runner=runner,
    )


def get_vpn_status(
    profile_name: str = "client",
    *,
    runner: Runner | None = None,
) -> VpnStatus:
    unit = _unit(profile_name)
    raw = command_output(
        ["systemctl", "show", unit, "-p", "ActiveState", "-p", "SubState"],
        runner=runner,
    )
    data = {}
    for line in raw.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            data[key] = value
    return VpnStatus(
        profile_name=profile_name,
        unit=unit,
        active_state=data.get("ActiveState") or None,
        sub_state=data.get("SubState") or None,
    )


def get_vpn_logs(
    profile_name: str = "client",
    *,
    lines: int = 100,
    runner: Runner | None = None,
) -> str:
    return command_output(
        ["journalctl", "-u", _unit(profile_name), "-n", str(lines), "--no-pager"],
        runner=runner,
    )
