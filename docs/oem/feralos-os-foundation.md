# FeralOS OS Foundation - OEM Overview

FeralOS is the Debian-based embedded OS image used as the runtime foundation for
the FeralBoard/Ramalhos control panel. It is built for Raspberry Pi hardware and
packages the operating system, kiosk UI stack, local services, update scripts,
and hardware-access defaults needed by the panel application.

This document is a concise OEM evaluation overview. It explains the control
system foundation without disclosing application source, firmware source, or
manufacturing-only internals.

Source inspected: `https://github.com/Feral-Ramalhos/feralos`, commit
`511b4ffbb415126fd9d24ffc4a207bf4489a764b`.

## Image Base

| Area | Value |
|------|-------|
| OS family | Debian-based embedded OS image |
| Base image | Raspberry Pi OS Bookworm 64-bit Lite |
| Build system | CustomPiOS |
| Architecture | `arm64` |
| FeralOS version in config | `0.20.0` |
| Locale defaults | `pt_PT.UTF-8`, Portuguese keyboard layout |
| Timezone default | `UTC` |
| Main UI mode | Local kiosk browser pointed at the panel app |

The image is designed for appliance-style operation: boot, start local services,
launch the panel app, and present the UI in kiosk mode.

## Storage Model

FeralOS uses a three-partition layout:

| Partition | Purpose |
|-----------|---------|
| `boot` | Firmware and boot assets. |
| `root` | Base OS filesystem. |
| `data` | Persistent writable data partition. |

The image configures `overlayroot` with the `data` partition as the writable
upper layer. This keeps the base OS more resilient while still allowing runtime
state, databases, logs, updates, and configuration to persist.

Important behavior:

- Root filesystem changes are controlled through the overlay model.
- Persistent data is mounted from a partition labelled `data`.
- Swap file service is disabled by default to avoid conflicts with the
  read-mostly root setup.

## Startup Services

The image enables these core services during build:

| Service | Purpose |
|---------|---------|
| `NetworkManager` | Network configuration and Wi-Fi/Ethernet management. |
| `mosquitto.service` | Local MQTT broker for app and integration messaging. |
| `redis-server.service` | Local key-value runtime configuration store. |
| `postgresql` | Local relational database for panel data. |
| `sddm` | Display manager with autologin into the kiosk session. |
| `wayvnc.service` | Remote support VNC server on the Wayland session. |
| `splashscreen.service` | Boot splash screen display. |
| `setup_postgres.service` | First-boot PostgreSQL database/config setup. |
| `setup_ttyS0.service` | First-boot serial port permissions for FeralBoard comms. |
| `redis_default_keys.service` | First-boot Redis defaults for app paths and runtime flags. |
| `update_check.service` | Watches for panel app `.deb` updates. |
| `downgrade_check.service` | Supports controlled downgrade/rollback flow. |
| `boot_fix.service` | Boot-time cmdline, splash, boot count, and autologin fixes. |

The image also carries support service files for workflows such as GPG key
setup, hostname/DUID update, Wi-Fi reconnect, and optional X11 VNC, but the
table above is the important startup set for the standard image.

Services intentionally disabled or de-emphasized in the image include Bluetooth
serial support (`hciuart`), first-boot Raspberry Pi config helpers, the default
swap-file service, `ModemManager`, and `lightdm`. This keeps the device closer
to a deterministic control-panel appliance.

## Local Network Services

Default service exposure from the inspected image:

| Port | Service | Notes |
|------|---------|-------|
| `1883` | MQTT TCP | Mosquitto local broker. |
| `9001` | MQTT WebSocket | Used by browser/UI MQTT clients. |
| `5432` | PostgreSQL | Local app database; deployment network should restrict access. |
| `6379` | Redis | Bound to localhost by the provided Redis config. |
| `5900` | WayVNC | Remote support display access. |
| `3007` | Panel web app | Default kiosk URL points to `http://localhost:3007`. |

Mosquitto is configured with TCP and WebSocket listeners. The inspected image
sets anonymous MQTT access, so production deployments should restrict access at
the network, VPN, or firewall layer.

## Kiosk UI Stack

The OS boots into a local graphical kiosk session:

- `sddm` autologin starts the `pi` graphical session.
- Sway/Wayfire are included for the Wayland compositor layer.
- Chromium runs in kiosk/app mode.
- The default kiosk URL is stored in Redis as `KIOSK_MODE_URL` and points to
  `http://localhost:3007`.
- Display rotation, scaling, and touchscreen calibration are configured for the
  target panel displays.
- WayVNC is available for remote support.

The panel app is expected to run as `ramalhos-panel-app`; the Chromium startup
script checks that service and restarts it if needed before launching the UI.

## Installed Package Groups

Key packages and tools installed into the image:

| Group | Packages and purpose |
|-------|----------------------|
| Runtime | Node.js `20.5.0`, Chromium support, Redis, PostgreSQL, Mosquitto. |
| UI/kiosk | `sddm`, `sway`, `wayfire`, `wayvnc`, `alacritty`, `fbi`, `plymouth`, `xloadimage`. |
| Network | `NetworkManager`, `openvpn`, `avahi-daemon`, `mosquitto-clients`, `socat`. |
| Hardware/debug | `i2c-tools`, `libinput-tools`, `pymcuprog`, `xdotool`, `xterm`, `screen`. |
| DevOps/support | `git`, `vim`, `expect`, `sysbench`, `inotify-tools`, `debsigs`, `rpm`, `checkinstall`. |
| USB update | `usbmount` package plus scripts for USB `.deb` app updates. |

This is not intended to be a full software bill of materials. It is the
practical foundation an OEM team needs to understand what is present at startup.

## Runtime Configuration Defaults

Redis is used as the local runtime configuration store. First-boot defaults
include:

- Kiosk mode enabled.
- Kiosk URL pointing to the local app server.
- App name set to `ramalhos-panel-app`.
- Paths for logs, app versions, USB media, scripts, assets, and AWS IoT files.
- FeralBoard serial port defaults for controller communication.
- Local PostgreSQL connection settings.

Actual deployment credentials, certificates, and customer network settings
should be provisioned per installation and are not part of this public OEM
document.

## App Update Flow

The image includes a simple field update mechanism for the panel application:

- `update_check.service` watches the app versions directory and USB media.
- Update packages are expected as `ramalhos-panel-app_*.deb`.
- The latest valid package is installed with `dpkg`.
- The panel app service is restarted after install.
- If the running app does not report the expected version after restart, the
  script attempts rollback to the previous `.deb`.
- `downgrade_check.service` supports an explicit downgrade trigger through
  Redis state.

This keeps application update logic outside the firmware and preserves a clear
separation between OS image, app package, and FeralBoard firmware.

## Hardware Integration Defaults

The image prepares the board for appliance control:

- Serial console is moved away from the application serial port.
- `/dev/ttyS0` ownership and permissions are set for the `pi` user and
  `dialout` group.
- UART overlays are added for additional serial interfaces.
- I2C and RTC overlays are enabled.
- Bluetooth-related services/modules are disabled to reduce boot noise and
  free serial resources.
- FeralBoard app communication defaults to the configured serial port from
  Redis/environment.

## OEM Integration Notes

- Treat FeralOS as the control-panel appliance base, not as a general desktop
  Linux distribution.
- Keep customer applications talking to documented SDK, HTTP, or MQTT surfaces
  rather than relying on private scripts.
- Restrict MQTT, PostgreSQL, and VNC access to trusted networks or VPN.
- Use the app `.deb` update path for panel software and the SDK firmware update
  path for FeralBoard firmware.
- Keep persistent customer data on the writable data layer, not in assumptions
  about the base root filesystem.
