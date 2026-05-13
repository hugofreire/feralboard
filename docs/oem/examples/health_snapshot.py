#!/usr/bin/env python3
"""Print a read-only FeralBoard health snapshot as JSON."""

from feralboard_sdk import collect_health_snapshot


def main():
    print(collect_health_snapshot().to_json())


if __name__ == "__main__":
    main()
