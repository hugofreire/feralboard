# FeralBoard OEM Documentation

Customer-facing evaluation documents for FeralBoard hardware and SDK packages.

## Documents

- `feralboard-device-sdk.md` - generic device SDK for board I/O, firmware HEX
  deploy, network, time, VPN, services, diagnostics, and identity.
- `feralboard-oven-simulator.md` - optional oven-domain simulator package for
  software-in-the-loop oven-control development.
- `ramalhos-mqtt-integration.md` - MQTT contract used by the Ramalhos oven
  panel app for OEM state monitoring and controlled command publishing.

## Package Positioning

```text
feralboard-sdk       Generic FeralBoard Device SDK
feralboard-oven      Optional oven simulator and oven-domain tooling
ramalhos-panel-mqtt  App-level MQTT integration for the Ramalhos oven panel
```

The Device SDK is the core OEM integration surface. The Oven Simulator is an
optional companion for oven customers who want realistic application development
before hardware-in-the-loop testing. The Ramalhos MQTT integration is for
customers that will use the existing oven panel application directly and need to
connect their own supervisory software to the app-level broker.
