"""Network configuration helpers backed by NetworkManager nmcli."""

from __future__ import annotations

from dataclasses import dataclass, field
import ipaddress

from ._system import CommandResult, Runner, command_output, run_command


@dataclass(frozen=True)
class NetworkConfig:
    """Declarative network configuration for one interface."""

    interface: str
    mode: str = "dhcp"
    ip_address: str | None = None
    subnet_mask: str | None = None
    prefix: int | None = None
    gateway: str | None = None
    dns: list[str] = field(default_factory=list)
    connection_name: str | None = None


@dataclass(frozen=True)
class InterfaceStatus:
    """NetworkManager status for one network interface."""

    interface: str
    state: str | None
    connection: str | None
    ip_addresses: tuple[str, ...]
    gateway: str | None
    dns: tuple[str, ...]
    mac_address: str | None


def _parse_nmcli_key_values(raw: str) -> dict[str, list[str]]:
    data: dict[str, list[str]] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data.setdefault(key.strip(), []).append(value.strip())
    return data


def _subnet_to_prefix(subnet_mask: str) -> int:
    return ipaddress.IPv4Network(f"0.0.0.0/{subnet_mask}").prefixlen


def _validate_config(config: NetworkConfig):
    if config.mode not in {"dhcp", "static"}:
        raise ValueError("Network mode must be 'dhcp' or 'static'")
    if config.mode == "static":
        if not config.ip_address:
            raise ValueError("Static network config requires ip_address")
        if config.prefix is None and not config.subnet_mask:
            raise ValueError("Static network config requires prefix or subnet_mask")
        ipaddress.IPv4Address(config.ip_address)
        if config.gateway:
            ipaddress.IPv4Address(config.gateway)
        for server in config.dns:
            ipaddress.IPv4Address(server)


def find_connection_name(
    interface: str,
    *,
    runner: Runner | None = None,
) -> str:
    """Find the NetworkManager connection profile for an interface."""
    active = command_output(
        ["nmcli", "-t", "-f", "NAME,DEVICE", "con", "show", "--active"],
        runner=runner,
    )
    for line in active.splitlines():
        name, _, device = line.partition(":")
        if device == interface:
            return name

    profiles = command_output(
        ["nmcli", "-t", "-f", "NAME,TYPE", "con", "show"],
        runner=runner,
    )
    for line in profiles.splitlines():
        name, _, conn_type = line.partition(":")
        if interface.startswith("eth") and conn_type == "ethernet":
            return name
        if interface.startswith("wlan") and conn_type == "wifi":
            return name
    raise RuntimeError(f"No NetworkManager connection found for {interface}")


def get_interface_status(
    interface: str,
    *,
    runner: Runner | None = None,
) -> InterfaceStatus:
    """Read current NetworkManager status for one interface."""
    status_raw = command_output(
        ["nmcli", "-t", "-f", "DEVICE,STATE,CONNECTION", "dev", "status"],
        runner=runner,
    )
    state = None
    connection = None
    for line in status_raw.splitlines():
        device, _, rest = line.partition(":")
        if device == interface:
            state, _, connection = rest.partition(":")
            connection = connection or None
            break

    show_raw = command_output(["nmcli", "-t", "dev", "show", interface], runner=runner)
    data = _parse_nmcli_key_values(show_raw)
    return InterfaceStatus(
        interface=interface,
        state=state,
        connection=connection,
        ip_addresses=tuple(data.get("IP4.ADDRESS[1]", [])),
        gateway=(data.get("IP4.GATEWAY", [None])[0] or None),
        dns=tuple(
            value for key, values in data.items()
            if key.startswith("IP4.DNS")
            for value in values
        ),
        mac_address=(data.get("GENERAL.HWADDR", [None])[0] or None),
    )


def apply_network_config(
    config: NetworkConfig,
    *,
    dry_run: bool = False,
    runner: Runner | None = None,
) -> list[CommandResult]:
    """Apply static or DHCP IPv4 config using nmcli."""
    _validate_config(config)
    if config.connection_name:
        connection_name = config.connection_name
    elif dry_run:
        connection_name = config.interface
    else:
        connection_name = find_connection_name(config.interface, runner=runner)
    commands: list[list[str]] = []

    if config.mode == "dhcp":
        commands.append([
            "nmcli", "con", "mod", connection_name,
            "ipv4.method", "auto",
            "ipv4.addresses", "",
            "ipv4.gateway", "",
            "ipv4.dns", "",
        ])
    else:
        prefix = config.prefix if config.prefix is not None else _subnet_to_prefix(
            config.subnet_mask or ""
        )
        commands.append([
            "nmcli", "con", "mod", connection_name,
            "ipv4.method", "manual",
            "ipv4.addresses", f"{config.ip_address}/{prefix}",
            "ipv4.gateway", config.gateway or "",
            "ipv4.dns", ",".join(config.dns),
        ])

    commands.append(["nmcli", "con", "up", connection_name])
    return [
        run_command(command, dry_run=dry_run, runner=runner)
        for command in commands
    ]
