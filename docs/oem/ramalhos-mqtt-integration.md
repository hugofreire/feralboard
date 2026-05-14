# Ramalhos Oven Panel MQTT Integration - OEM Evaluation Guide

This document describes the MQTT integration surface exposed by the Ramalhos
oven panel application. It is intended for OEM customers that want to use the
existing panel app directly and connect a supervisory system, test fixture, or
factory integration to the panel MQTT broker.

The MQTT API is app-level. It exposes oven state, application notifications, and
approved request/response commands. It does not expose firmware source, SDK
source, or the low-level serial protocol used between the app and FeralBoard.

## Integration Summary

- The oven manager controls hardware through the local application backend.
- MQTT broadcasts the consolidated oven state to the UI and integrations.
- MQTT requests can ask the app to perform approved actions.
- Request replies use `requestId` correlation.
- All payloads are UTF-8 JSON.
- State messages are not retained; clients should handle reconnect and wait for
  the next state broadcast.
- The customer integration should prefer read-only state subscription first,
  then add mutating commands only after safety review.

## Broker Endpoints

Typical local endpoints:

```text
mqtt://<panel-ip>:1883
ws://<panel-ip>:9001
```

The browser UI uses the websocket endpoint. Backend processes use the TCP MQTT
endpoint. Ports are configured by the deployed app environment:

```text
MOSQUITTO_HOST
MOSQUITTO_PORT
MOSQUITTO_WEBSOCKETS_PORT
```

The local Mosquitto configuration is optimized for embedded use and does not
guarantee persistent retained messages. Production deployments should restrict
broker access to the OEM network, VPN, or approved firewall rules.

## Discovering Panel IDs

MQTT topics include the registered panel identity:

```text
companyId/bakeryId/ovenPanelId/module/channel
```

The panel app exposes the local identity over HTTP:

```bash
curl http://<panel-ip>:8080/api/oven-panel
```

Example response shape:

```json
{
  "success": true,
  "data": {
    "id": "7c366bb0-f8b4-4b86-94a7-ea19173a8bdc",
    "bakeryId": "c68a401c-2465-49ef-8d2f-6eb9019af1ef",
    "companyId": "9f6b7093-a4d0-4150-b65d-2149c9a449c1",
    "serialNumber": "PANEL-SERIAL"
  }
}
```

For robust state monitoring, subscribe with a wildcard bakery segment:

```text
<companyId>/+/<ovenPanelId>/oven/global-oven-state
```

Some older builds may publish oven state with a placeholder bakery segment when
the bakery is not configured. The wildcard keeps the client compatible.

## Topic Model

Internal app topics use this structure:

```text
{companyId}/{bakeryId}/{ovenPanelId}/{module}/{channel}
```

Main modules used by OEM integrations:

| Module | Purpose |
|--------|---------|
| `oven` | Oven state broadcasts and oven-manager commands. |
| `main` | Network settings, general device settings, migrations, readiness. |
| `express` | HTTP/backend notifications such as panel settings changes. |
| `renderer` | UI-facing commands used by the cloud bridge. |
| `sync-in` | Sync commands used by the cloud bridge. |

Channels:

| Channel | Direction | Payload |
|---------|-----------|---------|
| `global-oven-state` | App to clients | Raw `GlobalOvenState` JSON. |
| `request` | Client to app | `RequestMessage`. |
| `response` | App to client | `ResponseMessage`. |
| `notification` | App to clients | `NotificationMessage`. |

Common subscriptions:

```text
+/+/+/oven/global-oven-state
<companyId>/+/<ovenPanelId>/oven/global-oven-state
<companyId>/<bakeryId>/<ovenPanelId>/oven/response
<companyId>/<bakeryId>/<ovenPanelId>/main/response
+/+/+/+/notification
```

## Message Envelopes

Request:

```json
{
  "requestId": "93d6329b-2535-42b9-95f8-801bb3b08be2",
  "command": "SET_OVEN_LIGHT",
  "params": {
    "status": true,
    "causedBy": "user"
  }
}
```

Response:

```json
{
  "requestId": "93d6329b-2535-42b9-95f8-801bb3b08be2",
  "command": "SET_OVEN_LIGHT",
  "success": true,
  "data": true
}
```

Error response:

```json
{
  "requestId": "93d6329b-2535-42b9-95f8-801bb3b08be2",
  "command": "SET_OVEN_LIGHT",
  "success": false,
  "message": "Request timeout."
}
```

Notification:

```json
{
  "notificationTypeId": 21,
  "data": {
    "temperature": 64,
    "threshold": 60
  }
}
```

Use `requestId` as the only correlation key for responses. Subscribe to the
response topic before publishing the request.

## Global Oven State

Topic:

```text
{companyId}/{bakeryId}/{ovenPanelId}/oven/global-oven-state
```

Payload is the raw state object, not wrapped in a notification envelope.

Condensed example:

```json
{
  "ovenState": {
    "temperature": {
      "ovenTemperature": 178,
      "pcbTemperature": 42,
      "secondThermocoupleTemperature": 176,
      "thirdThermocoupleTemperature": 0,
      "fourthThermocoupleTemperature": 0
    },
    "turbine": {
      "direction": "clockwise",
      "speed": "low"
    },
    "resistance": {"status": "on"},
    "steamOutletValve": {"status": "off"},
    "extractorFan": {"status": "off"},
    "steamCreation": {"status": "off"},
    "ovenLight": {"status": "on"},
    "door": {
      "manualDoorOpenedSignal": "off",
      "automaticDoorOpenedSignal": "off"
    },
    "errors": {
      "motorProtection": "off",
      "ovenOverheatSignal": "off",
      "turbineOverheatSignal": "off",
      "thermocoupleError": "off",
      "forcedCoolingActive": "off"
    }
  },
  "ovenIntentions": {
    "targetTemperature": {
      "temperature": 180,
      "causedBy": "recipe"
    },
    "ovenLight": {
      "status": true,
      "remainingTime": 120,
      "causedBy": "user"
    }
  },
  "recipeState": {
    "executionId": "recipe-run-id",
    "status": {
      "currentStatus": "baking",
      "causedBy": "user"
    },
    "recipeRemainingTime": 840
  },
  "washingState": null,
  "ovenStateCommands": {
    "turbine": {
      "direction": "clockwise",
      "speed": "low"
    },
    "resistance": {"status": "on"},
    "messageOriginIdentifier": 15
  },
  "elapsedTime": 123456,
  "tickElapsedTime": 250
}
```

Important state values:

| Field | Meaning |
|-------|---------|
| `ovenState.temperature.ovenTemperature` | Main chamber temperature. |
| `ovenState.temperature.pcbTemperature` | Controller PCB temperature. |
| `ovenState.turbine.direction` | `clockwise`, `counter-clockwise`, or `none`. |
| `ovenState.turbine.speed` | `low`, `high`, or `none`. |
| `ovenState.*.status` | Usually `on` or `off` for hardware states. |
| `ovenState.errors.*` | Fault and protection signals. |
| `ovenIntentions` | What the app is currently trying to command. |
| `recipeState.status.currentStatus` | Recipe lifecycle status. |
| `washingState.status.currentStatus` | Washing lifecycle status. |
| `ovenStateCommands` | Latest command frame intent sent toward the controller. |

Status string values are generally lowercase, for example `on`, `off`,
`low`, `high`, `none`, `clockwise`, and `counter-clockwise`.

## Request Flow

1. Build the base topic:

```text
{companyId}/{bakeryId}/{ovenPanelId}/{module}
```

2. Subscribe to the response channel:

```text
{companyId}/{bakeryId}/{ovenPanelId}/{module}/response
```

3. Publish the request to:

```text
{companyId}/{bakeryId}/{ovenPanelId}/{module}/request
```

4. Wait for a response where `response.requestId` matches the request.

Recommended client timeout is 10 to 30 seconds. The app uses shorter timeouts
internally for some backend clients, but an external client should tolerate
temporary load and reconnects.

## Main Module Commands

Base topic:

```text
{companyId}/{bakeryId}/{ovenPanelId}/main
```

General settings:

| Command | Params | Response `data` |
|---------|--------|-----------------|
| `GET_NTP_SERVER` | none | string |
| `SET_NTP_SERVER` | string | boolean |
| `GET_BRIGHTNESS` | none | number |
| `SET_BRIGHTNESS` | number | number |
| `GET_3V_GPIO` | none | `on` or `off` |
| `SET_3V_GPIO` | `on` or `off` | `on` or `off` |
| `RESET_3V_GPIO` | none | boolean |

Network settings:

| Command | Params | Response `data` |
|---------|--------|-----------------|
| `GET_ACTIVE_CONNECTION` | none | `ethernet`, `wifi`, or `none` |
| `GET_WIFI_STATUS` | none | boolean |
| `ENABLE_WIFI` | none | no data; `success` indicates result |
| `DISABLE_WIFI` | none | no data; `success` indicates result |
| `GET_WIFI_NETWORKS` | none | array of Wi-Fi networks |
| `GET_CONNECTED_WIFI_NETWORK` | none | Wi-Fi network or null |
| `CONNECT_TO_WIFI_NETWORK` | `{"ssid": "...", "password": "..."}` | boolean |
| `FORGET_WIFI_NETWORK` | Wi-Fi SSID string | no data; `success` indicates result |
| `GET_NETWORK_CONFIG` | `ethernet` or `wifi` | network config object |
| `SET_NETWORK_CONFIG` | `{"connection": "...", "config": {...}}` | boolean |
| `ENABLE_DHCP` | `ethernet` or `wifi` | boolean |

Network config object:

```json
{
  "type": "static",
  "ipAddress": "192.168.10.50",
  "subnetMask": "255.255.255.0",
  "gateway": "192.168.10.1",
  "dns1": "192.168.10.1",
  "dns2": "1.1.1.1"
}
```

Network commands can disconnect the panel from the current network. Treat them
as commissioning commands and test over a recovery path first.

## Oven Module Commands

Base topic:

```text
{companyId}/{bakeryId}/{ovenPanelId}/oven
```

Common enum values:

```text
causedBy: hardware | ovenManager | recipe | washing | user | scheduler
status: true | false
turbine speed: low | high | none
turbine direction: clockwise | counter-clockwise | none
```

Recommended OEM `causedBy` value for manual supervisory commands is `user`.

Operational commands:

| Command | Params |
|---------|--------|
| `RESET_OVEN_STATE` | none |
| `SET_OVEN_LIGHT` | `{"status": true, "causedBy": "user"}` |
| `SET_STEAM_OUTLET_VALVE` | `{"status": true, "causedBy": "user"}` |
| `SET_EXTRACTOR_FAN` | `{"status": true, "causedBy": "user"}` |
| `INIT_STEAM_CREATION` | `{"causedBy": "user"}` |
| `OPEN_AUTOMATIC_DOOR` | `{"causedBy": "user"}` |
| `UNBLOCK_ELECTRIC_LOCK` | `{"causedBy": "user"}` |
| `COOL_OVEN_FOR_DURATION` | `{"duration": 60, "causedBy": "user"}` |
| `STOP_OVEN_COOLING` | `{"causedBy": "user"}` |
| `ABORT_PROGRAMS` | `{"causedBy": "user"}` |

Manufacturer/service commands:

| Command | Params |
|---------|--------|
| `SET_MANUFACTURER_MODE` | `{"status": true}` |
| `SET_MANUFACTURER_TEMPERATURE` | `{"targetTemperature": 180, "causedBy": "user"}` |
| `SET_MANUFACTURER_RESISTANCE` | `{"status": true, "causedBy": "user"}` |
| `SET_MANUFACTURER_STEAM_CREATION` | `{"status": true, "causedBy": "user"}` |
| `SET_MANUFACTURER_STEAM_OUTLET_VALVE` | `{"status": true, "causedBy": "user"}` |
| `SET_MANUFACTURER_TURBINE_DIRECTION` | `{"direction": "clockwise", "causedBy": "user"}` |
| `SET_MANUFACTURER_TURBINE_SPEED` | `{"speed": "low", "causedBy": "user"}` |
| `SET_MANUFACTURER_OVEN_LIGHT` | `{"status": true, "causedBy": "user"}` |
| `SET_MANUFACTURER_EXTRACTOR_FAN` | `{"status": true, "causedBy": "user"}` |
| `SET_MANUFACTURER_INTERNAL_BUZZER` | `{"status": true, "causedBy": "user"}` |
| `SET_MANUFACTURER_EXTERNAL_BUZZER` | `{"status": true, "causedBy": "user"}` |
| `SET_MANUFACTURER_WATER_PUMP` | `{"status": true, "causedBy": "user"}` |
| `SET_MANUFACTURER_DETERGENT_PUMP` | `{"status": true, "causedBy": "user"}` |
| `SET_MANUFACTURER_DISCHARGE_PUMP` | `{"status": true, "causedBy": "user"}` |
| `SET_MANUFACTURER_WATER_VALVE` | `{"status": true, "causedBy": "user"}` |
| `SET_MANUFACTURER_WASHING` | `{"status": true}` |

Recipe commands:

| Command | Params |
|---------|--------|
| `LOAD_RECIPE` | `{"id": "recipe-id", "causedBy": "user"}` or full recipe object |
| `START_RECIPE` | `{"causedBy": "user"}` |
| `LOAD_AND_START_RECIPE` | `{"id": "recipe-id", "causedBy": "user"}` or full recipe object |
| `PAUSE_RECIPE` | `{"causedBy": "user"}` |
| `RESUME_RECIPE` | `{"causedBy": "user"}` |
| `ABORT_RECIPE` | `{"causedBy": "user"}` |
| `CHANGE_RECIPE_PHASE_TEMPERATURE` | `{"temperature": 180, "causedBy": "user"}` |
| `CHANGE_RECIPE_PHASE_REMAINING_DURATION` | `{"remainingDuration": 300, "causedBy": "user"}` |
| `CHANGE_RECIPE_PHASE_DURATION` | `{"duration": 900, "causedBy": "user"}` |
| `CHANGE_RECIPE_PHASE_STEAM_INJECTION_NUMBER` | `{"steamInjectionNumber": 2, "causedBy": "user"}` |
| `CHANGE_RECIPE_PHASE_STEAM_EXIT_VALVE` | `{"status": true, "causedBy": "user"}` |
| `CHANGE_RECIPE_PHASE_TURBINE_SPEED` | `{"speed": "low", "causedBy": "user"}` |
| `ADD_RECIPE_PHASE` | `{"recipePhase": {...}, "causedBy": "user"}` |
| `REMOVE_RECIPE_PHASE` | `{"causedBy": "user"}` |

Washing commands:

| Command | Params |
|---------|--------|
| `LOAD_WASHING` | `{"id": 1, "causedBy": "user"}` |
| `START_WASHING` | `{"causedBy": "user"}` |
| `LOAD_AND_START_WASHING` | `{"id": 1, "causedBy": "user"}` |
| `PAUSE_WASHING` | `{"causedBy": "user"}` |
| `RESUME_WASHING` | `{"causedBy": "user"}` |
| `ABORT_WASHING` | `{"causedBy": "user"}` |
| `SET_WATER_PUMP` | `{"status": true, "causedBy": "user"}` |
| `SET_DETERGENT_PUMP` | `{"status": true, "causedBy": "user"}` |
| `SET_DISCHARGE_PUMP` | `{"status": true, "causedBy": "user"}` |
| `SET_WATER_VALVE` | `{"status": true, "causedBy": "user"}` |
| `SET_DETERGENT_PERCENTAGE` | `{"percentage": 50, "causedBy": "user"}` |

Washing program IDs:

| ID | Program |
|----|---------|
| `1` | Short |
| `2` | Normal |
| `3` | Long |
| `4` | Manual |
| `5` | Test |

Direct manufacturer commands bypass normal recipe sequencing and should be
limited to commissioning, test mode, or supervised service workflows.

## Notifications

Subscribe:

```text
+/+/+/+/notification
```

Known public notification IDs:

| ID | Meaning |
|----|---------|
| `1` | Turned on |
| `2` | Turned off |
| `3` | Started recipe |
| `4` | Finished recipe |
| `5` | Started washing |
| `6` | Finished washing |
| `7` | Started sync-in |
| `8` | Finished sync-in |
| `9` | Sync-in failed |
| `10` | Started app update |
| `11` | Finished app update |
| `12` | App update failed |
| `13` | Started overheating |
| `14` | Stopped overheating |
| `15` | Started turbine overheating |
| `16` | Stopped turbine overheating |
| `17` | Started power failure |
| `18` | Stopped power failure |
| `19` | Oven panel settings changed |
| `20` | Needs maintenance |
| `21` | Started PCB overheating |
| `22` | Stopped PCB overheating |
| `23` | Started thermocouple error |
| `24` | Stopped thermocouple error |
| `25` | Started thermocouple temperature measurement error |
| `26` | Stopped thermocouple temperature measurement error |
| `27` | Started thermocouple connection error |
| `28` | Stopped thermocouple connection error |
| `29` | Started thermocouple temperature measurement stuck error |
| `30` | Stopped thermocouple temperature measurement stuck error |
| `31` | Started forced cooling active |
| `32` | Stopped forced cooling active |
| `33` | Started thermocouple over/under voltage error |
| `34` | Stopped thermocouple over/under voltage error |

Internal notifications use IDs `10000` and above. OEM clients should ignore
unknown IDs unless the deployment contract explicitly documents them.

## External Cloud Bridge

The app also contains an AWS IoT bridge with a reduced external topic format:

```text
{companyId}/{bakeryId}/{ovenPanelId}/{channel}
```

The bridge forwards only a small command set:

```text
TURN_ON
TURN_OFF
TOGGLE_STATUS
LOCK
UNLOCK
START_SYNC_IN
```

It is not a complete bridge for local oven state or all oven-manager commands.
For OEM plant-floor integrations, use the local broker unless the commercial
deployment explicitly includes AWS IoT credentials and policy.

## Python Examples

Install dependency:

```bash
python3 -m pip install paho-mqtt
```

Discover IDs:

```bash
python3 docs/oem/examples/mqtt/discover_panel_identity.py --host 192.168.10.50
```

Subscribe to oven state:

```bash
python3 docs/oem/examples/mqtt/subscribe_oven_state.py --host 192.168.10.50
```

Send a read-only main-module request:

```bash
python3 docs/oem/examples/mqtt/mqtt_request.py \
  --host 192.168.10.50 \
  --company-id 9f6b7093-a4d0-4150-b65d-2149c9a449c1 \
  --bakery-id c68a401c-2465-49ef-8d2f-6eb9019af1ef \
  --panel-id 7c366bb0-f8b4-4b86-94a7-ea19173a8bdc \
  --module main \
  --command GET_ACTIVE_CONNECTION
```

Turn oven light on through the app-level oven manager:

```bash
python3 docs/oem/examples/mqtt/set_oven_light.py \
  --host 192.168.10.50 \
  --company-id 9f6b7093-a4d0-4150-b65d-2149c9a449c1 \
  --bakery-id c68a401c-2465-49ef-8d2f-6eb9019af1ef \
  --panel-id 7c366bb0-f8b4-4b86-94a7-ea19173a8bdc \
  --on
```

## Safety Notes

- Treat MQTT publish access as control-plane access to the oven app.
- Do not expose the broker on an untrusted network.
- Subscribe and verify state before publishing mutating commands.
- Use `ABORT_PROGRAMS` or app-supported stop flows rather than direct output
  overrides for operator stop behavior.
- Avoid manufacturer commands in normal automation. They are direct service
  controls and can conflict with recipe, washing, or safety logic.
- Validate all command workflows on a simulator or test oven before production.
