# S7-200 SMART Communication Reference

> Extracted from: *S7-200 SMART System Manual, V2.4, 03/2019 (A5E03822230-AG)* -- 895 pages
> Firmware version: V2.4

---

## Product Overview

### CPU Models

**Standard Line** (expandable, Ethernet + RS485 + optional SB port):

| Model | Power / Output | I/O | Program | Data | Expansion | Signal Board |
|-------|---------------|-----|---------|------|-----------|--------------|
| CPU SR20 | AC/DC/Relay | 20 | 12 KB | 8 KB | 6 max | 1 |
| CPU ST20 | DC/DC/DC | 20 | 12 KB | 8 KB | 6 max | 1 |
| CPU SR30 | AC/DC/Relay | 30 | 18 KB | 12 KB | 6 max | 1 |
| CPU ST30 | DC/DC/DC | 30 | 18 KB | 12 KB | 6 max | 1 |
| CPU SR40 | AC/DC/Relay | 40 | 24 KB | 16 KB | 6 max | 1 |
| CPU ST40 | DC/DC/DC | 40 | 24 KB | 16 KB | 6 max | 1 |
| CPU SR60 | AC/DC/Relay | 60 | 30 KB | 20 KB | 6 max | 1 |
| CPU ST60 | DC/DC/DC | 60 | 30 KB | 20 KB | 6 max | 1 |

**Compact Line** (non-expandable, RS485 only, no Ethernet, no SB):

| Model | Power / Output | I/O | Program | Data |
|-------|---------------|-----|---------|------|
| CPU CR20s | AC/DC/Relay | 20 | 12 KB | 8 KB |
| CPU CR30s | AC/DC/Relay | 30 | 12 KB | 8 KB |
| CPU CR40s | AC/DC/Relay | 40 | 12 KB | 8 KB |
| CPU CR40 | AC/DC/Relay | 40 | 12 KB | 8 KB |
| CPU CR60s | AC/DC/Relay | 60 | 12 KB | 8 KB |
| CPU CR60 | AC/DC/Relay | 60 | 12 KB | 8 KB |

**Key difference:** Compact CRs/CR models have **no Ethernet port**, no signal board slot, and no expansion module support. They only have the integrated RS485 port (Port 0).

### Communication Interfaces per CPU

| Interface | Standard (SR/ST) | Compact (CRs/CR) |
|-----------|-----------------|-------------------|
| Ethernet (RJ45) | Yes | **No** |
| Integrated RS485 (Port 0) | Yes | Yes |
| CM01 Signal Board RS485/RS232 (Port 1) | Optional | **No** |
| PROFIBUS DP (EM DP01) | Up to 2 modules | **No** |

(Source: p18-25, p867-869)

---

## Communication Protocols

### Protocol Support Summary

| Protocol | Interface | Role | Default Port | Max Connections | Notes |
|----------|-----------|------|-------------|-----------------|-------|
| S7 GET/PUT | Ethernet | Peer-to-peer | ISO-on-TCP (102) | 8 active + 8 passive | Between S7-200 SMART CPUs only |
| Modbus TCP | Ethernet | Client / Server | 502 | Uses OUC connections | Library instruction |
| Modbus RTU | RS485 / RS232 | Master / Slave | N/A (serial) | 1 active msg at a time per master | Up to 2 masters supported |
| Open User Comm (OUC) | Ethernet | Client / Server | User-defined (2000-5000 recommended) | 8 active + 8 passive | TCP, UDP, or ISO-on-TCP |
| PROFINET IO | Ethernet | Controller | N/A | 8 devices, 64 modules | V2.4 firmware required, Standard CPUs only |
| PPI | RS485 / RS232 | Master-Slave | N/A (serial) | 5 on RS485, 4 on SB | Programming and HMI access |
| Freeport | RS485 / RS232 | User-defined | N/A (serial) | N/A | XMT/RCV instructions, user protocol |
| PROFIBUS DP | EM DP01 module | Device (slave) | N/A | 6 per EM DP01 | Up to 12 Mbps |
| USS | RS485 | Master | N/A (serial) | N/A | Siemens drive communication |

(Source: p25, p374-376)

---

## CPU Communication Connections

### Ethernet Port (Standard CPUs only)

| Connection Type | Max Simultaneous |
|----------------|-----------------|
| OUC active (client) | 8 |
| OUC passive (server) | 8 |
| HMI/OPC server | 8 |
| Programming device (PG) | 1 |
| GET/PUT active (client) | 8 |
| GET/PUT passive (server) | 8 |
| PROFINET devices | 8 |

### RS485 Port (Port 0) -- All CPUs

| Connection Type | Max Simultaneous |
|----------------|-----------------|
| HMI connections | 4 |
| Programming (STEP 7-Micro/WIN SMART) | 1 |
| **Total PPI connections** | **5** |

### CM01 Signal Board (Port 1) -- Standard CPUs only

| Connection Type | Max Simultaneous |
|----------------|-----------------|
| HMI connections | 4 |
| **Total PPI connections** | **4** |

### PROFIBUS (EM DP01)

| Connection Type | Max Simultaneous |
|----------------|-----------------|
| Connections per EM DP01 | 6 |

(Source: p375-376)

---

## Ethernet (GET/PUT) Communication

### Overview

GET and PUT provide peer-to-peer communication between S7-200 SMART CPUs over Ethernet. The CPU uses ISO-on-TCP (port 102) internally for transport. (p181-187)

### Specifications

| Parameter | Value |
|-----------|-------|
| GET max data read | 222 bytes |
| PUT max data write | 212 bytes |
| Max active GET/PUT at once | 16 total (any combination) |
| Max simultaneous connections | 8 |
| Accessible remote memory areas | I, Q, M, V, DB1 |
| Accessible local memory areas | I, Q, M, V, DB1 |
| Connection persistence | Maintained until CPU goes to STOP |
| Connection reuse | Single connection per unique remote IP |

### GET/PUT TABLE Parameter Structure

The TABLE parameter is a 16-byte buffer in V memory:

| Byte Offset | Content |
|-------------|---------|
| 0 | Status byte: D (Done, bit 7), A (Active, bit 6), E (Error, bit 5), Error code (bits 3-0) |
| 1-4 | Remote station IP address (4 bytes) |
| 5-6 | Reserved (must be 0) |
| 7-10 | Pointer to remote data area (indirect pointer to I, Q, M, V, or DB1) |
| 11 | Data length in bytes (1-222 for GET, 1-212 for PUT) |
| 12-15 | Pointer to local data area (indirect pointer to I, Q, M, V, or DB1) |

### GET/PUT Error Codes

| Code | Description |
|------|-------------|
| 0 | No error |
| 1 | Illegal parameter in table (invalid area, zero length, invalid IP, etc.) |
| 2 | Too many active (max 16) |
| 3 | No connection available (all connections busy) |
| 4 | Error from remote CPU (too much data, write-protected, etc.) |
| 5 | Remote CPU unreachable or no server connection available |

(Source: p181-187)

---

## Modbus RTU (Serial)

### Overview

Modbus RTU communication uses the serial ports (RS485 Port 0 or RS232/RS485 SB Port 1). Implemented as library instructions in STEP 7-Micro/WIN SMART. (p459-477)

### Supported Ports and Baud Rates

| Parameter | Value |
|-----------|-------|
| Ports | RS-485 (Port 0), RS-485 or RS-232 (Port 1 via CM01 SB) |
| Baud rates | 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200 |
| Parity options | 0 = None, 1 = Odd, 2 = Even (all use 1 start bit, 1 stop bit) |
| Max masters per CPU | 2 (MBUS_CTRL + MB_CTRL2 on different ports) |
| Slave address range | 1 to 247 (0 = broadcast, write only) |
| Max data per message | 240 bytes (1920 bits or 120 registers) |

### Modbus RTU Master Instructions

**MBUS_CTRL / MB_CTRL2** -- Initialize master (call every scan):

| Parameter | Type | Description |
|-----------|------|-------------|
| Mode | BOOL | 1 = enable Modbus, 0 = revert to PPI |
| Baud | DWORD | Baud rate (1200-115200) |
| Parity | BYTE | 0=None, 1=Odd, 2=Even |
| Port | BYTE | 0=RS485, 1=SB |
| Timeout | WORD | Response timeout in ms (1-32767, typical: 1000) |
| Done | BOOL | Completion flag |
| Error | BYTE | Error code |

**MBUS_MSG / MB_MSG2** -- Send request:

| Parameter | Type | Description |
|-----------|------|-------------|
| First | BOOL | Pulse on first scan of new request (use positive edge) |
| Slave | BYTE | Slave address (0-247) |
| RW | BYTE | 0=Read, 1=Write |
| Addr | DWORD | Modbus starting address |
| Count | INT | Number of bits or words |
| DataPtr | DWORD | Pointer to V memory for data (&VBx) |
| Done | BOOL | TRUE when response complete |
| Error | BYTE | Error code |

**Resource requirements:**
- 3 subroutines + 1 interrupt routine
- 1942 bytes program space
- 286 bytes V memory block (assigned via Library Memory)

### Modbus RTU Slave Instructions

**MBUS_INIT** -- Initialize slave (call once):

| Parameter | Type | Description |
|-----------|------|-------------|
| Mode | BYTE | 1=enable, 0=disable (revert to PPI) |
| Addr | BYTE | Slave address (1-247) |
| Baud | DWORD | Baud rate (1200-115200) |
| Parity | BYTE | 0=None, 1=Odd, 2=Even |
| Port | BYTE | 0=RS485, 1=SB |
| Delay | WORD | End-of-message timeout extension in ms (0-32767) |
| MaxIQ | WORD | Max I/Q points exposed (0-256, suggested: 256) |
| MaxAI | WORD | Max AI registers exposed (0-56, suggested: 56 or 0 for CRs) |
| MaxHold | WORD | Max holding register words in V memory |
| HoldStart | DWORD | Start of V memory holding area (e.g., &VB0) |
| Done | BOOL | Completion flag |
| Error | BYTE | Error code |

**MBUS_SLAVE** -- Service requests (call every scan):

| Parameter | Type | Description |
|-----------|------|-------------|
| Done | BOOL | TRUE when request serviced |
| Error | BYTE | Error code |

**Slave resource requirements:**
- 3 subroutines + 2 interrupt routines
- 2113 bytes program space
- 786 bytes V memory block

### Supported Modbus Functions (Slave)

| Function | Description |
|----------|-------------|
| 1 | Read coils (Q outputs) |
| 2 | Read discrete inputs (I inputs) |
| 3 | Read holding registers (V memory) |
| 4 | Read input registers (AI analog inputs) |
| 5 | Write single coil |
| 6 | Write single holding register |
| 15 | Write multiple coils (must start on byte boundary, count must be multiple of 8) |
| 16 | Write multiple holding registers (up to 120 words) |

### Modbus RTU Master Error Codes

| Code | Description |
|------|-------------|
| 0 | No error |
| 1 | Parity error in response |
| 3 | Receive timeout (no response from slave) |
| 4 | Error in request parameter (illegal Slave, RW, Addr, or Count) |
| 5 | Master not enabled (call MBUS_CTRL every scan) |
| 6 | Master busy with another request |
| 7 | Response does not match request |
| 8 | CRC error in response |
| 101 | Slave does not support requested function |
| 102 | Slave does not support data address |
| 103 | Slave does not support data type |
| 104 | Slave device failure |
| 105 | Response delayed (resend later) |
| 106 | Slave busy (retry) |
| 107 | Slave rejected for unknown reason |
| 108 | Slave memory parity error |

### Modbus RTU Slave Error Codes

| Code | Description |
|------|-------------|
| 0 | No error |
| 1 | Memory range error |
| 2 | Illegal baud rate or parity |
| 3 | Illegal slave address |
| 4 | Illegal Modbus parameter value |
| 5 | Holding registers overlap library symbols |
| 6 | Receive parity error |
| 7 | Receive CRC error |
| 8 | Illegal function / not supported |
| 9 | Illegal memory address in request |
| 10 | Slave function not enabled |
| 11 | Invalid port number |
| 12 | Signal board port 1 missing or not configured |

(Source: p459-477)

---

## Modbus TCP (Ethernet)

### Overview

Modbus TCP uses the Ethernet port for Modbus communication over TCP/IP. Implemented as library instructions (MBUS_CLIENT, MBUS_SERVER). Default port: **502**. (p478-494)

### Modbus TCP Client (MBUS_CLIENT)

| Parameter | Type | Description |
|-----------|------|-------------|
| Req | BOOL | TRUE = send request |
| Connect | BOOL | TRUE = connect/maintain, FALSE = disconnect |
| IPAddr1-4 | BYTE | Server IP address octets |
| IP_Port | WORD | Server port number (default: 502) |
| RW | BYTE | 0=Read, 1=Write |
| Addr | DWORD | Modbus starting address |
| Count | INT | Number of bits or words |
| DataPtr | DWORD | Pointer to V memory data |
| Done | BOOL | TRUE when request complete |
| Error | BYTE | Error code |

**Resource requirements:**
- 1 subroutine
- 2849 bytes program space
- 638 bytes V memory block

### Modbus TCP Function Code Mapping

| FC | Function | RW | Addr Range | Count | CPU Address |
|----|----------|----|-----------:|-------|-------------|
| 01 | Read Bits | 0 | 00001-09999 | 1-1920 bits | Q0.0-Q1151.7 |
| 02 | Read Bits | 0 | 10001-19999 | 1-1920 bits | I0.0-I1151.7 |
| 03 | Read Words | 0 | 40001-49999 / 400001-465535 | 1-120 words | V memory |
| 04 | Read Words | 0 | 30001-39999 | 1-120 words | AIW0-AIW110 |
| 05 | Write Single Bit | 1 | 00001-09999 | 1 bit | Q0.0-Q1151.7 |
| 06 | Write Single Word | 1 | 40001-49999 / 400001-465535 | 1 word | V memory |
| 15 | Write Multiple Bits | 1 | 00001-09999 | 1-1920 bits | Q0.0-Q1151.7 |
| 16 | Write Multiple Words | 1 | 40001-49999 / 400001-465535 | 1-120 words | V memory |

### Modbus TCP Server (MBUS_SERVER)

| Parameter | Type | Description |
|-----------|------|-------------|
| Connect | BOOL | TRUE = accept connections, FALSE = disconnect |
| IP_Port | WORD | Server port (default: 502) |
| MaxIQ | WORD | Max I/Q points (0-256, suggested: 256) |
| MaxAI | WORD | Max AI registers (0-56) |
| MaxHold | WORD | Max holding register words in V memory |
| HoldStart | DWORD | Start of holding registers in V memory (e.g., &VB0) |
| Done | BOOL | TRUE when request serviced |
| Error | BYTE | Error code |

**Resource requirements:**
- 1 subroutine
- 2969 bytes program space
- 445 bytes V memory block

### Modbus TCP Client Error Codes

| Code | Description |
|------|-------------|
| 0 | No error |
| 32 | Unknown state |
| 33 | Connection busy with another request |
| 34 | Illegal Addr value |
| 35 | Illegal Count value |
| 36 | Illegal RW value |
| 37 | Transaction ID mismatch |
| 38 | Invalid protocol ID from server |
| 39 | Byte count mismatch |
| 40 | Unit identifier mismatch |
| 41 | Function code mismatch |
| 42 | Write data mismatch |
| 43 | Receive timeout |
| 44 | Input values changed during active request |

### Modbus TCP Server Error Codes

| Code | Description |
|------|-------------|
| 0 | No error |
| 32 | Unknown state |
| 33 | Invalid MaxIQ |
| 34 | Invalid MaxAI |
| 35 | Invalid MaxHold |
| 36 | HoldStart out of V memory range |
| 37 | Holding registers overlap server symbols |
| 38 | Input values changed for current connection |

### Modbus TCP General Exception Codes

| Code | Description |
|------|-------------|
| 1 | Illegal Function (0x01) |
| 2 | Illegal Data Address (0x02) |
| 3 | Illegal Data Value (0x03) |
| 4 | Server Device Failure (0x04) |
| 5 | Acknowledge / delayed (0x05) |
| 6 | Server Device Busy (0x06) |
| 7 | Negative Acknowledge (0x07) |
| 10 | Gateway Path Unavailable (0x0A) |
| 11 | Gateway Target Failed to Respond (0x0B) |

(Source: p478-494)

---

## Modbus Address Mapping

All Modbus addresses are 1-based. (p456-458)

### Master/Client Addressing

| Modbus Address Range | Data Type | Access |
|---------------------|-----------|--------|
| 00001-09999 | Discrete outputs (coils) | Read/Write |
| 10001-19999 | Discrete inputs (contacts) | Read only |
| 30001-39999 | Input registers (analog) | Read only |
| 40001-49999 | Holding registers | Read/Write |
| 400001-465535 | Holding registers (extended) | Read/Write |

### Slave/Server Address-to-CPU Mapping

| Modbus Address | CPU Address | Notes |
|---------------|-------------|-------|
| 00001 | Q0.0 | First output bit |
| 00002 | Q0.1 | |
| 01025 | Q128.0 | PROFINET range (V2.4+) |
| 09216 | Q1151.7 | Last output bit |
| 10001 | I0.0 | First input bit |
| 19216 | I1151.7 | Last input bit |
| 30001 | AIW0 | First analog input register |
| 30002 | AIW2 | (word-aligned, +2 per register) |
| 30056 | AIW110 | Last analog input register |
| 40001 / 400001 | V(HoldStart) | First holding register |
| 40002 / 400002 | V(HoldStart+2) | +2 bytes per register |
| 4yyyy / 4zzzzz | V(HoldStart + 2*(yyyy-1)) | Calculated offset |

### Holding Register Memory Layout

Holding registers map directly to V memory words. Each Modbus register = 2 bytes = 1 VW word.

| CPU Byte Address | CPU Word Address | Modbus Register | Data |
|-----------------|-----------------|-----------------|------|
| VB(start) | VW(start) | 40001 | High byte, Low byte |
| VB(start+2) | VW(start+2) | 40002 | High byte, Low byte |
| VB(start+4) | VW(start+4) | 40003 | High byte, Low byte |

Example: If HoldStart = &VB0, then Modbus register 40001 = VW0, 40002 = VW2, 40003 = VW4, etc.

(Source: p456-458, p467)

---

## Open User Communication (OUC)

### Overview

OUC provides TCP, UDP, and ISO-on-TCP communication over Ethernet. Requires Standard CPUs (SR/ST models) with Ethernet port. (p204-215, p394-396, p495-518)

### Protocols

| Protocol | Description | Port |
|----------|-------------|------|
| TCP | Reliable, ordered, stream-based. No message delineation. | User-defined |
| UDP | Connectionless, datagram-based. No delivery guarantee. | User-defined |
| ISO-on-TCP | TCP with RFC 1006 message delineation. Each send = one receive. | Fixed: 102 (uses TSAPs) |

### Connection Limits

| Type | Maximum |
|------|---------|
| Active (client) connections | 8 |
| Passive (server) connections | 8 |
| Total OUC connections | 16 |

UDP connections count as passive connections.

### Port Number Rules

**Recommended range:** 2000-5000

**Restricted local port numbers (cannot be used):**

| Port | Purpose |
|------|---------|
| 20 | FTP data |
| 21 | FTP control |
| 25 | SMTP |
| 80 | Web server |
| 102 | ISO-on-TCP |
| 135 | DCE for PROFINET |
| 161 | SNMP |
| 162 | SNMP Trap |
| 443 | HTTPS |
| 34962-34964 | PROFINET |
| 49152-65535 | Dynamic/private (restricted) |

**Valid range:** 1-49151 (excluding restricted ports above)

Multiple active connections may share the same port number. Multiple passive connections must NOT share a local port number.

### TSAP Rules (ISO-on-TCP only)

- Must be 2 to 16 ASCII characters
- If exactly 2 characters, first must be hexadecimal 0xE0
- Cannot start with "SIMATIC-"
- TSAPs are passed as S7-200 SMART string data type (length byte + characters)

### OUC Library Instructions

| Instruction | Protocol | Purpose |
|-------------|----------|---------|
| TCP_CONNECT | TCP | Create active/passive TCP connection |
| ISO_CONNECT | ISO-on-TCP | Create active/passive ISO-on-TCP connection |
| UDP_CONNECT | UDP | Create passive UDP connection (open local port) |
| TCP_SEND | TCP, ISO-on-TCP | Send data over established connection |
| TCP_RECV | TCP, ISO-on-TCP | Receive data on established connection |
| UDP_SEND | UDP | Send datagram (specify remote IP/port per send) |
| UDP_RECV | UDP | Receive datagram |
| DISCONNECT | All | Terminate connection |

**Common parameters:**
- **ConnID** (WORD): Connection identifier, range 0-65534, must be unique per connection
- **Active** (BOOL): TRUE = client (active), FALSE = server (passive)
- **IPaddr1-4** (BYTE): Remote IP address; use 0.0.0.0 for passive to accept any remote
- **RemPort** (WORD): Remote port; ignored for passive connections
- **LocPort** (WORD): Local port; must be unique for passive connections

**OUC library requires 50 bytes of V memory.**

### OUC Communication Error Codes

| Code | Description |
|------|-------------|
| 161 | Data length > 1024 bytes |
| 162 | Data buffer not in I, Q, M, or V |
| 163 | Data buffer doesn't fit in memory area |
| 164 | Table parameter doesn't fit in memory area |
| 165 | Connection locked in another context |
| 166 | UDP IP address or port error |
| 167 | Instance mismatch (connection busy or input data mismatch) |
| 168 | Connection ID doesn't exist |
| 169 | TCON operation in progress |
| 170 | TDCON operation in progress |
| 171 | TSEND in progress |
| 172 | Temporary communication error (try later) |
| 173 | Partner refused/dropped connection |
| 174 | Partner unreachable |
| 175 | Connection aborted (inconsistency) |
| 176 | Connection ID in use with different IP/port/TSAP |
| 177 | No connection resource available |
| 178 | Port reserved or already in use for another passive connection |
| 179 | IP address invalid (0.0.0.0, self, broadcast, multicast) |
| 180 | TSAP error (ISO-on-TCP only) |
| 181 | Invalid connection ID (65535 reserved) |
| 182 | Active/passive error (UDP only allows passive) |
| 183 | Invalid connection type |
| 184 | No operation pending |
| 185 | Receive buffer too small (extra bytes discarded) |
| 191 | Unknown error |

(Source: p394-396, p495-518)

---

## OUC Base Instructions (Chapter 7.3.5)

These are the low-level instructions that the OUC library wraps. (p204-215)

| Instruction | STL | Description |
|-------------|-----|-------------|
| TCON | TCON TBL, ConnID | Establish active or passive connection |
| TSEND | TSEND TBL, ConnID | Send data on established connection |
| TRECV | TRECV TBL, ConnID | Receive data on established connection |
| TDCON | TDCON TBL, ConnID | Disconnect / close connection |

The TBL parameter contains connection parameters (IP, port/TSAP, protocol type, active/passive). The library instructions (TCP_CONNECT, etc.) build these tables automatically.

(Source: p204-215)

---

## PROFINET IO

### Overview

PROFINET IO is supported on Standard CPUs (SR/ST) with V2.4 firmware. The S7-200 SMART acts as a **PROFINET IO Controller**. (p369-373, p397-410, p869-870)

### Specifications

| Parameter | Value |
|-----------|-------|
| Supported CPUs | ST/SR 20, 30, 40, 60 (firmware V2.4+) |
| Max PROFINET devices | 8 |
| Device number range | 1-8 |
| Max modules/submodules total | 64 |
| Max input size per device | 128 bytes |
| Max output size per device | 128 bytes |
| GSDML specification supported | V2.33 or earlier (later importable but unvalidated) |
| Max imported GSDML files | 20 |
| Bandwidth | 100 Mbps full-duplex |

### PROFINET Process Image Address Mapping

Each PROFINET device gets a fixed 128-byte block for inputs and outputs:

| Device # | Input Address Range | Output Address Range |
|----------|-------------------|---------------------|
| 1 | I128.0 - I255.7 | Q128.0 - Q255.7 |
| 2 | I256.0 - I383.7 | Q256.0 - Q383.7 |
| 3 | I384.0 - I511.7 | Q384.0 - Q511.7 |
| 4 | I512.0 - I639.7 | Q512.0 - Q639.7 |
| 5 | I640.0 - I767.7 | Q640.0 - Q767.7 |
| 6 | I768.0 - I895.7 | Q768.0 - Q895.7 |
| 7 | I896.0 - I1023.7 | Q896.0 - Q1023.7 |
| 8 | I1024.0 - I1151.7 | Q1024.0 - Q1151.7 |

Total PROFINET I/O range: **I128.0 to I1151.7** and **Q128.0 to Q1151.7**

### PROFINET Instructions

| Instruction | Description |
|-------------|-------------|
| RDREC | Read data record from PROFINET device |
| WRREC | Write data record to PROFINET device |
| BLKMOV_BIR | Read multiple bytes from physical PROFINET input to memory |
| BLKMOV_BIW | Write multiple bytes from memory to physical PROFINET output |

(Source: p369-373, p397-410, p869-870)

---

## RS485/RS232 Serial Communication

### RS485 Network Characteristics

| Parameter | Value |
|-----------|-------|
| Topology | Differential, multi-point |
| Max addressable nodes per network | 126 |
| Max devices per segment | 32 |
| Baud rates (PPI) | 9.6, 19.2, 187.5 Kbps |
| Baud rates (Freeport) | 1.2, 2.4, 4.8, 9.6, 19.2, 38.4, 57.6, 115.2 Kbps |
| Default network address | 2 (CPU), 1 (HMI), 0 (STEP 7-Micro/WIN) |
| Address range | 0-126 |
| Cable type | Shielded twisted pair |
| Nominal impedance | 135-160 ohm |

### Cable Length Limits

| Baud Rate | Without Repeater | With Repeater |
|-----------|-----------------|---------------|
| 9.6-187.5 Kbps | 50 m | 1000 m |
| 500 Kbps | Not supported | 400 m |
| 1-1.5 Mbps | Not supported | 200 m |
| 3-12 Mbps | Not supported | 100 m |

Up to 9 repeaters in series. Total network length must not exceed 9600 m.

### RS485 Port Pin Assignments (Port 0, 9-pin D-sub)

| Pin | Signal | Description |
|-----|--------|-------------|
| 1 | Shield | Chassis ground |
| 2 | 24V Return | Logic common |
| 3 | RS485 Signal B | Data B |
| 4 | RTS | Request-to-Send (TTL) |
| 5 | 5V Return | Logic common |
| 6 | +5V | +5V output, 100 ohm series resistor |
| 7 | +24V | +24V output |
| 8 | RS485 Signal A | Data A |
| 9 | Programmer detection | Input; CRs models use this to detect USB-PPI cable |

### CM01 Signal Board (Port 1, 6-pin)

| Pin | Signal | Description |
|-----|--------|-------------|
| 1 | Ground | Chassis ground |
| 2 | Tx/B | RS232-Tx or RS485-B |
| 3 | RTS | Request-to-Send (TTL) |
| 4 | M-ground | Logic common |
| 5 | Rx/A | RS232-Rx or RS485-A |
| 6 | +5V DC | +5V, 100 ohm series resistor |

Article number: 6ES7288-5CM01-0AA0

CM01 SB configuration options: RS485 or RS232 (selected in system block). Default baud rate for PPI: 9.6 Kbps. PPI baud rates: 9.6, 19.2, 187.5 Kbps.

### RS232 Characteristics

| Parameter | Value |
|-----------|-------|
| Connection type | Point-to-point (2 devices) |
| Max speed | 115.2 Kbps |
| Max cable length | 10 m (shielded) |

(Source: p152-153, p432-453, p805-806)

---

## Freeport Communication

### Overview

Freeport mode gives user program control of the serial port for custom protocols. Active only when CPU is in RUN mode. Setting CPU to STOP reverts port to PPI. (p188-200, p449-452)

### Configuration

Freeport is configured via special memory bytes:
- **SMB30**: Port 0 (integrated RS485) control
- **SMB130**: Port 1 (CM01 SB) control

### Key Instructions

| Instruction | STL | Description |
|-------------|-----|-------------|
| XMT | XMT TBL, PORT | Transmit data buffer (up to 255 bytes) |
| RCV | RCV TBL, PORT | Receive message with configurable start/end conditions |

PORT: 0 = RS485, 1 = CM01 SB

### Receive Message Configuration (SM memory)

The RCV instruction uses SM bytes to configure message start and end conditions:

**Port 0**: SMB86 - SMB94
**Port 1**: SMB186 - SMB194

Configurable conditions include:
- Start on idle-line detection or specific start character
- End on character count, end character, idle-line timeout, or inter-character timeout
- Max message size: 255 bytes

### Freeport Baud Rates

Supported (set via SM memory, not system block):
1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200 bps

### CRs Model Note

On CRs models (CR20s, CR30s, CR40s, CR60s), the RS485 port is also the programming port. Attaching a USB-PPI cable forces exit from Freeport mode. Pin 9 is used for USB-PPI detection on CRs models only.

(Source: p188-200, p449-452, p846-847)

---

## PROFIBUS DP (EM DP01)

### Overview

The EM DP01 module connects the S7-200 SMART as a **PROFIBUS DP device** (slave). Standard CPUs only. (p411-432, p808-811)

### Specifications

| Parameter | Value |
|-----------|-------|
| Module | EM DP01 |
| Max modules per CPU | 2 |
| Speed | Up to 12 Mbps |
| Addressable devices per network | 126 |
| Connections per EM DP01 | 6 |
| Role | DP device (slave) |

(Source: p411-432, p808-811)

---

## I/O and Data Addressing

### Memory Area Ranges

| Memory Area | Range (Compact CRs/CR) | Range (SR20/ST20) | Range (SR30/ST30) | Range (SR40/ST40) | Range (SR60/ST60) |
|-------------|----------------------|-------------------|-------------------|-------------------|-------------------|
| V (Variable) | VB0-VB8191 | VB0-VB8191 | VB0-VB12287 | VB0-VB16383 | VB0-VB20479 |
| I (Process Input) | I0.0-I31.7 | I0.0-I31.7 | I0.0-I31.7 | I0.0-I31.7 | I0.0-I31.7 |
| Q (Process Output) | Q0.0-Q31.7 | Q0.0-Q31.7 | Q0.0-Q31.7 | Q0.0-Q31.7 | Q0.0-Q31.7 |
| M (Flag/Marker) | M0.0-M31.7 | M0.0-M31.7 | M0.0-M31.7 | M0.0-M31.7 | M0.0-M31.7 |
| SM (Special Memory) | SM0.0-SM2047.7 | SM0.0-SM2047.7 | SM0.0-SM2047.7 | SM0.0-SM2047.7 | SM0.0-SM2047.7 |
| AI (Analog Input) | -- | AIW0-AIW110 | AIW0-AIW110 | AIW0-AIW110 | AIW0-AIW110 |
| AQ (Analog Output) | -- | AQW0-AQW110 | AQW0-AQW110 | AQW0-AQW110 | AQW0-AQW110 |
| L (Local) | LB0-LB63 | LB0-LB63 | LB0-LB63 | LB0-LB63 | LB0-LB63 |
| T (Timers) | T0-T255 | T0-T255 | T0-T255 | T0-T255 | T0-T255 |
| C (Counters) | C0-C255 | C0-C255 | C0-C255 | C0-C255 | C0-C255 |
| HC (High-Speed Ctr) | HC0-HC3 | HC0-HC5 | HC0-HC5 | HC0-HC5 | HC0-HC5 |
| S (Seq Control Relay) | S0.0-S31.7 | S0.0-S31.7 | S0.0-S31.7 | S0.0-S31.7 | S0.0-S31.7 |
| AC (Accumulators) | AC0-AC3 | AC0-AC3 | AC0-AC3 | AC0-AC3 | AC0-AC3 |

### PROFINET Extended I/O Range (V2.4, Standard CPUs only)

| Area | Range |
|------|-------|
| PROFINET Inputs | I128.0 - I1151.7 |
| PROFINET Outputs | Q128.0 - Q1151.7 |

### V Memory Size Summary

| CPU | V Memory Range | Size (bytes) | Max Holding Registers (words) |
|-----|---------------|-------------|------------------------------|
| CRs/CR, SR20, ST20 | VB0-VB8191 | 8,192 | 4,096 |
| SR30, ST30 | VB0-VB12287 | 12,288 | 6,144 |
| SR40, ST40 | VB0-VB16383 | 16,384 | 8,192 |
| SR60, ST60 | VB0-VB20479 | 20,480 | 10,240 |

### Address Format Reference

| Type | Bit Format | Byte/Word/DWord Format | Example |
|------|-----------|----------------------|---------|
| I | I[byte].[bit] | IB/IW/ID[byte] | I0.1, IB4, IW7 |
| Q | Q[byte].[bit] | QB/QW/QD[byte] | Q1.1, QB5, QW14 |
| V | V[byte].[bit] | VB/VW/VD[byte] | V10.2, VB16, VW100, VD2136 |
| M | M[byte].[bit] | MB/MW/MD[byte] | M26.7, MB0, MW11 |
| SM | SM[byte].[bit] | SMB/SMW/SMD[byte] | SM0.1, SMB86, SMW300 |
| AI | -- | AIW[byte] | AIW0, AIW2, AIW4 (even only) |
| AQ | -- | AQW[byte] | AQW0, AQW2, AQW4 (even only) |
| T | T[number] | -- | T24 |
| C | C[number] | -- | C24 |
| HC | HC[number] | -- | HC1 (32-bit read-only) |
| AC | AC[number] | -- | AC0 (byte/word/dword) |
| L | L[byte].[bit] | LB/LW/LD[byte] | L0.0, LB33, LW5 |

### Data Type Sizes

| Type | Size | Signed Range | Unsigned Range |
|------|------|-------------|----------------|
| Byte (B) | 8 bits | -128 to +127 | 0 to 255 |
| Word (W) | 16 bits | -32,768 to +32,767 | 0 to 65,535 |
| Double Word (D) | 32 bits | -2,147,483,648 to +2,147,483,647 | 0 to 4,294,967,295 |
| Real (IEEE 32-bit) | 32 bits | +/-1.175495E-38 to +/-3.402823E+38 | -- |

### Expansion I/O Address Mapping

| Position | Digital I Start | Digital Q Start | Analog AI Start | Analog AQ Start |
|----------|----------------|----------------|-----------------|-----------------|
| CPU (built-in) | I0.0 | Q0.0 | -- | -- |
| Signal Board | I7.0 | Q7.0 | AI12 | AQ12 |
| Expansion Module 0 | I8.0 | Q8.0 | AI16 | AQ16 |
| Expansion Module 1 | I12.0 | Q12.0 | AI32 | AQ32 |
| Expansion Module 2 | I16.0 | Q16.0 | AI48 | AQ48 |
| Expansion Module 3 | I20.0 | Q20.0 | AI64 | AQ64 |
| Expansion Module 4 | I24.0 | Q24.0 | AI80 | AQ80 |
| Expansion Module 5 | I28.0 | Q28.0 | AI96 | AQ96 |

(Source: p65-77, p867-870)

---

## Communication Background Time

The percentage of scan cycle time dedicated to communication processing is configurable in the system block. (p128-129)

| Parameter | Value |
|-----------|-------|
| Default | 10% |
| Adjustment increment | 5% |
| Maximum | 50% |

Higher values improve communication throughput but increase scan time. Scan time only increases when there are active communication requests.

Situations requiring increased background time:
- Multiple GET/PUT connections active
- EM DP01 PROFIBUS with HMIs or other CPUs
- Open User Communication (OUC) operations
- Multiple HMI connections

---

## Ethernet Configuration

### Default IP Address

All S7-200 SMART CPUs ship with: **192.168.2.1**

### IP Configuration Methods

1. **Communications dialog** -- dynamic, immediate, no download required
2. **System Block** -- static, requires project download
3. **SIP_ADDR instruction** -- dynamic, programmatic, immediate

Static IP: Check "IP address data is fixed" in system block. Can only be changed via system block re-download.
Dynamic IP: Uncheck the "fixed" checkbox. Can be changed via Communications dialog or SIP_ADDR instruction.

### Station Name Rules

- Max 63 characters
- Allowed: lowercase a-z, digits 0-9, hyphen (-), period (.)
- Cannot have format n.n.n.n (where n = 0-999)
- Cannot start with "port-nnn" or "port-nnn-nnnnn"
- Cannot start or end with hyphen or period

(Source: p128-129, p378-390)

---

## USS Protocol (Drive Communication)

The USS protocol library communicates with Siemens drives (e.g., SIMODRIVE MicroMaster) over RS485. (p539-555)

### Instructions

| Instruction | Description |
|-------------|-------------|
| USS_INIT | Initialize USS communication (call once on first scan) |
| USS_CTRL | Control drive speed/direction |
| USS_RPM_x | Read drive parameter |
| USS_WPM_x | Write drive parameter |

Communication is master-slave: CPU is master, drives are slaves.

(Source: p539-555)

---

## Quick Reference: Communication Instructions Summary

### Ethernet Instructions

| Instruction | Type | Description |
|-------------|------|-------------|
| GET | Built-in | Read data from remote S7-200 SMART CPU |
| PUT | Built-in | Write data to remote S7-200 SMART CPU |
| GIP | Built-in | Get CPU IP address, subnet mask, gateway |
| SIP | Built-in | Set CPU IP address, subnet mask, gateway |
| TCON | Built-in (OUC) | Establish/open connection |
| TSEND | Built-in (OUC) | Send data on connection |
| TRECV | Built-in (OUC) | Receive data on connection |
| TDCON | Built-in (OUC) | Disconnect/close connection |
| MBUS_CLIENT | Library | Modbus TCP client |
| MBUS_SERVER | Library | Modbus TCP server |
| TCP_CONNECT | Library | Create TCP connection |
| ISO_CONNECT | Library | Create ISO-on-TCP connection |
| UDP_CONNECT | Library | Create UDP connection |
| TCP_SEND | Library | Send data (TCP/ISO-on-TCP) |
| TCP_RECV | Library | Receive data (TCP/ISO-on-TCP) |
| UDP_SEND | Library | Send UDP datagram |
| UDP_RECV | Library | Receive UDP datagram |
| DISCONNECT | Library | Close any OUC connection |

### Serial Instructions

| Instruction | Type | Description |
|-------------|------|-------------|
| XMT | Built-in | Freeport transmit (up to 255 bytes) |
| RCV | Built-in | Freeport receive with configurable conditions |
| GPA | Built-in | Get RS485 port address |
| SPA | Built-in | Set RS485 port address |
| MBUS_CTRL | Library | Initialize Modbus RTU master (port 0) |
| MB_CTRL2 | Library | Initialize Modbus RTU master 2 (port 1) |
| MBUS_MSG | Library | Send Modbus RTU master request (port 0) |
| MB_MSG2 | Library | Send Modbus RTU master 2 request (port 1) |
| MBUS_INIT | Library | Initialize Modbus RTU slave |
| MBUS_SLAVE | Library | Service Modbus RTU slave requests |
| USS_INIT | Library | Initialize USS drive communication |
| USS_CTRL | Library | Control USS drive |

### PROFINET Instructions

| Instruction | Type | Description |
|-------------|------|-------------|
| RDREC | Built-in | Read data record from PROFINET device |
| WRREC | Built-in | Write data record to PROFINET device |
| BLKMOV_BIR | Built-in | Block read PROFINET input to memory |
| BLKMOV_BIW | Built-in | Block write memory to PROFINET output |

(Source: p867)
