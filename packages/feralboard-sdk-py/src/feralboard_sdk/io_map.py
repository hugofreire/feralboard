"""DI0-DI7 / DO0-DO11 channel definitions and bit mappings.

Each output is (name, tx_byte_index, bit_index, rx_byte_index).
Each input is (name, rx_byte_index, bit_index).
"""

OUTPUTS = [
    ("DO0", 0, 0, 0),
    ("DO1", 0, 1, 0),
    ("DO2", 0, 2, 0),
    ("DO3", 0, 3, 0),
    ("DO4", 0, 4, 0),
    ("DO5", 0, 5, 0),
    ("DO6", 0, 6, 0),
    ("DO7", 0, 7, 0),
    ("DO8", 2, 6, 2),
    ("DO9", 2, 7, 2),
    ("DO10", 3, 0, 3),
    ("DO11", 3, 1, 3),
]

INPUTS = [
    ("DI0", 4, 0),
    ("DI1", 4, 1),
    ("DI2", 4, 2),
    ("DI3", 4, 3),
    ("DI4", 4, 4),
    ("DI5", 4, 5),
    ("DI6", 4, 6),
    ("DI7", 4, 7),
]

OUTPUT_LEGACY_NAMES = {
    "DO0": "Direction 1",
    "DO1": "Direction 2",
    "DO2": "Speed 1",
    "DO3": "Speed 2",
    "DO4": "Resistor",
    "DO5": "Vapour Exit",
    "DO6": "Extractor",
    "DO7": "Vapour Creation",
    "DO8": "Oven Illumination",
    "DO9": "External Buzzer",
    "DO10": "Internal Buzzer",
    "DO11": "Cooling Fan",
}

INPUT_LEGACY_NAMES = {
    "DI0": "Door End Stop",
    "DI1": "Electric Protection",
    "DI2": "Oven Over Temp",
    "DI3": "Motor Over Temp",
    "DI4": "Door Switch Locked",
    "DI5": "Door Switch Locking 1",
    "DI6": "Door Switch Locking 2",
    "DI7": "Door Switch Traction",
}


def get_output(channel_name: str):
    for output in OUTPUTS:
        if output[0] == channel_name:
            return output
    raise ValueError(f"Unknown output channel: {channel_name}")


def get_input(channel_name: str):
    for input_channel in INPUTS:
        if input_channel[0] == channel_name:
            return input_channel
    raise ValueError(f"Unknown input channel: {channel_name}")
