#!/usr/bin/env python3
"""
End-to-end test: FeralBoard outputs via UART -> raspi-gpio GPIO verification.

Can be run standalone or via pytest:
    python3 tests/test_outputs_e2e.py [--port /dev/ttyAMA0] [--gpio-host 192.168.0.142]
    pytest tests/test_outputs_e2e.py --port /dev/ttyAMA0
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.serial_comm import SerialCommunicator
from lib.gpio_client import GpioClient
from lib.io_map import OUTPUTS

SETTLE_TIME = 3.0
VALID_RX_TIMEOUT = 10.0


def set_output_on(comm, tx_byte, bit_idx):
    """Turn on a single FeralBoard output bit."""
    mask = 1 << bit_idx
    if tx_byte == 6:
        comm.set_lavagem_outputs(mask)
    else:
        kwargs = {f"byte{tx_byte}": mask}
        comm.set_control_outputs(**kwargs)


def wait_valid_rx(comm, timeout):
    deadline = time.time() + timeout
    while time.time() < deadline:
        _, valid = comm.get_rx_buffer()
        _, rx_count, _ = comm.get_stats()
        if valid and rx_count > 0:
            return True
        time.sleep(0.05)
    return False


def test_all_outputs(communicator, gpio_client, settle_time):
    """Test all 12 FeralBoard outputs via GPIO verification."""
    comm = communicator

    # Reset GPIO pins
    gpio_client.setup_inputs()

    # Clear all outputs and capture baseline
    comm.clear_all_outputs()
    time.sleep(settle_time)
    baseline = gpio_client.read_all()

    results = []

    for name, tx_byte, bit_idx, rx_echo_byte in OUTPUTS:
        # Ensure all OFF
        comm.clear_all_outputs()
        time.sleep(1.0)

        pre_gpio = gpio_client.read_all()

        # Turn ON the output
        set_output_on(comm, tx_byte, bit_idx)
        time.sleep(settle_time)

        # Check RX echo
        rx_buffer, valid = comm.get_rx_buffer()
        echo_ok = False
        if valid and rx_buffer:
            echo_val = rx_buffer[rx_echo_byte]
            echo_ok = (echo_val >> bit_idx) & 1 == 1

        # Read post-state from raspi-gpio
        post_gpio = gpio_client.read_all()

        # Compare
        changes = []
        for pin in sorted(pre_gpio, key=lambda x: int(x)):
            pre_val = pre_gpio[pin]
            post_val = post_gpio[pin]
            if pre_val != -1 and post_val != -1 and pre_val != post_val:
                direction = "HIGH->LOW" if post_val == 0 else "LOW->HIGH"
                changes.append((int(pin), direction))

        results.append((name, changes, echo_ok))

        # Turn OFF
        comm.clear_all_outputs()
        time.sleep(1.0)

    # Print summary
    mapped = sum(1 for _, c, _ in results if c)
    print(f"\nOutput test results: {mapped}/{len(results)} mapped to GPIO")
    for name, changes, echo in results:
        gpio_str = ", ".join(f"GPIO {p} ({d})" for p, d in changes) if changes else "none"
        echo_str = "ECHOED" if echo else "NOT echoed"
        print(f"  {name:<8} {echo_str:<14} {gpio_str}")


# Standalone runner
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="E2E output test: FeralBoard -> raspi-gpio")
    parser.add_argument("--port", default="/dev/ttyAMA0", help="Serial port")
    parser.add_argument("--gpio-host", default="192.168.0.142", help="raspi-gpio IP")
    parser.add_argument("--gpio-port", type=int, default=5555, help="GPIO API port")
    parser.add_argument("--settle", type=float, default=SETTLE_TIME, help="Settle time (s)")
    args = parser.parse_args()

    print("=" * 64)
    print("  End-to-End Output Test: FeralBoard -> raspi-gpio GPIO")
    print("=" * 64)

    gpio = GpioClient(host=args.gpio_host, port=args.gpio_port)
    if not gpio.ping():
        print("FAIL: GPIO API not reachable")
        sys.exit(1)
    print("  GPIO API: OK")

    comm = SerialCommunicator(args.port)
    if not comm.open():
        print("  FAIL: Could not open serial port")
        sys.exit(1)
    comm.start()
    time.sleep(0.5)

    if not wait_valid_rx(comm, VALID_RX_TIMEOUT):
        print("  FAIL: No valid RX from FeralBoard")
        comm.stop()
        comm.close()
        sys.exit(1)

    try:
        test_all_outputs(comm, gpio, args.settle)
    finally:
        comm.clear_all_outputs()
        time.sleep(0.3)
        comm.stop()
        comm.close()
