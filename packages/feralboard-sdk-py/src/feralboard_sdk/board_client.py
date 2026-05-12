"""High-level client for named FeralBoard I/O operations."""

import time

from .io_map import INPUTS, OUTPUTS
from .protocol import TX_INTERVAL
from .serial_comm import SerialCommunicator


class FeralBoardClient:
    """Small facade around SerialCommunicator with named I/O helpers."""

    def __init__(self, port: str):
        self.port = port
        self.communicator = SerialCommunicator(port)

    def connect(self) -> bool:
        if not self.communicator.open():
            return False
        self.communicator.start()
        return True

    def disconnect(self):
        if self.communicator.running:
            self.clear_all_outputs()
            time.sleep(TX_INTERVAL + 0.05)
        self.communicator.stop()
        self.communicator.close()

    def __enter__(self):
        if not self.connect():
            raise RuntimeError(f"Could not open serial port {self.port}")
        return self

    def __exit__(self, exc_type, exc, tb):
        self.disconnect()

    def set_output(self, channel_name: str, value: bool):
        self.communicator.set_output(channel_name, value)

    def clear_all_outputs(self):
        self.communicator.clear_all_outputs()

    def send_command_once(self, command: int):
        self.communicator.send_command_once(command)

    def read_input(self, channel_name: str):
        rx_buffer, valid = self.communicator.get_rx_buffer()
        if not valid or not rx_buffer:
            return None
        for name, rx_byte, bit_idx in INPUTS:
            if name == channel_name:
                return (rx_buffer[rx_byte] >> bit_idx) & 1 == 1
        raise ValueError(f"Unknown input channel: {channel_name}")

    def read_output_echo(self, channel_name: str):
        rx_buffer, valid = self.communicator.get_rx_buffer()
        if not valid or not rx_buffer:
            return None
        for name, _, bit_idx, rx_echo_byte in OUTPUTS:
            if name == channel_name:
                return (rx_buffer[rx_echo_byte] >> bit_idx) & 1 == 1
        raise ValueError(f"Unknown output channel: {channel_name}")

    def get_rx_buffer(self):
        return self.communicator.get_rx_buffer()

    def get_tx_state(self):
        return self.communicator.get_tx_state()

    def get_stats(self):
        return self.communicator.get_stats()
