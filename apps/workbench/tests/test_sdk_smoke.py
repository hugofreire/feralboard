"""Non-hardware smoke tests for the FeralBoard SDK extraction."""

from feralboard_sdk import FeralBoardClient
from feralboard_sdk.crc8 import calculate_crc8, verify_crc8
from feralboard_sdk.io_map import INPUTS, OUTPUTS
from feralboard_sdk.protocol import TX_BUFFER_SIZE
from feralboard_sdk.serial_comm import SerialCommunicator
from lib.serial_comm import SerialCommunicator as CompatSerialCommunicator


def test_crc8_known_value_and_frame_verification():
    assert calculate_crc8(bytes(range(10))) == 133

    comm = SerialCommunicator("/dev/null")
    frame = comm._build_tx_buffer()

    assert len(frame) == TX_BUFFER_SIZE
    assert verify_crc8(frame)


def test_named_output_helper_sets_expected_tx_bits():
    comm = SerialCommunicator("/dev/null")

    comm.set_output("DO0", True)
    comm.set_output("DO8", True)
    comm.set_output("DO10", True)

    assert comm.get_tx_state() == (1, 0, 64, 1, 0)

    comm.set_output("DO8", False)

    assert comm.get_tx_state() == (1, 0, 0, 1, 0)


def test_sdk_exports_and_compatibility_wrappers():
    assert len(OUTPUTS) == 12
    assert len(INPUTS) == 8
    assert FeralBoardClient("/dev/null").port == "/dev/null"
    assert CompatSerialCommunicator is SerialCommunicator
