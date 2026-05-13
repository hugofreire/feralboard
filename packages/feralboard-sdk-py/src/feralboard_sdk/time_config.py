"""Time, timezone, and NTP configuration helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ._system import CommandResult, Runner, command_output, run_command


TIMESYNCD_DROPIN = "/etc/systemd/timesyncd.conf.d/feralboard-sdk.conf"


@dataclass(frozen=True)
class TimeConfig:
    """Declarative system time configuration."""

    timezone: str | None = None
    ntp_enabled: bool | None = True
    ntp_servers: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class TimeStatus:
    """Current system time synchronization status."""

    timezone: str | None
    ntp_enabled: bool | None
    ntp_synchronized: bool | None
    raw: dict[str, str]


def _parse_show(raw: str) -> dict[str, str]:
    data = {}
    for line in raw.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            data[key] = value
    return data


def _to_bool(value: str | None) -> bool | None:
    if value is None or value == "":
        return None
    return value.lower() in {"yes", "true", "1"}


def get_time_status(*, runner: Runner | None = None) -> TimeStatus:
    """Read current timedatectl status."""
    raw = command_output(
        [
            "timedatectl", "show",
            "-p", "Timezone",
            "-p", "NTP",
            "-p", "NTPSynchronized",
        ],
        runner=runner,
    )
    data = _parse_show(raw)
    return TimeStatus(
        timezone=data.get("Timezone") or None,
        ntp_enabled=_to_bool(data.get("NTP")),
        ntp_synchronized=_to_bool(data.get("NTPSynchronized")),
        raw=data,
    )


def _write_timesyncd_dropin(
    ntp_servers: list[str],
    *,
    dry_run: bool,
) -> CommandResult:
    command = (
        "write-file",
        TIMESYNCD_DROPIN,
        f"NTP={' '.join(ntp_servers)}",
    )
    if dry_run:
        return CommandResult(command, None, "", "", dry_run=True)

    path = Path(TIMESYNCD_DROPIN)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "[Time]\n"
        f"NTP={' '.join(ntp_servers)}\n",
        encoding="utf-8",
    )
    return CommandResult(command, 0, "", "")


def apply_time_config(
    config: TimeConfig,
    *,
    dry_run: bool = False,
    runner: Runner | None = None,
) -> list[CommandResult]:
    """Apply timezone and NTP settings."""
    results: list[CommandResult] = []
    if config.timezone:
        results.append(
            run_command(
                ["timedatectl", "set-timezone", config.timezone],
                dry_run=dry_run,
                runner=runner,
            )
        )
    if config.ntp_enabled is not None:
        results.append(
            run_command(
                ["timedatectl", "set-ntp", "true" if config.ntp_enabled else "false"],
                dry_run=dry_run,
                runner=runner,
            )
        )
    if config.ntp_servers:
        results.append(_write_timesyncd_dropin(config.ntp_servers, dry_run=dry_run))
        results.append(
            run_command(
                ["systemctl", "restart", "systemd-timesyncd"],
                dry_run=dry_run,
                runner=runner,
            )
        )
    return results
