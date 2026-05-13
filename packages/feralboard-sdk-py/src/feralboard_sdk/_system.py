"""Internal helpers for whitelisted device-management commands."""

from __future__ import annotations

from dataclasses import dataclass
import subprocess
from typing import Callable, Sequence


Runner = Callable[..., subprocess.CompletedProcess]


@dataclass(frozen=True)
class CommandResult:
    """Structured result for a command executed or planned by the SDK."""

    command: tuple[str, ...]
    returncode: int | None
    stdout: str
    stderr: str
    dry_run: bool = False


def run_command(
    command: Sequence[str],
    *,
    dry_run: bool = False,
    check: bool = True,
    timeout: float | None = None,
    runner: Runner | None = None,
) -> CommandResult:
    """Run a command safely without invoking a shell."""
    command_tuple = tuple(str(part) for part in command)
    if dry_run:
        return CommandResult(command_tuple, None, "", "", dry_run=True)

    run = runner or subprocess.run
    completed = run(
        list(command_tuple),
        check=False,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    result = CommandResult(
        command=command_tuple,
        returncode=completed.returncode,
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
    )
    if check and completed.returncode:
        raise RuntimeError(
            f"Command failed ({completed.returncode}): {' '.join(command_tuple)}\n"
            f"{result.stderr or result.stdout}"
        )
    return result


def command_output(
    command: Sequence[str],
    *,
    timeout: float | None = None,
    runner: Runner | None = None,
) -> str:
    """Return stdout from a command or an empty string if it fails."""
    try:
        return run_command(
            command,
            check=False,
            timeout=timeout,
            runner=runner,
        ).stdout.strip()
    except Exception:
        return ""
