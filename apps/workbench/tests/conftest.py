"""Shared pytest fixtures for E2E tests."""

import sys
import os
import time
import pytest

# Ensure lib/ is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.serial_comm import SerialCommunicator
from lib.gpio_client import GpioClient


DEFAULT_PORT = "/dev/ttyAMA0"
DEFAULT_GPIO_HOST = "192.168.0.142"
DEFAULT_GPIO_PORT = 5555
VALID_RX_TIMEOUT = 10.0


def pytest_addoption(parser):
    parser.addoption("--port", default=DEFAULT_PORT, help="Serial port")
    parser.addoption("--gpio-host", default=DEFAULT_GPIO_HOST, help="raspi-gpio IP")
    parser.addoption("--gpio-port", type=int, default=DEFAULT_GPIO_PORT, help="GPIO API port")
    parser.addoption("--settle", type=float, default=3.0, help="Settle time (s)")


@pytest.fixture(scope="session")
def serial_port(request):
    return request.config.getoption("--port")


@pytest.fixture(scope="session")
def gpio_host(request):
    return request.config.getoption("--gpio-host")


@pytest.fixture(scope="session")
def gpio_port(request):
    return request.config.getoption("--gpio-port")


@pytest.fixture(scope="session")
def settle_time(request):
    return request.config.getoption("--settle")


@pytest.fixture(scope="session")
def gpio_client(gpio_host, gpio_port):
    client = GpioClient(host=gpio_host, port=gpio_port)
    assert client.ping(), f"GPIO API not reachable at {gpio_host}:{gpio_port}"
    return client


@pytest.fixture(scope="session")
def communicator(serial_port):
    comm = SerialCommunicator(serial_port)
    assert comm.open(), f"Could not open serial port {serial_port}"
    comm.start()
    time.sleep(0.5)

    # Wait for valid RX
    deadline = time.time() + VALID_RX_TIMEOUT
    while time.time() < deadline:
        _, valid = comm.get_rx_buffer()
        _, rx_count, _ = comm.get_stats()
        if valid and rx_count > 0:
            break
        time.sleep(0.05)
    else:
        comm.stop()
        comm.close()
        pytest.fail("No valid RX from FeralBoard within timeout")

    yield comm

    comm.clear_all_outputs()
    time.sleep(0.3)
    comm.stop()
    comm.close()
