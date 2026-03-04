# S7-200 Communication Reference

> Extracted from: *S7-200 Programmable Controller System Manual* (554 pages)
> Siemens SIMATIC S7-200 Micro PLC — Legacy product line

---

## Product Overview

The S7-200 series of micro-programmable logic controllers (Micro PLCs) are compact automation controllers with integrated I/O, communications ports, and expansion capability.

### CPU Models

| Feature | CPU 221 | CPU 222 | CPU 224 | CPU 224XP / 224XPsi | CPU 226 |
|---|---|---|---|---|---|
| Physical size (mm) | 90 x 80 x 62 | 90 x 80 x 62 | 120.5 x 80 x 62 | 140 x 80 x 62 | 190 x 80 x 62 |
| Program memory (with/without edit) | 4096 / 4096 bytes | 4096 / 4096 bytes | 8192 / 12288 bytes | 12288 / 16384 bytes | 16384 / 24576 bytes |
| Data memory | 2048 bytes | 2048 bytes | 8192 bytes | 10240 bytes | 10240 bytes |
| Local digital I/O | 6 In / 4 Out | 8 In / 6 Out | 14 In / 10 Out | 14 In / 10 Out, 2 AI / 1 AO | 24 In / 16 Out |
| Expansion modules | 0 | 2 | 7 | 7 | 7 |
| Communications ports | 1 RS-485 | 1 RS-485 | 1 RS-485 | 2 RS-485 | 2 RS-485 |
| Boolean exec speed | 0.22 us/instr | 0.22 us/instr | 0.22 us/instr | 0.22 us/instr | 0.22 us/instr |

*(p17, Table 1-1)*

### Communication Interfaces

The S7-200 supports the following interface types for network access *(p224)*:

- **PPI Multi-Master cables** (RS-232/PPI or USB/PPI) -- most common programming connection
- **CP communication cards** (CP 5512, CP 5611) -- for MPI/PROFIBUS at higher baud rates
- **Ethernet communication cards** (CP 1613, CP 1512) -- for TCP/IP

### Communication Expansion Modules

| Module | Type | Order Number |
|---|---|---|
| EM 277 PROFIBUS-DP | PROFIBUS slave + MPI slave | 6ES7 277-0AA22-0XA0 |
| CP 243-1 Ethernet | Ethernet (Industrial Ethernet) | 6GK7 243-1EX00-0XE0 |
| CP 243-1 IT Internet | Ethernet + IT (HTTP/FTP/Email) | 6GK7 243-1GX00-0XE0 |
| CP 243-2 AS-Interface | AS-Interface master | 6GK7 243-2AX01-0XA0 |
| EM 241 Modem | Telephone modem | -- |

*(p18, Table 1-2; p452-478)*

---

## Communication Protocols

### PPI (Point-to-Point Interface)

PPI is the **default** protocol for S7-200 communication. It is a master-slave protocol based on the PROFIBUS standard (EN 50170). *(p228)*

**Key characteristics:**

- **Protocol type:** Master-slave, token ring
- **Physical layer:** RS-485 on 9-pin sub-D connector
- **Data format:** Asynchronous, 1 start bit, 8 data bits, even parity, 1 stop bit
- **Baud rates:** 9.6 kbaud, 19.2 kbaud, 187.5 kbaud
- **Network addresses:** 0 to 126
- **Default address:** S7-200 CPU = 2, STEP 7-Micro/WIN = 0, HMI = 1
- **Max 32 masters** per network; unlimited masters can communicate with any one slave
- **Connections per CPU port:** 4 (PPI Advanced)

**Master/slave operation:**
- Masters (STEP 7-Micro/WIN, HMI devices, S7-300/400) initiate requests to slaves
- Slaves (S7-200) respond to master requests only
- S7-200 CPUs can act as **PPI masters** in RUN mode by enabling PPI master mode in SMB30 and using NETR/NETW instructions for peer-to-peer communication *(p228, p295)*

**PPI variants:**
- **PPI** -- basic master-slave communication
- **PPI Advanced** -- connection-oriented communication with limited connections per device

*(p228, Table 7-3)*

### MPI (Multi-Point Interface)

MPI supports both master-master and master-slave communications. *(p229)*

**Key characteristics:**

- **Protocol type:** Master-master and master-slave
- **Baud rates:** 9.6 kbaud to 187.5 kbaud (CPU port), up to 12 Mbaud (via EM 277)
- **Network addresses:** 0 to 126
- **Used for:** Connecting S7-200 to S7-300 and S7-400 PLCs
- S7-300/400 use **XGET** and **XPUT** instructions to read/write S7-200 data
- MPI does not communicate with an S7-200 CPU operating as a master
- STEP 7-Micro/WIN uses MPI protocol with a CP card for baud rates above 187.5 kbaud

*(p229, Table 7-3)*

### PROFIBUS DP

PROFIBUS DP (Distributed Peripherals) is a high-speed fieldbus protocol for remote I/O, defined by European Standard EN 50170. The S7-200 connects to PROFIBUS networks via the **EM 277 PROFIBUS-DP** expansion module. *(p229, p452-463)*

**Key characteristics:**

- **Protocol type:** Master-slave cyclic I/O exchange
- **S7-200 role:** DP slave only (via EM 277 module)
- **Baud rates:** 9.6 kbaud to 12 Mbaud (auto-detect)
- **Station address:** 0 to 99 (set by rotary switches on EM 277)
- **Max stations per segment:** 32
- **Max stations per network:** 126 (up to 99 EM 277 stations)
- **MPI connections on EM 277:** 6 total (1 reserved for PG, 1 for OP, 4 general)
- **Data exchange:** Master writes outputs to V memory in S7-200, reads inputs from V memory
- **Max data:** Up to 128 bytes input + 128 bytes output (total 256 bytes)

**I/O configuration options (EM 277):**

| Config | Inputs to Master | Outputs from Master | Consistency |
|---|---|---|---|
| 1 | 1 word | 1 word | Word |
| 2 (default) | 2 words | 2 words | Word |
| 3 | 4 words | 4 words | Word |
| 4 | 8 words | 8 words | Word |
| 5 | 16 words | 16 words | Word |
| 6 | 32 words | 32 words | Word |
| 13 | 2 bytes | 2 bytes | Byte |
| 14 | 8 bytes | 8 bytes | Byte |
| 15 | 32 bytes | 32 bytes | Byte |
| 16 | 64 bytes | 64 bytes | Byte |
| 18 | 8 bytes | 8 bytes | Buffer |
| 19 | 12 bytes | 12 bytes | Buffer |
| 20 | 16 bytes | 16 bytes | Buffer |

Asymmetric configurations (e.g. 2 words out / 8 words in) are also available. *(p456, Table A-42)*

**V memory mapping:**
- The DP master specifies a V memory offset during initialization
- Output buffer (from master) starts at V[offset]
- Input buffer (to master) immediately follows the output buffer
- Default offset is VB0; configurable range 0 to 10239

**Data consistency types:**
- **Byte consistency** -- individual bytes transferred atomically
- **Word consistency** -- 16-bit word transfers are atomic (use for integers)
- **Buffer consistency** -- entire buffer transferred atomically (use for double words, floats, or related data groups)

**GSD file:** SIEM089D.GSD (Ident Number 0x089D) *(p460-461)*

**EM 277 limitations:**
- Always a slave device; cannot be used for NETR/NETW peer-to-peer communication
- Cannot be used for Freeport communications

*(p452-463)*

### Modbus RTU

The S7-200 supports Modbus RTU communication via the STEP 7-Micro/WIN Instruction Library. The S7-200 can be configured as either a **Modbus master** or a **Modbus slave**. *(p361-378)*

**Key characteristics:**

- **Protocol type:** Modbus RTU (binary, not ASCII)
- **Physical layer:** RS-485 (Freeport mode)
- **Baud rates:** 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200
- **Parity:** None, odd, or even (1 stop bit for all)
- **Slave addresses:** 1 to 247 (address 0 = broadcast for master write only)
- **S7-200 firmware:** Version 2.00 or later required for master library
- **Slave library:** Port 0 only
- **Master library:** Port 0 or Port 1 (separate \_P1 library variant)

**Modbus address mapping (slave mode):**

| Modbus Address | Function | S7-200 Address | Count |
|---|---|---|---|
| 00001 to 00128 | Discrete outputs (coils) | Q0.0 to Q15.7 | Up to 128 |
| 10001 to 10128 | Discrete inputs (contacts) | I0.0 to I15.7 | Up to 128 |
| 30001 to 30032 | Input registers (analog) | AIW0 to AIW62 | Up to 32 |
| 40001 to 4xxxx | Holding registers | V memory (HoldStart) | Configurable (MaxHold) |

*(p364, Table 12-1)*

**Holding register V memory mapping:**
- Modbus register 40001 maps to HoldStart (e.g., VB0)
- Modbus register 40002 maps to HoldStart + 2 (e.g., VB2)
- Modbus register 4xxxx maps to HoldStart + 2 x (xxxx - 1)
- S7-200 words are big-endian, matching Modbus register format

*(p372, Table 12-10)*

**Supported Modbus function codes:**

| Function Code | Description | Read/Write |
|---|---|---|
| 1 | Read coils (Q outputs) | Read |
| 2 | Read discrete inputs (I inputs) | Read |
| 3 | Read holding registers (V memory) | Read |
| 4 | Read input registers (AI) | Read |
| 5 | Write single coil | Write |
| 6 | Write single holding register | Write |
| 15 | Write multiple coils | Write |
| 16 | Write multiple holding registers | Write |

- Max read/write per request: 120 words (240 bytes) or 1920 bits
- Function 15 (write multiple coils): starting point must be on byte boundary (e.g. Q0.0, Q2.0), count must be multiple of 8

*(p366, Table 12-3)*

**Modbus instructions:**

| Instruction | Role | Description |
|---|---|---|
| MBUS_INIT | Slave init | Enable/disable Modbus slave on port 0, set address, baud, parity, memory limits |
| MBUS_SLAVE | Slave handler | Called every scan to service incoming Modbus requests |
| MBUS_CTRL / MBUS_CTRL_P1 | Master init | Enable/disable Modbus master on port 0/1, set baud, parity, timeout |
| MBUS_MSG / MBUS_MSG_P1 | Master message | Send read/write request to a slave device |

**Resource usage:**
- Slave: 1857 bytes program space, 779 bytes V memory
- Master: 1620 bytes program space, 284 bytes V memory

*(p362-374)*

### Freeport (Serial)

Freeport mode gives user programs direct control of the S7-200 serial port(s) for implementing custom communication protocols. *(p100-109, p240-241)*

**Key characteristics:**

- **Supported baud rates:** 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200
  - 57600 and 115200 require CPU firmware version 1.2 or later
- **Data bits:** 7 or 8
- **Parity:** None, even, or odd
- **Stop bits:** 1
- **Max message size:** 255 bytes (XMT/RCV)
- **Active only in RUN mode** -- switching to STOP reverts to PPI protocol
- **Controlled via:** SMB30 (Port 0) and SMB130 (Port 1)

**Freeport control register (SMB30 / SMB130):**

| Bits | Field | Values |
|---|---|---|
| 7-6 (pp) | Parity | 00 = no parity, 01 = even, 10 = no parity, 11 = odd |
| 5 (d) | Data bits | 0 = 8 bits, 1 = 7 bits |
| 4-2 (bbb) | Baud rate | 000=38400, 001=19200, 010=9600, 011=4800, 100=2400, 101=1200, 110=115200, 111=57600 |
| 1-0 (mm) | Protocol | 00=PPI/slave, 01=Freeport, 10=PPI/master, 11=Reserved |

*(p101, Figure 6-8)*

**Instructions:**

- **XMT (Transmit):** Send up to 255 bytes from a buffer
  - Interrupt event 9 (port 0) or 26 (port 1) on transmit complete
  - Setting byte count to 0 sends a BREAK condition
- **RCV (Receive):** Receive messages with configurable start/end conditions
  - Interrupt event 23 (port 0) or 24 (port 1) on receive complete

**Receive start conditions:**
1. Idle line detection (SMW90/SMW190 = idle time in ms)
2. Start character detection (SMB88/SMB188 = start char)
3. Idle line + start character (combined)
4. Break detection
5. Break + start character
6. Any character (idle time = 0, immediate start)

**Receive end conditions:**
1. End character detection (SMB89/SMB189)
2. Inter-character timer timeout (SMW92/SMW192)
3. Message timer timeout (SMW92/SMW192)
4. Maximum character count (SMB94/SMB194, 1 to 255)
5. Parity error (automatic)
6. User termination (disable via SMB87/SMB187)

**Receive message control bytes (SMB86-SMB94 for port 0, SMB186-SMB194 for port 1):**

| SM Byte | Description |
|---|---|
| SMB86/186 | Status byte (n=user disable, r=param error, e=end char, t=timer, c=max count, p=parity) |
| SMB87/187 | Control byte (en=enable, sc=start char, ec=end char, il=idle line, c/m=timer mode, tmr=timer enable, bk=break) |
| SMB88/188 | Start character |
| SMB89/189 | End character |
| SMW90/190 | Idle line timeout (ms) |
| SMW92/192 | Inter-character / message timer timeout (ms) |
| SMB94/194 | Maximum character count (1-255) |

*(p100-108, Table 6-13)*

**Character interrupt mode:**
- Each received character triggers an interrupt (event 8 for port 0, event 25 for port 1)
- Character is placed in SMB2; parity status in SM3.0
- At 115.2 kbaud, inter-character time is only 86 microseconds -- keep interrupt routines short

*(p106)*

### USS Protocol

The USS (Universal Serial Interface) protocol is used to control Siemens MicroMaster variable-frequency drives. *(p345-360)*

**Key characteristics:**

- **Protocol type:** USS (proprietary Siemens drive protocol)
- **Physical layer:** RS-485 via S7-200 Freeport
- **Baud rates:** 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200
- **Drive addresses:** 0 to 31 (max 31 drives per port)
- **Ports:** Port 0 (USS_INIT) or Port 1 (USS_INIT_P1)
- **Supported drives:** MicroMaster Series 3 (MM3) and Series 4 (MM4)

**Polling times per drive (no parameter access active):**

| Baud Rate | Time Between Polls |
|---|---|
| 1200 | 240 ms x number of drives |
| 2400 | 130 ms x number of drives |
| 4800 | 75 ms x number of drives |
| 9600 | 50 ms x number of drives |
| 19200 | 35 ms x number of drives |
| 38400 | 30 ms x number of drives |
| 57600 | 25 ms x number of drives |
| 115200 | 25 ms x number of drives |

*(p347, Table 11-1)*

**USS instructions:**

| Instruction | Description |
|---|---|
| USS_INIT / USS_INIT_P1 | Initialize USS protocol on port 0/1, set baud rate, active drives |
| USS_CTRL / USS_CTRL_P1 | Control a drive (RUN/STOP, speed setpoint, direction) |
| USS_RPM_W / USS_RPM_D / USS_RPM_R | Read word/dword/real parameter from a drive |
| USS_WPM_W / USS_WPM_D / USS_WPM_R | Write word/dword/real parameter to a drive |

**Resource usage:**
- Program space: 2150 to 3500 bytes
- V memory: 400-byte block (user-assigned starting address)
- Each USS_RPM/USS_WPM instance needs a 16-byte buffer
- Uses accumulators AC0-AC3 (values are overwritten during execution)
- Cannot be used in interrupt routines

*(p346-355)*

### Ethernet (TCP/IP)

The S7-200 supports Ethernet communication through the **CP 243-1** (Ethernet) and **CP 243-1 IT** (Internet) expansion modules. *(p229, p472-476)*

**Key characteristics:**

- **Protocol:** TCP/IP (S7 communication)
- **Speed:** 10/100 Mbit/s
- **Interface:** 8-pin RJ45 socket
- **Max connections:** 8 S7 connections + 1 STEP 7-Micro/WIN connection per CP module
- **User data per transaction:**
  - Client: up to 212 bytes (XPUT/XGET)
  - Server: up to 222 bytes read (XGET/READ), 212 bytes write (XPUT/WRITE)
- **Only one CP 243-1 module per S7-200 CPU**
- Requires 24 VDC external power supply

**Compatible CPUs:** CPU 222 (Rel 1.10+), CPU 224 (Rel 1.10+), CPU 224XP (Rel 2.00+), CPU 226 (Rel 1.00+) *(p473, Table A-59)*

**CP 243-1 capabilities:**
- S7-200 to S7-200 communication over Ethernet
- S7-200 to S7-300/S7-400 communication
- Remote programming via STEP 7-Micro/WIN over Ethernet
- OPC server integration
- Configured via STEP 7-Micro/WIN Ethernet Wizard

**CP 243-1 IT additional features:**
- Built-in HTTP server (web browser access)
- FTP server and client
- Email sending capability (max 1024 chars)
- 8 MB flash file system

*(p472-476)*

---

## I/O and Data Addressing

### Memory Area Ranges by CPU

| Area | CPU 221 | CPU 222 | CPU 224 | CPU 224XP/XPsi | CPU 226 |
|---|---|---|---|---|---|
| V memory | VB0-VB2047 | VB0-VB2047 | VB0-VB8191 | VB0-VB10239 | VB0-VB10239 |
| Process-image inputs (I) | I0.0-I15.7 | I0.0-I15.7 | I0.0-I15.7 | I0.0-I15.7 | I0.0-I15.7 |
| Process-image outputs (Q) | Q0.0-Q15.7 | Q0.0-Q15.7 | Q0.0-Q15.7 | Q0.0-Q15.7 | Q0.0-Q15.7 |
| Bit memory (M) | M0.0-M31.7 | M0.0-M31.7 | M0.0-M31.7 | M0.0-M31.7 | M0.0-M31.7 |
| Special memory (SM) | SM0.0-SM179.7 | SM0.0-SM299.7 | SM0.0-SM549.7 | SM0.0-SM549.7 | SM0.0-SM549.7 |
| Analog inputs (AI) | AIW0-AIW30 | AIW0-AIW30 | AIW0-AIW62 | AIW0-AIW62 | AIW0-AIW62 |
| Analog outputs (AQ) | AQW0-AQW30 | AQW0-AQW30 | AQW0-AQW62 | AQW0-AQW62 | AQW0-AQW62 |
| Timers (T) | T0-T255 | T0-T255 | T0-T255 | T0-T255 | T0-T255 |
| Counters (C) | C0-C255 | C0-C255 | C0-C255 | C0-C255 | C0-C255 |
| High-speed counters (HC) | HC0-HC5 | HC0-HC5 | HC0-HC5 | HC0-HC5 | HC0-HC5 |
| Local memory (L) | LB0-LB63 | LB0-LB63 | LB0-LB63 | LB0-LB63 | LB0-LB63 |
| Accumulators (AC) | AC0-AC3 | AC0-AC3 | AC0-AC3 | AC0-AC3 | AC0-AC3 |
| Comm ports | Port 0 | Port 0 | Port 0 | Port 0, Port 1 | Port 0, Port 1 |

*(p82, Table 6-1)*

### Data Types

| Representation | Byte (B) | Word (W) | Double Word (D) |
|---|---|---|---|
| Unsigned integer | 0 to 255 | 0 to 65535 | 0 to 4,294,967,295 |
| Signed integer | -128 to +127 | -32768 to +32767 | -2,147,483,648 to +2,147,483,647 |
| Real (float) | N/A | N/A | IEEE 754 single precision |

*(p41, Table 4-1)*

### Access Methods

- **Bit:** I[byte].[bit] -- example: I0.1, Q1.7, V10.2, M26.7
- **Byte:** [area]B[byte] -- example: VB100, IB4, MB0
- **Word:** [area]W[byte] -- example: VW100 (bytes 100-101), AIW0
- **Double word:** [area]D[byte] -- example: VD100 (bytes 100-103)
- **Indirect (pointer):** *VD, *LD, *AC -- use & to create pointer (e.g. MOVD &VB200, AC1)

*(p41-49)*

### Communication-Relevant Special Memory (SM) Bits

| SM Address | Port | Description |
|---|---|---|
| SM0.1 | -- | First scan bit (use for initialization) |
| SM0.7 | -- | Mode switch position (0=TERM, 1=RUN) -- use to control Freeport enable |
| SMB2 | 0/1 | Freeport receive character buffer (shared) |
| SM3.0 | 0/1 | Freeport parity error (shared) |
| SM4.5 | 0 | Port 0 transmitter idle |
| SM4.6 | 1 | Port 1 transmitter idle |
| SMB30 | 0 | Port 0 Freeport control register (protocol, baud, parity, data bits) |
| SMB130 | 1 | Port 1 Freeport control register (same format as SMB30) |
| SMB86-SMB94 | 0 | Port 0 receive message control (status, config, start/end chars, timeouts) |
| SMB186-SMB194 | 1 | Port 1 receive message control |
| SMB200-SMB549 | -- | Intelligent module status (50 bytes per slot, slots 0-6) |

*(p496-507, Appendix D)*

---

## Communication Instructions

### Network Read (NETR) and Network Write (NETW)

Used for peer-to-peer communication between S7-200 CPUs over PPI networks. *(p95-99)*

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| TBL | BYTE | Pointer to communication table (VB, MB, *VD, *LD, *AC) |
| PORT | BYTE | 0 (CPU 221/222/224), 0 or 1 (CPU 224XP/226) |

**TBL structure (8 + data bytes):**

| Offset | Field | Description |
|---|---|---|
| 0 | Status | Bit 7=Done, Bit 6=Active, Bit 5=Error, Bits 3-0=Error code |
| 1 | Remote address | Station address of remote S7-200 (0-126) |
| 2-5 | Data pointer | Indirect pointer to data area in remote station (I, Q, M, or V) |
| 6 | Data length | Number of bytes (1-16) |
| 7-22 | Data | Read: received data; Write: data to send |

**Constraints:**
- Max 16 bytes per transfer
- Max 8 NETR/NETW active simultaneously (any combination)
- Requires PPI master mode enabled in SMB30 (bit 1 = 1, bit 0 = 0)

**Error codes:**

| Code | Meaning |
|---|---|
| 0 | No error |
| 1 | Timeout -- remote not responding |
| 2 | Receive error (parity, framing, checksum) |
| 3 | Offline (duplicate address or hardware failure) |
| 4 | Queue overflow (more than 8 active) |
| 5 | Protocol violation (PPI master not enabled) |
| 6 | Illegal parameter in TBL |
| 7 | No resource (remote busy with upload/download) |
| 8 | Layer 7 application protocol error |
| 9 | Wrong data address or incorrect data length |

*(p95-99, Table 6-11)*

### Transmit (XMT) and Receive (RCV)

Used for Freeport serial communication. See the [Freeport section](#freeport-serial) above for full details. *(p100-108)*

| Parameter | Type | Description |
|---|---|---|
| TBL | BYTE | Pointer to transmit/receive buffer |
| PORT | BYTE | 0 (CPU 221/222/224), 0 or 1 (CPU 224XP/226) |

### Get Port Address (GPA) and Set Port Address (SPA)

Read or set the network station address of a CPU port at runtime. *(p109)*

| Parameter | Type | Description |
|---|---|---|
| ADDR | BYTE | Address value (read or write) |
| PORT | BYTE | Port number |

- SPA changes are **not saved permanently** -- after power cycle, reverts to the system block value
- SPA cannot be executed in an interrupt routine

### Modbus Instructions

See the [Modbus RTU section](#modbus-rtu) above for full details. *(p367-374)*

- **MBUS_INIT** -- Initialize Modbus slave (port 0)
- **MBUS_SLAVE** -- Service Modbus slave requests (call every scan)
- **MBUS_CTRL / MBUS_CTRL_P1** -- Initialize Modbus master (port 0/1)
- **MBUS_MSG / MBUS_MSG_P1** -- Send Modbus master read/write request

### USS Instructions

See the [USS Protocol section](#uss-protocol) above for full details. *(p348-354)*

- **USS_INIT / USS_INIT_P1** -- Initialize USS protocol on port 0/1
- **USS_CTRL / USS_CTRL_P1** -- Control a MicroMaster drive
- **USS_RPM_W / USS_RPM_D / USS_RPM_R** -- Read drive parameter (word/dword/real)
- **USS_WPM_W / USS_WPM_D / USS_WPM_R** -- Write drive parameter (word/dword/real)

---

## Connection Parameters

### Network Addressing

| Parameter | Value |
|---|---|
| Address range | 0 to 126 (PROFIBUS/PPI/MPI standard) |
| Default S7-200 CPU address | 2 |
| Default STEP 7-Micro/WIN address | 0 |
| Default HMI (TD 200) address | 1 |
| EM 277 address range | 0 to 99 (rotary switches) |
| Modbus slave address range | 1 to 247 |
| USS drive address range | 0 to 31 |

*(p225, Table 7-2; p367; p348)*

### Baud Rates by Protocol

| Protocol/Interface | Supported Baud Rates |
|---|---|
| PPI (CPU port) | 9.6, 19.2, 187.5 kbaud |
| MPI (CPU port) | 9.6, 19.2, 187.5 kbaud |
| MPI/PROFIBUS (via EM 277) | 9.6, 19.2, 45.45, 93.75, 187.5, 500 kbaud; 1, 1.5, 3, 6, 12 Mbaud |
| Freeport | 1200, 2400, 4800, 9600, 19200, 38400 baud; 57.6, 115.2 kbaud |
| Modbus RTU | 1200, 2400, 4800, 9600, 19200, 38400 baud; 57.6, 115.2 kbaud |
| USS | 1200, 2400, 4800, 9600, 19200, 38400 baud; 57.6, 115.2 kbaud |
| Ethernet (CP 243-1) | 10/100 Mbit/s |

*(p225, Table 7-1; p101; p452)*

### Maximum Connections

| Interface | Connections |
|---|---|
| S7-200 CPU Port 0 (PPI Advanced) | 4 |
| S7-200 CPU Port 1 (PPI Advanced) | 4 |
| EM 277 PROFIBUS-DP module | 6 per module (1 PG + 1 OP + 4 general) |
| CP 243-1 Ethernet module | 8 S7 connections + 1 STEP 7-Micro/WIN |
| CP 243-1 IT Internet module | 8 S7 + 1 Micro/WIN + 1 FTP server + 1 FTP client + 1 email + 4 HTTP |

*(p228, Table 7-3; p229, Table 7-4; p472-474)*

### Network Cable Specifications

| Specification | Value |
|---|---|
| Cable type | Shielded, twisted pair (RS-485) |
| Nominal impedance | 135 to 160 ohm (3-20 MHz) |
| Loop resistance | 115 ohm/km |
| Effective capacitance | 30 pF/m |
| Cross-section | 0.3 to 0.5 mm2 |
| Max devices per segment | 32 |

*(p236, Table 7-6)*

### Maximum Cable Lengths

| Baud Rate | Non-isolated CPU Port | With Repeater or EM 277 |
|---|---|---|
| 9.6 to 187.5 kbaud | 50 m | 1000 m |
| 500 kbaud | Not supported | 400 m |
| 1 to 1.5 Mbaud | Not supported | 200 m |
| 3 to 12 Mbaud | Not supported | 100 m |

- Up to 9 repeaters in series; max total network length 9600 m
- Each segment: max 32 devices within 50 m at 9.6 kbaud
- RS-485 repeater adds isolation, bias, and termination

*(p235, Table 7-5)*

### RS-485 Connector Pin Assignments

| Pin | PROFIBUS Signal | S7-200 Function |
|---|---|---|
| 1 | Shield | Chassis ground |
| 2 | 24V Return | Logic common |
| 3 | RS-485 Signal B | RxD/TxD+ |
| 4 | Request-to-Send | RTS (TTL) |
| 5 | 5V Return | Logic common |
| 6 | +5V | +5V, 100 ohm series resistor |
| 7 | +24V | +24V |
| 8 | RS-485 Signal A | RxD/TxD- |
| 9 | N/A | 10-bit protocol select (input) |
| Shell | Shield | Chassis ground |

*(p237, Table 7-7)*

---

## Protocol Support Summary Table

| Protocol | Supported | Role | Default Port | Default Baud | Address Range | Module Required | Notes |
|---|---|---|---|---|---|---|---|
| PPI | Yes (built-in) | Master or Slave | Port 0 (RS-485) | 9.6 kbaud | 0-126 | None | Default protocol. Master mode via SMB30 |
| PPI Advanced | Yes (built-in) | Master or Slave | Port 0 (RS-485) | 9.6 kbaud | 0-126 | None | Connection-oriented; 4 connections/port |
| MPI | Yes (built-in) | Slave only | Port 0 (RS-485) | 9.6 kbaud | 0-126 | None (EM 277 for >187.5k) | S7-300/400 use XGET/XPUT |
| PROFIBUS DP | Yes | Slave only | EM 277 port | Auto-detect | 0-99 | EM 277 | 9.6k to 12 Mbaud, up to 128 bytes I/O |
| Modbus RTU | Yes (library) | Master or Slave | Port 0 or 1 | 9600 | 1-247 | None (Freeport) | Via instruction library; slave = port 0 only |
| Freeport | Yes (built-in) | User-defined | Port 0 or 1 | 9600 | N/A | None | Custom protocols via XMT/RCV instructions |
| USS | Yes (library) | Master | Port 0 or 1 | 9600 | 0-31 | None (Freeport) | MicroMaster drive control |
| Ethernet (TCP/IP) | Yes | Client or Server | RJ45 | 10/100 Mbit/s | IP-based | CP 243-1 | S7 communication; max 8+1 connections |
| Internet (HTTP/FTP) | Yes | Server | RJ45 | 10/100 Mbit/s | IP-based | CP 243-1 IT | Web server, FTP, email capabilities |
| AS-Interface | Yes | Master | AS-i cable | N/A | N/A | CP 243-2 | Up to 62 AS-i slaves |

---

## PPI Multi-Master Cable Reference

### RS-232/PPI Multi-Master Cable

- **Order number:** 6ES7 901-3CB30-0XA0
- **Interface:** RS-232 (PC side) to RS-485 (S7-200 side)
- **Provides electrical isolation** between PC and S7-200 network
- **DIP switch settings:**
  - Switch 5: 0 = PPI/Freeport mode, 1 = PPI mode
  - Switch 6: 0 = Local operation, 1 = Remote (modem) operation
- **Max baud rate:** 187.5 kbaud (PPI), 115.2 kbaud (Freeport)

### USB/PPI Multi-Master Cable

- **Order number:** 6ES7 901-3DB30-0XA0
- **Interface:** USB 1.1 (PC side) to RS-485 (S7-200 side)
- **Plug and play** -- no DIP switches to configure
- **Provides electrical isolation**
- **Max baud rate:** 187.5 kbaud
- Only one USB/PPI cable per PC at a time

*(p238, p481-484)*

### LED Indicators (Both Cable Types)

| LED | Meaning |
|---|---|
| Tx | Cable is transmitting to the PC |
| Rx | Cable is receiving from the PC |
| PPI | Cable is transmitting on the network (on steady = active, flashing = waiting to join) |

---

## Quick Reference: CP Cards and Protocols

| Card | Interface | Baud Rate | Protocols |
|---|---|---|---|
| RS-232/PPI Multi-Master cable | RS-232 serial | 9.6-187.5 kbaud | PPI |
| USB/PPI Multi-Master cable | USB | 9.6-187.5 kbaud | PPI |
| PC Adapter USB V1.1+ | USB | 9.6-187.5 kbaud | PPI, MPI, PROFIBUS |
| CP 5512 (PCMCIA) | PCMCIA | 9.6 kbaud - 12 Mbaud | PPI, MPI, PROFIBUS |
| CP 5611 V3+ (PCI) | PCI | 9.6 kbaud - 12 Mbaud | PPI, MPI, PROFIBUS |
| CP 1613 (PCI) | PCI + Ethernet | 10/100 Mbaud | TCP/IP |

*(p238-239, Table 7-8)*
