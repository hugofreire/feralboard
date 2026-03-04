# S7-1500 / ET 200MP Communication Reference

> Extracted from: *SIMATIC S7-1500, ET 200MP Automation System - System Manual, Edition 11/2025*
> (A5E03461182-AN, 468 pages)
>
> For detailed protocol configuration, refer to the **Communication Function Manual**:
> https://support.industry.siemens.com/cs/ww/en/view/59192925

---

## Product Overview

### S7-1500 CPU Family

The SIMATIC S7-1500 is Siemens' Advanced Controller platform for medium-to-high-end automation. All CPUs run user programs in STEP 7 (TIA Portal) and include integrated PROFINET interfaces, web server, OPC UA server/client, and system diagnostics. (p79-80)

**Standard and F-CPUs** (p103-105):

| CPU | Code Memory | Data Memory | PROFINET IO Interfaces | PROFINET Ports | PROFIBUS DP |
|-----|------------|-------------|----------------------|----------------|-------------|
| 1511-1 PN / 1511F-1 PN | 300 KB / 450 KB | 1.5 MB | 1 | 2 | --- |
| 1513-1 PN / 1513F-1 PN | 600 KB / 900 KB | 2.5 MB | 1 | 2 | --- |
| 1515-2 PN / 1515F-2 PN | 1 MB / 1.5 MB | 4.5 MB | 2 | 3 | --- |
| 1516-3 PN/DP / 1516F-3 PN/DP | 2 MB / 3 MB | 7.5 MB | 2 | 5 | 1 |
| 1517-3 PN / 1517F-3 PN | 4 MB / 6 MB | 25 MB | 2 + 1 PN | 5 | --- |
| 1518-3 PN / 1518F-3 PN | 12 MB / 18 MB | 50 MB | 2 + 1 PN | 5 | --- |
| 1518-4 PN/DP MFP / 1518F-4 PN/DP MFP | 6 MB / 9 MB | 60 MB | 2 + 1 PN | 4 | 1 |

- T-CPUs (Technology) add extended motion control; TF-CPUs combine fail-safe + technology.
- All CPUs: supply voltage 19.2 - 28.8 V DC; isochronous mode (centralized and distributed); integrated web server. (p105-106)

**Compact CPUs** (p106):

| CPU | Code Memory | Data Memory | PN Interfaces | PN Ports | Integrated I/O |
|-----|------------|-------------|---------------|----------|----------------|
| 1511C-1 PN | 300 KB | 1.5 MB | 1 | 2 | 16 DI / 16 DQ / 5 AI / 2 AQ |
| 1512C-1 PN | 400 KB | 2 MB | 1 | 2 | 32 DI / 32 DQ / 5 AI / 2 AQ |

### ET 200MP as Distributed I/O

SIMATIC ET 200MP is a modular, distributed I/O system that connects to a central CPU via PROFINET or PROFIBUS through an interface module (IM). It uses the same I/O modules as S7-1500 on an identical mounting rail. (p83, p89, p91)

- PROFINET interface modules: IM 155-5 PN HF, IM 155-5 PN ST, IM 155-5 PN BA, IM 155-5 MF HF
- PROFIBUS interface module: IM 155-5 DP ST
- Maximum 30 I/O modules per station (PN HF/MF HF), or 12 modules (PN BA, DP ST) (p114, p164-166)

> **Note:** The ET 200SP CPU is a separate product family. For ET 200SP communication details, refer to the S7-1500 Communication Function Manual.

---

## Communication Protocols

### Communication Options Matrix

Source: Table on p133 (Section 5.7.1)

| Communication Option | PN/IE | DP | Serial |
|----------------------|-------|-----|--------|
| PG communication (commissioning, testing, diagnostics) | X | X | --- |
| HMI communication (operator control and monitoring) | X | X | --- |
| Open User Communication | X | --- | --- |
| Secure Open User Communication | X | --- | --- |
| OPC UA server | X | --- | --- |
| OPC UA client | X | --- | --- |
| Direct data exchange between IO controllers | X | --- | --- |
| Modbus TCP | X | --- | --- |
| UDP Multicast | X | --- | --- |
| Sending process alarms via e-mail | X | --- | --- |
| FTP (client and server via CP) | X | --- | --- |
| S7 communication | X | X | --- |
| Serial point-to-point (Freeport, 3964(R), USS, Modbus RTU) | --- | --- | X |
| Web server (HTTP/HTTPS) | X | --- | --- |
| SNMP | X | --- | --- |
| Time synchronization (NTP) | X | X | --- |

---

### PROFINET

PROFINET IO is the primary fieldbus for S7-1500. All S7-1500 CPUs have at least one integrated PROFINET IO interface with a 2-port or 3-port switch. (p80, p105)

**Roles:**
- **IO Controller**: The CPU acts as the PROFINET IO controller, managing cyclic data exchange with IO devices.
- **IO Device**: The ET 200MP (via IM 155-5 PN) acts as an IO device to a higher-level IO controller.
- **I-Device (Intelligent Device)**: An S7-1500 CPU can simultaneously act as an IO controller and an IO device to another IO controller. This enables CPU-to-CPU data exchange via PROFINET. (p138)

**Key Features** (p115):

| Feature | IM 155-5 MF HF | IM 155-5 PN HF | IM 155-5 PN ST | IM 155-5 PN BA |
|---------|---------------|----------------|----------------|----------------|
| IRT (Isochronous Real-Time) | X | X (HF only) | --- | --- |
| Isochronous mode (shortest cycle) | 250 us | 250 us | --- | --- |
| Shared device (IO controllers) | 4 | 2-4 (HF: 4) | 2 | --- |
| MRP (Media Redundancy Protocol) | X | X | X | --- |
| MRPD (MRP with planned duplication) | X | X (HF only) | --- | --- |
| System redundancy (S7-1500R/H) | X | X (HF only) | --- | --- |
| I&M data | I&M 0-3 | I&M 0-3 | I&M 0-3 | --- |
| Max I/O modules | 30 | 30 | 12 | 12 |

**PROFINET interface details** (p82, p105):
- Data rate: 100 Mbps (integrated ports), 1 Gbps on CP modules
- PROFINET CBA: Not specifically mentioned in this system manual
- LLDP-based device replacement without programming device (all PN interface modules) (p115)
- GSD file for ET 200MP PROFINET: https://support.industry.siemens.com/cs/ww/en/view/68189683

**Communication priority note** (p264): Communication (e.g., PG test functions) operates at priority 15. OBs with time-critical requirements should be assigned priority > 15 to avoid being delayed by communication tasks.

---

### PROFIBUS DP

PROFIBUS DP is supported as a secondary fieldbus. Only the CPU 1516-3 PN/DP and CPU 1518-4 PN/DP MFP families have an integrated PROFIBUS DP interface. Other CPUs use CM 1542-5 or CP 1542-5 communication modules. (p105, p135)

**Roles:**
- **DP Master**: The CPU acts as DP master (via integrated interface or CM/CP module).
- **DP Slave/Device**: The ET 200MP (via IM 155-5 DP ST) acts as a DP device.

**IM 155-5 DP ST interface module** (p115):
- Interface: 1 x PROFIBUS (RS485)
- Min slave interval: 100 us
- IRT/isochronous mode: Not supported
- Shared device / MRP: Not supported
- Data rate: 9600 bps to 12 Mbps
- Max I/O modules: 12
- GSD file: https://support.industry.siemens.com/cs/ww/en/view/80206700

**PROFIBUS CM/CP modules** (p135):

| Module | Article Number | Protocols |
|--------|---------------|-----------|
| CM 1542-5 | 6GK7542-5DX10-0XE0 | DPV1 master/slave, S7 communication, PG/OP communication, Open User Communication |
| CP 1542-5 | 6GK7542-5FX10-0XE0 | DPV1 master/slave, S7 communication, PG/OP communication, FDL |

---

### OPC UA

All S7-1500 CPUs support OPC UA as both server and client over PROFINET/Industrial Ethernet. (p96, p101, p133)

**Capabilities:**
- OPC UA Server: Integrated in all S7-1500 CPUs
- OPC UA Client: Integrated in all S7-1500 CPUs
- Enables cross-vendor, platform-independent communication (p28, p31)
- Security via certificate-based authentication (p58, p60)
- Detailed security policies and namespace configuration: refer to the Communication Function Manual

**OPC UA instructions** (p269-270):

Session management instructions (per-connection limits defined in CPU equipment manual):
- `OPC_UA_Connect`, `OPC_UA_Disconnect`, `OPC_UA_ConnectionGetStatus`
- `OPC_UA_NamespaceGetIndexList`, `OPC_UA_NodeGetHandleList`
- `OPC_UA_MethodGetHandleList`, `OPC_UA_TranslatePathList`
- `OPC_UA_NodeReleaseHandleList`, `OPC_UA_MethodReleaseHandleList`

Data access instructions:
- `OPC_UA_ReadList`, `OPC_UA_WriteList`, `OPC_UA_MethodCall`

Max simultaneous jobs: Calculated as (max connections) x (max simultaneous calls per connection). Exact values vary by CPU model; consult the equipment manual technical specifications or https://sieportal.siemens.com/su/blVMV (p269).

---

### S7 Communication

S7 communication is Siemens' proprietary protocol for PLC-to-PLC and PLC-to-HMI data exchange. Supported over both PROFINET/IE and PROFIBUS DP. (p133, p268)

**Instructions:**
- **PUT / GET**: One-sided communication; the active partner reads/writes data in the passive partner without the passive partner needing to execute any instructions. Default port: TCP 102.
- **USEND / URCV**: Uncoordinated send/receive for unidirectional data transfer.
- **BSEND / BRCV**: Block send/receive for transferring large data volumes (up to 64 KB per transfer).

**Access control note** (p298-299): In the "No access (complete protection)" access level, the PUT/GET server function is disabled and cannot be changed. Communication between CPUs via PUT/GET requires the passive CPU to have PUT/GET access explicitly enabled in its properties.

**Max simultaneous S7 communication jobs** (shared pool for PUT, GET, USEND, URCV, BSEND, BRCV) (p268):

| CPU Family | Max Jobs |
|-----------|----------|
| 1505SP (F/T) | 264 |
| 1511 (up to V2.9x) | 288 |
| 1511 (V3.0+), 1507S, 1512C, 1513 | 384 |
| 1515 (up to V2.9x) | 576 |
| 1515 (V3.0+), 1516 | 768 |
| 1517 | 960 |
| 1518, 1518 MFP | 1,152 |

---

### Modbus TCP

Modbus TCP is supported on all S7-1500 CPUs over PROFINET/Industrial Ethernet. (p133)

**Instructions** (p268):
- `MB_CLIENT`: Modbus TCP client. Uses lower-level TSEND, TUSEND, TRCV, TURCV, TCON, TDISCON instructions.
- `MB_SERVER`: Modbus TCP server. Uses the same lower-level OUC instructions.

**Default port:** TCP 502 (standard Modbus TCP port).

Modbus TCP is also supported on CM 1542-1, CP 1543-1, and CP 1545-1 communication modules. (p134)

**Modbus RTU** (serial): Supported on CM PtP RS232 HF and CM PtP RS422/485 HF modules via Modbus RTU master and Modbus RTU device protocols. (p136) The `Modbus_Comm_Load` instruction uses lower-level RDREC/WRREC. (p269)

---

### Open User Communication (OUC)

Open User Communication provides protocol-independent data exchange over TCP, UDP, and ISO-on-TCP. Supported on all CPUs via PROFINET/IE. (p133)

**Transport protocols:**
- TCP (connection-oriented)
- UDP (connectionless), including UDP Multicast
- ISO-on-TCP (RFC 1006)

**Instructions** (p267-268):

| Instruction | Purpose |
|-------------|---------|
| TCON | Establish a connection |
| TDISCON | Terminate a connection |
| TSEND / TUSEND | Send data |
| TRCV / TURCV | Receive data |
| TSEND_C | Compact send (uses TSEND, TUSEND, TRCV, TCON, TDISCON internally) |
| TRCV_C | Compact receive (uses TSEND, TUSEND, TRCV, TURCV, TCON, TDISCON internally) |
| TMAIL_C | Send email (uses TSEND, TUSEND, TRCV, TURCV, TCON, TDISCON internally) |
| T_CONFIG | Configure connections at runtime (max 1 simultaneous job) |
| T_RESET | Reset a connection |
| T_DIAG | Diagnose a connection |
| TCONSettings | Configure connection settings |

**Max simultaneous OUC jobs** (per instruction, same pool) (p267-268):

| CPU Family | Max Jobs |
|-----------|----------|
| 1505SP (F/T) | 88 |
| 1511 (up to V2.9x) | 96 |
| 1511 (V3.0+), 1507S, 1512C, 1513 | 128 |
| 1515 (up to V2.9x) | 192 |
| 1515 (V3.0+), 1516 | 256 |
| 1517 | 320 |
| 1518, 1518 MFP | 384 |

---

### Web Server

All S7-1500 CPUs have an integrated web server. (p107-108)

**Features** (p60, p107-108):
- Display CPU status, diagnostics, and process data via web browser
- Standard system web pages: Overview, Diagnostics, User program, Messages/DataLogs, Maintenance (p31)
- User-defined web pages for custom HMI and diagnostics
- HTTPS with CA-signed or self-signed certificates
- Access control via local or central user management
- Web API for programmatic access (reading tags, technology objects, API sessions, CPU info) (p32)
- Certificate management during CPU runtime (load/update in RUN mode) (p35)

**Security** (p60):
- Activation per interface (can be enabled/disabled per PROFINET interface)
- Secure HTTPS transmission using web server certificate
- Authentication via local or central user management
- Password changes at runtime via Web API method `Api.ChangePassword`

**Reference:** Web server Function Manual: https://support.industry.siemens.com/cs/ww/en/view/59193560

---

### Secure Communication

**Secure Open User Communication:** Encrypted OUC connections over TLS. Supported on CPUs and on CP 1543-1 / CP 1545-1 modules. (p133, p134)

**TLS support** (p58, p65, p67-68):
- TLS is used for secure OUC, OPC UA, PG/HMI communication, web server (HTTPS), and syslog forwarding
- Certificate management via TIA Portal for: Secure OUC, OPC UA, Secure PG/HMI, Web server (p58)
- Syslog transfer ports: UDP 514 (unsecured) or TLS/TCP 6514 (secured) (p68)

**CP modules with security functions** (p62):
- CP 1543-1 and CP 1545-1 provide additional firewall, VPN (via SINEMA RC), and Secure OUC capabilities
- CP 1543-1 manual: https://support.industry.siemens.com/cs/us/en/view/67700710
- CP 1545-1 manual: https://support.industry.siemens.com/cs/us/en/view/109771664

**PROFINET Security Class 1**: Protects configuration of CPUs and interface modules. See PROFINET Function Manual: https://support.industry.siemens.com/cs/ww/en/view/49948856 (p61)

---

### SNMP

SNMP (Simple Network Management Protocol) is supported over PROFINET/IE. (p133)

- SNMPv1 on CM 1542-1
- SNMPv1/V3 on CP 1543-1 and CP 1545-1 (p134)
- As of STEP 7 V20, SNMP settings can be centrally configured for an entire PROFINET IO system. IO devices automatically synchronize SNMP settings from the IO controller. (p28, p31)

---

### Additional Protocols

**FTP** (File Transfer Protocol): CP modules can act as FTP client and FTP server. The `FTP_CMD` instruction uses lower-level TSEND, TRCV, TCON, TDISCON. (p133, p269)

**MQTT**: Supported on CP 1545-1 for cloud connectivity. (p134)

**DCP** (Discovery and Configuration Protocol): As of STEP 7 V20, write-protected mode is activated by default for DCP when IO controllers and IO devices support it. (p28)

**Email**: Process alarms can be sent via email over PN/IE. SMTPS supported on CP 1543-1 and CP 1545-1. `TMAIL_C` instruction. (p133, p134)

**Time synchronization** (p355-356): NTP mode (client). Up to 4 NTP servers per CPU. Update interval: 10 s to 86,400 s. NTP servers can be configured in STEP 7, set via `T_CONFIG` instruction, or obtained via DHCP (FW V2.9+).

---

## I/O and Data Addressing

### Process Image and Process Image Partitions (PIP)

The process image is a memory area in the CPU that mirrors the signal states of input/output modules. (p257)

- The CPU supports up to **32 process image partitions** (PIP 0 to PIP 31). (p258)
- **PIP 0** (automatic update) is updated every program cycle and assigned to OB 1.
- PIP 1-31 can be assigned to other OBs during configuration.
- The CPU reads the PIP inputs (PIPI) before processing the associated OB and outputs the PIP outputs (PIPQ) at the end.
- Maximum consistent data width per submodule: **1024 bytes** for PROFINET IO. (p257)

**Manual PIP update instructions** (p258):
- `UPDAT_PI`: Update process image partition of inputs
- `UPDAT_PO`: Update process image partition of outputs
- `SYNC_PI` / `SYNC_PO`: Update PIPs in isochronous mode interrupt OBs

Direct I/O access is also available as an alternative to process image access. A direct write also updates the process image to prevent overwriting. (p259)

### Addressing Modes

**Digital module addressing** (p253): Address = byte address + bit address (e.g., I 1.2 = Input, byte 1, bit 2). STEP 7 assigns default addresses when modules are inserted.

**Analog module addressing** (p255): Address = word address. Channels are assigned word-aligned addresses starting from the module start address (e.g., start address 256: channels at IW 256, IW 258, IW 260, ...).

**Hardware identifiers** (p253): STEP 7 auto-assigns HW identifiers for module/submodule identification, used in diagnostics and instructions.

**Value status** (p255-256): Optional binary information per channel indicating validity of the process signal (1 = valid, 0 = substitute value / deactivated / faulty).

### Memory Areas (p449-450)

| Area | Capacity | Persistence |
|------|----------|-------------|
| Load memory (SIMATIC Memory Card) | 4 MB to 32 GB | Permanent |
| Code work memory | 300 KB to 18 MB (by CPU) | During operation |
| Data work memory | 1.5 MB to 150 MB (by CPU) | During operation |
| Retentive memory | Up to 4.5 MB (by CPU) | Permanent |

### Module Slot Addressing for ET 200MP

**S7-1500 central rack** (p163, p166):
- Slot 0: PS or PM
- Slot 1: CPU
- Slots 2-31: I/O modules, communication modules, technology modules
- Max 32 modules total; max 30 I/O modules

**ET 200MP with PROFINET IM (IM 155-5 PN HF/ST)** (p165):
- Slot 0: PS (optional)
- Slot 1: Interface module
- Slots 2-31: I/O, CM PtP, technology modules
- Max 30 I/O modules (HF/ST) or 12 modules (BA)

**ET 200MP with PROFIBUS IM (IM 155-5 DP ST)** (p166):
- Slot 2: Interface module
- Slots 3-14: I/O, CM PtP, technology modules
- Max 12 modules

**Communication module slot limits by CPU** (p163):

| CPU | Max CM/CP Modules (PROFINET/Ethernet, PROFIBUS) |
|-----|--------------------------------------------------|
| 1511-1 PN, 1511C-1 PN | 4 |
| 1512C-1 PN, 1513-1 PN, 1515-2 PN | 6 |
| 1516-3 PN/DP, 1517-3 PN, 1518 | 8 |

---

## Communication Modules

### PROFINET / Industrial Ethernet Modules (p134)

| Module | Article Number | Speed | Key Protocols |
|--------|---------------|-------|--------------|
| CM 1542-1 | 6GK7542-1AX10-0XE0 | 10/100 Mbps | TCP/IP, ISO-on-TCP, UDP, Modbus TCP, S7 comm, SNMPV1 |
| CP 1543-1 | 6GK7543-1AX10-0XE0 | 10/100/1000 Mbps | TCP/IP, ISO, UDP, Modbus TCP, S7 comm, Security, Secure OUC, SMTPS, SNMPV1/V3, DHCP, FTP, email, IPv4/IPv6 |
| CP 1545-1 | 6GK7545-1GX10-0XE0 | 10/100/1000 Mbps | Same as CP 1543-1 plus MQTT for cloud connectivity |

### PROFIBUS Modules (p135)

| Module | Article Number | Speed | Key Protocols |
|--------|---------------|-------|--------------|
| CM 1542-5 | 6GK7542-5DX10-0XE0 | 9600 bps - 12 Mbps | DPV1 master/slave, S7 comm, PG/OP, Open User Communication |
| CP 1542-5 | 6GK7542-5FX10-0XE0 | 9600 bps - 12 Mbps | DPV1 master/slave, S7 comm, PG/OP, FDL |

### Point-to-Point (Serial) Modules (p135-136)

| Module | Interface | Speed (HF / BA) | Protocols (HF / BA) |
|--------|-----------|-----------------|---------------------|
| CM PtP RS232 HF | RS232 | 300-115,200 bps | Freeport, 3964(R), Modbus RTU master/device |
| CM PtP RS232 BA | RS232 | 300-19,200 bps | Freeport, 3964(R) |
| CM PtP RS422/485 HF | RS422/RS485 | 300-115,200 bps | Freeport, 3964(R), Modbus RTU master/device |
| CM PtP RS422/485 BA | RS422/RS485 | 300-19,200 bps | Freeport, 3964(R) |

- HF modules: max frame length 4 KB; BA modules: max frame length 1 KB
- Article numbers: HF RS232 = 6ES7541-1AD00-0AB0; BA RS232 = 6ES7540-1AD00-0AA0; HF RS422/485 = 6ES7541-1AB00-0AB0; BA RS422/485 = 6ES7540-1AB00-0AA0
- Can be used centrally in S7-1500 and distributed in ET 200MP (p136)

### IO-Link Master Module (p136-137)

| Property | Value |
|----------|-------|
| Module | CM 8x IO-Link |
| Article Number | 6ES7547-1JF00-0AB0 |
| Ports | 8 |
| Data rates | COM1 (4.8 kbaud), COM2 (38.4 kbaud), COM3 (230.4 kbaud) |
| Protocols | IO-Link 1.0, IO-Link 1.1 |
| Diagnostic interrupt | Yes |
| Equipment Manual | https://support.industry.siemens.com/cs/ww/en/view/109763143 |

IO-Link is a point-to-point connection between master and device using standard 3-wire technology with unshielded cables. Supports parameter changes during CPU runtime for production variant changeovers. (p136)

---

## Connection Resources

### Open User Communication Resources by CPU (p267-268)

These are the maximum number of simultaneously running asynchronous instruction jobs. OUC instructions (TSEND, TRCV, TCON, TDISCON, etc.) share the same resource pool.

| CPU Family | OUC Jobs (TSEND/TRCV/TCON/...) | S7 Comm Jobs (PUT/GET/BSEND/BRCV/...) |
|-----------|-------------------------------|---------------------------------------|
| 1505SP (F/T) | 88 | 264 |
| 1511 (up to FW V2.9x) | 96 | 288 |
| 1511 (FW V3.0+), 1507S, 1512C, 1513 | 128 | 384 |
| 1515 (up to FW V2.9x) | 192 | 576 |
| 1515 (FW V3.0+), 1516 | 256 | 768 |
| 1517 | 320 | 960 |
| 1518, 1518 MFP | 384 | 1,152 |

**Note:** MB_CLIENT and MB_SERVER (Modbus TCP) use the OUC resource pool internally. TSEND_C, TRCV_C, and TMAIL_C are compound instructions that consume multiple OUC resources per instance. (p268)

### Distributed I/O Instruction Resources (all CPUs, same limits) (p266)

| Instruction | Max Simultaneous Jobs |
|-------------|----------------------|
| RDREC | 20 |
| WRREC | 20 |
| RD_REC | 10 |
| WR_REC | 10 |
| D_ACT_DP | 8 |
| DPNRM_DG | 8 |
| DPSYC_FR | 2 |
| DP_TOPOL | 1 |
| ReconfigIOSystem | Uses RDREC, WRREC, D_ACT_DP, DPSYC_FR |

### OPC UA Connection Resources (p269-270)

Max simultaneous OPC UA jobs depend on CPU model. Calculation:
- Session management: (max connections) x (max simultaneous session calls per connection)
- Data access: (max connections) x (max simultaneous data access calls per connection)
- `OPC_UA_MethodCall`: Direct value from technical specifications

Consult the equipment manual for your specific CPU: https://sieportal.siemens.com/su/blVMV

---

## Interface Modules for ET 200MP

### PROFINET Interface Modules (p114-115)

| Property | IM 155-5 MF HF | IM 155-5 PN HF | IM 155-5 PN ST | IM 155-5 PN BA |
|----------|---------------|----------------|----------------|----------------|
| Article No. (HF) | 6ES7155-5MU00-0CN0 | 6ES7155-5AA00-0AC0 | --- | --- |
| Article No. (ST) | --- | 6ES7155-5AA01-0AB0 | --- | --- |
| Article No. (BA) | --- | --- | 6ES7155-5AA00-0AA0 | --- |
| Interface | 1x PN IO; 2-port switch + 2 via BusAdapter | 1x PN IO; 2-port switch | 1x PN IO; 2-port switch | 1x PN IO; 2-port switch |
| Max I/O modules | 30 | 30 | 30 | 12 |
| IRT | X | X (HF) | --- | --- |
| Isochronous mode | 250 us min (FW V5.2.1+) | 250 us min | --- | --- |
| MRP | X | X | X | --- |
| Shared device | 4 IO controllers | 2-4 IO controllers | 2 IO controllers | --- |
| System redundancy R/H | X | X (HF) | --- | --- |

### PROFIBUS Interface Module (p114-115)

| Property | IM 155-5 DP ST |
|----------|---------------|
| Article Number | 6ES7155-5BA00-0AB0 |
| Interface | 1x PROFIBUS (RS485) |
| Max I/O modules | 12 |
| Min slave interval | 100 us |
| IRT / Isochronous mode | --- |
| MRP / Shared device | --- |
| I&M data | I&M 0-3 |

---

## Safety-Related Communication

Fail-safe S7-1500 F-CPUs exchange safety-related data with fail-safe I/O modules (F-DI, F-DQ) via PROFIsafe over PROFINET IO or PROFIBUS DP. (p92-94, p138)

**Communication paths** (p138):
1. Safety-related IO controller to IO controller communication (via PROFINET)
2. Safety-related IO controller to I-Device communication (via PROFINET)
3. Safety-related IO controller to I-Device communication via IE/PB link to PROFIBUS

**Safety classes achievable** (p95):
- Up to SIL 3 (IEC 61508:2010)
- Up to Category 4 / Performance Level e (ISO 13849-1:2015)

**Reference:** SIMATIC Safety - Configuring and Programming: https://support.automation.siemens.com/WW/view/en/54110126

---

## Protocol Support Summary Table

| Protocol | Supported | Role(s) | Default Port / Interface | Notes |
|----------|-----------|---------|--------------------------|-------|
| PROFINET IO | Yes | IO Controller, IO Device, I-Device | RJ45, 100 Mbps | All CPUs; IRT on HF modules (p105, p115) |
| PROFIBUS DP | Yes | DP Master, DP Slave | RS485, up to 12 Mbps | CPU 1516/1518 integrated; others via CM/CP (p105, p135) |
| OPC UA | Yes | Server and Client | TCP 4840 (default) | All CPUs; certificate-based security (p133, p269) |
| S7 Communication | Yes | PUT/GET, BSEND/BRCV, USEND/URCV | TCP 102 | PN/IE and PROFIBUS (p133, p268) |
| Modbus TCP | Yes | Client (MB_CLIENT), Server (MB_SERVER) | TCP 502 | Uses OUC resources internally (p133, p268) |
| Modbus RTU | Yes | Master, Device | RS232/RS422/RS485 | CM PtP HF modules only (p136) |
| Open User Communication | Yes | TCP, UDP, ISO-on-TCP | Configurable | TCON/TSEND/TRCV; Secure OUC via TLS (p133, p267) |
| Web Server | Yes | HTTP/HTTPS server | TCP 80 / 443 | All CPUs; user-defined pages; Web API (p107, p60) |
| OPC UA PubSub | --- | --- | --- | Listed as not supported on current CM/CP modules (p134) |
| MQTT | Yes | Publisher | Configurable | CP 1545-1 only (p134) |
| FTP | Yes | Client and Server | TCP 20/21 | Via CP modules (p133, p134) |
| SMTP/SMTPS | Yes | Email client | TCP 25/465/587 | CP 1543-1 and CP 1545-1 (p134) |
| SNMP | Yes | Agent | UDP 161 | SNMPv1 (CM 1542-1); SNMPv1/V3 (CP modules) (p134) |
| NTP | Yes | Client | UDP 123 | Up to 4 NTP servers; 10s-86400s interval (p355) |
| IO-Link | Yes | Master (8 ports) | 3-wire, unshielded | CM 8x IO-Link; protocols 1.0 and 1.1 (p136-137) |
| Freeport | Yes | Serial data exchange | RS232/RS422/RS485 | All CM PtP modules (p136) |
| 3964(R) | Yes | Serial data exchange | RS232/RS422/RS485 | All CM PtP modules (p136) |
| USS | Yes | Serial drive communication | RS232/RS422/RS485 | Via CM PtP and USS_Port_Scan instruction (p133, p269) |
| PROFIsafe | Yes | Safety I/O over PROFINET/PROFIBUS | Over PN or DP | F-CPUs with F-modules; up to SIL 3 / PL e (p138) |
| PROFIenergy | Yes | Energy management | Over PROFINET | PE_START_END, PE_CMD instructions (p266) |
| DCP | Yes | Device discovery/config | Over PROFINET | Write-protected by default as of STEP 7 V20 (p28) |
| LLDP | Yes | Topology discovery | Over PROFINET | Used for device replacement without PG (p115) |

---

## Key Reference Documents

| Document | URL |
|----------|-----|
| Communication Function Manual | https://support.industry.siemens.com/cs/ww/en/view/59192925 |
| Web Server Function Manual | https://support.industry.siemens.com/cs/ww/en/view/59193560 |
| PROFINET Function Manual | https://support.industry.siemens.com/cs/ww/en/view/49948856 |
| SIMATIC Safety - Config and Programming | https://support.automation.siemens.com/WW/view/en/54110126 |
| CP 1543-1 Operating Instructions | https://support.industry.siemens.com/cs/us/en/view/67700710 |
| CP 1545-1 Operating Instructions | https://support.industry.siemens.com/cs/us/en/view/109771664 |
| ET 200MP PROFINET GSD File | https://support.industry.siemens.com/cs/ww/en/view/68189683 |
| ET 200MP PROFIBUS GSD File | https://support.industry.siemens.com/cs/ww/en/view/80206700 |
| Cycle and Response Times Function Manual | https://support.automation.siemens.com/WW/view/en/59193558 |
| CPU Memory Structure Function Manual | https://support.industry.siemens.com/cs/de/de/view/59193101/en |
| Diagnostics Function Manual | https://support.automation.siemens.com/WW/view/en/59192926 |
| Analog Value Processing Function Manual | https://support.automation.siemens.com/WW/view/en/67989094 |
| OPC UA CPU Technical Specs | https://sieportal.siemens.com/su/blVMV |
| Industrial Security Configuration Manual | https://support.industry.siemens.com/cs/us/en/view/108862708 |
