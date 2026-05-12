#!/usr/bin/env python3
"""Simple application loop: mirror one input into one output."""

import argparse
import time

from feralboard_sdk import FeralBoardClient


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default="/dev/ttyAMA0")
    parser.add_argument("--input", default="DI0")
    parser.add_argument("--output", default="DO0")
    parser.add_argument("--interval", type=float, default=0.1)
    args = parser.parse_args()

    with FeralBoardClient(args.port) as board:
        while True:
            input_state = board.read_input(args.input)
            if input_state is not None:
                board.set_output(args.output, input_state)
            time.sleep(args.interval)


if __name__ == "__main__":
    main()
