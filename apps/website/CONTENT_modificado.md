# FeralBoard AIO-500 — Product Datasheet v1.1

> **This file is the single source of truth for all webpage content.**
> Edit sections here, then update `src/data/product.ts` and the corresponding
> component in `src/components/landing/` to match.

---

## HERO

- **Brand:** FERALBYTE
- **Logo mark:** FB
- **Doc type label:** Product Datasheet
- **Product name:** FeralBoard AIO-500
- **Revision line:** ALL-IN-ONE HMI + PLC CONTROLLER · HW REV V5 · DS REV 1.1
- **Subtitle:** Embedded industrial controller combining a 7″ HMI touchscreen with a high-density I/O PLC engine, optically isolated inputs, RS-485 communication (with galvanic isolatation or not), and cloud connectivity.

> Component: `src/components/landing/Hero.tsx`

---

## HIGHLIGHTS BAR

| Value | Label |
|-------|-------|
| 4× | TC Channels |
| 24 | Relay Outputs |
| 16 | Isolated Inputs |
| 4× | PWM Outputs |
| 3× | SSR Outputs |
| 1× | RS-485 Port |
| 1× | DAC Output |

> Component: `src/components/landing/Highlights.tsx`
> Data: `product.ts → highlights`

---

## PRODUCT OVERVIEW

The **FeralBoard AIO-500** is an integrated HMI+PLC platform for industrial process control, automation, and monitoring. It combines a real-time I/O controller (`ATMEGA4809-AFR`) with an embedded Linux-based HMI panel, MQTT-based communication, and a cloud management portal. The controller features a multi-rail on-board power supply accepting AC mains via an integrated transformer, with regulated 24V / 12V / 5V / 3.3V rails. A `HT1232ARZ` hardware watchdog supervisor ensures reliable unattended operation.

### Application Tags

- Thermal Process Control
- HVAC Systems
- Packaging Machinery
- Conveyor & Handling
- Environmental Chambers
- Food Processing
- Water Treatment
- Custom OEM

> Component: `src/components/landing/Overview.tsx`
> Data: `product.ts → applicationTags`

---

## PLC ENGINE — DIGITAL OUTPUTS

### PWM Outputs (2× H-Bridge)

- 2 PWM outputs (24VDC maximum) via `TB67H451AFNG,EL` H-bridge drivers
- Allows for independent control of 2 DC motors with variable speed and direction

### DAC Output (1x))

- Analog speed ref via `MCP4725A0T-E/CH` 12-bit DAC (10 levels) + `OPA192IDR` conditioning (0-10V)

### SSR Outputs (3×)

- 3× solid-state relay drive: `SSR_A` `SSR_B` `SSR_C`
- Driven via `BXT420N03M` MOSFETs
- Firmware PWM available (1 Hz, duty 0–100%) for proportional control

### Indicator & Alert Outputs

- On-board status LEDs (Red / Blue)
- Internal piezo buzzer (`CPI-148-24-90T-67`) — vol 0–255, patterns: single → quintuple, interval & continuous

### Latched Relay Bank (24×)

- 3× `TPIC6C595DG4` cascaded shift registers driving 24× `HF49FD/024-1H12T` relays
- 4× common bus sections with independent power feeds
- Switches relays, contactors, solenoids, fans, horns, valves, indicators
- Fused/protected wiring to screw terminal connectors

> Component: `src/components/landing/DigitalOutputs.tsx`
> Data: `product.ts → motorControlSpecs, ssrOutputSpecs, indicatorSpecs, relayBankSpecs`

---

## PLC ENGINE — INPUTS & SENSING

| Function | Details |
|----------|---------|
| **Digital Inputs (16×)** `[Isolated]` | 16-ch via `CD74HCT4067M` analog MUX. Front-end: 4× `TLP293-4(GBTPR,E` quad optocouplers (galvanic isolation). 4 groups × 4 inputs (IN0–IN3), each with independent common (COM-0 … COM-3). ESD/TVS protected. |
| **Thermocouple (4×)** | `MAX31856MUD+T` SPI converter via `CD74HC4052PWR` 4-ch TC MUX. 1 primary + 3 auxiliary channels. DRDY & FAULT monitored. K/J/T/N/E/R/S/B types. Level-shifted via `TXS0108EPWR` (5V ↔ 3.3V). |
| **Board Temperature** | Firmware-reported internal PCB ambient temperature. |

> Component: `src/components/landing/InputsSensing.tsx`
> Data: `product.ts → inputRows`

---

## FIRMWARE & PLC RUNTIME

- CRC-8 framed serial protocol for reliable host ↔ controller comms
- Persistent EEPROM configuration (survives power cycles)
- Configurable I/O mapping and threshold parameters
- Real-time fault/status telemetry — continuous health reporting
- Hardware watchdog supervisor (`HT1232ARZ`) for unattended reliability
- UPDI programming interface

> Component: `src/components/landing/FirmwareRuntime.tsx`
> Data: `product.ts → firmwareLeft, firmwareRight`

---

## COMMUNICATION INTERFACES

### RS-485

- The same communication bus is used between the microcontroller and both RS-485 ICs which means they cannot be used at the same time

#### RS-485 `[Galvanic Isolated]`

- **IC:** `ISO3088DWR`
- **Isolation:** `R1SE-0505` isolated DC-DC
- **Speed:** 9600 bps (default)
- Half-duplex, DE control, multi-drop

#### RS-485 `[Not Isolated]`

- **IC:** `ST485EBDR`
- **Isolation:** Non-isolated
- **Speed:** 9600 bps (default)
- Half-duplex, standard RS-485

### UART · I²C · SPI

#### UART × 2

- **UART0** (Debug) — Up to 921600 bps
- **UART1** (Aux) — 9600 bps default

#### I²C Bus

- On-board `MCP4725A0T-E/CH` DAC
- Extensible for sensors, displays, EEPROM

#### SPI Bus

- On-board `MAX31856MUD+T` via `TXS0108EPWR`
- 3× `TPIC6C595DG4` shift-reg latch

> Component: `src/components/landing/CommInterfaces.tsx`
> Data: `product.ts → rs485Ports, commCards`

---

## ON-BOARD POWER SUPPLY

| Rail | Regulator IC | Notes |
|------|-------------|-------|
| 24VAC Input | Needs to be regulated by external transformer | `744290103` Common mode chocke | Varistor + TVS protected input stage |
| 24VDC | `LMR51430XDDCR` buck | Main bus for relays & PWM drivers |
| 12VDC | `LMR51430XDDCR` buck | Supplementary loads & 12V relays (if used) |
| 5VDC | `LMR51450SDRRR` buck | MCU, peripherals, dedicated RPi supply |
| 3.3VDC | `K7803M-1000R3` buck | MAX31856MUD+T, TXS0108EPWR level shifters |
| Isolated 5VDC | `R1SE-0505` isolated DC-DC | Galvanic isolation domain for RS-485 |

> Component: `src/components/landing/PowerSupply.tsx`
> Data: `product.ts → powerRails`

---

## MICROCONTROLLER

### MCU Core

- **IC:** `ATMEGA4809-AFR`
- **Package:** TQFP-48
- **UART Ports:** 3× (UART0, UART1, UART3→RS-485)
- **Programming:** UPDI interface

### Supervisory

- **Watchdog:** `HT1232ARZ` external supervisor
- **Reset:** Dedicated RESET-PIN line
- **Protection:** ESD/TVS on all I/O buses
- **Connector:** 2× JST-NSH (3 & 6 pin)

> Component: `src/components/landing/Microcontroller.tsx`
> Data: `product.ts → mcuCore, mcuSupervisory`

---

## SYSTEM ARCHITECTURE

```
[AC Mains → On-Board PSU]  --24V/12V/5V/3.3V-->  [AIO-500 PLC Engine]  --RS-485/UART/MQTT-->  [HMI Touch Panel]  --HTTPS/VPN/OTA-->  [Cloud Portal & Web Access]
                                                      ATmega4809                               Raspberry Pi 4B                              Remote Config
```

> Component: `src/components/landing/SystemArchitecture.tsx`
> Data: `product.ts → archNodes, archArrows`

---

## HMI TOUCHSCREEN PANEL

### `[HMI]` 7″ Capacitive Touchscreen — Debian-Based Kiosk System

- **SBC:** Raspberry Pi 4B + RTC module
- **Display:** 7″ capacitive touchscreen
- **OS:** Debian-based Linux, kiosk mode
- **Vision:** Camera with YOLOv11 object detection
- **Protocol:** MQTT broker — full bidirectional I/O control
- **Telemetry:** Real-time data acquisition & logging
- **Remote:** VNC server for remote desktop access
- **Updates:** OTA — software + firmware over-the-air

### `[Hardware]` Raspberry Pi 4B — Connectivity & I/O

- **Ethernet:** Gigabit Ethernet (RJ45) — primary network / cloud uplink
- **USB:** 2× USB 3.0 + 2× USB 2.0 — peripherals, storage, pen updates
- **GPIO:** 40-pin header — spare I/O, 1-Wire sensors, additional SPI/I²C/UART
- **Wi-Fi:** 802.11ac dual-band (2.4 / 5 GHz) — wireless connectivity
- **Bluetooth:** Bluetooth 5.0 + BLE — wireless peripherals & beacons
- **Camera (CSI):** MIPI CSI-2 port — YOLOv11 vision pipeline input
- **Display (DSI):** MIPI DSI port — 7″ capacitive touchscreen interface
- **Storage:** microSD slot — OS, application data, local logging

> Component: `src/components/landing/HMIPanel.tsx`
> Data: `product.ts → hmiItems, hmiHardwareItems`

---

## CLOUD & REMOTE MANAGEMENT

### `[Cloud]` Remote Configuration & Monitoring Portal

- **Web Portal:** Browser-based access to edit SBC configuration, application logic, and parameters remotely
- **Telemetry Dashboard:** Cloud-hosted monitoring of process data, alarms, and device health
- **Pen Updates:** USB-based offline update capability for field deployments without network access

> Component: `src/components/landing/CloudRemote.tsx`
> Data: `product.ts → cloudItems`

---

## FEATURES (Summary Cards)

| Icon | Title | Description |
|------|-------|-------------|
| Cpu | ATMEGA4809-AFR PLC Engine | Real-time I/O controller with CRC-8 protocol, EEPROM persistence, and HT1232ARZ hardware watchdog. |
| Zap | High-Density I/O | 24 relay outputs, 16 isolated inputs, 3 SSR drives, 2 H-bridge controllers — all in a single board. |
| ThermometerSun | 4-Channel Thermocouple | MAX31856MUD+T SPI converter supporting K/J/T/N/E/R/S/B types with fault monitoring. |
| Wifi | RS-485 + Cloud | One galvanically isolated port (ISO3088DWR), MQTT protocol, and remote cloud management portal. |
| Monitor | 7″ HMI Touchscreen | Raspberry Pi 4B powered capacitive display with Debian kiosk, YOLOv11 vision, and OTA updates. |
| Shield | Industrial-Grade Power | 24VAC mains input from external transformer with regulated 24V / 12V / 5V / 3.3V rails, TVS protected. |

> Component: `src/components/landing/Features.tsx`
> Data: `product.ts → featureCards`

---

## APPLICATIONS

Tags: Thermal Process Control, HVAC Systems, Packaging Machinery, Conveyor & Handling, Environmental Chambers, Food Processing, Water Treatment, Custom OEM

> Component: `src/components/landing/Applications.tsx`
> Data: `product.ts → applicationTags`

---

## SPECIFICATIONS & ORDERING

| Spec | Value |
|------|-------|
| Model | AIO-500-V5 |
| Input Voltage | 24VAC via external transformer |
| Internal Rails | 24V / 12V / 5V / 3.3V (all regulated) + isolated 5V domain |
| Operating Temp | 0 °C to +50 °C |
| Digital Outputs | 24× latched relay (`HF49FD/024-1H12T`) + 3× SSR + 2× H-bridge |
| Digital Inputs | 16× optically isolated (`TLP293-4(GBTPR,E`) |
| Analog Inputs | 4× thermocouple (`MAX31856MUD+T`, types K/J/T/N/E/R/S/B) + PCB temp |
| Communication | RS-485 (1 isolated + 1 not isolated) + 2× UART + I²C + SPI |
| MCU | `ATMEGA4809-AFR` + `HT1232ARZ` hardware watchdog |
| HMI | 7″ capacitive touch, Raspberry Pi 4B, Debian Linux, MQTT |
| Enclosure Rating | TBD |
| Certifications | CE (pending) — designed with EMC best practices |

> Component: `src/components/landing/Specs.tsx`
> Data: `product.ts → specifications`

---

## I/O SUMMARY AT A GLANCE

### Outputs

| Count | Description |
|-------|-------------|
| 24× | Latched relay outputs (HF49FD) |
| 3× | SSR drive outputs (MOSFET) |
| 2× | Bidirectional H-bridge motors |
| 1× | DAC analog output (12-bit) |
| 1× | Piezo buzzer (programmable) |
| 2× | Status LEDs (Red / Blue) |

### Inputs

| Count | Description |
|-------|-------------|
| 16× | Optically isolated digital (24V) |
| 4× | Thermocouple channels |
| 1× | PCB ambient temperature |

> Component: `src/components/landing/IOSummary.tsx`
> Data: `product.ts → ioOutputs, ioInputs`

---

## NOTE BOX

**DS Rev 1.1 — Grounded in hardware schematic (KiCad v9, PlacaControlo_v9).** All I/O counts, IC references, and interface claims verified against actual board design. Contact Feralbyte for custom I/O configurations and OEM integration options.

> Component: `src/components/landing/NoteBox.tsx`

---

## BOARD BASE ASSEMBLY

- 12V RAIL IS NOT SOLDERED, ONLY 24V AND 5V
- 10 SOLDERED output RELAYS THAT CAN BE EXPANDED TO 24
- 4 AC INPUTS AND 4 DC INPUTS THAT CAN BE EXPANDED TO 16
- 1 THERMOCOUPLE CHANNEL THAT CAN BE EXPANdED TO 4
- SSR OUTPUTS ARE NOT SOLDERED
- DAC ANALOG OUTPUT IS NOT SOLDERED
- RS485 WITH GALVANIC ISOLATION IS NOT SOLDERED
- K7803M-1000R3 IS NOT SOLDERED | +3V3 COMES FROM RASPBERRY REGULATOR


## FOOTER

- **Logo:** FB / FERALBYTE
- **Text:** Feralbyte Lda. — DS-AIO500-V5 R1.1

> Component: `src/components/landing/Footer.tsx`

---

## PAGE SECTION ORDER

```
1.  Hero                    (id="hero")
2.  Navbar                  (sticky)
3.  Highlights              (id="highlights")
4.  Overview                (id="overview")
5.  Digital Outputs         (id="outputs")
6.  Inputs & Sensing        (id="inputs")
7.  Firmware Runtime        (id="firmware")
8.  Comm Interfaces         (id="comm")
9.  Power Supply            (id="power")
10. Microcontroller         (id="mcu")
11. System Architecture     (id="architecture")
12. HMI Panel               (id="hmi")
13. Cloud & Remote           (id="cloud")
14. Features                (id="features")
15. Applications            (id="applications")
16. Specs                   (id="specs")
17. I/O Summary             (id="io-summary")
18. Note Box                (no nav link)
19. Footer                  (id="contact")
```

---

## IC PART NUMBER INDEX

| IC | Used In | Purpose |
|----|---------|---------|
| ATmega4809 | MCU Core | Main PLC microcontroller (TQFP-48) |
| MAX1232 | Supervisory | Hardware watchdog supervisor |
| TB67H451AFNG | Motor Control | H-bridge motor driver |
| MCP4725 | Motor Control / I²C | 12-bit DAC for analog speed ref |
| OPA192 | Motor Control | DAC output conditioning |
| NTR4170N | SSR Outputs | MOSFET SSR drivers |
| CEM-1212S | Indicators | Piezo buzzer |
| TPIC6C595 | Relay Bank / SPI | Cascaded shift registers (×3) |
| HF49FD | Relay Bank | Latched relays (×24) |
| CD74HCT4067 | Digital Inputs | 16-ch analog MUX |
| TLP29X-4 | Digital Inputs | Quad optocouplers (×4) |
| MAX31856 | Thermocouple / SPI | SPI thermocouple converter |
| CD74HCX4052 | Thermocouple | 4-ch TC MUX |
| TXS0108E | Thermocouple / SPI | 5V ↔ 3.3V level shifter |
| ISO3082 | RS-485 Port 1 | Isolated RS-485 transceiver |
| R1SE | RS-485 Port 1 / Power | Isolated DC-DC converter |
| MAX485 | RS-485 Port 2 | Non-isolated RS-485 transceiver |
| CPI-148-24-90T-67 | Power Supply | AC mains transformer |
| LMR51420/30 | Power Supply | 12V buck regulator (×2) |
| LMR51440/50 | Power Supply | 5V buck regulator |
| TSR-1E | Power Supply | 5V DC-DC for RPi (×2) |
| LMR544XX | Power Supply | 3.3V buck regulator |
