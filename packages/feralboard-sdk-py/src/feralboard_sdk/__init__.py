"""Python SDK for FeralBoard board I/O."""

from .board_client import FeralBoardClient
from .diagnostics import HealthSnapshot, collect_health_snapshot
from .firmware import (
    FirmwareDeployer,
    FirmwareDeploymentError,
    FirmwareDeploymentResult,
    HexValidationError,
    deploy_firmware_hex,
)
from .gpio_client import GpioClient
from .identity import DeviceIdentity, get_device_identity, set_device_name, set_hostname
from .network import (
    InterfaceStatus,
    NetworkConfig,
    apply_network_config,
    get_interface_status,
)
from .serial_comm import SerialCommunicator, list_serial_ports
from .services import (
    ServiceStatus,
    disable_service,
    enable_service,
    get_service_status,
    restart_service,
)
from .time_config import TimeConfig, TimeStatus, apply_time_config, get_time_status
from .vpn import (
    VpnStatus,
    disable_vpn,
    enable_vpn,
    get_vpn_logs,
    get_vpn_status,
    install_openvpn_profile,
)

__all__ = [
    "DeviceIdentity",
    "FeralBoardClient",
    "FirmwareDeployer",
    "FirmwareDeploymentError",
    "FirmwareDeploymentResult",
    "GpioClient",
    "HealthSnapshot",
    "HexValidationError",
    "InterfaceStatus",
    "NetworkConfig",
    "ServiceStatus",
    "SerialCommunicator",
    "TimeConfig",
    "TimeStatus",
    "VpnStatus",
    "apply_network_config",
    "apply_time_config",
    "collect_health_snapshot",
    "deploy_firmware_hex",
    "disable_service",
    "disable_vpn",
    "enable_service",
    "enable_vpn",
    "get_device_identity",
    "get_interface_status",
    "get_service_status",
    "get_time_status",
    "get_vpn_logs",
    "get_vpn_status",
    "install_openvpn_profile",
    "list_serial_ports",
    "restart_service",
    "set_device_name",
    "set_hostname",
]
