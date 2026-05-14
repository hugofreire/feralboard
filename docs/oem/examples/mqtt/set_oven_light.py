#!/usr/bin/env python3
"""Set the oven light through the Ramalhos app-level MQTT API."""

import argparse
import json
import queue
import sys
import uuid

import paho.mqtt.client as mqtt


def make_client(client_id):
    try:
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
    except (AttributeError, TypeError):
        return mqtt.Client(client_id=client_id)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, default=1883)
    parser.add_argument("--company-id", required=True)
    parser.add_argument("--bakery-id", required=True)
    parser.add_argument("--panel-id", required=True)
    state = parser.add_mutually_exclusive_group(required=True)
    state.add_argument("--on", action="store_true")
    state.add_argument("--off", action="store_true")
    parser.add_argument("--timeout", type=float, default=15.0)
    args = parser.parse_args()

    request_id = str(uuid.uuid4())
    base_topic = f"{args.company_id}/{args.bakery_id}/{args.panel_id}/oven"
    request = {
        "requestId": request_id,
        "command": "SET_OVEN_LIGHT",
        "params": {
            "status": bool(args.on),
            "causedBy": "user",
        },
    }
    responses = queue.Queue()

    def on_connect(client, userdata, flags, reason_code, properties=None):
        client.subscribe(f"{base_topic}/response")
        client.publish(f"{base_topic}/request", json.dumps(request))

    def on_message(client, userdata, message):
        payload = json.loads(message.payload.decode("utf-8"))
        if payload.get("requestId") == request_id:
            responses.put(payload)

    client = make_client(client_id=f"oem-light-{request_id}")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(args.host, args.port, keepalive=30)
    client.loop_start()

    try:
        response = responses.get(timeout=args.timeout)
    except queue.Empty:
        print(f"Timed out waiting for response to requestId={request_id}", file=sys.stderr)
        raise SystemExit(2)
    finally:
        client.loop_stop()
        client.disconnect()

    print(json.dumps(response, indent=2, sort_keys=True))
    if not response.get("success") or response.get("data") is not True:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
