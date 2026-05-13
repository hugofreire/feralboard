#!/usr/bin/env python3
"""Read or update FeralBoard identity fields."""

import argparse

from feralboard_sdk import get_device_identity, set_device_name, set_hostname


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hostname")
    parser.add_argument("--device-name")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if args.hostname:
        print(" ".join(set_hostname(args.hostname, dry_run=not args.apply).command))
    if args.device_name:
        print(" ".join(set_device_name(args.device_name, dry_run=not args.apply).command))

    print(get_device_identity())


if __name__ == "__main__":
    main()
