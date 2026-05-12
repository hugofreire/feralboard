#!/usr/bin/env python3
"""Print communication counters and input snapshots."""

import argparse
import time

from feralboard_sdk import FeralBoardClient


INPUTS = [f"DI{i}" for i in range(8)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default="/dev/ttyAMA0")
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args()

    with FeralBoardClient(args.port) as board:
        while True:
            tx_count, rx_count, error_count = board.get_stats()
            inputs = {name: board.read_input(name) for name in INPUTS}
            print({
                "tx_count": tx_count,
                "rx_count": rx_count,
                "error_count": error_count,
                "inputs": inputs,
            })
            time.sleep(args.interval)


if __name__ == "__main__":
    main()
