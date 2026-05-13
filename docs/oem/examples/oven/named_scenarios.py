#!/usr/bin/env python3
"""Print built-in oven simulator scenarios."""

from dataclasses import asdict
import json

from feralboard_oven import (
    door_open,
    electric_protection_trip,
    motor_over_temperature,
    oven_over_temperature,
    ready_oven,
)


def main():
    scenarios = {
        "ready": ready_oven(),
        "door_open": door_open(),
        "oven_over_temperature": oven_over_temperature(),
        "motor_over_temperature": motor_over_temperature(),
        "electric_protection_trip": electric_protection_trip(),
    }
    payload = {
        name: asdict(sim.snapshot())
        for name, sim in scenarios.items()
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
