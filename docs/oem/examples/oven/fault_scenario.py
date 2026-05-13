#!/usr/bin/env python3
"""Demonstrate oven fault simulation."""

from dataclasses import asdict
import json

from feralboard_oven import OvenSimulator


def main():
    sim = OvenSimulator()
    sim.set_door_closed(True)
    sim.set_temperature(265)
    sim.set_fault("motor_over_temperature", True)

    print(json.dumps(asdict(sim.snapshot()), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
