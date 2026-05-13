"""Command-line interface for the FeralBoard oven simulator."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import threading

from .simulator import OvenSimulator


def _interactive_shell(simulator: OvenSimulator):
    print("Interactive commands: status, temp <c>, door open|closed, fault <name> on|off, clear, quit")
    while True:
        try:
            raw = input("oven-sim> ").strip()
        except EOFError:
            return
        if not raw:
            continue
        parts = raw.split()
        command = parts[0].lower()
        if command in {"quit", "exit"}:
            return
        if command == "status":
            print(json.dumps(asdict(simulator.snapshot()), indent=2, sort_keys=True))
        elif command == "temp" and len(parts) == 2:
            simulator.set_temperature(float(parts[1]))
        elif command == "door" and len(parts) == 2:
            simulator.set_door_closed(parts[1].lower() == "closed")
        elif command == "fault" and len(parts) == 3:
            simulator.set_fault(parts[1], parts[2].lower() in {"on", "true", "1"})
        elif command == "clear":
            simulator.clear_faults()
        else:
            print("Unknown command")


def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="FeralBoard oven simulator")
    parser.add_argument("--serial", help="Serial or PTY path to serve")
    parser.add_argument("--baudrate", type=int, default=9600)
    parser.add_argument("--temperature", type=float, default=25.0)
    parser.add_argument("--door", choices=("open", "closed"), default="closed")
    parser.add_argument("--no-interactive", action="store_true")
    args = parser.parse_args(argv)

    simulator = OvenSimulator()
    simulator.set_temperature(args.temperature)
    simulator.set_door_closed(args.door == "closed")

    if args.serial:
        worker = threading.Thread(
            target=simulator.run_serial,
            args=(args.serial,),
            kwargs={"baudrate": args.baudrate},
            daemon=True,
        )
        worker.start()
        print(f"Serving FeralBoard oven simulation on {args.serial}")

    if args.no_interactive:
        if args.serial:
            worker.join()
        else:
            print(json.dumps(asdict(simulator.snapshot()), indent=2, sort_keys=True))
        return

    _interactive_shell(simulator)


if __name__ == "__main__":
    main()
