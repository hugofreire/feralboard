"""Oven-domain data models used by the FeralBoard simulator."""

from __future__ import annotations

from dataclasses import dataclass, field
from time import time

from feralboard_sdk.protocol import (
    DOOR_STATE_CLOSED,
    DOOR_STATE_INTERMEDIATE,
    DOOR_STATE_OPEN,
    DOOR_STATE_UNKNOWN,
)


DOOR_STATE_NAMES = {
    DOOR_STATE_UNKNOWN: "unknown",
    DOOR_STATE_OPEN: "open",
    DOOR_STATE_INTERMEDIATE: "intermediate",
    DOOR_STATE_CLOSED: "closed",
}


@dataclass
class OvenInputs:
    """Raw digital input state exposed by the simulated FeralBoard."""

    door_end_stop: bool = True
    electric_protection_ok: bool = True
    oven_over_temp: bool = False
    motor_over_temp: bool = False
    door_switch_locked: bool = True
    door_switch_locking_1: bool = False
    door_switch_locking_2: bool = False
    door_switch_traction: bool = False

    def to_rx_byte(self) -> int:
        bits = [
            self.door_end_stop,
            self.electric_protection_ok,
            self.oven_over_temp,
            self.motor_over_temp,
            self.door_switch_locked,
            self.door_switch_locking_1,
            self.door_switch_locking_2,
            self.door_switch_traction,
        ]
        value = 0
        for index, active in enumerate(bits):
            if active:
                value |= 1 << index
        return value


@dataclass
class OvenFaults:
    """High-level simulated fault conditions."""

    oven_over_temperature: bool = False
    motor_over_temperature: bool = False
    sensor_fault: bool = False
    electric_protection: bool = False

    def to_error_byte(self) -> int:
        value = 0
        if self.oven_over_temperature:
            value |= 1 << 0
        if self.motor_over_temperature:
            value |= 1 << 1
        if self.sensor_fault:
            value |= 1 << 2
        if self.electric_protection:
            value |= 1 << 3
        return value


@dataclass
class OvenTemperatures:
    """Simulated oven temperatures in Celsius."""

    main_c: float = 25.0
    lavagem_c: float = 25.0
    pcb_c: float = 35.0
    ambient_c: float = 25.0


@dataclass
class OvenProfile:
    """Simple thermal profile for scenario simulation."""

    heat_rate_c_per_s: float = 1.4
    cool_rate_c_per_s: float = 0.18
    door_open_cool_rate_c_per_s: float = 0.65
    over_temperature_c: float = 260.0


@dataclass
class OvenState:
    """Complete simulated oven state."""

    inputs: OvenInputs = field(default_factory=OvenInputs)
    faults: OvenFaults = field(default_factory=OvenFaults)
    temperatures: OvenTemperatures = field(default_factory=OvenTemperatures)
    profile: OvenProfile = field(default_factory=OvenProfile)
    door_state: int = DOOR_STATE_CLOSED
    output_echo: dict[str, bool] = field(default_factory=dict)
    last_update_s: float = field(default_factory=time)

    def set_door_closed(self, closed: bool):
        self.door_state = DOOR_STATE_CLOSED if closed else DOOR_STATE_OPEN
        self.inputs.door_end_stop = closed
        self.inputs.door_switch_locked = closed

    def set_temperature(self, temperature_c: float):
        self.temperatures.main_c = float(temperature_c)
        self.faults.oven_over_temperature = (
            self.temperatures.main_c >= self.profile.over_temperature_c
        )
        self.inputs.oven_over_temp = self.faults.oven_over_temperature

    def clear_faults(self):
        self.faults = OvenFaults()
        self.inputs.oven_over_temp = False
        self.inputs.motor_over_temp = False
        self.inputs.electric_protection_ok = True


@dataclass(frozen=True)
class OvenSnapshot:
    """Customer-facing simulator snapshot."""

    door_state: str
    main_temp_c: float
    lavagem_temp_c: float
    pcb_temp_c: float
    inputs: dict[str, bool]
    outputs: dict[str, bool]
    faults: dict[str, bool]
