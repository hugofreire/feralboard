"""DI0-DI7 / DO0-DO11 channel definitions and bit mappings.

Each output is (name, tx_byte_index, bit_index, rx_byte_index).
Each input is (name, rx_byte_index, bit_index).
"""

# Digital outputs: (name, tx_byte, bit, rx_echo_byte)
OUTPUTS = [
    ("DO0",  0, 0, 0),   # Direction 1
    ("DO1",  0, 1, 0),   # Direction 2
    ("DO2",  0, 2, 0),   # Speed 1
    ("DO3",  0, 3, 0),   # Speed 2
    ("DO4",  0, 4, 0),   # Resistor
    ("DO5",  0, 5, 0),   # Vapour Exit
    ("DO6",  0, 6, 0),   # Extractor
    ("DO7",  0, 7, 0),   # Vapour Creation
    ("DO8",  2, 6, 2),   # Oven Illumination
    ("DO9",  2, 7, 2),   # External Buzzer
    ("DO10", 3, 0, 3),   # Internal Buzzer
    ("DO11", 3, 1, 3),   # Cooling Fan
]

# Digital inputs: (name, rx_byte, bit)
INPUTS = [
    ("DI0", 4, 0),  # Door End Stop
    ("DI1", 4, 1),  # Electric Protection
    ("DI2", 4, 2),  # Oven Over Temp
    ("DI3", 4, 3),  # Motor Over Temp
    ("DI4", 4, 4),  # Door Switch Locked
    ("DI5", 4, 5),  # Door Switch Locking 1
    ("DI6", 4, 6),  # Door Switch Locking 2
    ("DI7", 4, 7),  # Door Switch Traction
]

# Legacy name aliases for display
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
