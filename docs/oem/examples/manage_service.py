#!/usr/bin/env python3
"""Restart or inspect an approved FeralBoard service."""

import argparse

from feralboard_sdk import get_service_status, restart_service


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("service", choices=("vpn", "mqtt", "postgres"))
    parser.add_argument("--restart", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if args.restart:
        result = restart_service(args.service, dry_run=not args.apply)
        print(" ".join(result.command))

    print(get_service_status(args.service))


if __name__ == "__main__":
    main()
