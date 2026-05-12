"""CRC-8 checksum calculation for FeralBoard serial frames."""

CRC8_POLY = 0x07


def calculate_crc8(data: bytes) -> int:
    crc = 0x00
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ CRC8_POLY) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc


def verify_crc8(data: bytes) -> bool:
    if len(data) < 2:
        return False
    calculated = calculate_crc8(data[:-1])
    return calculated == data[-1]
