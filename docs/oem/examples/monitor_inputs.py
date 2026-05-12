#!/usr/bin/env python3
"""Print FeralBoard digital input changes."""

import argparse
import time

from feralboard_sdk import FeralBoardClient


INPUTS = [f"DI{i}" for i in range(8)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default="/dev/ttyAMA0")
    parser.add_argument("--interval", type=float, default=0.1)
    args = parser.parse_args()

    with FeralBoardClient(args.port) as board:
        previous = {}
        while True:
            current = {name: board.read_input(name) for name in INPUTS}
            if current != previous:
                print(current)
                previous = current
            time.sleep(args.interval)


if __name__ == "__main__":
    main()
