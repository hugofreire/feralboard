#!/usr/bin/env python3
"""Install or control an OpenVPN client profile."""

import argparse

from feralboard_sdk import (
    disable_vpn,
    enable_vpn,
    get_vpn_logs,
    get_vpn_status,
    install_openvpn_profile,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile")
    parser.add_argument("--name", default="client")
    parser.add_argument("--enable", action="store_true")
    parser.add_argument("--disable", action="store_true")
    parser.add_argument("--logs", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if args.profile:
        for result in install_openvpn_profile(
            args.profile,
            profile_name=args.name,
            dry_run=not args.apply,
        ):
            print(" ".join(result.command))
    if args.enable:
        print(" ".join(enable_vpn(args.name, dry_run=not args.apply).command))
    if args.disable:
        print(" ".join(disable_vpn(args.name, dry_run=not args.apply).command))
    if args.logs:
        print(get_vpn_logs(args.name))
    print(get_vpn_status(args.name))


if __name__ == "__main__":
    main()
