"""GLib.timeout_add bridge between serial thread and GTK main loop."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GLib

from lib.serial_comm import SerialCommunicator
from lib.io_map import OUTPUTS


class SerialBridge:
    """Polls SerialCommunicator via GLib.timeout_add and invokes callbacks on change."""

    def __init__(self, communicator: SerialCommunicator):
        self.comm = communicator
        self._last_rx = None
        self._callbacks = []
        self._timer_id = None

    def start(self):
        """Start polling at 10Hz."""
        if self._timer_id is None:
            self._timer_id = GLib.timeout_add(100, self._poll)

    def stop(self):
        """Stop polling."""
        if self._timer_id is not None:
            GLib.source_remove(self._timer_id)
            self._timer_id = None

    def on_state_changed(self, callback):
        """Register a callback: callback(rx_buffer: bytes)."""
        self._callbacks.append(callback)

    def _poll(self):
        rx_buffer, valid = self.comm.get_rx_buffer()
        if valid and rx_buffer:
            if rx_buffer != self._last_rx:
                self._last_rx = rx_buffer
                for cb in self._callbacks:
                    cb(rx_buffer)
        return True  # keep polling

    def set_output(self, channel_name: str, value: bool):
        """Set or clear a single output bit in the TX buffer."""
        for name, tx_byte, bit_idx, _ in OUTPUTS:
            if name == channel_name:
                with self.comm.lock:
                    attr_map = {0: 'tx_byte0', 1: 'tx_byte1',
                                2: 'tx_byte2', 3: 'tx_byte3'}
                    attr = attr_map.get(tx_byte)
                    if attr:
                        current = getattr(self.comm, attr)
                        if value:
                            setattr(self.comm, attr, current | (1 << bit_idx))
                        else:
                            setattr(self.comm, attr, current & ~(1 << bit_idx))
                return

    def clear_all_outputs(self):
        self.comm.clear_all_outputs()

    def send_command(self, cmd: int):
        self.comm.send_command_once(cmd)
