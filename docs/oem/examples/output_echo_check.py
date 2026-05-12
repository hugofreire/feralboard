#!/usr/bin/env python3
"""Set an output and check the board-reported output echo state."""

import argparse
import time

from feralboard_sdk import FeralBoardClient


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default="/dev/ttyAMA0")
    parser.add_argument("--output", default="DO0")
    args = parser.parse_args()

    with FeralBoardClient(args.port) as board:
        board.set_output(args.output, True)
        time.sleep(0.5)

        echo = board.read_output_echo(args.output)
        if echo is None:
            print("No valid board state yet")
        else:
            print(f"{args.output} echo: {'ON' if echo else 'OFF'}")

        board.clear_all_outputs()


if __name__ == "__main__":
    main()
