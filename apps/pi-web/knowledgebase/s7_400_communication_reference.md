# S7-400 Communication Reference

> Extracted from Siemens manuals: *S7-400 Hardware and Installation* (424ish_e.pdf) and *S7-400 Module Data* (module_data_en_en-US.pdf). Page references are PDF page numbers.

---

## Product Overview

The S7-400 is a high-end, legacy Siemens programmable logic controller (PLC) designed for large-scale automation tasks. It uses a modular rack-based architecture with swing-mounted modules.
(Source: 424ish_e.pdf, p13-16)

### Key System Components

| Component | Function |
|-----------|----------|
| Racks (UR/CR/ER) | Provide mechanical and electrical connections between S7-400 modules |
| Power Supply Modules (PS 405/407) | Convert line voltage (120/230 VAC or 24 VDC) to 5 VDC and 24 VDC operating voltages |
| CPUs | Execute user program; communicate via MPI with other CPUs or programming devices |
| Memory Cards | Store user program and parameters (RAM or Flash) |
| Signal Modules (SM) | Interface between PLC and process (digital/analog I/O) |
| Interface Modules (IM) | Interconnect individual racks of an S7-400 system |
| IF 964-DP | Connect distributed I/Os via PROFIBUS-DP |
| Communications Processors (CP) | Modules for point-to-point and bus connections (e.g., Ethernet, PROFIBUS) |

### CPU Models Referenced

- CPU 412-1
- CPU 413-1, CPU 413-2
- CPU 414-1, CPU 414-2 (with integrated DP interface), CPU 414-3
- CPU 416-1, CPU 416-3
- CPU 417-4, CPU 417-4H (H = high-availability)

(Source: 424ish_e.pdf, p15, p111, p146; module_data_en_en-US.pdf, p342-343)

---

## Communication Interfaces Overview

The S7-400 can connect to multiple subnet types:
(Source: 424ish_e.pdf, p50, p100)

- **MPI subnet** -- via the integrated MPI interface on the CPU
- **PROFIBUS DP subnet** -- via the integrated PROFIBUS-DP interface on certain CPUs, or via IM 467/IM 467 FO modules
- **PROFIBUS subnet** -- via SIMATIC NET CP PROFIBUS modules
- **Industrial Ethernet subnet** -- via SIMATIC NET CP Ethernet modules (e.g., CP 443-1)

---

## Communication Protocols

### MPI (Multi-Point Interface)

MPI is the native programming interface on every S7-400 CPU. It uses a SIMATIC S7-specific protocol for communication with programming devices (STEP 7), operator panels (OP/HMI), and other S7 CPUs. The bus structure corresponds to PROFIBUS.
(Source: 424ish_e.pdf, p100, p217)

**Key Parameters:**

| Parameter | Value |
|-----------|-------|
| Max. nodes | 127 (default: 32) |
| Baud rates | 19.2 kbps to 12 Mbps |
| Segment cable length | 50 m (all transmission rates) |
| Physical layer | RS 485 via 9-pin sub-D connector |
| Default PG address | 0 |
| Default OP address | 1 |
| Default CPU address | 2 |
| Default highest MPI address | 31 |

(Source: 424ish_e.pdf, p101-102, p113)

**Connectable Nodes via MPI:**
- Programming devices (PGs)
- Operator interfaces (SIMATIC OP, WinCC)
- S7-400 CPUs
- S7-300 CPUs

**MPI Address Rules:**
- All MPI addresses in a network must be unique
- The highest possible MPI address must be equal to or higher than the highest actual MPI address
- The highest MPI address must be set to the same value on all nodes
- Reserve address 0 for a service PG, address 1 for a service OP, address 2 for a new CPU
- MPI address and highest MPI address persist through memory reset, voltage failure, and CPU removal/reinsertion

(Source: 424ish_e.pdf, p102-103, p106, p137)

**PG Connection:**
Connect a programming device to the S7-400 via a PG cable to the MPI port on the CPU. This allows access via the communication bus to all CPUs and programmable modules. The CPU communicates with the PG in RUN, STOP, STARTUP, and HOLD modes.
(Source: 424ish_e.pdf, p133-134)

**Routing:**
PG access beyond network limits is possible using STEP 7 v5.0+ with routing-capable modules. A CPU with connections to multiple networks can bridge MPI, PROFIBUS-DP, and Ethernet subnets.
(Source: 424ish_e.pdf, p112)

---

### PROFIBUS DP

PROFIBUS DP (Decentralized Periphery) is the primary fieldbus protocol for the S7-400. It connects the CPU to distributed I/O devices, drives, valve terminals, and other field devices. Standardized per IEC 61784-1:2002 Ed1 CP 3/1 and EN 50170.
(Source: 424ish_e.pdf, p50, p100, p219; module_data_en_en-US.pdf, p363)

**Key Parameters:**

| Parameter | Value |
|-----------|-------|
| Max. nodes | 127 (1 master reserved, 1 PG port reserved, 125 slaves or other masters) |
| Baud rates | 9.6 kbps to 12 Mbps |
| Physical layer | RS 485 (copper) or fiber-optic cable |
| Max. segment length (copper) | 100 m to 1,000 m depending on baud rate |
| Max. segments in series | 10 (interconnected via RS 485 repeaters) |
| Max. nodes per segment | 32 |
| Default PG address | 0 (reserved for service PG) |

(Source: 424ish_e.pdf, p101-102, p105, p113)

**PROFIBUS DP Access Methods:**
- Built-in DP interface on CPUs such as CPU 414-2 DP, CPU 414-3, CPU 416-3, CPU 417-4
- IM 467 / IM 467 FO PROFIBUS DP master interface module (up to 4 per central rack)
- SIMATIC NET CP PROFIBUS modules

**Distributed I/O Slave Devices:**
- ET 200M
- ET 200S
- ET 200X
- ET 200eco
- All DP standard slaves (e.g., S5-95U, ET 200B, drives, valve modules)

(Source: 424ish_e.pdf, p50, p110)

**Starting Up a PROFIBUS-DP Subnet:**
1. Set up the PROFIBUS-DP subnet physically (Chapter 5)
2. Configure the subnet in STEP 7 and assign PROFIBUS-DP addresses and address areas to all nodes
3. Load the configuration from the PG into the CPU
4. Switch on all DP slaves
5. Switch the CPU from STOP to RUN
6. During startup, the CPU compares preset and actual configurations

(Source: 424ish_e.pdf, p145)

---

### Industrial Ethernet

Ethernet connectivity on the S7-400 requires optional Communication Processor modules. The manuals reference SIMATIC NET CP Ethernet modules (e.g., CP 443-1) for connecting to Industrial Ethernet subnets.
(Source: 424ish_e.pdf, p50, p100)

> **Note:** Detailed Ethernet CP module specifications are covered in separate SIMATIC NET manuals. The S7-400 hardware manual and module data manual focus on MPI and PROFIBUS DP as the primary communication protocols.

---

### Point-to-Point Communication

Point-to-point connections are handled by Communications Processor modules (CPs). The glossary defines CPs as modules for point-to-point and bus connections.
(Source: 424ish_e.pdf, p210)

> **Note:** CP 440/441 point-to-point modules are not detailed in these two manuals. Refer to separate SIMATIC NET CP manuals.

---

## Network Configuration

### Configuring a Network

The same bus components and configuration rules used for PROFIBUS DP networks are recommended for MPI network configurations.
(Source: 424ish_e.pdf, p100)

All CPU-related communication data is in the *Reference Manual CPU Data*. Address assignment is performed via the *Configuring Hardware and Communication Connections STEP 7* manual.

### Network Configuration Rules

(Source: 424ish_e.pdf, p105-112)

1. **Addressing:** Before interconnecting nodes, assign each node an MPI address (and highest MPI address) or PROFIBUS-DP address
2. **Power off before connecting:** Switch off supply voltage before inserting a new node in the network
3. **Linear topology:** Connect all nodes in a row; include fixed PGs and OPs directly in the network; use spur lines only for PGs/OPs needed during startup or maintenance
4. **Segment limit:** Max 32 nodes per segment; use RS 485 repeaters for more than 32 nodes
5. **Segment connectivity:** In a PROFIBUS-DP network, all segments together must have at least one DP master and one DP slave
6. **Grounded/ungrounded segments:** Connect grounded and ungrounded bus segments via RS 485 repeaters
7. **Repeater node count:** Each RS 485 repeater in a segment reduces the max other nodes in that segment to 31; up to 10 segments can be connected in series
8. **Terminating resistors:** Switch on the terminating resistor at the first and last node of every segment; ensure these nodes always have power applied

### Network Topologies

- **MPI network:** Linear bus topology with optional spur lines for PGs/OPs
- **PROFIBUS-DP network:** Linear bus topology (copper); partyline topology (fiber-optic)
- **Mixed MPI + PROFIBUS-DP:** A CPU with both interfaces (e.g., CPU 414-2 DP) can participate in both networks simultaneously with separate node numbering

(Source: 424ish_e.pdf, p108-111)

---

## Cable Specifications

### PROFIBUS-DP Copper Bus Cable

The PROFIBUS-DP bus cable is a twisted, shielded pair.
(Source: 424ish_e.pdf, p116)

| Characteristic | Value |
|----------------|-------|
| Impedance | 135 to 160 ohm (f = 3 to 20 MHz) |
| Loop resistance | <= 115 ohm/km |
| Working capacitance | 30 nF/km |
| Attenuation | 0.9 dB/100 m (f = 200 kHz) |
| Core cross-section | 0.3 to 0.5 mm2 |
| Cable diameter | 8 mm +/- 0.5 mm |
| Bending radius (single bend) | >= 80 mm (10x outer diameter) |
| Bending radius (repeated bends) | >= 160 mm (20x outer diameter) |
| Installation temperature range | -5 C to +50 C |
| Storage/operating temperature range | -30 C to +65 C |

**Available Cable Types:**

| Cable Type | Order Number |
|------------|-------------|
| PROFIBUS-DP bus cable | 6XV1830-0AH10 |
| PROFIBUS-DP cable for burying in ground | 6XV1830-3AH10 |
| PROFIBUS-DP trailing cable | 6XV1830-3BH10 |
| PROFIBUS-DP bus cable with PE sheath (food industry) | 6XV1830-0BH10 |
| PROFIBUS-DP bus cable festoons | 6XV1830-3CH10 |

### Maximum Copper Cable Lengths per Segment

(Source: 424ish_e.pdf, p113; module_data_en_en-US.pdf, p369, p388)

| Transmission Rate | MPI Segment (m) | PROFIBUS-DP Segment (m) |
|-------------------|-----------------|------------------------|
| 9.6 kbps | -- | 1,000 |
| 19.2 kbps | 50 | 1,000 |
| 93.75 kbps | -- | 1,000 |
| 187.5 kbps | 50 | 1,000 |
| 500 kbps | -- | 400 |
| 1.5 Mbps | -- | 200 |
| 3 Mbps | -- | 100 |
| 6 Mbps | -- | 100 |
| 12 Mbps | 50 | 100 |

### Maximum Total Cable Length with RS 485 Repeaters

Up to 10 segments can be connected in series via RS 485 repeaters. Maximum cable length between two RS 485 repeaters equals the segment length above.
(Source: module_data_en_en-US.pdf, p388)

| Transmission Rate | Max Total Length (m) |
|-------------------|---------------------|
| 9.6 to 187.5 kbps | 10,000 |
| 500 kbps | 4,000 |
| 1.5 Mbps | 2,000 |
| 3 to 12 Mbps | 1,000 |

### Spur Line Lengths

Spur lines connect PGs or OPs that are not directly on the main bus line. Not permissible at rates greater than 1.5 Mbps.
(Source: 424ish_e.pdf, p114)

| Transmission Rate | Max Spur Length | Max Nodes per Spur (1.5-1.6 m) | Max Nodes per Spur (3 m) | Max Total Spur per Segment |
|-------------------|----------------|-------------------------------|--------------------------|---------------------------|
| 9.6 to 93.75 kbps | 3 m | 32 | 32 | 96 m |
| 187.5 kbps | 3 m | 32 | 25 | 75 m |
| 500 kbps | 3 m | 20 | 10 | 30 m |
| 1.5 Mbps | 3 m | 6 | 3 | 10 m |

---

## Fiber-Optic PROFIBUS-DP Network

Fiber-optic cables provide electrical isolation, EMC insensitivity, no electromagnetic emission, and cable lengths independent of transmission rate.
(Source: 424ish_e.pdf, p120-128)

### Topology

Fiber-optic PROFIBUS-DP uses a **partyline topology**. Nodes are interconnected in pairs via duplex fiber-optic cables. Up to 32 PROFIBUS nodes with fiber-optic interfaces can be series-connected. Each bus node has repeater functionality.

> **Caution:** If a node fails in a partyline topology, all downstream DP slaves become inaccessible.

### Supported Transmission Rates (Fiber-Optic Partyline)

9.6 kbps, 19.2 kbps, 45.45 kbps, 93.75 kbps, 187.5 kbps, 500 kbps, 1.5 Mbps, 12 Mbps
(Source: 424ish_e.pdf, p121)

### Fiber-Optic Cable Types and Maximum Lengths

(Source: 424ish_e.pdf, p122-123, p126)

| Cable Type | Max Length Between Two Nodes | Max for 32-Node Network | Application |
|------------|----------------------------|------------------------|-------------|
| Plastic fiber-optic duplex conductor | 50 m | 1,550 m | Indoor, low mechanical load (lab, cabinets) |
| Plastic fiber-optic standard cable | 50 m | 1,550 m | Indoor applications |
| PCF fiber-optic standard cable | 300 m | 9,300 m | Indoor applications, longer distances |

**Mixed cable use** is supported: plastic fiber-optic for local connections (<50 m) and PCF fiber-optic for longer runs (>50 m).

### Fiber-Optic Cable Specifications

| Property | Plastic Duplex | Plastic Standard | PCF Standard |
|----------|---------------|-----------------|-------------|
| Core diameter | 980 um | 980 um | 200 um |
| Core material | PMMA | PMMA | Quartz glass |
| Attenuation | <= 230 dB/km at 660 nm | <= 230 dB/km at 660 nm | <= 10 dB/km at 660 nm |
| Min bend radius (single) | >= 30 mm | >= 100 mm | >= 75 mm |
| Min bend radius (repeated) | >= 50 mm | >= 150 mm | >= 75 mm |
| Operating temp | -30 to +70 C | -30 to +70 C | -20 to +70 C |
| Number of fibers | 2 | 2 | 2 |

### Electrical-to-Optical Conversion

Two methods:
1. **Optical Bus Terminal (OBT)** or **Optical Link Module (OLM):** Connects nodes with RS 485 interfaces to the optical network
2. **Integrated fiber-optic interface:** Devices like ET 200M (IM 153-2 FO) or S7-400 (IM 467 FO) connect directly to the optical network

(Source: 424ish_e.pdf, p120)

---

## Bus Connectors

Bus connectors connect the PROFIBUS-DP bus cable to MPI or PROFIBUS-DP interfaces. Available with or without PG connector.
(Source: 424ish_e.pdf, p117-118)

**Bus Connector Order Numbers:**

| Type | Order Numbers |
|------|--------------|
| Without PG connector | 6ES7972-0BA12-0XA0, 6ES7972-0BA41-0XA0, 6ES7972-0BA50-0XA0, 6ES7972-0BA60-0XA0, 6ES7972-0BA30-0XA0 |
| With PG connector | 6ES7972-0BB12-0XA0, 6ES7972-0BB41-0XA0, 6ES7972-0BB50-0XA0, 6ES7972-0BB60-0XA0 |

**Important:** A bus connector with a looped-through bus cable can be removed from the PROFIBUS-DP interface at any time without interrupting data traffic. The terminating resistor in a bus connector is powered by the station; stations with active terminating resistors must always be under power.

---

## RS 485 Repeater

The RS 485 repeater (6ES7972-0AA01-0XA0) amplifies data signals on bus lines and couples bus segments. Required when:
- More than 32 nodes are connected
- Grounded and ungrounded segments must be connected
- Maximum cable length of a segment is exceeded

(Source: 424ish_e.pdf, p119; module_data_en_en-US.pdf, p387-393)

### RS 485 Repeater Specifications

| Parameter | Value |
|-----------|-------|
| Dimensions (W x H x D) | 45 x 128 x 67 mm |
| Power supply | 24 VDC (20.4 to 28.8 VDC) |
| Current consumption (no PG/OP load) | 200 mA |
| Current consumption (PG/OP 5 V/90 mA) | 230 mA |
| Isolation | Yes, 500 VAC |
| Fiber-optic connection | Yes, via repeater adapters |
| Redundancy mode | No |
| Transmission rate | Auto-detected: 9.6 kbps to 12 Mbps |
| Max RS 485 repeaters in series | 9 |
| Degree of protection | IP 20 |
| Weight | 350 g |

### Key Design Features

- Bus segments 1 and 2 are electrically isolated
- PG/OP interface is internally connected to bus segment 1
- Signals are amplified between segment 1 and segment 2, and between PG/OP socket and segment 2
- Grounded operation: jumper terminals M and PE
- Ungrounded operation: do not connect M and PE; supply voltage must also be ungrounded

### Connector Pin Assignment (PG/OP Socket, 9-Pin Sub-D)

| Pin | Signal | Designation |
|-----|--------|-------------|
| 1 | -- | -- |
| 2 | M24V | Ground 24 V |
| 3 | RxD/TxD-P | Data line B |
| 4 | RTS | Request to send |
| 5 | M5V2 | Data reference potential |
| 6 | P5V2 | Supply plus |
| 7 | P24V | 24 V |
| 8 | RxD/TxD-N | Data line A |
| 9 | -- | -- |

---

## PROFIBUS DP Master Interface: IM 467 / IM 467 FO

The IM 467 and IM 467 FO are PROFIBUS DP master interface modules designed for the S7-400 central rack. They enable the S7-400 to connect to PROFIBUS DP for communication with distributed I/O and field devices.
(Source: module_data_en_en-US.pdf, p363-376)

### Variants

| Variant | Order Number | Connection Type |
|---------|-------------|----------------|
| IM 467 | 6ES7467-5GJ02-0AB0 | RS 485 (9-pin sub-D socket) |
| IM 467 FO | 6ES7467-5FJ00-0AB0 | Fiber-optic cable (2x duplex sockets, wavelength 660 nm) |

### Design Rules

- Maximum 4 IM 467/IM 467 FO modules per central rack; no slot rules
- The IM 467/IM 467 FO **cannot** be used together with the CP 443-5 Extended
- Transmission rate configurable from 9.6 kbps to 12 Mbps (IM 467 FO: 3 Mbps and 6 Mbps **not** approved)
- Can be operated without a fan
- Configuration and programming are possible via PROFIBUS DP (do not change DP parameters during operation)

### Communication Services

1. **PROFIBUS DP:** DP master per EN 50 170; configured entirely with STEP 7; no function calls required in user program for DP communication
2. **S7 Functions:** PG functions and operator control/monitoring via PROFIBUS DP; no additional configuration required; can run in parallel with DP (affects bus cycle time)

### IM 467 Specifications (Copper, 6ES7467-5GJ02-0AB0)

| Parameter | Value |
|-----------|-------|
| Dimensions (W x H x D) | 25 x 290 x 210 mm |
| Weight | 700 g |
| Standard | PROFIBUS DP, EN 50 170 |
| Transmission rate | 9.6 kbps to 12 Mbps (configurable) |
| Transmission technology | RS 485 via 9-pin sub-D socket |
| Supply voltage | 5 VDC via backplane bus |
| Current consumption (5 VDC) | 1.3 A |
| 24 VDC current | No consumption; voltage made available at MPI/DP interface (max 150 mA for connected components) |
| Addressing range | Max 4 KB inputs + 4 KB outputs |
| DP master | Yes |
| DPV1 support | No |
| Enable/disable | No |
| Max connectable slaves | 96 |
| S7 function connections | 32 + 1 diagnostic connection |
| Data volume per slave | Max 244 bytes |
| Consistency | Max 128 bytes |
| DP slave capability | No |
| Configuration software | STEP 7 |

### IM 467 FO Specifications (Fiber-Optic, 6ES7467-5FJ00-0AB0)

| Parameter | Value |
|-----------|-------|
| Dimensions (W x H x D) | 25 x 290 x 210 mm |
| Weight | 700 g |
| Standard | PROFIBUS DP, EN 50 170 |
| Transmission rate | 9.6 kbps to 12 Mbps (3 Mbps and 6 Mbps **not possible**) |
| Transmission technology | FOC, wavelength 660 nm, 2x duplex sockets |
| Supply voltage | 5 VDC via backplane bus |
| Current consumption (5 VDC) | 1.3 A |
| Addressing range | Max 4 KB inputs + 4 KB outputs |
| DP master | Yes |
| DPV1 support | No |
| Max connectable slaves | 96 |
| S7 function connections | 32 + 1 diagnostic connection |
| Data volume per slave | Max 244 bytes |
| Consistency | Max 128 bytes |
| DP slave capability | No |
| Configuration software | STEP 7 |

### IM 467 LED Indicators

| STOP (yellow) | RUN (green) | EXTF (red) | INTF (red) | Operating Mode |
|---------------|-------------|------------|------------|---------------|
| On | Flashing | Off | Off | Startup |
| Off | On | Off | Off | RUN |
| Flashing | On | Off | Off | STOPPING |
| On | Off | Off | Off | STOP |
| On | Off | Off | On | STOP with internal error (not configured) |
| Off | On | On | Off | RUN + PROFIBUS DP bus fault |
| Off | On | Flashing | Off | RUN + faults on DP line (slave not participating or module fault) |
| Flashing | Flashing | Flashing | Flashing | Module error / system error |

(Source: module_data_en_en-US.pdf, p366)

### IM 467 Connector Pin Assignment (9-Pin Sub-D)

| Pin | Signal | Designation | RS 485 |
|-----|--------|-------------|--------|
| 1 | PE | Protective earth | Yes |
| 2 | -- | -- | -- |
| 3 | RxD/TxD-P | Data transfer line B | Yes |
| 4 | RTS (AG) | Control A | -- |
| 5 | M5V2 | Data reference potential | Yes |
| 6 | P5V2 | Supply plus | Yes |
| 7 | BATT | -- | -- |
| 8 | RxD/TxD-N | Data transfer line A | Yes |
| 9 | -- | -- | -- |

(Source: module_data_en_en-US.pdf, p370)

### IM 467 FO Fiber-Optic Connection

Required accessories:
- Simplex connectors and polishing set (6GK1901-0FB00-0AA0)
- Plug-in adapters (6ES7195-1BE00-0XA0)

Installation notes:
- Transmitter plugs into receiver socket; receiver plugs into transmitter socket
- If the IM 467 FO is the last node, close the unoccupied fiber-optic interface with blanking plugs
- Minimum bending radius for fiber-optic cable: 30 mm
- Do not look directly into optical sender diodes

(Source: module_data_en_en-US.pdf, p372-374)

### Configuration

- Configured with STEP 7 v5.00 or higher
- Configuration data retained through power failure (no memory module required)
- Configuration stored in the load memory of the CPU (battery backup or EPROM)
- Module replacement does not require explicit reload of configuration data
- In multiprocessor operation, connected DP slaves can only be assigned to and processed by one CPU
- Configuration and diagnostics via MPI cannot run simultaneously

(Source: module_data_en_en-US.pdf, p368)

### IM 467 Maximum Cable Lengths (Copper)

| Speed (kbps) | 9.6 | 19.2 | 93.75 | 187.5 | 500 | 1,500 | 3,000 | 6,000 | 12,000 |
|-------------|-----|------|-------|-------|-----|-------|-------|-------|--------|
| Max segment (m) | 1,000 | 1,000 | 1,000 | 1,000 | 400 | 200 | 100 | 100 | 100 |
| Max segments | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 |
| Max total (m) | 10,000 | 10,000 | 10,000 | 10,000 | 4,000 | 2,000 | 1,000 | 1,000 | 1,000 |

(Source: module_data_en_en-US.pdf, p369)

---

## Interface Modules for Rack Expansion

Interface modules connect Central Racks (CR) to Expansion Racks (ER). These are used in send/receive pairs.
(Source: module_data_en_en-US.pdf, p325-343)

### Interface Module Summary

| Send IM | Receive IM | Connection Type | Max Distance | Max ERs per Line | 5V Transfer | Comm. Bus |
|---------|-----------|----------------|-------------|------------------|-------------|-----------|
| IM 460-0 | IM 461-0 | Local | 5 m | 4 | No | Yes |
| IM 460-1 | IM 461-1 | Local | 1.5 m | 1 | Yes (5A) | No |
| IM 460-3 | IM 461-3 | Remote | 102.25 m | 4 | No | Yes |
| IM 460-4 | IM 461-4 | Remote | 605 m | 4 | No | No |

### Expansion Rules

- Max 21 ERs connected to one CR
- Max 6 send IMs per CR (max 2 with 5V transfer)
- Each send IM line: up to 4 ERs (without 5V transfer) or 1 ER (with 5V transfer)
- Communication bus exchange limited to 7 racks (CR + ER numbers 1-6)
- Last ER in a line must have a terminator in the lower front connector of the receive IM

---

## I/O Module Addressing

(Source: 424ish_e.pdf, p53-60)

### Address Types

- **Geographical address:** Determined by physical location: rack number (0-21), slot number (1-18 or 1-9), channel number (0-31)
- **Logical address:** Freely selectable; used in the program; assigned via STEP 7

### Default Address Formulas

Default addressing applies when: no multicomputing, only signal modules inserted (no IM/CP/FM), modules at default settings, modules inserted in STOP or power-off state.

**Digital modules:**
```
Default address = (slot number - 1) x 4
```
Range: 0 (slot 1) to 68 (slot 18)

**Analog modules:**
```
Default address = (slot number - 1) x 64 + 512
```
Range: 512 (slot 1) to 1,600 (slot 18)

### Channel Addressing

- **Digital channels:** Addressed bit-wise. A 32-input digital module uses 4 bytes from the default address (e.g., slot 12 = address 44, channels I 44.0 through I 47.7)
- **Analog channels:** Addressed word-wise. An 8-channel analog module uses 8 words from the default address (e.g., slot 6 = address 832, channels QW 832 through QW 846)

---

## Connection Parameters Summary

### MPI Settings

| Parameter | Default | Notes |
|-----------|---------|-------|
| PG address | 0 | Reserved for service PG |
| OP address | 1 | Reserved for service OP |
| CPU address | 2 | Reserved for replacement CPU |
| Highest MPI address | 31 | Must match across all nodes |
| Transmission rate | 187.5 kbps | Typical default; persists through reset |

### PROFIBUS Addressing

| Parameter | Default | Notes |
|-----------|---------|-------|
| PG address | 0 | Reserved for service PG |
| Address range | 0-126 | 127 addresses total |
| Masters | At least 1 required across all segments |
| Slaves | Address set in STEP 7 config + hardware switches on some slaves |

### Maximum Connections

The maximum number of connections via MPI varies by CPU model. Process communication (PLC-PLC and PLC-OS/OP) has priority over PG communication. When communication resources are fully occupied by process communication, PG access may be severely hampered.

For IM 467: 32 S7 function connections + 1 diagnostic connection per module.
(Source: 424ish_e.pdf, p103-104; module_data_en_en-US.pdf, p375)

---

## Surge Protection for Networked PLCs

For networked S7-400 PLCs across lightning protection zones, the following protection components are recommended at each transition boundary:
(Source: 424ish_e.pdf, p196-197)

| Component | Purpose | Transition |
|-----------|---------|-----------|
| Lightning arrestor (DEHNbloc) | High-voltage protection against direct strike and surge | Zone 0 to 1 |
| Surge arrestor (DEHNguard 275) | High-voltage surge protection | Zone 1 to 2 |
| Blitzductor CT type MD/HF | Low-voltage surge protection for RS 485 interfaces | Zone 1 to 2 |
| FDK 2 D modules | Low-voltage surge protection for digital/analog I/O | Zone 1 to 2 |
| Shield mounting with EMC spring clamp | Interference current discharge | All transitions |
| Equipotential bonding cable (16 mm2) | Reference potential equalization | All transitions |

---

## Interference-Free Configuration

(Source: 424ish_e.pdf, p75-76)

### Local Connections
No special shielding/grounding required when using approved interface modules. Requirements:
- All racks must have low-impedance connections to each other
- Grounded arrangements must use star grounding
- Rack contact springs must be clean and unbent

### Remote Connections
Normally no special shielding needed. In high-interference environments:
- Connect cable shields to shield bus immediately after cabinet entry
- Maximize braided shield contact area (use metal hose clamps)
- Connect shield bus to frame/cabinet wall and chassis ground
- If potential difference between grounding points exceeds limits, install equipotential bonding conductor (copper, >= 16 mm2 cross-section)

---

## Protocol Support Summary

| Protocol | Supported | Interface | Default Speed | Max Speed | Notes |
|----------|-----------|-----------|--------------|-----------|-------|
| MPI | Yes (built-in) | 9-pin sub-D on CPU | 187.5 kbps | 12 Mbps | Every S7-400 CPU; SIMATIC S7-specific protocol |
| PROFIBUS DP | Yes (built-in on some CPUs, or via IM 467) | 9-pin sub-D (RS 485) or fiber-optic | 1.5 Mbps | 12 Mbps | Primary fieldbus; EN 50 170 / IEC 61784-1 |
| Industrial Ethernet | Optional (CP modules) | RJ45 / fiber via CP 443-x | 10 Mbps | 100 Mbps | Requires separate CP module and SIMATIC NET software |
| Point-to-Point | Optional (CP modules) | Serial via CP 440/441 | Varies | Varies | Separate manual; not covered in these documents |
| S7 Communication | Yes (via MPI/DP) | MPI or PROFIBUS DP | -- | -- | PG functions, monitoring, cross-network routing |

---

## Glossary of Communication Terms

(Source: 424ish_e.pdf, p209-224; module_data_en_en-US.pdf, p441+)

- **MPI (Multipoint Interface):** Programming device interface in SIMATIC S7; enables simultaneous operation of multiple nodes (PGs, OPs, CPUs); each node identified by MPI address
- **PROFIBUS DP:** Fieldbus protocol per EN 50 170, Part 3; connects CPUs to distributed I/O across distances up to 23 km; modules addressed the same as local I/O
- **DP Master:** EN 50 170-compliant master that interconnects CPU and distributed I/O; exchanges data via PROFIBUS DP
- **DP Slave:** Device operated on PROFIBUS with DP protocol; prepares local encoder/actuator data for transfer to CPU
- **DPV1:** Enhancement of distributed I/O per IEC 61158; adds acyclic services and interrupt functions (not supported by IM 467)
- **CP (Communications Processor):** Module for point-to-point and bus connections
- **Segment:** Bus cable between two terminating resistors; max 32 nodes per segment
- **Terminating Resistor:** Terminates data transfer lines to avoid reflections on the bus
- **Node:** Any station connected to a network (CPU, PG, OP, slave, repeater)
- **RS 485:** Electrical signaling standard used by MPI and PROFIBUS DP copper connections
