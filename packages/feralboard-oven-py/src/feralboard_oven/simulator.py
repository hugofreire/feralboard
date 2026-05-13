"""Oven simulator behavior and serial loop."""

from __future__ import annotations

import time

from feralboard_sdk.protocol import TX_BUFFER_SIZE

from .models import DOOR_STATE_NAMES, OvenSnapshot, OvenState
from .serial_protocol import (
    ControlPanelCommand,
    FrameValidationError,
    build_rx_frame,
    parse_tx_frame,
)


class OvenSimulator:
    """Stateful oven simulator compatible with FeralBoard frame timing."""

    def __init__(self, state: OvenState | None = None):
        self.state = state or OvenState()
        self.last_command: ControlPanelCommand | None = None
        self.frame_errors = 0

    def set_temperature(self, temperature_c: float):
        self.state.set_temperature(temperature_c)

    def set_door_closed(self, closed: bool):
        self.state.set_door_closed(closed)

    def set_fault(self, name: str, active: bool = True):
        if not hasattr(self.state.faults, name):
            raise ValueError(f"Unknown oven fault: {name}")
        setattr(self.state.faults, name, active)
        self.state.inputs.oven_over_temp = self.state.faults.oven_over_temperature
        self.state.inputs.motor_over_temp = self.state.faults.motor_over_temperature
        self.state.inputs.electric_protection_ok = not self.state.faults.electric_protection

    def clear_faults(self):
        self.state.clear_faults()

    def apply_tx_frame(self, frame: bytes) -> bytes:
        """Decode a controller TX frame and return a simulated RX frame."""
        try:
            command = parse_tx_frame(frame)
        except FrameValidationError:
            self.frame_errors += 1
            return build_rx_frame(self.state)

        self.last_command = command
        self.state.output_echo = command.outputs.copy()
        self.advance()
        return build_rx_frame(self.state)

    def advance(self, now_s: float | None = None):
        """Advance the thermal model based on current output state."""
        now = now_s if now_s is not None else time.time()
        elapsed = max(0.0, now - self.state.last_update_s)
        self.state.last_update_s = now

        heater_on = self.state.output_echo.get("DO4", False)
        door_open = DOOR_STATE_NAMES.get(self.state.door_state) == "open"
        temps = self.state.temperatures
        profile = self.state.profile

        if heater_on:
            temps.main_c += profile.heat_rate_c_per_s * elapsed
        else:
            cool_rate = (
                profile.door_open_cool_rate_c_per_s
                if door_open
                else profile.cool_rate_c_per_s
            )
            temps.main_c = max(
                temps.ambient_c,
                temps.main_c - cool_rate * elapsed,
            )

        self.state.set_temperature(temps.main_c)

    def snapshot(self) -> OvenSnapshot:
        """Return a customer-facing snapshot of the simulator state."""
        inputs = {
            "DI0_door_end_stop": self.state.inputs.door_end_stop,
            "DI1_electric_protection_ok": self.state.inputs.electric_protection_ok,
            "DI2_oven_over_temp": self.state.inputs.oven_over_temp,
            "DI3_motor_over_temp": self.state.inputs.motor_over_temp,
            "DI4_door_switch_locked": self.state.inputs.door_switch_locked,
            "DI5_door_switch_locking_1": self.state.inputs.door_switch_locking_1,
            "DI6_door_switch_locking_2": self.state.inputs.door_switch_locking_2,
            "DI7_door_switch_traction": self.state.inputs.door_switch_traction,
        }
        return OvenSnapshot(
            door_state=DOOR_STATE_NAMES.get(self.state.door_state, "unknown"),
            main_temp_c=round(self.state.temperatures.main_c, 2),
            lavagem_temp_c=round(self.state.temperatures.lavagem_c, 2),
            pcb_temp_c=round(self.state.temperatures.pcb_c, 2),
            inputs=inputs,
            outputs=self.state.output_echo.copy(),
            faults=self.state.faults.__dict__.copy(),
        )

    def run_serial(self, serial_port: str, *, baudrate: int = 9600):
        """Run the simulator on a serial device path."""
        import serial

        with serial.Serial(serial_port, baudrate=baudrate, timeout=1) as ser:
            while True:
                frame = ser.read(TX_BUFFER_SIZE)
                if not frame:
                    self.advance()
                    continue
                if len(frame) != TX_BUFFER_SIZE:
                    self.frame_errors += 1
                    continue
                ser.write(self.apply_tx_frame(frame))
                ser.flush()
