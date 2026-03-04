# S7-300 Communication Reference

> Extracted from *S7-300 Automation System, Hardware and Installation: CPU 312IFM–318-2 DP* (A5E00203919-01) and *S7-300 Module Data Equipment Manual* (A5E00105505-AK, 05/2022).

---

## 1. Product Overview

### 1.1 CPU Models in the S7-300 Family

The S7-300 CPUs covered in the installation manual span from CPU 312 IFM to CPU 318-2 DP. Key models with communication relevance:

| CPU | Order Number | MPI | PROFIBUS DP | Notes |
|-----|-------------|-----|-------------|-------|
| CPU 312 IFM | — | Yes (187.5 kbps) | No | Single-rack only; 10 DI / 6 DO integrated |
| CPU 313 | — | Yes (187.5 kbps) | No | Single-rack only |
| CPU 314 IFM | — | Yes (187.5 kbps) | No | 20 DI / 16 DO / 4 AI / 1 AO integrated |
| CPU 315 | 6ES7 315-1AF03-0AB0 | Yes (187.5 kbps) | No | Supports user-defined addressing |
| CPU 315-2 DP | 6ES7 315-2AF03-0AB0 | Yes (187.5 kbps) | Yes (master or slave) | DP address area: 1024 bytes |
| CPU 316-2 DP | 6ES7 316-2AG00-0AB0 | Yes (187.5 kbps) | Yes (master or slave) | DP address area: 2048 bytes |
| CPU 318-2 DP | 6ES7 318-2AJ00-0AB0 | Yes (up to 12 Mbps) | Yes (master or slave) | DP address area: 8192 bytes; DPV1 support |

*(IHB p23–26, p60–64, p107, p135)*

### 1.2 Communication Interfaces

All S7-300 CPUs have a built-in MPI interface. The "-2 DP" variants (315-2, 316-2, 318-2) add a second PROFIBUS DP port. Industrial Ethernet and point-to-point links require optional CP modules.

### 1.3 Rack and Slot System

- Rack 0 (central unit): PS in slot 1, CPU in slot 2, optional IM in slot 3, then up to 8 signal/function/communication modules in slots 4–11.
- Racks 1–3 (expansion): connected via IM 360/361 (up to 10 m) or IM 365 (1 m, hardwired pair). Each rack holds up to 8 modules.
- Maximum 4 racks total (rack 0 + 3 expansion racks).
- IM 365 does **not** route the communication bus to rack 1 — FMs/CPs with comm bus function cannot be placed there.
- Backplane bus current limit: 1.2 A per rack (0.8 A for CPU 312 IFM).

*(IHB p35–37; Module Data p427–432)*

---

## 2. Communication Protocols

### 2.1 MPI (Multi-Point Interface)

MPI is the default programming and networking interface on every S7-300 CPU.

| Parameter | Value |
|-----------|-------|
| Default baud rate | 187.5 kbps |
| Optional baud rates | 19.2 kbps (for S7-200 communication); up to 12 Mbps (CPU 318-2 DP only) |
| Max nodes per subnet | 127 (addresses 0–126); default address space = 32 |
| Reserved addresses | 0 = PG, 1 = OP, 2 = CPU (recommended default) |
| Max cable length (segment) | 50 m at 187.5 kbps (non-isolated interface); 1000 m at 187.5 kbps (isolated, e.g. CPU 318-2 DP) |
| Physical layer | RS-485, shielded twisted-pair PROFIBUS cable |

**Key behaviour:**
- MPI retains its last-configured transmission rate, node number and highest MPI address even after memory reset or power loss.
- The CPU automatically broadcasts its bus parameters so a PG can auto-detect and connect.
- During RUN mode only PGs may be connected; connecting OPs/TPs while running risks data corruption.

**MPI address assignment for CPs/FMs in one station:**
- *Option 1 (manual):* Assign arbitrary MPI addresses in STEP 7.
- *Option 2 (default/auto):* CPU address, CPU address +1, CPU address +2.
- *CPU 318-2 DP special:* Uses only one MPI address for CPU and all attached CPs.

*(IHB p58–64, p68, p70–71, p120–124)*

### 2.2 PROFIBUS DP

PROFIBUS DP is available as a built-in second interface on CPU 31x-2 DP variants, or via CP 342-5 communication processors.

| Parameter | Value |
|-----------|-------|
| Baud rates | 9.6 kbps to 12 Mbps |
| Max nodes per subnet | 126 (addresses 0–125); 1 master reserved, 1 PG connection (address 0) |
| Master classes | Class 1 (cyclic I/O) and Class 2 (acyclic/diagnostics) |
| Interface modes | DP Master or DP Slave (configurable per CPU) |
| DPV1 support | CPU 318-2 DP (firmware >= V3.0) |

**Cable specifications (PROFIBUS copper):**

| Property | Value |
|----------|-------|
| Impedance | 135–160 ohm (3–20 MHz) |
| Loop resistance | <= 115 ohm/km |
| Effective capacitance | 30 nF/km |
| Attenuation | 0.9 dB/100 m (200 kHz) |
| Conductor cross-section | 0.3–0.5 mm² |
| Cable diameter | 8 mm +/- 0.5 mm |
| Bending radius (one-off) | >= 80 mm |
| Bending radius (repeated) | >= 160 mm |

**Max cable lengths per segment:**

| Baud Rate | Max Segment Length |
|-----------|--------------------|
| 9.6 kbps – 187.5 kbps | 1000 m |
| 500 kbps | 400 m |
| 1.5 Mbps | 200 m |
| 3 Mbps – 12 Mbps | 100 m |

**Stub cable limits per segment:**

| Baud Rate | Max Stub Length | Max Stubs (6.6 m) | Max Stubs (1 m) |
|-----------|----------------|--------------------|-----------------|
| 9.6–93.75 kbps | 96 m total | 32 | 32 |
| 187.5 kbps | 75 m total | 32 | 25 |
| 500 kbps | 30 m total | 20 | 10 |
| 1.5 Mbps | 10 m total | 6 | 3 |
| 3–12 Mbps | PG patch cord only | — | — |

**Important:** At 3 Mbps and above, use the PG patch cord (6ES7 901-4BD00-0XA0) only. No other stub cables are permitted.

*(IHB p60–69)*

### 2.3 Industrial Ethernet

S7-300 CPUs can only connect to Industrial Ethernet via communication processors (CP 343-1 family). The CPUs have no built-in Ethernet port.

- Used at process and cell level for high-volume, high-speed data exchange.
- Supports S7 communication, TCP/IP, and ISO transport protocols.
- Provides offsite networking options via gateway.

*(IHB p59)*

### 2.4 Point-to-Point (PtP) Communication

Point-to-point serial communication is available via CP 340 and CP 341 modules.

| Interface | Protocols |
|-----------|-----------|
| RS-232C | ASCII, 3964(R), RK 512 |
| RS-422/485 | ASCII, 3964(R), RK 512 |
| 20 mA TTY | ASCII, 3964(R) |

*(IHB p64)*

### 2.5 ASI (Actuator/Sensor Interface)

ASI is the lowest-level subnet for networking digital sensors and actuators (max 4 bits per slave station). Requires a communication processor — no built-in ASI support on S7-300 CPUs.

*(IHB p59)*

---

## 3. Network Configuration

### 3.1 Network Topologies

The S7-300 uses a **linear bus topology** for both MPI and PROFIBUS. Key topology rules:

- A **segment** is a bus link between two terminating resistors, with up to 32 nodes.
- Segments are extended using RS-485 repeaters (up to 9 repeaters in series).
- Each segment must be terminated at both ends. The terminating resistor is built into the bus connector (switch to ON position). Bus connector 6ES7 972-0BA30-0XA0 has no terminating resistor and cannot be used at segment ends.
- Terminating resistors draw power from the station — if a station at the segment end is powered off, the terminator has no effect and bus errors may occur.
- The PROFIBUS Terminator can be used as an active (externally powered) bus termination alternative.

**Typical MPI subnet layout:**
- Multiple S7-300 stations, OPs, and PGs connected on a single bus segment.
- PGs typically connected via stub cable for commissioning/maintenance.
- RS-485 repeaters used to extend beyond 50 m segments.

**Typical PROFIBUS subnet layout:**
- CPU 31x-2 DP as master with ET 200M, ET 200B, ET 200S, S5-95U, or other S7-300 DP slaves.
- Can combine MPI and PROFIBUS: a CPU 31x-2 DP is simultaneously an MPI node and a PROFIBUS master/slave.

**Routing across network boundaries:**
- STEP 7 V5.0+ supports PG access across subnet boundaries.
- Requires modules with routing capability at network boundaries.
- All networks must be configured in NETPRO, compiled, and downloaded to every router.

*(IHB p70–76)*

### 3.2 Network Components

| Component | Order Number | Purpose |
|-----------|-------------|---------|
| RS-485 bus connector (90°, no PG port) | 6ES7 972-0BA11-0XA0 | Connect PROFIBUS cable to MPI/DP interface |
| RS-485 bus connector (90°, with PG port) | 6ES7 972-0BB11-0XA0 | Same, plus inline PG connection point |
| Fast Connect bus connector (90°, no PG) | 6ES7 972-0BA50-0XA0 | Insulation-displacement technology |
| Fast Connect bus connector (90°, with PG) | 6ES7 972-0BB50-0XA0 | Same with PG port |
| RS-485 bus connector (35°, no PG) | 6ES7 972-0BA40-0XA0 | Angled exit (not for CPU 31xC, 312, some 314/315-2 DP) |
| RS-485 bus connector (35°, with PG) | 6ES7 972-0BB40-0XA0 | Same with PG port |
| RS-485 repeater | 6ES7 972-0AA00-0XA0 | Amplifies signals, couples segments |
| PG patch cord | 6ES7 901-4BD00-0XA0 | Required for PG connection at > 3 Mbps |

**RS-485 Repeater notes:**
- Required when: exceeding 32 nodes per segment, exceeding max segment cable length, or bridging grounded and ungrounded segments.
- Up to 9 repeaters in series permitted.
- Each repeater counts as a node for subnet sizing, even though it does not have its own MPI/PROFIBUS address.
- Max cable length between two repeaters equals the segment length for the configured baud rate.

**Bus cable options:**

| Cable Type | Order Number |
|------------|-------------|
| PROFIBUS cable (standard) | 6XV1 830-0AH10 |
| PROFIBUS cable (halogen-free) | 6XV1 830-0CH10 |
| PROFIBUS underground cable | 6XV1 830-3AH10 |
| PROFIBUS trailing cable | 6XV1 830-3BH10 |
| PROFIBUS cable (PUR sheath, chemical/mechanical) | 6XV1 830-0DH10 |
| PROFIBUS cable (PE sheath, food & beverage) | 6XV1 830-0BH10 |
| PROFIBUS cable (festooning) | 6XV1 830-3CH10 |

*(IHB p65–69)*

---

## 4. I/O Module Addressing

### 4.1 Slot-Based Addressing (Default)

Each slot has a fixed module start address. Input and output addresses share the same start address.

**Rack 0 (central unit):**

| Slot | Digital Start Address | Analog Start Address |
|------|----------------------|---------------------|
| 4 | 0 | 256 |
| 5 | 4 | 272 |
| 6 | 8 | 288 |
| 7 | 12 | 304 |
| 8 | 16 | 320 |
| 9 | 20 | 336 |
| 10 | 24 | 352 |
| 11 | 28 | 368 |

**Rack 1:**

| Slot | Digital Start Address | Analog Start Address |
|------|----------------------|---------------------|
| 4 | 32 | 384 |
| 5 | 36 | 400 |
| 6 | 40 | 416 |
| 7 | 44 | 432 |
| 8 | 48 | 448 |
| 9 | 52 | 464 |
| 10 | 56 | 480 |
| 11 | 60 | 496 |

**Rack 2:** Digital starts at 64 (analog 512); **Rack 3:** Digital starts at 96 (analog 640). Each slot increments by 4 (digital) or 16 (analog).

### 4.2 Digital Module Addressing

- Address = byte address + bit address.
- Byte address comes from the module start address; bit address is the channel number printed on the module (0–7).
- Example: a 16-channel DI module in slot 4 occupies byte 0, bits 0–7 and byte 1, bits 0–7, giving addresses I 0.0 through I 1.7.

### 4.3 Analog Module Addressing

- Each analog channel occupies a 16-bit word address.
- First analog module in slot 4 starts at address 256; channels are at 256, 258, 260, etc.
- Analog I/O modules share the same start address for inputs and outputs.

### 4.4 User-Defined Addressing

Available on CPUs 315, 315-2 DP, 316-2 DP, and 318-2 DP (requires firmware V1.0.0+ / V3.0.0+ for 318-2). Configured in STEP 7 HW Config. Eliminates address gaps and enables standardized software addressing.

### 4.5 Integrated I/O Addresses

**CPU 312 IFM:** 10 DI at 124.0–125.1; 6 DO at 124.0–124.5.

**CPU 314 IFM:** 20 DI at 124.0–126.3; 16 DO at 124.0–125.7; 4 AI at 128–135; 1 AO at 128–129.

### 4.6 Consistent Data

- CPUs 315-2 DP and 316-2 DP: consistent data is not automatically updated in the process image even if the addresses are within the PI range. Use SFC 14 (DPRD_DAT) and SFC 15 (DPWR_DAT) to read/write consistent data.
- CPU 318-2 DP (firmware >= V3.0): you can choose whether to update consistent data in the process image. Direct access (L PEW / T PAW) is also possible.
- Maximum consistent data transfer: 32 bytes per area.

*(IHB p105–112)*

---

## 5. PROFIBUS DP Commissioning

### 5.1 DP Address Areas by CPU

| CPU | DP Address Area (I/Os) | Process Image Range |
|-----|----------------------|---------------------|
| CPU 315-2 DP | 1024 bytes | Bytes 0–127 |
| CPU 316-2 DP | 2048 bytes | Bytes 0–127 |
| CPU 318-2 DP | 8192 bytes | Bytes 0–255 (default), configurable up to byte 2047 |

### 5.2 Software Requirements

| CPU | STEP 7 | COM PROFIBUS |
|-----|--------|--------------|
| CPU 315-2 DP | STEP 7 V3.1+ | COM PROFIBUS V3.0+ |
| CPU 316-2 DP | STEP 7 V5.x+ | COM PROFIBUS V5.0+ |
| CPU 318-2 DP | STEP 7 V5.x+ | COM PROFIBUS V5.0+ |

### 5.3 Commissioning as DP Master

1. Configure the CPU as DP master in STEP 7 HW Config: assign PROFIBUS address, master diagnostic address, and integrate DP slaves.
2. Download the PROFIBUS subnet configuration from PG to CPU.
3. Power on all DP slaves.
4. Switch CPU from STOP to RUN.

**Start-up behaviour:**
- If preset config = actual config: CPU goes to RUN.
- If mismatch and "Start-up with preset configuration not equal to actual configuration = Yes": CPU goes to RUN but BUSF LED flashes for unreachable slaves.
- If mismatch and setting = No: CPU stays in STOP; BUSF LED flashes after monitoring timeout expires.

**Important:** Do not assign address 0 as a PROFIBUS address. Always program OB 82 (diagnostic interrupt) and OB 86 (rack failure) when commissioning as DP master.

### 5.4 Commissioning as DP Slave

1. Configure the CPU as DP slave in STEP 7: assign PROFIBUS address, slave diagnostic address, specify S7 or non-S7 master, define address areas for data exchange.
2. Power on, keep CPU in STOP.
3. Power on all other DP masters/slaves.
4. Switch CPU to RUN.

**Transfer memory:**
- Up to 32 I/O address areas configurable.
- Max 32 bytes per address area.
- Max 244 input bytes and 244 output bytes total.
- Data exchange uses SFC 14 (DPRD_DAT) and SFC 15 (DPWR_DAT), or load/transfer instructions for process-image addresses.

**GSD file:** Required for configuring CPU 31x-2 DP as a slave in non-Siemens or older DP masters. Included in COM PROFIBUS V4.0+.

### 5.5 Programming and Status/Control via PROFIBUS

As an alternative to the MPI interface, you can program the CPU and execute Status/Modify functions via the PROFIBUS DP interface. This must be enabled in STEP 7 configuration (for slave mode). Using Status/Control via PROFIBUS extends the DP cycle time.

### 5.6 Direct Data Exchange

Available in STEP 7 V5.x+. PROFIBUS nodes "listen" on the bus for data a DP slave returns to its master, enabling receivers to access input data from remote slaves without routing through the master.

- Sender: DP slave.
- Receiver: DP slave, DP master, or CPU not integrated in a master system.
- Other DP slaves (ET 200M, ET 200X, ET 200S) can only be senders.

### 5.7 DP Event Recognition

**Events detected by DP Master (CPU 31x-2):**

| Event | Response |
|-------|----------|
| Bus failure (short-circuit, connector unplugged) | OB 86 called (station failure); OB 122 on I/O access |
| DP slave RUN to STOP | OB 82 called (module error, OB82_MDL_STOP=1) |
| DP slave STOP to RUN | OB 82 called (module OK, OB82_MDL_STOP=0) |

**Events detected by DP Slave (CPU 31x-2):**

| Event | Response |
|-------|----------|
| Bus failure (short-circuit, connector unplugged) | OB 86 called (station failure); OB 122 on I/O access |
| DP master RUN to STOP | OB 82 called (module error, OB82_MDL_STOP=1) |
| DP master STOP to RUN | OB 82 called (module OK, OB82_MDL_STOP=0) |

**STOP behaviour:**
- DP slave goes to STOP: transfer memory overwritten with 0; DP master reads 0.
- DP master goes to STOP: actual data in slave transfer memory is maintained and can still be read.

### 5.8 DP Diagnostics

Diagnostic addresses occupy 1 byte per DP master and DP slave in the input address area. STEP 7 assigns these from the highest byte address downward if not manually specified.

For CPU 318-2 DP as DPV1 master, two diagnostic addresses are assigned per I-Slave:
- Slot 0 address: reports all slave-level events (e.g., node failure).
- Slot 2 address: reports module-level events (e.g., operating mode transitions).

**Diagnostic evaluation in user program:**
1. OB 82 called with `OB82_MDL_ADDR` (diagnostic address) and `OB82_IO_FLAG`.
2. Read complete slave diagnostics with SFC 13 (DPNRM_DG) — asynchronous, may require multiple calls.
3. Or use SFB 54 (RALRM) with MODE=1 for interrupt information (CPU 318-2 DP).
4. Or use SFC 51 (RDSYSST) with SZL_ID W#16#00B3 for module diagnostic data.

*(IHB p135–146, p170–180)*

---

## 6. Communication Modules (CPs)

### 6.1 CP 342-5 (PROFIBUS)

Connects the S7-300 to PROFIBUS DP as an additional DP interface (separate from the CPU's built-in DP port if present). Occupies a standard module slot. Configured via STEP 7.

### 6.2 CP 343-1 (Industrial Ethernet)

Connects the S7-300 to Industrial Ethernet. Supports S7 communication, TCP/IP, and ISO transport. This is the **only** way to connect an S7-300 to Ethernet — no CPU has a built-in Ethernet port.

### 6.3 CP 340 / CP 341 (Point-to-Point)

Serial communication processors supporting RS-232C, RS-422/RS-485, and 20 mA (TTY) interfaces with ASCII, 3964(R), and RK 512 protocols.

### 6.4 CP Addressing

CPs installed in an S7-300 station can receive MPI addresses in two ways:
- Explicitly assigned in STEP 7 (option 1).
- Auto-assigned by the CPU as CPU_addr + 1, CPU_addr + 2, etc. (default).

With CPU 318-2 DP, CPs do not have separate MPI addresses — the CPU's single MPI address covers all attached CPs/FMs.

In addition to an MPI address, a CP with PROFIBUS connectivity also has a separate PROFIBUS address.

*(IHB p25, p62, p70)*

---

## 7. I/O Module Types Summary

### 7.1 Digital Input Modules (SM 321)

| Module | Inputs | Voltage | Key Features |
|--------|--------|---------|-------------|
| DI 64 x DC 24V (-1BP00-) | 64 | 24 VDC | Sinking/sourcing |
| DI 32 x DC 24V (-1BL00-) | 32 | 24 VDC | Standard |
| DI 32 x AC 120V (-1EL00-) | 32 | 120 VAC | AC inputs |
| DI 16 x DC 24V (-1BH02-) | 16 | 24 VDC | Standard |
| DI 16 x DC 24V HS (-1BH10-) | 16 | 24 VDC | Isochronous mode |
| DI 16 x DC 24V (-7BH01-) | 16 | 24 VDC | Diagnostic/hardware interrupt |
| DI 16 x DC 24/125V (-7EH00-) | 16 | 24–125 VDC | Diagnostic/hardware interrupt |
| DI 16 x DC 24V source (-1BH50-) | 16 | 24 VDC | Source input |
| DI 16 x UC 24/48V (-1CH00-) | 16 | 24–48 VDC/VAC | Universal |
| DI 16 x DC 48-125V (-1CH20-) | 16 | 48–125 VDC | High voltage |
| DI 16 x AC 120/230V (-1FH00-) | 16 | 120/230 VAC | AC mains |
| DI 8 x AC 120/230V (-1FF01-) | 8 | 120/230 VAC | AC mains |
| DI 8 x AC 120/230V ISOL (-1FF10-) | 8 | 120/230 VAC | Individually isolated |

### 7.2 Digital Output Modules (SM 322)

| Module | Outputs | Current | Voltage | Key Features |
|--------|---------|---------|---------|-------------|
| DO 64 x DC 24V/0.3A sourcing (-1BP00-) | 64 | 0.3 A | 24 VDC | High density |
| DO 64 x DC 24V/0.3A sinking (-1BP50-) | 64 | 0.3 A | 24 VDC | High density |
| DO 32 x DC 24V/0.5A (-1BL00-) | 32 | 0.5 A | 24 VDC | Standard |
| DO 32 x AC 120/230V/1A (-1FL00-) | 32 | 1.0 A | 120/230 VAC | AC outputs |
| DO 16 x DC 24V/0.5A (-1BH01-) | 16 | 0.5 A | 24 VDC | Standard |
| DO 16 x DC 24V/0.5A HS (-1BH10-) | 16 | 0.5 A | 24 VDC | Isochronous |
| DO 16 x DC 24V/0.5A (-8BH10-) | 16 | 0.5 A | 24 VDC | Diagnostics, substitute values |
| DO 8 x DC 24V/2A (-1BF01-) | 8 | 2.0 A | 24 VDC | High current |
| DO 8 x DC 24V/0.5A diag (-8BF00-) | 8 | 0.5 A | 24 VDC | Diagnostic interrupt |
| DO 8 x AC 120/230V/2A (-1FF01-) | 8 | 2.0 A | 120/230 VAC | Fuse per group |
| DO 8 x AC 120/230V/2A ISOL (-5FF00-) | 8 | 2.0 A | 120/230 VAC | Individually isolated, diagnostics |

### 7.3 Relay Output Modules (SM 322)

| Module | Outputs | Voltage | Key Features |
|--------|---------|---------|-------------|
| DO 16 x Rel. AC 120V (-1HH01-) | 16 | 24–120 VDC / 48–230 VAC | Groups of 8 |
| DO 8 x Rel. AC 230V (-1HF01-) | 8 | 24–120 VDC / 48–230 VAC | Groups of 2 |
| DO 8 x Rel. AC 230V/5A (-5HF00-) | 8 | 24–120 VDC / 24–230 VAC | Individually isolated, diagnostics |
| DO 8 x Rel. AC 230V/5A (-1HF10-) | 8 | 24–120 VDC / 48–230 VAC | Individually isolated |

### 7.4 Analog Input Modules (SM 331)

| Module | Channels | Resolution | Measurement Types |
|--------|----------|-----------|-------------------|
| AI 8 x 16 Bit (-7NF00-) | 8 | 15 bits + sign | Voltage, Current |
| AI 8 x 16 Bit (-7NF10-) | 8 | 15 bits + sign | Voltage, Current |
| AI 8 x 14 Bit HS (-7HF0x-) | 8 | 13 bits + sign | Voltage, Current |
| AI 8 x 13 Bit (-1KF02-) | 8 | 12 bits + sign | Voltage, Current, Resistance, Temperature |
| AI 8 x 12 Bit (-7KF02-) | 8 | 9–14 bits + sign | Voltage, Current, Resistance, Temperature |
| AI 2 x 12 Bit (-7KB02-) | 2 | 9–14 bits + sign | Voltage, Current, Resistance, Temperature |
| AI 8 x RTD (-7PF01-) | 8 | 15 bits + sign | Resistance, Temperature |
| AI 8 x TC (-7PF11-) | 8 | 15 bits + sign | Temperature (thermocouple) |
| AI 6 x TC isolated (-7PE10-) | 6 | 15 bits + sign | Voltage, Temperature |

### 7.5 Analog Output Modules (SM 332)

| Module | Channels | Resolution | Output Types |
|--------|----------|-----------|-------------|
| AO 8 x 12 Bit (-5HF00-) | 8 | 12 bits | Voltage, Current |
| AO 4 x 16 Bit (-7ND02-) | 4 | 16 bits | Voltage, Current (isochronous) |
| AO 4 x 12 Bit (-5HD01-) | 4 | 12 bits | Voltage, Current |
| AO 2 x 12 Bit (-5HB01-) | 2 | 12 bits | Voltage, Current |

### 7.6 Analog I/O Modules (SM 334)

| Module | Inputs | Outputs | Resolution |
|--------|--------|---------|-----------|
| AI 4/AO 2 x 8/8 Bit (-0CE01-) | 4 | 2 | 8 bits |
| AI 4/AO 2 x 12 Bit (-0KE00-) | 4 | 2 | 12 bits + sign |

### 7.7 Interface Modules (IM)

| Module | Order Number | Rack Position | Max Distance | Notes |
|--------|-------------|--------------|-------------|-------|
| IM 360 | 6ES7 360-3AA01-0AA0 | Rack 0 (send) | 10 m | Routes comm bus and backplane |
| IM 361 | 6ES7 361-3CA01-0AA0 | Rack 1–3 (receive) | 10 m | 24 VDC supply, 0.8 A backplane |
| IM 365 | 6ES7 365-0BA01-0AA0 | Rack 0+1 (pair) | 1 m (fixed cable) | Does NOT route comm bus to rack 1 |

*(Module Data p46–51, p251–255, p427–432)*

---

## 8. Connection Parameters — Quick Reference

### 8.1 MPI Defaults

| Parameter | Default Value |
|-----------|--------------|
| Baud rate | 187.5 kbps |
| Highest MPI address | 31 (address space = 32) |
| PG address | 0 |
| OP address | 1 |
| CPU address | 2 |
| Max nodes | 32 (expandable to 127 via STEP 7) |

### 8.2 PROFIBUS DP Defaults

| Parameter | Default Value |
|-----------|--------------|
| PG address | 0 (reserved for service PG) |
| Baud rate | Set in STEP 7 during configuration |
| DP diagnostic addresses | Assigned by STEP 7 from highest byte address downward if not manually specified |

### 8.3 Equidistant Mode

As of STEP 7 V5.x, equidistant (constant bus cycle time) PROFIBUS operation can be configured for deterministic data exchange.

---

## 9. Surge Protection for Networked PLCs

When S7-300 PLCs are networked across cabinets or buildings, the following lightning/surge protection zones apply:

| Zone Transition | Protection Required | Example Component |
|----------------|--------------------|--------------------|
| Zone 0 to 1 (building entry) | Lightning arrestor | DEHNbloc/3 (900 110) |
| Zone 1 to 2 (cabinet entry) | Surge arrester for power | DEHNguard 275 (900 600) |
| Zone 1 to 2 (RS-485 interfaces) | Low-voltage surge arrester | Blitzductor CT type MD/HF (919 506 + 919 570) |
| Zone 0 to 1 (RS-485 building transition) | High-voltage surge arrester | Blitzductor CT Type B (919 506 + 919 510) |
| Signal module I/O at zone 1-2 | Module-specific protection | FDK 2 D 60V (DI), FDK 2 D 5 24V (DO), MD 12V (AI) |

Additionally:
- Bus cable shielding must be grounded via EMC spring clamp (919 508) on Blitzductor CT base unit.
- Equipotential bonding cable: 16 mm² minimum.

*(IHB p210–211)*

---

## 10. Protocol Support Summary

| Protocol | Supported | Interface | Default Speed | Max Speed | Notes |
|----------|-----------|-----------|--------------|-----------|-------|
| MPI | Built-in (all CPUs) | RS-485 (9-pin D-sub) | 187.5 kbps | 12 Mbps (318-2 DP only) | PG/OP connections, small data exchange |
| PROFIBUS DP | Built-in (31x-2 DP) or CP 342-5 | RS-485 (9-pin D-sub) | Configured in STEP 7 | 12 Mbps | Master/slave, cyclic I/O exchange |
| PROFIBUS FDL/FMS | Via CP | RS-485 | — | 12 Mbps | Cell-level equal-rights communication |
| Industrial Ethernet | CP 343-1 only | RJ-45 | 10/100 Mbps | 100 Mbps | S7 communication, TCP/IP, ISO |
| Point-to-Point | CP 340/341 | RS-232C, RS-422/485, 20mA | Varies | — | ASCII, 3964(R), RK 512 |
| ASI | Via CP | ASI cable (yellow flat) | — | — | 4-bit per slave, lowest field level |

---

## Appendix: Key Order Numbers

| Component | Order Number |
|-----------|-------------|
| CPU 315-2 DP | 6ES7 315-2AF03-0AB0 |
| CPU 316-2 DP | 6ES7 316-2AG00-0AB0 |
| CPU 318-2 DP | 6ES7 318-2AJ00-0AB0 |
| RS-485 bus connector (with PG) | 6ES7 972-0BB11-0XA0 |
| RS-485 repeater | 6ES7 972-0AA00-0XA0 |
| PG patch cord | 6ES7 901-4BD00-0XA0 |
| PROFIBUS cable (standard) | 6XV1 830-0AH10 |
| IM 360 (send) | 6ES7 360-3AA01-0AA0 |
| IM 361 (receive) | 6ES7 361-3CA01-0AA0 |
| IM 365 (pair) | 6ES7 365-0BA01-0AA0 |
| Connecting cable 1 m | 6ES7 368-3BB01-0AA0 |
| Connecting cable 5 m | 6ES7 368-3BF01-0AA0 |
| Connecting cable 10 m | 6ES7 368-3CB01-0AA0 |
