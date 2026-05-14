#!/usr/bin/env python3
"""Publish a Ramalhos panel MQTT request and wait for the matching response."""

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


def build_base_topic(company_id, bakery_id, panel_id, module):
    return f"{company_id}/{bakery_id}/{panel_id}/{module}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, default=1883)
    parser.add_argument("--company-id", required=True)
    parser.add_argument("--bakery-id", required=True)
    parser.add_argument("--panel-id", required=True)
    parser.add_argument("--module", default="main", choices=["main", "oven"])
    parser.add_argument("--command", required=True)
    parser.add_argument("--params", help="JSON params payload. Omit for no params.")
    parser.add_argument("--timeout", type=float, default=15.0)
    args = parser.parse_args()

    request_id = str(uuid.uuid4())
    request = {
        "requestId": request_id,
        "command": args.command,
    }
    if args.params is not None:
        request["params"] = json.loads(args.params)

    base_topic = build_base_topic(args.company_id, args.bakery_id, args.panel_id, args.module)
    request_topic = f"{base_topic}/request"
    response_topic = f"{base_topic}/response"
    responses = queue.Queue()

    def on_connect(client, userdata, flags, reason_code, properties=None):
        client.subscribe(response_topic)
        client.publish(request_topic, json.dumps(request))

    def on_message(client, userdata, message):
        payload = json.loads(message.payload.decode("utf-8"))
        if payload.get("requestId") == request_id:
            responses.put(payload)

    client = make_client(client_id=f"oem-request-{request_id}")
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
    if not response.get("success"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
