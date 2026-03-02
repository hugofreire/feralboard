#!/usr/bin/env python3
"""
End-to-end test: raspi-gpio GPIO -> FeralBoard inputs via UART verification.

Can be run standalone or via pytest:
    python3 tests/test_inputs_e2e.py [--port /dev/ttyAMA0] [--gpio-host 192.168.0.142]
    pytest tests/test_inputs_e2e.py --port /dev/ttyAMA0
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.serial_comm import SerialCommunicator
from lib.gpio_client import GpioClient

# GPIO pin -> FeralBoard input mapping
# (gpio_pin, rx_byte, bit_idx, name)
INPUT_TESTS = [
    (15, 4, 0, "DI0 - Door End Stop"),
    (18, 4, 1, "DI1 - Electric Protection"),
    (17, 4, 2, "DI2 - Oven Over Temp"),
    (17, 4, 3, "DI3 - Motor Over Temp"),
]

SETTLE_TIME = 2.0
CHANGE_TIMEOUT = 5.0
VALID_RX_TIMEOUT = 10.0
STABLE_READINGS = 3


def read_stable_bit(comm, rx_byte_idx, bit_idx, timeout=3.0):
    """Read a stable input bit value. Returns (bit_value, success)."""
    deadline = time.time() + timeout
    last_rx_count = 0
    readings = []

    while time.time() < deadline:
        rx_buffer, valid = comm.get_rx_buffer()
        _, rx_count, _ = comm.get_stats()
        if valid and rx_buffer and rx_count > last_rx_count:
            last_rx_count = rx_count
            bit = (rx_buffer[rx_byte_idx] >> bit_idx) & 1
            readings.append(bit)
            if len(readings) >= STABLE_READINGS:
                recent = readings[-STABLE_READINGS:]
                if all(b == recent[0] for b in recent):
                    return recent[0], True
        time.sleep(0.05)

    if readings:
        return readings[-1], True
    return 0, False


def wait_for_bit(comm, rx_byte_idx, bit_idx, expected, timeout):
    """Wait for input bit to reach expected value with stable confirmation."""
    deadline = time.time() + timeout
    last_rx_count = 0
    streak = 0

    while time.time() < deadline:
        rx_buffer, valid = comm.get_rx_buffer()
        _, rx_count, _ = comm.get_stats()
        if valid and rx_buffer and rx_count > last_rx_count:
            last_rx_count = rx_count
            bit = (rx_buffer[rx_byte_idx] >> bit_idx) & 1
            if bit == expected:
                streak += 1
                if streak >= STABLE_READINGS:
                    return True
            else:
                streak = 0
        time.sleep(0.05)
    return False


def wait_valid_rx(comm, timeout):
    deadline = time.time() + timeout
    while time.time() < deadline:
        _, valid = comm.get_rx_buffer()
        _, rx_count, _ = comm.get_stats()
        if valid and rx_count > 0:
            return True
        time.sleep(0.05)
    return False


def test_all_inputs(communicator, gpio_client, settle_time):
    """Test all known input mappings via GPIO drive.

    Inputs sharing a GPIO pin (e.g. DI2+DI3 on pin 17) are tested
    together in a single drive cycle to avoid baseline instability.
    """
    comm = communicator

    # Setup GPIO output pins (LOW initially)
    gpio_pins = sorted(set(pin for pin, _, _, _ in INPUT_TESTS))
    for pin in gpio_pins:
        gpio_client.write(pin, 0)

    # Group inputs by GPIO pin
    from collections import OrderedDict
    pin_groups = OrderedDict()
    for gpio_pin, rx_byte, bit_idx, name in INPUT_TESTS:
        pin_groups.setdefault(gpio_pin, []).append((rx_byte, bit_idx, name))

    results = []

    for gpio_pin, inputs in pin_groups.items():
        # Ensure GPIO LOW and let settle
        gpio_client.write(gpio_pin, 0)
        time.sleep(settle_time)

        # Read baselines for all bits on this pin
        baselines = {}
        skip_group = False
        for rx_byte, bit_idx, name in inputs:
            baseline, ok = read_stable_bit(comm, rx_byte, bit_idx)
            if not ok:
                results.append((name, False, "no stable baseline"))
                skip_group = True
            else:
                baselines[(rx_byte, bit_idx)] = baseline
        if skip_group:
            continue

        # Drive GPIO HIGH — expect all mapped bits to toggle
        gpio_client.write(gpio_pin, 1)
        time.sleep(settle_time)

        changed = {}
        for rx_byte, bit_idx, name in inputs:
            bl = baselines[(rx_byte, bit_idx)]
            expected = 0 if bl == 1 else 1
            changed[(rx_byte, bit_idx)] = wait_for_bit(
                comm, rx_byte, bit_idx, expected, CHANGE_TIMEOUT
            )

        # Drive GPIO LOW — expect return to baseline
        gpio_client.write(gpio_pin, 0)
        time.sleep(settle_time)

        for rx_byte, bit_idx, name in inputs:
            bl = baselines[(rx_byte, bit_idx)]
            bit_changed = changed[(rx_byte, bit_idx)]
            bit_returned = wait_for_bit(
                comm, rx_byte, bit_idx, bl, CHANGE_TIMEOUT
            )

            if bit_changed and bit_returned:
                results.append((name, True, ""))
            elif bit_changed:
                results.append((name, False, "did not return to baseline"))
            else:
                results.append((name, False, "no state change"))

    # Cleanup
    for pin in gpio_pins:
        gpio_client.write(pin, 0)
    for pin in gpio_pins:
        gpio_client.reset(pin)

    # Print summary
    passed = sum(1 for _, p, _ in results if p)
    print(f"\nInput test results: {passed}/{len(results)} passed")
    for name, ok, reason in results:
        status = "PASS" if ok else f"FAIL: {reason}"
        print(f"  {name:<30} {status}")

    assert passed == len(results), f"Input tests failed: {len(results) - passed} failures"


# Standalone runner
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="E2E input test: raspi-gpio GPIO -> FeralBoard")
    parser.add_argument("--port", default="/dev/ttyAMA0", help="Serial port")
    parser.add_argument("--gpio-host", default="192.168.0.142", help="raspi-gpio IP")
    parser.add_argument("--gpio-port", type=int, default=5555, help="GPIO API port")
    args = parser.parse_args()

    print("=" * 64)
    print("  End-to-End Input Test: raspi-gpio GPIO -> FeralBoard")
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
        test_all_inputs(comm, gpio, args.settle if hasattr(args, 'settle') else 2.0)
    finally:
        comm.clear_all_outputs()
        time.sleep(0.3)
        comm.stop()
        comm.close()
