"""FeralBoard serial protocol constants and frame definitions."""

import struct

# Serial configuration
BAUD_RATE = 9600
TIMEOUT = 0.5
TX_INTERVAL = 0.250

# Buffer sizes
TX_BUFFER_SIZE = 11
RX_BUFFER_SIZE = 41

# TX buffer byte locations
TX_OVEN_OUTPUTS_00_07 = 0
TX_OVEN_OUTPUTS_08_15 = 1
TX_OVEN_OUTPUTS_16_23 = 2
TX_OVEN_OUTPUTS_EXTRA = 3
TX_COMMAND_ID = 4
TX_COMMAND_DATA = 5
TX_LAVAGEM_OUTPUTS = 6
TX_LAVAGEM_CMD_ID = 7
TX_LAVAGEM_CMD_DATA = 8
TX_ORIGIN_ID = 9
TX_CHECKSUM = 10

# RX buffer byte locations
RX_OUTPUTS_00_07 = 0
RX_OUTPUTS_16_23 = 2
RX_OUTPUTS_EXTRA = 3
RX_INPUTS_00_07 = 4
RX_MAIN_TEMP_OFFSET = 6      # bytes 6-9, float32 LE
RX_PCB_TEMP = 22
RX_ERROR_FLAGS = 23
RX_MODE_STATE = 24
RX_LAVAGEM_OUTPUTS = 28
RX_LAVAGEM_INPUTS = 29
RX_LAVAGEM_TEMP_OFFSET = 30  # bytes 30-33, float32 LE
RX_LAVAGEM_PCB_TEMP = 34
RX_LAVAGEM_ERRORS = 36
RX_CHECKSUM = 40

# Command IDs
CMD_SET_STATES = 0x00
CMD_GET_STATES = 0x01
CMD_RST_STATES = 0x02
CMD_SET_INVERT = 0x03
CMD_CLR_INVERT = 0x04
CMD_FACTORY_MODE = 0x05
CMD_OPEN_DOOR = 0x06
CMD_CLOSE_DOOR = 0x07
CMD_MOTOR_CONTROL = 0x08
CMD_OVEN_MODEL = 0x09

# Door states (byte 24, bits 6-7)
DOOR_STATE_UNKNOWN = 0b00
DOOR_STATE_OPEN = 0b01
DOOR_STATE_INTERMEDIATE = 0b10
DOOR_STATE_CLOSED = 0b11


def bytes_to_float(data: bytes, offset: int) -> float:
    return struct.unpack('<f', data[offset:offset + 4])[0]


def get_door_state(rx_buffer: bytes) -> int:
    if rx_buffer is None:
        return DOOR_STATE_UNKNOWN
    return (rx_buffer[RX_MODE_STATE] >> 6) & 0x03
