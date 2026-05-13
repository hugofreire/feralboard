"""Whitelisted FeralBoard service helpers."""

from __future__ import annotations

from dataclasses import dataclass

from ._system import CommandResult, Runner, command_output, run_command


SERVICE_ALIASES = {
    "vpn": "openvpn-client@client",
    "openvpn": "openvpn-client@client",
    "mqtt": "mosquitto",
    "postgres": "postgresql",
    "postgresql": "postgresql",
}


@dataclass(frozen=True)
class ServiceStatus:
    """systemd status for an approved service."""

    name: str
    unit: str
    active_state: str | None
    sub_state: str | None


def resolve_service(name: str) -> str:
    try:
        return SERVICE_ALIASES[name]
    except KeyError as exc:
        allowed = ", ".join(sorted(SERVICE_ALIASES))
        raise ValueError(f"Service is not approved: {name}. Allowed: {allowed}") from exc


def get_service_status(name: str, *, runner: Runner | None = None) -> ServiceStatus:
    """Read status for a whitelisted service."""
    unit = resolve_service(name)
    raw = command_output(
        ["systemctl", "show", unit, "-p", "ActiveState", "-p", "SubState"],
        runner=runner,
    )
    data = {}
    for line in raw.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            data[key] = value
    return ServiceStatus(
        name=name,
        unit=unit,
        active_state=data.get("ActiveState") or None,
        sub_state=data.get("SubState") or None,
    )


def restart_service(
    name: str,
    *,
    dry_run: bool = False,
    runner: Runner | None = None,
) -> CommandResult:
    """Restart an approved FeralBoard service."""
    return run_command(
        ["systemctl", "restart", resolve_service(name)],
        dry_run=dry_run,
        runner=runner,
    )


def enable_service(
    name: str,
    *,
    dry_run: bool = False,
    runner: Runner | None = None,
) -> CommandResult:
    """Enable an approved FeralBoard service."""
    return run_command(
        ["systemctl", "enable", resolve_service(name)],
        dry_run=dry_run,
        runner=runner,
    )


def disable_service(
    name: str,
    *,
    dry_run: bool = False,
    runner: Runner | None = None,
) -> CommandResult:
    """Disable an approved FeralBoard service."""
    return run_command(
        ["systemctl", "disable", resolve_service(name)],
        dry_run=dry_run,
        runner=runner,
    )
