"""Threaded serial communicator for FeralBoard TX/RX loop."""

import serial
import serial.tools.list_ports
import threading
import time

from .crc8 import calculate_crc8, verify_crc8
from .protocol import (
    BAUD_RATE, TIMEOUT, TX_INTERVAL,
    TX_BUFFER_SIZE, RX_BUFFER_SIZE,
    TX_OVEN_OUTPUTS_00_07, TX_OVEN_OUTPUTS_08_15,
    TX_OVEN_OUTPUTS_16_23, TX_OVEN_OUTPUTS_EXTRA,
    TX_COMMAND_ID, TX_COMMAND_DATA,
    TX_LAVAGEM_OUTPUTS, TX_LAVAGEM_CMD_ID, TX_LAVAGEM_CMD_DATA,
    TX_ORIGIN_ID, TX_CHECKSUM,
    CMD_SET_STATES,
)


class SerialCommunicator:
    """Handles continuous serial communication with the FeralBoard.

    Sends an 11-byte TX frame every 250ms and reads back a 41-byte RX frame.
    Thread-safe: all state access is protected by self.lock.
    """

    def __init__(self, port: str):
        self.port = port
        self.ser = None
        self.running = False
        self.thread = None
        self.lock = threading.Lock()

        # TX buffer state
        self.tx_byte0 = 0  # Oven outputs 00-07
        self.tx_byte1 = 0  # Oven outputs 08-15
        self.tx_byte2 = 0  # Oven outputs 16-23
        self.tx_byte3 = 0  # Oven outputs extra
        self.tx_lavagem = 0  # Lavagem outputs
        self.tx_command = CMD_SET_STATES
        self.tx_command_data = 0
        self.pending_command = None  # One-shot command to send once

        self.rx_buffer = None
        self.rx_valid = False
        self.rx_count = 0
        self.rx_error_count = 0
        self.tx_count = 0

    def open(self) -> bool:
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=BAUD_RATE,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=TIMEOUT,
            )
            return True
        except serial.SerialException as e:
            print(f"ERROR: Could not open serial port: {e}")
            return False

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._communication_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)

    def _build_tx_buffer(self) -> bytes:
        buffer = bytearray(TX_BUFFER_SIZE)
        with self.lock:
            buffer[TX_OVEN_OUTPUTS_00_07] = self.tx_byte0
            buffer[TX_OVEN_OUTPUTS_08_15] = self.tx_byte1
            buffer[TX_OVEN_OUTPUTS_16_23] = self.tx_byte2
            buffer[TX_OVEN_OUTPUTS_EXTRA] = self.tx_byte3

            if self.pending_command is not None:
                buffer[TX_COMMAND_ID] = self.pending_command
                buffer[TX_COMMAND_DATA] = 0
                self.pending_command = None
            else:
                buffer[TX_COMMAND_ID] = self.tx_command
                buffer[TX_COMMAND_DATA] = self.tx_command_data

            buffer[TX_LAVAGEM_OUTPUTS] = self.tx_lavagem
            buffer[TX_LAVAGEM_CMD_ID] = 0
            buffer[TX_LAVAGEM_CMD_DATA] = 0
            buffer[TX_ORIGIN_ID] = 0
        buffer[TX_CHECKSUM] = calculate_crc8(bytes(buffer[:-1]))
        return bytes(buffer)

    def _communication_loop(self):
        while self.running:
            loop_start = time.time()
            try:
                tx_buffer = self._build_tx_buffer()
                self.ser.reset_input_buffer()
                self.ser.write(tx_buffer)
                self.ser.flush()
                self.tx_count += 1

                rx_data = self.ser.read(RX_BUFFER_SIZE)

                with self.lock:
                    if len(rx_data) == RX_BUFFER_SIZE:
                        if verify_crc8(rx_data):
                            self.rx_buffer = rx_data
                            self.rx_valid = True
                            self.rx_count += 1
                        else:
                            self.rx_valid = False
                            self.rx_error_count += 1
                    else:
                        self.rx_valid = False
                        if len(rx_data) > 0:
                            self.rx_error_count += 1

            except serial.SerialException:
                self.rx_valid = False

            elapsed = time.time() - loop_start
            sleep_time = TX_INTERVAL - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    def set_control_outputs(self, byte0: int = 0, byte1: int = 0,
                            byte2: int = 0, byte3: int = 0):
        with self.lock:
            self.tx_byte0 = byte0
            self.tx_byte1 = byte1
            self.tx_byte2 = byte2
            self.tx_byte3 = byte3

    def set_lavagem_outputs(self, lavagem: int = 0):
        with self.lock:
            self.tx_lavagem = lavagem

    def clear_all_outputs(self):
        with self.lock:
            self.tx_byte0 = 0
            self.tx_byte1 = 0
            self.tx_byte2 = 0
            self.tx_byte3 = 0
            self.tx_lavagem = 0

    def send_command_once(self, command: int):
        """Queue a command to be sent once on the next TX."""
        with self.lock:
            self.pending_command = command

    def get_rx_buffer(self):
        with self.lock:
            return self.rx_buffer, self.rx_valid

    def get_tx_state(self):
        with self.lock:
            return (self.tx_byte0, self.tx_byte1, self.tx_byte2,
                    self.tx_byte3, self.tx_lavagem)

    def get_stats(self) -> tuple:
        with self.lock:
            return (self.tx_count, self.rx_count, self.rx_error_count)


def list_serial_ports() -> list:
    ports = serial.tools.list_ports.comports()
    return [(p.device, p.description) for p in ports]
