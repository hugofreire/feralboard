# S7-1200 G2 Communication Reference

> Extracted from: _S7-1200 G2 Programmable Logic Controller System Manual, V1.0 01/2025_ (A5E52923928-AA, 357 pages) and _Update to the S7-1200 G2 System Manual_ (A5E54421713-AA, 08/2025).

---

## Product Overview

The S7-1200 G2 PLC family is Generation 2 of the S7-1200, offering a significantly narrower footprint than the first generation. All CPUs include a built-in PROFINET interface with two switched ports (one interface) and support up to 3 communication modules (CMs). (p.17)

### CPU Models

| CPU Model | Article Numbers | Dimensions (W x H x D) | Work Memory (Program / Data) | Digital I/O | SB/CB Slots | SM+CM Max |
| --- | --- | --- | --- | --- | --- | --- |
| CPU 1212C | 6ES7212-1BG50 (AC/DC/Relay), 6ES7212-1HG50 (DC/DC/Relay), 6ES7212-1AG50 (DC/DC/DC) | 70 x 125 x 100 mm | 150 KB / 500 KB | 8 DI / 6 DQ | 1 | 6 |
| CPU 1212FC | 6ES7212-1HF50 (DC/DC/Relay), 6ES7212-1AF50 (DC/DC/DC) | 70 x 125 x 100 mm | 200 KB / 500 KB | 8 DI / 6 DQ | 1 | 6 |
| CPU 1214C | 6ES7214-1BH50 (AC/DC/Relay), 6ES7214-1HH50 (DC/DC/Relay), 6ES7214-1AH50 (DC/DC/DC) | 80 x 125 x 100 mm | 250 KB / 750 KB | 14 DI / 10 DQ | 2 | 10 |
| CPU 1214FC | 6ES7214-1HF50 (DC/DC/Relay), 6ES7214-1AF50 (DC/DC/DC) | 80 x 125 x 100 mm | 300 KB / 750 KB | 14 DI / 10 DQ | 2 | 10 |

FC variants add fail-safe (safety) capability with SIL 3 / PL e ratings. (p.251, p.274)

**Common to all models:**
- 8 MB internal load memory; up to 32 GB via SIMATIC SD card (p.240, p.263)
- 20 KB retentive memory (p.240, p.263)
- 1024 bytes process image inputs (I) / 1024 bytes process image outputs (Q) (p.240, p.263)
- 8192 bytes bit memory (M) (p.240)
- Firmware version: V1.0 (01/2025) (p.1)
- PROFINET interface: 2 switched ports (RJ-45), 100 Mb/s, CAT5e shielded cable (p.243, p.266)
- No built-in analog I/O (available via optional SBs/SMs) (p.340)

### Communication Interfaces

- **PROFINET:** 1 interface, 2 switched ports (all CPU models) (p.341)
- **Communication Modules (CMs):** Up to 3 CMs supported, adding RS232/422/485 connectivity. CMs connect to the right side of the CPU. (p.19)
- **Communication Boards (CBs):** Plug-in boards (e.g., RS485) for additional communication capability. 1212 CPUs support 1 CB, 1214 CPUs support 2 CBs. (p.19)
- **NFC:** Near Field Communication via S7-1200 G2 NFC iPhone app for maintenance operations (p.188)

---

## Communication Protocols and Ports

### Transport Layer Ports and Protocols (p.131-132)

| Port(s) | Direction | Protocol | Application | Description | Default |
| --- | --- | --- | --- | --- | --- |
| 25 | Outbound | TCP | SMTP | Sending e-mails | Deactivated. Enable via TMAIL_C instruction. |
| 68 | Outbound | UDP | DHCP | IP address obtained from DHCP server at PROFINET interface startup | Deactivated. Configurable in CPU properties. |
| 102 | Inbound/Outbound | TCP | ISO-on-TCP | ISO-on-TCP (RFC 1006). S7 protocol uses this for PG/HMI communication with TIA Portal. | **Always activated. Cannot be deactivated.** |
| 123 | Outbound | UDP | NTP | Synchronization of CPU system time with NTP server | Deactivated. Configurable in CPU properties. |
| 161 | Inbound | UDP | SNMP | Reading/setting network management data (SNMP managed objects) | Deactivated. Enable via STEP 7 or CPU properties. Customizable community strings. |
| 443 | Inbound | TCP | HTTPS | Secure communication with CPU-internal web server over TLS | Deactivated. Enable by enabling Web server in CPU properties. |
| 465, 587 | Outbound | TCP | SMTPS | Sending e-mails over secure connections | Deactivated. Enable via TMAIL_C instruction. |
| **502** | **Inbound/Outbound** | **TCP** | **Modbus** | **Modbus/TCP used by MB_CLIENT/MB_SERVER instructions.** | **Deactivated. Activate via Modbus instructions. Port 502 is default but configurable.** |
| 6514, 514 | Outbound | TCP (6514) / UDP (514) | Syslog Client | Transferring syslog messages to a server. System logging collection within CPU cannot be disabled. | Deactivated. Enable in CPU properties. Port 6514 is STEP 7 default for syslog. |
| 34964 | Inbound/Outbound | UDP | PROFINET Context Manager | Endpoint mapper to establish PROFINET application relation (AR) | **Always enabled. Cannot be deactivated.** |

### OUC Port Ranges (p.132)

| Port Range | Direction | Protocol | Application | Notes |
| --- | --- | --- | --- | --- |
| 1-1999 | Varies | TCP/UDP | OUC | Can be used to limited extent, excluding already used ports |
| **2000-5000** | **Varies** | **TCP/UDP** | **OUC** | **Recommended port range for OUC** |
| 5001-49151 | Varies | TCP/UDP | OUC | Can be used to limited extent, excluding already used ports |
| 49152-65535 | Outbound | TCP/UDP | Varies | Dynamic port area for active connection endpoints when application does not specify local port |

### Data Link and Network Layer Protocols (Layer 2/3) (p.132-133)

| Protocol | Direction | Ethertype | Description |
| --- | --- | --- | --- |
| PROFINET DCP | Inbound/Outbound | 0x8892 | Device discovery and basic settings. Multicast MACs: 01-0E-CF-00-00-00, 01-0E-CF-00-00-01 |
| LLDP | Outbound | 0x88CC | Neighbor relationship discovery/management. Multicast MAC: 01-80-C2-00-00-0E |
| PROFINET IO | Inbound/Outbound | 0x8892 | Cyclic IO data transmission between IO controller and IO devices |
| ICMP | Inbound | 0x0800 | Diagnostic or control purposes |
| MRP | Inbound/Outbound | 0x88E3 | Redundant transmission paths in ring topology. Multicast MACs: 01:15:4E:00:00:01, 01:15:4E:00:00:02 |

### Restricted Ports for Passive Connections (p.156)

Do not use these when setting up passive connections with TCON:

- **ISO TSAP (passive):** 01.00, 01.01, 02.00, 02.01, 03.00, 03.01; 10.00, 10.01, 11.00, 11.01 ... BF.00, BF.01
- **TCP/UDP port (passive):** 20, 21, 25, 80, 102, 443, 5001, 34962, 34963, 34964, 49152-65535

---

## Connection Resources (p.133-134)

S7-1200 G2 CPUs have **88 total connection resources**: 10 reserved + 78 dynamic. Dynamic resources are shared across all connection types. Since dynamic connections are shared, it is not possible to max out all connection types simultaneously. (p.134)

| Connection Type | Guaranteed (Reserved) | Dynamic (Shared Pool) | Total Possible |
| --- | --- | --- | --- |
| Programming device (PG) | 4 | 78 | 82 |
| HMI communication | 4 | 78 | 82 |
| S7 communication | 0 | 78 | 78 |
| Open User Communication (OUC) | 0 | 78 | 78 |
| Web communication | 2 | 78 | 80 |

### Communication Services (p.133)

| Communication Service | Functionality | Ethernet |
| --- | --- | --- |
| PG communication | Commissioning, testing, diagnostics | Yes |
| HMI communication | Operator control and monitoring | Yes |
| S7 communication | Data exchange using configured connections | Yes |
| PROFINET IO | Data exchange between I/O controllers and I/O devices | Yes |
| Web server | Diagnostics, maintenance, and process data | Yes |
| SNMP (V1, no TRAPs) | Network diagnostics and parameterization | Yes |
| Open communication over TCP/IP | Data exchange with TCP/IP protocol (OUC instructions) | Yes |
| Open communication over ISO on TCP | Data exchange with ISO on TCP protocol (OUC instructions) | Yes |
| Open communication over UDP | Data exchange with UDP protocol (OUC instructions) | Yes |

---

## Secure Communication (p.130)

S7-1200 G2 CPUs implement secure communication using TLS 1.3 (Transport Layer Security) between PLCs and TIA Portal, SIMATIC Automation Tool, and HMIs. The S7-1200 G2 CPU does not support legacy PG/PC communication. (p.130)

Secure communication provides:
- **Confidentiality:** Data remains confidential and inaccessible to unauthorized individuals
- **Integrity:** Received messages have not been modified during transmission
- **End point authentication:** Verifies the identity of the communication partner

The CPU uses X.509 certificates to provide secure communication. Clients such as STEP 7 and SIMATIC Automation Tool may require trusting the certificate in the CPU. (p.130)

### Supported Certificates (p.135)

Certificates can be created or selected from these TIA Portal CPU Properties areas:
- **Web server > Security:** For Web server certificates
- **Protection & Security > Connection mechanisms:** For PLC communication or Secure PG/PC and HMI communication certificates
- **Protection & Security > Certificate manager:** For all certificate types (default is TLS certificates for Secure OUC)

---

## PROFINET (p.135-178)

### Overview

PROFINET (PN) is used for exchanging data through the STEP 7 program with other communications partners through Ethernet. The S7-1200 G2 supports 31 IO devices with a maximum of 512 submodules. (p.129)

### PROFINET IO Controller Services (p.243-244, p.266-267)

| Feature | Supported | Notes |
| --- | --- | --- |
| PROFINET IO Controller | Yes | - |
| PROFINET IO Device | Yes | - |
| IRT (Isochronous Real-Time) | Yes | Hardware support (new in G2 vs software-only in S7-1200) (p.341) |
| RT (Real-Time) | Yes | Hardware support |
| MRP (Media Redundancy Protocol) | Yes | Manager, Manager (Auto), or Client roles (p.176) |
| MRPD | Yes | Requires IRT sync domain (p.176) |
| PROFIenergy | Yes | Per user program |
| Prioritized startup | Yes | Max. 16 PROFINET devices |
| Max IO devices | 31 | 30 if I-Device, 29 if shared I-Device (p.147) |
| Max submodules | 512 | - |
| S7 routing | No | - |
| Isochronous mode | Yes | - |
| RT send clock | 1 ms to 512 ms | - |
| IRT send clock | 1 ms to 512 ms | 1 ms resolution |

### PROFINET I-Device (p.166-174)

The I-device (intelligent IO device) functionality allows a CPU to operate as an intelligent preprocessing unit. The I-device is linked as an IO device to a higher-level IO controller. (p.166)

| Feature | Value |
| --- | --- |
| Max I-Device connections | 2 |
| Max IO controllers with shared device | 2 |
| Max transfer area size | 1024 input or output bytes (p.174) |
| Shared device support | Yes (p.174) |
| IRT support as I-Device | Yes |
| Isochronous mode as I-Device | No |

### IP Address Configuration Methods (p.138-145)

The CPU has no pre-configured IP address. It must be manually assigned. Three methods: (p.143-144)

1. **Set IP address in the project** -- configured in STEP 7 and downloaded to CPU
2. **IP address from DHCP server** -- external DHCP server provides IP based on MAC or client ID
3. **IP address is set directly at the device** -- changed via SIMATIC Automation Tool, Online & Diagnostics, or T_CONFIG instruction after download

The CPU interface is designated as X1. Three sequential MAC addresses are assigned: lowest for X1 interface, next for port P1R, highest for port P2R. (p.138)

### Device Naming and Address Assignment at Startup (p.147-148)

The controller broadcasts device names to the network; devices respond with MAC addresses. The controller assigns IP addresses via PROFINET DCP protocol. Default Configuration time is 60,000 ms (1 minute), configurable in CPU Properties > Startup > Configuration time. (p.148)

### NTP Time Synchronization (p.148)

NTP client is disabled by default. When enabled, only configured IP addresses can act as NTP servers. Uses port 123 (UDP, outbound). (p.131, p.148)

### SNMP (p.177-178)

SNMP is disabled by default on S7-1200 G2 CPUs. The CPU supports SNMP V1 without TRAPs. (p.133, p.177)

- Enable/disable from Device configuration: Advanced configuration > SNMP
- Configurable Read-only community string (default: "public") and Read-write community string (default: "private")
- Restoring CPU to factory defaults disables SNMP (p.178)
- When disabled, topology detection in TIA Portal is inoperable (p.178)

---

## Open User Communication (OUC) (p.149-156)

### Supported Protocols

| Protocol | Max Data Length | Addressing | Key Features | Instructions |
| --- | --- | --- | --- | --- |
| TCP | 8192 bytes | Port numbers | Connection-oriented, reliable, static data lengths, message acknowledgment | TSEND_C, TRCV_C, TCON, TCONSettings, TDISCON, TSEND, TRCV, T_RESET, T_DIAG |
| ISO on TCP (RFC 1006) | 8192 bytes | TSAPs | Dynamic data lengths, message-oriented with end-of-data identification, supports WAN routing | TSEND_C, TRCV_C, TCON, TCONSettings, TDISCON, TSEND, TRCV, T_RESET, T_DIAG |
| UDP | 2048 bytes (1472 for broadcast) | Port numbers | Connectionless, fast, unacknowledged, supports broadcast | TUSEND, TURCV |

### Ad Hoc Mode (p.151)

TCP and ISO on TCP normally receive data packets of a specified length (1-8192 bytes). The TRCV_C and TRCV instructions also provide an ad hoc mode that can receive data packets of variable length from 1 to 1460 bytes. (p.151)

### Connection IDs (p.152)

- Each TSEND_C, TRCV_C, or TCON instruction creates a new connection with a unique instance DB
- Connection ID range: 1 to 4095
- Both local and partner CPU can use the same connection ID number for the same connection (not required to match)
- TCONSettings can request a connection ID from the CPU

### Transport Layer Security (TLS) (p.153)

TLS increases security and privacy in OUC communication. Connection types TCON_QDN_SEC and TCON_IP_V4_SEC use TLS. (p.153)

### DNS Configuration (p.153)

Required when specifying connection partners by FQDN (fully qualified domain name). Configure DNS servers in CPU Properties > General > Advanced configuration > DNS configuration. (p.153)

---

## S7 Communication (PUT/GET) (p.179-183)

### Overview

PUT and GET instructions communicate with S7 CPUs through PROFINET connections using configured S7 connections. (p.179)

### Data Access Rules (p.179)

- **Remote CPU variables:** Only absolute addresses in ADDR_x input field (S7-200/300/400/1200)
- **Standard DB on remote CPU:** Only absolute addresses in ADDR_x input field
- **Optimized DB on remote S7-1200 G2:** **Cannot access** DB variables in an optimized DB
- **Local CPU data:** Can use absolute or symbolic addresses in RD_x/SD_x input fields

### Enabling PUT/GET Access (p.179)

PUT/GET is **not automatically enabled**. To enable: (p.179)

1. In Project tree > Security settings > Users and roles, enable the Anonymous user
2. In Roles tab, add a new role
3. In Runtime rights tab, assign at least one right (HMI access, Read Access, or Full access) for the PLC
4. In Users tab, assign the new role to the Anonymous user
5. In CPU Device configuration > Properties > Protection & Security > Connection mechanisms, enable "Permit access with PUT/GET communication from remote partner"

### Security Warning (p.180)

PUT/GET, T-Block, and communication module (CM) communications have **no built-in security features**. PROFINET I/O exchange also has no security features. These must be protected by network security measures. (p.130, p.180)

### Connection Parameters (p.181-183)

| Parameter | Description |
| --- | --- |
| End point | Local and Partner CPU names |
| Interface | Names assigned to interfaces |
| Subnet | Type of subnet |
| Address | Assigned IP addresses |
| Connection ID (hex) | Auto-generated by GET/PUT connection parameter assignment |
| Connection name | Auto-generated data storage location |
| Active connection establishment | Checkbox to select Local CPU as active connection |
| One-way | Read-only; in PROFINET GET/PUT both devices can act as server or client (two-way) |

---

## Modbus Communication (p.184-187)

### Overview

Modbus TCP uses the PROFINET connector on the CPU for TCP/IP communication. It uses Open User Communication (OUC) connections as a Modbus communication path. Default port is **502** (configurable). (p.186)

- A CPU can operate as both a Modbus TCP **client** and **server**
- Mixed client and server connections are supported up to the maximum number of connections (88)
- Each MB_SERVER connection must use a unique instance DB and port number
- Only one connection per port number is supported for MB_SERVER (p.186)

### Modbus Function Codes (p.185)

**Read Functions:**

| Function Code | Description |
| --- | --- |
| 01 | Read output bits: 1 to 2000 bits per request |
| 02 | Read input bits: 1 to 2000 bits per request |
| 03 | Read holding registers: 1 to 125 words per request |
| 04 | Read input words: 1 to 125 words per request |

**Write Functions:**

| Function Code | Description |
| --- | --- |
| 05 | Write one output bit: 1 bit per request |
| 06 | Write one holding register: 1 word per request |
| 15 | Write one or more output bits: 1 to 1968 bits per request |
| 16 | Write one or more holding registers: 1 to 123 words per request |
| 23 | Write and read holding registers: 1 to 121/125 (Write/Read) words per request |

### Modbus Memory Addresses (p.186)

| Address Type | Range |
| --- | --- |
| Standard memory address | 10K |
| Extended memory address | 64K |

### Modbus TCP Instructions (p.187)

- **MB_CLIENT:** Modbus TCP client instruction
- **MB_SERVER:** Modbus TCP server instruction
- Found in MODBUS (TCP) V4.0 and later library
- For TIA Portal instruction topics, follow the S7-1500 option (p.187)

### Modbus Network Addressing (p.185)

Each device is uniquely addressed using its IP address and port number. The Modbus protocol uses this address information to access and communicate with devices over the network. (p.185)

---

## OPC UA (p.340, p.343)

The S7-1200 G2 **does not support OPC UA Server** at this time. This is listed as a "Future" capability. The original S7-1200 supported OPC UA Server. (p.340, p.343)

---

## Web Server (p.195-196)

### Overview

The S7-1200 G2 CPU Web server provides a **Web API** for developing custom Web pages that can read and write process data. It implements the S7-1500 Web API functionality. (p.195)

### Key Details

| Feature | Value |
| --- | --- |
| Port | 443 (HTTPS over TLS) (p.131) |
| Default state | Deactivated (p.131) |
| Max concurrent API sessions | 30 (p.195) |
| Standard Web pages | Not provided -- design your own (p.195) |
| AWP commands | Not supported -- use Web API instead (p.195) |
| Firmware update via Web API | Not supported (p.195) |

### Unsupported API Methods (vs S7-1500) (p.195)

- `Plc.CreateBackup`
- `Plc.RestoreBackup`

### Default Page Methods (p.195)

- `WebServer.SetDefaultPage`
- `WebApp.SetDefaultPage`

### Certificate Requirements (p.196)

A trusted Certificate Authority (CA) must be installed on the programming device for HTTPS communication. Requires:
- TIA Portal project protection enabled
- PLC communication certificate created
- Web server enabled in CPU device configuration
- Certificate installed/exported via Security settings > Security features > Certificate manager

---

## HMI Communication (p.160-161)

### Supported Connection Mechanisms by Panel Type (p.161)

| Panel Type | Supported Mechanisms |
| --- | --- |
| Basic Panel | GET/PUT; Secure PG/PC and HMI Communication |
| Comfort Panel | GET/PUT; Secure PG/PC and HMI Communication |
| Unified Panel | GET/PUT; Secure PG/PC and HMI Communication; Standard Modbus TCP/IP |

### HMI Limits (p.161)

- Max tags per HMI: 2000
- Max HMI subscriptions: 250
- HMI driver: S7-1200 G2 uses "SIMATIC S7-1500" driver for Basic/Comfort panels and "SIMATIC S7-1200/1500" driver for Unified panels (p.160)

---

## I/O and Data Addressing (p.87-92)

### Memory Areas (p.87-88)

| Memory Area | Description | Force | Retentive |
| --- | --- | --- | --- |
| I (Process image input) | Copied from physical inputs at start of scan cycle | No | No |
| I_:P (Physical input) | Immediate read of physical input points | Yes | No |
| Q (Process image output) | Copied to physical outputs at start of scan cycle | No | No |
| Q_:P (Physical output) | Immediate write to physical output points | Yes | No |
| M (Bit memory) | Control and data memory | No | Yes (optional) |
| DB (Data block) | Data memory and parameter memory for FBs | No | Yes (optional) |
| Temp memory | Temporary data local to a block | No | No |

### Absolute Addressing Formats (p.88-91)

| Memory | Bit | Byte/Word/DWord |
| --- | --- | --- |
| I (input) | I[byte].[bit] (e.g., I0.1) | IB4, IW5, ID12 |
| I:P (immediate) | I[byte].[bit]:P | IB4:P, IW5:P, ID12:P |
| Q (output) | Q[byte].[bit] (e.g., Q1.1) | QB5, QW10, QD40 |
| Q:P (immediate) | Q[byte].[bit]:P | QB5:P, QW10:P, QD40:P |
| M (bit memory) | M[byte].[bit] (e.g., M26.7) | MB20, MW30, MD50 |
| DB (data block) | DB[n].DBX[byte].[bit] | DB1.DBB4, DB10.DBW2, DB20.DBD8 |

Long data types (64-bit: LWORD, LINT, ULINT, LREAL, LTIME, LTOD, LDT) cannot use absolute addressing; symbolic addressing is required. (p.89)

### Memory Limits (p.90)

- 16 KB temp (local) memory per block (OB/FB/FC)
- 64 KB total temp (local) memory per event priority class

---

## Cycle Time and Communication Load (p.78-80)

### Cycle Time Configuration (p.79)

| Parameter | Range | Default |
| --- | --- | --- |
| Maximum scan cycle time | 1 to 6000 ms | 150 ms |
| Minimum scan cycle time | 1 ms to max cycle time | 1 ms (enabled by default) |

The S7-1200 G2 has minimum cycle time **enabled by default** at 1 ms (vs disabled in S7-1200). (p.344)

### Communication Load (p.80)

- Communication tasks have a **priority of 15**. CPU events with priority 16 or higher can interrupt communication processing. (p.80)
- Default communication load: **50%** of cycle time (vs 20% in S7-1200) (p.344)
- Configurable in Device configuration > CPU properties > Communication load
- If using high-priority OBs that strain the execution cycle, reduce communication load from 50% to a lower value (p.80)

### Interrupt Latency (p.78)

Approximately 200 us from event notification until CPU begins executing the first instruction in the servicing OB, provided a program cycle OB is the only active event service routine. (p.78)

---

## Diagnostic Events for Distributed I/O (p.183)

| Error Type | Station Diagnostic Info | Diagnostics Buffer Entry | CPU Mode |
| --- | --- | --- | --- |
| Diagnostic error | Yes | Yes | Stays in RUN |
| Rack or station failure | Yes | Yes | Stays in RUN |
| I/O access error | No | Yes | Stays in RUN |
| Peripheral access error | No | Yes | Stays in RUN |
| Pull/plug event | Yes | Yes | Stays in RUN |

Use GET_DIAG instruction with station LADDR to obtain diagnostic information programmatically. (p.183)

---

## Comparison: S7-1200 vs S7-1200 G2 Communication Features (p.340-344)

| Feature | S7-1200 | S7-1200 G2 |
| --- | --- | --- |
| Number of Ethernet ports | 1211C/1212C/1214C: 1 port; 1215C/1217C: 2 ports | All CPUs: 2 switched ports |
| Max PROFINET IO devices | 16 | 31 |
| Total CPU connections | 68 | 88 |
| Communication priority | 1 | 15 |
| Communication load default | 20% | 50% |
| IRT (Isochronous Real-Time) | No | Yes (hardware support) |
| RT (Real-Time) | Software support | Hardware support |
| MRPD | No | Yes |
| DHCP | No | Yes |
| DNS | No | Yes |
| OPC UA Server | Yes | No (Future) |
| PROFIBUS CM | Yes | No |
| AS-i Master CM | Yes | No |
| LTE CM | Yes | No |
| S7 Routing | Yes | No |
| Max concurrent Web API sessions | 50 | 30 |
| NFC Application | No | Yes |
| Modbus TCP redundancy instructions | Yes | No |

---

## Protocol Support Summary Table

| Protocol | Supported | Role | Default Port | Max Data | Default State | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| PROFINET IO | Yes | IO Controller / IO Device | Ethertype 0x8892 | - | Active | Up to 31 IO devices, 512 submodules |
| PROFINET IRT | Yes | Sync master or slave | Ethertype 0x8892 | - | Active | Hardware support, 1 ms send clock |
| S7 Communication (PUT/GET) | Yes | Client and Server | 102 (ISO-on-TCP) | Specified length | Active (port 102 always on) | Must explicitly enable PUT/GET access |
| Modbus TCP | Yes | Client and Server | **502** | Per function code | Deactivated | Configurable port; MB_CLIENT/MB_SERVER instructions |
| TCP (OUC) | Yes | Active/Passive | User-defined (2000-5000 recommended) | 8192 bytes | Deactivated | TSEND_C/TRCV_C, ad hoc mode up to 1460 bytes |
| ISO on TCP (OUC) | Yes | Active/Passive | TSAP-based | 8192 bytes | Deactivated | RFC 1006, message-oriented |
| UDP (OUC) | Yes | Active/Passive | User-defined (2000-5000 recommended) | 2048 bytes (1472 broadcast) | Deactivated | Connectionless; TUSEND/TURCV |
| HTTPS (Web API) | Yes | Server | 443 | - | Deactivated | TLS required, max 30 concurrent sessions |
| OPC UA | **No** | - | - | - | - | Listed as "Future" capability |
| SNMP | Yes | Client (V1, no TRAPs) | 161 | - | Deactivated | Read-only/Read-write community strings |
| NTP | Yes | Client | 123 | - | Deactivated | UDP outbound |
| SMTP/SMTPS | Yes | Client (outbound only) | 25 / 465, 587 | - | Deactivated | Via TMAIL_C instruction |
| DHCP | Yes | Client | 68 | - | Deactivated | New in G2 |
| Syslog | Yes | Client | 6514 (TCP) / 514 (UDP) | - | Deactivated | System logging events always collected internally |
| MRP | Yes | Manager or Client | Ethertype 0x88E3 | - | - | Ring redundancy |
| MRPD | Yes | - | - | - | - | Requires IRT sync domain; new in G2 |
| NFC | Yes | Server (passive tag) | - | - | Disabled | iPhone app; read/write CPU data |

---

## Communication Instructions Summary (p.127)

| Instruction Group | Instructions | Purpose |
| --- | --- | --- |
| S7 Communication | PUT, GET | Read/write data from/to remote CPU using S7 protocol |
| Open User Communication | TSEND_C, TRCV_C, TCON, TCONSettings, TDISCON, TSEND, TRCV, T_RESET, T_DIAG, TUSEND, TURCV, TMAIL_C | Establish/terminate connections, send/receive data, send emails |
| Modbus TCP | MB_CLIENT, MB_SERVER | Exchange data via Modbus TCP (client or server) |
| Communication Processor | PtP Communication, USS communication, MODBUS (RTU) | Serial communications (point-to-point, USS, Modbus RTU) |

---

## Errata / Manual Updates (A5E54421713-AA, 08/2025)

The 2-page update addendum (dated 08/2025) addresses the following issue:

**Terminal block connector installation safety warning:** CPU high-voltage 6, 8, or 12 pin terminal block connectors can be incorrectly installed into relay signal modules and relay analog signal modules due to insufficient keying. Affected modules: (p.1 of update)

- SM 1222 DQ 16xRelay (6ES7222-5HH50-0XB0)
- SM 1223 DI 8x24VDC / DQ 8xRelay (6ES7223-5PH50-0XB0)
- SM 1231 AI 8x14bit (6ES7231-4HF50-0XB0)
- SM 1232 AQ 8x14bit (6ES7232-4HF50-0XB0)
- SM 1233 AI 4x14bit / AQ 4x14bit (6ES7233-4HF50-0XB0)

**Risk:** Hazardous voltage levels on DIN rail and connected machinery if wrong connector is installed. Ensure terminal block and receptacle have the same number of pins and both levers are locked before restoring power.

The update also reiterates standard cybersecurity guidance for industrial systems. (p.2 of update)

---

## Quick Reference: Key Numbers

| Parameter | Value | Source |
| --- | --- | --- |
| Total CPU connections | 88 (10 reserved + 78 dynamic) | p.134 |
| Max PROFINET IO devices | 31 (30 with I-Device, 29 with shared I-Device) | p.129, p.147 |
| Max PROFINET submodules | 512 | p.129 |
| Modbus TCP default port | 502 | p.132 |
| Max TCP/ISO-on-TCP data length | 8192 bytes | p.149-150 |
| Max UDP data length | 2048 bytes (1472 broadcast) | p.150 |
| Max ad hoc receive length | 1460 bytes | p.151 |
| OUC Connection ID range | 1 to 4095 | p.152 |
| Max Web API sessions | 30 | p.195 |
| Max HMI tags per HMI | 2000 | p.161 |
| Max HMI subscriptions | 250 | p.161 |
| Communication priority | 15 | p.80 |
| Default communication load | 50% | p.344 |
| Default max scan cycle time | 150 ms | p.79 |
| Default min scan cycle time | 1 ms (enabled) | p.79 |
| Modbus standard address range | 10K | p.186 |
| Modbus extended address range | 64K | p.186 |
| Max Modbus holding registers per read | 125 words | p.185 |
| Max Modbus holding registers per write | 123 words | p.185 |
| Max Modbus output bits per write | 1968 bits | p.185 |
| PROFINET default configuration time | 60,000 ms (1 min) | p.148 |
| I-Device max transfer area | 1024 bytes I or Q | p.174 |
