#!/usr/bin/env python3
"""Run the oven simulator on a serial or PTY path."""

import argparse

from feralboard_oven import OvenSimulator


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--serial", required=True)
    parser.add_argument("--temperature", type=float, default=25.0)
    parser.add_argument("--door-open", action="store_true")
    args = parser.parse_args()

    sim = OvenSimulator()
    sim.set_temperature(args.temperature)
    sim.set_door_closed(not args.door_open)
    sim.run_serial(args.serial)


if __name__ == "__main__":
    main()
