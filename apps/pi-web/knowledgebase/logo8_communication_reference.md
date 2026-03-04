# LOGO! 8 Communication Reference

Extracted from Siemens LOGO! 8 System Manual (10/2020, A5E33039675-AG) and LOGO!Soft Comfort V8.3.1 Online Help (1/2022).

---

## Product Overview

### Product Family

LOGO! 8 is a Siemens universal logic module integrating controls, power supply, display, Ethernet interface, and expansion module interfaces. The 0BA8 series is the base hardware generation; firmware variants include LOGO! 8 (0BA8.Standard), LOGO! 8.1 & 8.2 (8.FS4), and LOGO! 8.3.

### CPU / Base Module Variants

| Variant | Order Number | Voltage Class | Notes |
| --- | --- | --- | --- |
| LOGO! 12/24RCE (Basic) | 6ED1052-1MD08-0BA1 | 12/24 VDC | With display, analog inputs |
| LOGO! 24CE (Basic) | 6ED1052-1CC08-0BA1 | 24 VDC | With display, analog inputs |
| LOGO! 24RCE (Basic) | 6ED1052-1HB08-0BA1 | 24 VAC/VDC | With display |
| LOGO! 230RCE (Basic) | 6ED1052-1FB08-0BA1 | 115-240 VAC/VDC | With display |
| LOGO! 12/24RCEo (Pure) | 6ED1052-2MD08-0BA1 | 12/24 VDC | No display, analog inputs |
| LOGO! 24CEo (Pure) | 6ED1052-2CC08-0BA1 | 24 VDC | No display, analog inputs |
| LOGO! 24RCEo (Pure) | 6ED1052-2HB08-0BA1 | 24 VAC/VDC | No display |
| LOGO! 230RCEo (Pure) | 6ED1052-2FB08-0BA1 | 115-240 VAC/VDC | No display |

(Manual p.363)

### Display Modules

| Module | Order Number | Notes |
| --- | --- | --- |
| LOGO! TDE | 6ED1055-4MH08-0BA1 | Text Display with Ethernet, 160x96 FSTN, 10 keys |

(Manual p.363)

### Firmware Versions Referenced

- LOGO! 0BA7: older generation, S7 connections only
- LOGO! 0BA8 (8.Standard): base 0BA8 hardware, S7 connections only
- LOGO! 8.FS4 (8.1 & 8.2): adds Modbus TCP client/server support, NTP
- LOGO! 8.3: adds Cloud IoT (AWS), HTTPS, enhanced security

### Communication Interfaces

- **Ethernet**: 10/100 Mbit/s RJ45 on every Base Module (Manual p.50)
- **Expansion bus**: proprietary bus to DM/AM modules (not IP-based)
- **LOGO! TDE**: two 10/100 Mbit Ethernet ports, max 30 m cable (Manual p.342)

---

## Communication Protocols

### S7 Communication (ISO-on-TCP)

- **Port**: 102 (unsecured) (Manual p.292)
- **Supported roles**: Client and Server
- **Connection type**: TCP/IP-based S7 protocol (ISO-on-TCP)
- **TSAP range**: 20.00 to FF.FF on LOGO! server side; if connecting to an Operator Panel (HMI), TSAP is set to 02.00 (Help p.131)
- **Max data transfers per client connection**: 32 (Help p.129)
- **Max transfer data length**: 212 bytes per data transfer (Help p.129)
- **Compatible partners**: other LOGO! 8 devices, SIMATIC S7 PLCs, SIMATIC HMI panels (max 1 HMI per LOGO!) (Manual p.27)
- **Address types for read**: Local VB 0-850; Remote VB/DB.DBB/MB/IB/QB 0-65535 (Help p.131)
- **Address types for write**: Local VB/MB/IB/QB; Remote VB/DB.DBB/MB/IB/QB 0-65535 (Help p.132)
- **Constraint**: Local address + Data length - 1 must be <= 850 (Help p.132)
- **Security note**: S7 connections are disabled by default in programs created by LOGO!Soft Comfort V8.3; enabled by default in programs converted from earlier versions (Manual p.292)

### Modbus TCP

**Availability**: LOGO! 8.FS4 (firmware 8.1/8.2) and later versions only (Help p.132)

- **Supported roles**: Client and Server
- **Default port range**: 502 to 510 (Manual p.292, Help p.135)
- **Connection limits**: up to 16 TCP/IP-based S7/Modbus connections total, of which max 8 can be static (Manual p.27-28)
- **Max data transfers per client connection**: 32 (Help p.133)
- **Sync interval**: configurable time interval for data synchronization with server (Help p.133)
- **Unit ID**: configurable for Modbus RTU device addressing (Help p.133)
- **Security note**: Modbus connections are disabled by default in programs created by LOGO!Soft Comfort V8.3 (Manual p.292)
- **Recommendation**: Siemens recommends S7 over Modbus when a device supports both (Manual p.28)

#### Modbus Address Space (CRITICAL)

The mapping between LOGO! resource types and Modbus register addresses (Help p.61):

| LOGO! Type | LOGO! Range | Modbus Object | Modbus Address | Direction | Data Unit |
| --- | --- | --- | --- | --- | --- |
| I (Digital Input) | 1 - 24 | Discrete Input | 1 - 24 | R | bit |
| Q (Digital Output) | 1 - 20 | Coil | 8193 - 8212 | R/W | bit |
| M (Flag) | 1 - 64 | Coil | 8257 - 8320 | R/W | bit |
| V (Variable bit) | 0.0 - 850.7 | Coil | 1 - 6800 | R/W | bit |
| AI (Analog Input) | 1 - 8 | Input Register | 1 - 8 | R | word |
| VW (Variable Word) | 0 - 850 | Holding Register | 1 - 425 | R/W | word |
| AQ (Analog Output) | 1 - 8 | Holding Register | 513 - 520 | R/W | word |
| AM (Analog Flag) | 1 - 64 | Holding Register | 529 - 592 | R/W | word |

**Notes on Modbus address mapping:**
- VW0 maps to Holding Register 1 (offset by 1). VW addresses increment by 2 bytes per register, so VW0 = HR1, VW2 = HR2, ... VW848 = HR425.
- V bit addresses: V0.0 = Coil 1, V0.1 = Coil 2, ... V0.7 = Coil 8, V1.0 = Coil 9, etc., up to V850.7 = Coil 6808 (though table says 6800, representing V0.0 through V849.7 as the usable range).
- Q outputs start at Coil 8193 (not at Coil 1) to avoid overlap with V bit space.
- AI inputs are read-only Input Registers (function code 4).
- AQ outputs start at Holding Register 513, leaving a gap after VW space (HR 1-425).

#### Modbus Client Read Address Restrictions

| Local Address (LOGO!) | Range | Remote Address (Modbus device) | Range |
| --- | --- | --- | --- |
| I | 1 - 24 bit | Coil / Discrete Input | 1 - 65535 bit |
| Q | 1 - 20 bit | Coil / Discrete Input | 1 - 65535 bit |
| M | 1 - 64 bit | Coil / Discrete Input | 1 - 65535 bit |
| V | 0.0 - 850.7 bit | Coil / Discrete Input | 1 - 65535 bit |
| VW | 0 - 850 word | Holding Register / Input Register | 1 - 65535 word |
| AQ | 1 - 8 word | Holding Register / Input Register | 1 - 65535 word |
| AM | 1 - 64 word | Holding Register / Input Register | 1 - 65535 word |
| AI | 1 - 8 word | Holding Register / Input Register | 1 - 65535 word |

(Help p.135)

#### Modbus Client Write Address Restrictions

| Local Address (LOGO!) | Range | Remote Address (Modbus device) | Range |
| --- | --- | --- | --- |
| I | 1 - 24 bit | Coil | 1 - 65535 bit |
| Q | 1 - 20 bit | Coil | 1 - 65535 bit |
| M | 1 - 64 bit | Coil | 1 - 65535 bit |
| V | 0.0 - 850.7 bit | Coil | 1 - 65535 bit |
| VW | 0 - 850 word | Holding Register | 1 - 65535 word |
| AQ | 1 - 8 word | Holding Register | 1 - 65535 word |
| AM | 1 - 64 word | Holding Register | 1 - 65535 word |
| AI | 1 - 8 word | Holding Register | 1 - 65535 word |

(Help p.136)

### Web Server

- **Protocols**: HTTP (port 80) and HTTPS (port 443) (Manual p.245, p.291)
- **Enabling**: via LOGO!Soft Comfort user profile settings; must enable Web user access (Manual p.245)
- **Default password**: "LOGO" (Manual p.247)
- **Max concurrent HTTPS sessions**: 2 connections between LOGO! 8.3 BM and LOGO! Access Tool/Web Browser (Manual p.291)
- **Capabilities** (Manual p.245-254):
  - View system information (module type, FW version, IP address, status)
  - Operate virtual LOGO! Base Module and TDE (cursor keys, function keys, ESC/OK)
  - View and acknowledge message texts
  - Set configurable parameters (double-click to edit)
  - View and edit Variable Memory (VM) tables
  - View LWE (LOGO! Web Editor) projects deployed on BM
- **Supported browsers**: IE 11+, Firefox 30+, Chrome 45+, Safari 10+, Opera 42+ (Manual p.245)
- **Supported devices**: PC, iPhone, iPad, Android 2.0+ smartphones/tablets (Manual p.246)
- **Languages**: German, English, Italian, French, Spanish, Chinese Simplified, Japanese (Manual p.246)
- **Restriction**: When Cloud connection is enabled, Web server / Mobile App / Access Tool connections are unavailable (Manual p.291)

### Cloud IoT (AWS)

- **Availability**: LOGO! 8.3 and later (Manual p.255)
- **Protocol**: MQTT over TLS (OASIS standard v3.1 / v3.1.1) (Manual p.255)
- **Cloud provider**: AWS IoT (Manual p.255)
- **Capabilities**: publish LOGO! BM data to AWS Cloud; change BM data remotely through AWS (Manual p.255)
- **Data format**: AWS Device Shadow (JSON), custom Siemens format (Manual p.257-259)
- **JSON key format**: `"range.sub_range.data_type:start_addr-number":"value"` (Manual p.258)
- **Supported ranges in JSON**: I, Q, M, AI, AQ, AM, NI, NQ, NAI, NAQ, V, VB, VW, VD, CK (Cursor Key), FK (Function Key), SR (Shift Register) (Manual p.258)
- **Configuration**: via LOGO!Soft Comfort V8.3 (register BM to AWS IoT, download Amazon Root CA cert) (Manual p.256)
- **Constraint**: Cloud connection only active when circuit diagram is in RUN mode (Manual p.255)

### NTP (Network Time Protocol)

- **Availability**: LOGO! 8.FS4 and later versions only (Manual p.100)
- **Roles**: NTP Client and/or NTP Server (both can be active simultaneously) (Manual p.101)
- **Default state**: disabled (Manual p.101)
- **Sync interval**: every 4096 seconds; immediate sync on power-on, Stop-to-Run, server IP change, or manual trigger (Manual p.102)
- **Time zone**: configurable, default is GMT (Manual p.102)
- **Limitation**: LOGO! can only recognize IP addresses, not host names (Help p.87)
- **Configuration**: via BM/TDE menu or LOGO!Soft Comfort (Manual p.101)

---

## Network Configuration

### IP Addressing

- **Default IP - LOGO! 0BA8**: 192.168.000.001 (Manual p.105)
- **Default IP - LOGO! TDE**: 192.168.000.002 (Manual p.105)
- **Default IP - LOGO! 8.FS4+**: 192.168.000.003 (Manual p.105)
- **Configurable fields**: IP address, Subnet mask, Gateway (Manual p.104)
- **Access requirement**: Administrator access level required to change network settings (Manual p.104)
- **History**: LOGO! stores up to 4 previously configured addresses (Manual p.105)
- **Configuration tool**: LOGO!Soft Comfort > Tools > Transfer > Configure Network Address, or via BM front panel (Manual p.104, Help p.83)

### Maximum Network Size

A single LOGO! 8 Base Module supports (Manual p.27-28):

- **16** TCP/IP-based S7/Modbus communication connections total
  - Up to **8 static** connections (reserved resources for stable transfer)
  - Remaining connections are **dynamic** (respond only when free resources available)
- **1** TCP/IP Ethernet connection to LOGO! TDE (TDE can switch between BMs but only communicates with one at a time)
- **1** TCP/IP Ethernet connection to a PC running LOGO!Soft Comfort V8.2+

### Network Topology

Typical setup includes (Manual p.29):
- Physical Ethernet connections between devices
- Logical PC-to-LOGO! connection for programming (via TCP/IP Ethernet)
- Logical S7/Modbus connections between SIMATIC devices

### Master/Slave Mode

- A LOGO! 0BA8 operates in either **master** or **slave** mode (Manual p.108)
- **Master mode**: supports client-server communication with S7 PLCs, HMIs, other 0BA8 devices; can also act as master to slave LOGO! devices
- **Slave mode**: functions as a network I/O expansion module; no circuit program required; master reads/writes slave I/O (Manual p.108)
- **Slave I/O limits**: max 24 DI, 8 AI, 20 DQ, 8 AQ (plus own expansion modules) (Manual p.108)
- **Security note**: switching to slave mode enables unsecure ports 102 and 502-510 (Manual p.108)

### Ethernet Cabling

- Max cable length between two LOGO! Base Modules: **100 meters** (CAT5e shielded) (Manual p.321)
- LOGO! TDE connection distance: max **30 meters** (Manual p.342)
- LOGO! CSM12/24 switch: 4x RJ45 ports, 10/100 Mbps, MDI-X, autonegotiation (Manual p.342)

---

## I/O and Data Addressing

### I/O Limits per Base Module

| I/O Type | Identifier | Count |
| --- | --- | --- |
| Digital Inputs | I1 - I24 | 24 |
| Analog Inputs | AI1 - AI8 | 8 |
| Digital Outputs | Q1 - Q20 | 20 |
| Analog Outputs | AQ1 - AQ8 | 8 |
| Digital Flags | M1 - M64 | 64 |
| Analog Flags | AM1 - AM64 | 64 |
| Network Digital Inputs | NI1 - NI64 | 64 |
| Network Analog Inputs | NAI1 - NAI32 | 32 |
| Network Digital Outputs | NQ1 - NQ64 | 64 |
| Network Analog Outputs | NAQ1 - NAQ16 | 16 |
| Shift Register Bits | S1.1 - S4.8 | 32 |
| Cursor Keys | C (up/down/left/right) | 4 |

(Manual p.16-17, p.107-108)

### Variable Memory (VM)

The VM area (V0 through V850) is the local data communication buffer used for data exchange over Ethernet connections. Total user-addressable range: **V0 to V850** (851 bytes). (Help p.136)

VM addressing supports multiple data widths:
- **V** (bit): V0.0 through V850.7 -- individual bits
- **VB** (byte): VB0 through VB850 -- single bytes
- **VW** (word): VW0 through VW849 -- 16-bit words (2 bytes each)
- **VD** (double word): VD0 through VD847 -- 32-bit values (4 bytes each)

(Help p.137, p.182)

### VM Address Mapping: I/O to VM (LOGO! 0BA8)

The following reserved VM regions map physical and network I/O to fixed VM addresses (Help p.139):

| Block Type | VM Address (From) | VM Address (To) | Range |
| --- | --- | --- | --- |
| I (Digital Inputs) | 1024 | 1031 | 8 bytes |
| AI (Analog Inputs) | 1032 | 1063 | 32 bytes |
| Q (Digital Outputs) | 1064 | 1071 | 8 bytes |
| AQ (Analog Outputs) | 1072 | 1103 | 32 bytes |
| M (Digital Flags) | 1104 | 1117 | 14 bytes |
| AM (Analog Flags) | 1118 | 1245 | 128 bytes |
| NI (Network DI) | 1246 | 1261 | 16 bytes |
| NAI (Network AI) | 1262 | 1389 | 128 bytes |
| NQ (Network DQ) | 1390 | 1405 | 16 bytes |
| NAQ (Network AQ) | 1406 | 1469 | 64 bytes |

**Note**: These addresses (1024+) are above the user-configurable range (0-850). They are system-reserved for I/O mirroring.

### VM Address Mapping: I/O to VM (LOGO! 0BA7)

Individual I/O-to-VM mappings for the 0BA7 (also applicable as a reference for 0BA8) (Help p.139-140):

**Digital Inputs and Outputs:**

| DI | VM Address | DQ | VM Address |
| --- | --- | --- | --- |
| I1 | V923.0 | Q1 | V942.0 |
| I2 | V923.1 | Q2 | V942.1 |
| I3 | V923.2 | Q3 | V942.2 |
| I4 | V923.3 | Q4 | V942.3 |
| I5 | V923.4 | Q5 | V942.4 |
| I6 | V923.5 | Q6 | V942.5 |
| I7 | V923.6 | Q7 | V942.6 |
| I8 | V923.7 | Q8 | V942.7 |
| I9 | V924.0 | Q9 | V943.0 |
| I10 | V924.1 | Q10 | V943.1 |
| I11 | V924.2 | Q11 | V943.2 |
| I12 | V924.3 | Q12 | V943.3 |
| I13 | V924.4 | Q13 | V943.4 |
| I14 | V924.5 | Q14 | V943.5 |
| I15 | V924.6 | Q15 | V943.6 |
| I16 | V924.7 | Q16 | V943.7 |
| I17 | V925.0 | | |
| I18 | V925.1 | | |
| I19 | V925.2 | | |
| I20 | V925.3 | | |
| I21 | V925.4 | | |
| I22 | V925.5 | | |
| I23 | V925.6 | | |
| I24 | V925.7 | | |

**Analog Inputs and Outputs:**

| AI | VM Address | AQ | VM Address |
| --- | --- | --- | --- |
| AI1 | VW926 | AQ1 | VW944 |
| AI2 | VW928 | AQ2 | VW946 |
| AI3 | VW930 | | |
| AI4 | VW932 | | |
| AI5 | VW934 | | |
| AI6 | VW936 | | |
| AI7 | VW938 | | |
| AI8 | VW940 | | |

**Analog Flags and Digital Flags:**

| AM | VM Address | M | VM Address |
| --- | --- | --- | --- |
| AM1 | VW952 | M1 | V948.0 |
| AM2 | VW954 | M2 | V948.1 |
| AM3 | VW956 | M3 | V948.2 |
| AM4 | VW958 | M4 | V948.3 |
| AM5 | VW960 | M5 | V948.4 |
| AM6 | VW962 | M6 | V948.5 |
| AM7 | VW964 | M7 | V948.6 |
| AM8 | VW966 | M8 | V948.7 |
| AM9 | VW968 | M9 | V949.0 |
| AM10 | VW970 | M10 | V949.1 |
| AM11 | VW972 | M11 | V949.2 |
| AM12 | VW974 | M12 | V949.3 |
| AM13 | VW976 | M13 | V949.4 |
| AM14 | VW978 | M14 | V949.5 |
| AM15 | VW980 | M15 | V949.6 |
| AM16 | VW982 | M16 | V949.7 |
| | | M17 | V950.0 |
| | | M18 | V950.1 |
| | | M19 | V950.2 |
| | | M20 | V950.3 |
| | | M21 | V950.4 |
| | | M22 | V950.5 |
| | | M23 | V950.6 |
| | | M24 | V950.7 |
| | | M25 | V951.0 |
| | | M26 | V951.1 |
| | | M27 | V951.2 |

### Reserved VM Addresses (Special Purpose)

| VM Address | Reserved For | Size |
| --- | --- | --- |
| 984 | Diagnostic Bits Array | 1 Byte |
| 985 | Year of Real Time Clock (RTC) | 1 Byte |
| 986 | Month of RTC | 1 Byte |
| 987 | Day of RTC | 1 Byte |
| 988 | Hour of RTC | 1 Byte |
| 989 | Minute of RTC | 1 Byte |
| 990 | Second of RTC | 1 Byte |

LOGO! BM can also share time and date information with S7/Modbus devices using VM addresses 991-1002. (Help p.141)

### Data Types Shareable via VM

| Data Type | Count | Memory Type |
| --- | --- | --- |
| Digital input | 24 | Byte |
| Digital output | 16 | Byte |
| Digital flag | 27 | Byte |
| Analog input | 8 | Word |
| Analog output | 2 | Word |
| Analog flag | 16 | Word |
| Value parameter | varies | varies |
| Actual value | varies | varies |

(Help p.141)

### Parameter VM Mapping

Up to **64 parameters** can be mapped to VM addresses per Base Module. The mapping links SFB (Special Function Block) parameters to specific VM addresses so they can be read/written by partner devices over S7 or Modbus. (Help p.137-138)

Parameter address range: **0 to 850**. LOGO!Soft Comfort reserves some bytes; addresses above 850 are system-reserved for I/O mapping. (Help p.138)

Parameter properties:
- Writable setting value (pen icon)
- Read-only actual value (lock icon)
- Writable actual value (only Counter parameter of Up/Down Counter)
- Referenced value from another function block

Analog values viewable range: -32768 to 32767 (16-bit signed). Values exceeding this range are clamped. (Help p.141)

---

## Connection Parameters

### Port Numbers Summary

| Port | Protocol/Service | Security | Notes |
| --- | --- | --- | --- |
| 80 | HTTP (Web Server) | Unsecured | Web server access (Manual p.291) |
| 102 | S7 (ISO-on-TCP) | Unsecured | S7 communication (Manual p.292) |
| 135 | TCP (TDE) | Unsecured | LOGO! TDE to BM connection, enabled by default (Manual p.292) |
| 443 | HTTPS (Web Server) | TLS | Secure web server access (Manual p.291) |
| 502-510 | Modbus TCP | Unsecured | Modbus communication, 9 ports available (Manual p.292) |
| 8080 | HTTP (Mobile App) | Unsecured | LOGO! Mobile APP, does not support HTTPS (Manual p.291) |
| 8443 | HTTPS (LSC/LWE) | TLS | LOGO!Soft Comfort V8.3 / LOGO! Web Editor V1.1 to BM/TDE (Manual p.291) |

### Max Simultaneous Connections

| Connection Type | Max Count | Notes |
| --- | --- | --- |
| S7/Modbus communication | 16 total | Up to 8 static + remaining dynamic (Manual p.27) |
| Static connections | 8 | Reserved resources for stable transfer (Manual p.28) |
| LOGO! TDE | 1 | Per Base Module (Manual p.28) |
| LOGO!Soft Comfort | 1 | Per Base Module (Manual p.28, p.291) |
| Web server (HTTPS) | 2 | LOGO! Access Tool / Web Browser combined (Manual p.291) |
| Cloud (AWS) | 1 | Exclusive: disables Web/Mobile/Access Tool when active (Manual p.291) |
| Data transfers per client connection | 32 | Per S7 or Modbus client connection (Help p.129, p.133) |

### Timeout and Cycle Information

- **Cycle time per function block**: < 0.1 ms (Manual p.321)
- **Startup time at power-up**: typ. 1.2 s (Manual p.321)
- **NTP sync interval**: 4096 seconds (Manual p.102)
- **Max data transfer length**: 212 bytes per individual data transfer (Help p.129)

---

## Network Security

### Security Architecture (LOGO! 8.3)

LOGO! 8.3 uses HTTPS for the following connections (Manual p.290):
- LOGO!Soft Comfort V8.3 <-> LOGO! 8.3 TDE (port 8443)
- LOGO! BM <-> LOGO!Soft Comfort V8.3 / LOGO! Web Editor V1.1 (port 8443)
- LOGO! Access Tool / Web Browser <-> LOGO! 8.3 BM (port 443)

Cloud connection uses MQTT over TLS. (Manual p.291)

### Access Control

- **Dynamic Server IP Filter (ACL)**: up to 8 allowed IP addresses can be configured; or allow all requests (Help p.108-109)
- **Web server accounts**: Web User (full access) and Web Guest (limited access) (Manual p.291)
- **Menu access levels**: Administrator (full) and Operator (restricted menus); default password "LOGO" (Manual p.295)
- **Program password**: protects circuit program from unauthorized reading/editing (Manual p.293)
- **Program copy protection**: binds circuit program to specific micro SD card (Manual p.293)
- **Circuit program encryption**: programs created in LOGO! 8 (6ED1052-xxx08-0BA1) and later are encrypted (Manual p.293)

### Security Recommendations (from Siemens)

- Enable HTTPS for Web server access (Manual p.292)
- Use strong passwords (10+ chars, mixed letters/numbers/special) (Manual p.292)
- Use VPN when connecting via HTTP (Manual p.292)
- Open ports only at firewalls within a Secure Network (Manual p.292)
- Protect physical access to LOGO! devices (lock in cabinet) (Manual p.290)
- S7/Modbus protocol allows unauthenticated access; protect with network-level security (Manual p.290)

---

## LOGO! TDE Technical Data

| Parameter | Value |
| --- | --- |
| Display | FSTN-Graphic, 160 x 96 pixels, LED backlight (white/amber/red) |
| Keyboard | Membrane keypad, 10 keys |
| Input voltage | 24 VAC/VDC or 12 VDC |
| Permissible range | 20.4-26.4 VAC / 10.2-28.8 VDC |
| Power consumption (12 VDC) | typ. 150 mA |
| Power consumption (24 VDC) | typ. 75 mA |
| Ethernet | Two 10/100M full/half duplex ports |
| Max connection distance | 30 m |
| Protection | IP20 (body), IP65 (front panel) |
| Backlight lifetime | 20,000 hours |
| Display lifetime | 50,000 hours |
| BM connection port | 135 (TCP, unsecured) |
| Dimensions (WxHxD) | 128.2 x 86 x 38.7 mm |
| Weight | approx. 220 g |

(Manual p.341-342)

---

## Memory and Program Resources

| Resource | LOGO! 0BA8 Limit |
| --- | --- |
| Program memory | 8500 bytes |
| Max blocks | 400 |
| Retentive memory (REM) | 250 bytes |
| User VM range | V0 - V850 (851 bytes) |
| Max VM parameter mappings | 64 |

(Manual p.116, Help p.138)

---

## Protocol Support Summary Table

| Protocol | Supported | Role | Default Port(s) | Min FW Version | Notes |
| --- | --- | --- | --- | --- | --- |
| S7 (ISO-on-TCP) | Yes | Client/Server | 102 | 0BA7 | Unsecured; disabled by default in V8.3 programs |
| Modbus TCP | Yes | Client/Server | 502-510 | 8.FS4 (8.1) | Unsecured; disabled by default in V8.3 programs |
| HTTP (Web Server) | Yes | Server | 80 | 0BA8 | Web server for browser/mobile access |
| HTTPS (Web Server) | Yes | Server | 443 | 8.3 | Recommended; requires LOGO! Root certificate |
| HTTPS (LSC/LWE) | Yes | Server | 8443 | 8.3 | LOGO!Soft Comfort / Web Editor connection |
| HTTP (Mobile App) | Yes | Server | 8080 | 0BA8 | LOGO! Mobile APP; no HTTPS support |
| TCP (TDE) | Yes | Server | 135 | 0BA8 | LOGO! TDE connection; unsecured |
| MQTT over TLS | Yes | Client | varies | 8.3 | AWS IoT Cloud connection |
| NTP | Yes | Client/Server | 123 (standard) | 8.FS4 | Network time synchronization |
| OPC UA | No | -- | -- | -- | Not supported on LOGO! 8 |
| Ethernet/IP | No | -- | -- | -- | Not supported; uses S7 protocol instead |
| PROFINET | No | -- | -- | -- | Not supported on LOGO! 8 |

---

## AWS Cloud JSON Data Format Reference

For Cloud data exchange, LOGO! uses a custom JSON format in the AWS Device Shadow (Manual p.258-259):

**Key format**: `"range.sub_range.data_type:start_addr-number":"value"`

| Field | Required | Description |
| --- | --- | --- |
| range | Yes | Block type: I, Q, M, AI, AQ, AM, NI, NQ, NAI, NAQ, V, VB, VW, VD, CK, FK, SR (uppercase) |
| sub_range | No | Reserved |
| data_type | No | 1=bit, 2=byte, 4=word, 6=double word |
| start_addr | Yes | Starting address of data |
| number | Yes | Length of data value (unit depends on data_type) |
| value | Yes | Hex string |

**Data type defaults by range:**

| Range Category | Ranges | Default data_type | start_addr range |
| --- | --- | --- | --- |
| Bit range | I, Q, M, NI, NQ, CK, FK | 1 | 1 to n |
| Word range | AI, AM, AQ, NAI, NAQ | 4 | 1 to n |
| V range | V | 1, 2, 4, or 6 (default 2) | 0 to n (bit: 0.0) |
| Shift register | SR | 1 | 1.1 to n.8 |

**Examples:**
- Read Q1-Q2: `"Q..1:1-2":"03"` (bit range, 2 outputs, hex value 03 = Q1 on, Q2 on)
- Read AI2-AI3: `"AI..4:2-2":"22223333"` (word range, 2 analog inputs)
- Read VB0-VB1: `"V..2:0-2":"0011"` (byte range, 2 bytes)
- Read VW2-VW3: `"V..4:2-2":"22334455"` (word range, 2 words)
- Read VD3: `"V..6:3-1":"33445566"` (dword range, 1 double word)

**Parsing rules:**
- Values not byte-aligned get '0' prepended (e.g., "3" becomes "03")
- Left-aligned parsing for multi-element values
- Short values: remaining elements default to 0
- Long values: extra data is discarded
