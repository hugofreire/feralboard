#!/usr/bin/env python3
"""Preview or apply timezone and NTP settings."""

import argparse

from feralboard_sdk import TimeConfig, apply_time_config, get_time_status


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--timezone")
    parser.add_argument("--ntp-server", action="append", default=[])
    parser.add_argument("--disable-ntp", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if args.status:
        print(get_time_status())
        return

    results = apply_time_config(
        TimeConfig(
            timezone=args.timezone,
            ntp_enabled=not args.disable_ntp,
            ntp_servers=args.ntp_server,
        ),
        dry_run=not args.apply,
    )

    for result in results:
        print(" ".join(result.command))


if __name__ == "__main__":
    main()
