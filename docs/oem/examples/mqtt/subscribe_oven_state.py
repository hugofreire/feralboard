#!/usr/bin/env python3
"""Subscribe to Ramalhos global oven state and print a compact live snapshot."""

import argparse
import json
import time

import paho.mqtt.client as mqtt


def make_client(client_id):
    try:
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
    except (AttributeError, TypeError):
        return mqtt.Client(client_id=client_id)


def compact_state(topic, state):
    oven_state = state.get("ovenState") or {}
    temperature = oven_state.get("temperature") or {}
    turbine = oven_state.get("turbine") or {}
    errors = oven_state.get("errors") or {}
    recipe_state = state.get("recipeState") or {}
    recipe_status = recipe_state.get("status") or {}

    return {
        "topic": topic,
        "ovenTemperature": temperature.get("ovenTemperature"),
        "pcbTemperature": temperature.get("pcbTemperature"),
        "turbineDirection": turbine.get("direction"),
        "turbineSpeed": turbine.get("speed"),
        "resistance": (oven_state.get("resistance") or {}).get("status"),
        "ovenLight": (oven_state.get("ovenLight") or {}).get("status"),
        "doorManualOpen": (oven_state.get("door") or {}).get("manualDoorOpenedSignal"),
        "ovenOverheatSignal": errors.get("ovenOverheatSignal"),
        "turbineOverheatSignal": errors.get("turbineOverheatSignal"),
        "recipeStatus": recipe_status.get("currentStatus"),
        "elapsedTime": state.get("elapsedTime"),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, default=1883)
    parser.add_argument("--company-id", default="+")
    parser.add_argument("--bakery-id", default="+")
    parser.add_argument("--panel-id", default="+")
    parser.add_argument("--raw", action="store_true", help="Print full JSON payload")
    args = parser.parse_args()

    topic = f"{args.company_id}/{args.bakery_id}/{args.panel_id}/oven/global-oven-state"

    def on_connect(client, userdata, flags, reason_code, properties=None):
        client.subscribe(topic)
        print(f"Subscribed to {topic}")

    def on_message(client, userdata, message):
        payload = json.loads(message.payload.decode("utf-8"))
        output = payload if args.raw else compact_state(message.topic, payload)
        print(json.dumps(output, indent=2, sort_keys=True))

    client = make_client(client_id=f"oem-state-{int(time.time())}")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(args.host, args.port, keepalive=30)
    client.loop_forever()


if __name__ == "__main__":
    main()
