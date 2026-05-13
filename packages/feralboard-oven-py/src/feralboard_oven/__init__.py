"""Oven-domain simulator companion package for FeralBoard."""

from .models import (
    OvenFaults,
    OvenInputs,
    OvenProfile,
    OvenSnapshot,
    OvenState,
    OvenTemperatures,
)
from .serial_protocol import ControlPanelCommand, build_rx_frame, parse_tx_frame
from .simulator import OvenSimulator
from .scenarios import (
    door_open,
    electric_protection_trip,
    motor_over_temperature,
    oven_over_temperature,
    ready_oven,
)

__all__ = [
    "ControlPanelCommand",
    "OvenFaults",
    "OvenInputs",
    "OvenProfile",
    "OvenSimulator",
    "OvenSnapshot",
    "OvenState",
    "OvenTemperatures",
    "build_rx_frame",
    "door_open",
    "electric_protection_trip",
    "motor_over_temperature",
    "oven_over_temperature",
    "parse_tx_frame",
    "ready_oven",
]
