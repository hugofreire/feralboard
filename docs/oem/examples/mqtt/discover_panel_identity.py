#!/usr/bin/env python3
"""Read the local Ramalhos panel identity used in MQTT topic paths."""

import argparse
import json
import urllib.request


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True, help="Panel IP or hostname")
    parser.add_argument("--port", type=int, default=8080, help="Panel HTTP API port")
    args = parser.parse_args()

    url = f"http://{args.host}:{args.port}/api/oven-panel"
    with urllib.request.urlopen(url, timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))

    if not payload.get("success"):
        raise SystemExit(f"Panel API returned an error: {payload}")

    panel = payload.get("data")
    if panel is None:
        raise SystemExit("Panel is not registered yet.")

    result = {
        "companyId": panel.get("companyId"),
        "bakeryId": panel.get("bakeryId"),
        "ovenPanelId": panel.get("id"),
        "serialNumber": panel.get("serialNumber"),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
