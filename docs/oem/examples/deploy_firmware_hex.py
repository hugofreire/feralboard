#!/usr/bin/env python3
"""Deploy a release HEX file to FeralBoard over serialUPDI."""

import argparse

from feralboard_sdk import deploy_firmware_hex


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("hex_file")
    parser.add_argument("--port", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    result = deploy_firmware_hex(
        args.hex_file,
        port=args.port,
        dry_run=args.dry_run,
    )

    print(f"HEX: {result.hex_path}")
    print(f"Port: {result.port}")
    for command in result.commands:
        print(" ".join(command))


if __name__ == "__main__":
    main()
