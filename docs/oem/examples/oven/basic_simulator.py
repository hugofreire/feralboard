#!/usr/bin/env python3
"""Create an oven simulator and print a customer-facing snapshot."""

from dataclasses import asdict
import json

from feralboard_oven import OvenSimulator


def main():
    sim = OvenSimulator()
    sim.set_temperature(180)
    sim.set_door_closed(True)

    print(json.dumps(asdict(sim.snapshot()), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
