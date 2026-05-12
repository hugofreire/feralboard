#!/usr/bin/env python3
"""Minimal FeralBoard SDK example: set one output, then clear all outputs."""

import argparse
import time

from feralboard_sdk import FeralBoardClient


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default="/dev/ttyAMA0")
    parser.add_argument("--output", default="DO0")
    parser.add_argument("--seconds", type=float, default=2.0)
    args = parser.parse_args()

    with FeralBoardClient(args.port) as board:
        board.set_output(args.output, True)
        time.sleep(args.seconds)
        board.clear_all_outputs()


if __name__ == "__main__":
    main()
