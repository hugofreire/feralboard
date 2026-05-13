#!/usr/bin/env python3
"""Preview or apply an Ethernet network configuration with nmcli."""

import argparse

from feralboard_sdk import NetworkConfig, apply_network_config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interface", default="eth0")
    parser.add_argument("--mode", choices=("dhcp", "static"), default="dhcp")
    parser.add_argument("--ip")
    parser.add_argument("--prefix", type=int)
    parser.add_argument("--gateway")
    parser.add_argument("--dns", action="append", default=[])
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    results = apply_network_config(
        NetworkConfig(
            interface=args.interface,
            mode=args.mode,
            ip_address=args.ip,
            prefix=args.prefix,
            gateway=args.gateway,
            dns=args.dns,
        ),
        dry_run=not args.apply,
    )

    for result in results:
        print(" ".join(result.command))


if __name__ == "__main__":
    main()
