"""FeralBoard serial frame helpers for oven simulation."""

from __future__ import annotations

from dataclasses import dataclass
import struct

from feralboard_sdk.crc8 import calculate_crc8, verify_crc8
from feralboard_sdk.io_map import OUTPUTS
from feralboard_sdk.protocol import (
    RX_BUFFER_SIZE,
    RX_CHECKSUM,
    RX_ERROR_FLAGS,
    RX_INPUTS_00_07,
    RX_LAVAGEM_ERRORS,
    RX_LAVAGEM_PCB_TEMP,
    RX_LAVAGEM_TEMP_OFFSET,
    RX_MAIN_TEMP_OFFSET,
    RX_MODE_STATE,
    RX_PCB_TEMP,
    TX_BUFFER_SIZE,
    TX_COMMAND_DATA,
    TX_COMMAND_ID,
    TX_LAVAGEM_OUTPUTS,
    TX_OVEN_OUTPUTS_00_07,
    TX_OVEN_OUTPUTS_08_15,
    TX_OVEN_OUTPUTS_16_23,
    TX_OVEN_OUTPUTS_EXTRA,
)

from .models import OvenState


class FrameValidationError(ValueError):
    """Raised when a simulator frame cannot be parsed."""


@dataclass(frozen=True)
class ControlPanelCommand:
    """Decoded command frame sent by an oven controller."""

    command_id: int
    command_data: int
    outputs: dict[str, bool]
    lavagem_outputs: int
    raw: bytes


def parse_tx_frame(frame: bytes) -> ControlPanelCommand:
    """Parse an 11-byte FeralBoard TX frame."""
    if len(frame) != TX_BUFFER_SIZE:
        raise FrameValidationError(
            f"Expected {TX_BUFFER_SIZE} TX bytes, got {len(frame)}"
        )
    if not verify_crc8(frame):
        raise FrameValidationError("TX frame CRC is invalid")

    tx_bytes = {
        0: frame[TX_OVEN_OUTPUTS_00_07],
        1: frame[TX_OVEN_OUTPUTS_08_15],
        2: frame[TX_OVEN_OUTPUTS_16_23],
        3: frame[TX_OVEN_OUTPUTS_EXTRA],
        6: frame[TX_LAVAGEM_OUTPUTS],
    }
    outputs = {}
    for name, tx_byte, bit_index, _ in OUTPUTS:
        outputs[name] = bool(tx_bytes.get(tx_byte, 0) & (1 << bit_index))

    return ControlPanelCommand(
        command_id=frame[TX_COMMAND_ID],
        command_data=frame[TX_COMMAND_DATA],
        outputs=outputs,
        lavagem_outputs=frame[TX_LAVAGEM_OUTPUTS],
        raw=frame,
    )


def build_rx_frame(state: OvenState) -> bytes:
    """Build a 41-byte FeralBoard RX frame from simulated oven state."""
    buffer = bytearray(RX_BUFFER_SIZE)

    for name, _, bit_index, rx_echo_byte in OUTPUTS:
        if state.output_echo.get(name, False):
            buffer[rx_echo_byte] |= 1 << bit_index

    buffer[RX_INPUTS_00_07] = state.inputs.to_rx_byte()
    struct.pack_into("<f", buffer, RX_MAIN_TEMP_OFFSET, state.temperatures.main_c)
    buffer[RX_PCB_TEMP] = max(0, min(255, int(state.temperatures.pcb_c)))
    buffer[RX_ERROR_FLAGS] = state.faults.to_error_byte()
    buffer[RX_MODE_STATE] = (state.door_state & 0x03) << 6

    struct.pack_into("<f", buffer, RX_LAVAGEM_TEMP_OFFSET, state.temperatures.lavagem_c)
    buffer[RX_LAVAGEM_PCB_TEMP] = max(0, min(255, int(state.temperatures.pcb_c)))
    buffer[RX_LAVAGEM_ERRORS] = state.faults.to_error_byte()
    buffer[RX_CHECKSUM] = calculate_crc8(bytes(buffer[:-1]))
    return bytes(buffer)
