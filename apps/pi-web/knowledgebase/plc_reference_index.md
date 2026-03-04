# Siemens PLC Communication Reference Index

Generated from 12 source PDFs (110MB total). Each reference file was extracted using automated PDF text and table extraction.

## Reference Files

| # | PLC Family | Reference File | Source PDF(s) | Lines |
|---|-----------|---------------|---------------|-------|
| 1 | LOGO! 8 | [logo8_communication_reference.md](./logo8_communication_reference.md) | Manual-LOGO-2020.pdf, Help_en-US_en-US.pdf | 551 |
| 2 | S7-1200 G2 | [s7_1200_g2_communication_reference.md](./s7_1200_g2_communication_reference.md) | S71200_G2_system_manual_en-US.pdf, S71200_G2_manual_update_en-US_en-US.pdf | 561 |
| 3 | S7-200 SMART | [s7_200_smart_communication_reference.md](./s7_200_smart_communication_reference.md) | s7-200-smart-system-manual-en-us.pdf | 957 |
| 4 | S7-200 | [s7_200_communication_reference.md](./s7_200_communication_reference.md) | s7200_system_manual_en-US.pdf | 664 |
| 5 | S7-1500 / ET 200MP | [s7_1500_et200mp_communication_reference.md](./s7_1500_et200mp_communication_reference.md) | s71500_et200mp_system_manual_en-US_en-US.pdf | 557 |
| 6 | S7-300 | [s7_300_communication_reference.md](./s7_300_communication_reference.md) | s7300_module_data_manual_en-US_en-US.pdf, S7-300_IHB_e.pdf | 565 |
| 7 | S7-400 | [s7_400_communication_reference.md](./s7_400_communication_reference.md) | 424ish_e.pdf, module_data_en_en-US.pdf | 661 |

### Skipped

- **ET 200SP** (`et200sp_cpu1510sp_1_pn_manual_en-US_en-US.pdf`, 43 pages) — Datasheet-level document with zero communication protocol hits. ET 200SP CPUs use the S7-1500 instruction set; refer to the S7-1500 / ET 200MP reference for communication details.

## Protocol Support Matrix

Cross-family comparison of communication protocol support.

| Protocol | LOGO! 8 | S7-1200 G2 | S7-200 SMART | S7-200 | S7-1500 | S7-300 | S7-400 |
|----------|---------|------------|--------------|--------|---------|--------|--------|
| **PROFINET IO** | -- | Controller / Device | Controller | -- | Controller / Device / I-Device | via CP | via CP |
| **PROFIBUS DP** | -- | -- | via EM DP01 | Slave (EM 277) | Master / Slave | Built-in (DP CPUs) or CP | Built-in or IM 467 |
| **Modbus TCP** | Client / Server (port 502-510) | Client / Server (port 502) | Client / Server (port 502) | -- | Client / Server (port 502) | -- | -- |
| **Modbus RTU** | -- | -- | Master / Slave | Master / Slave | Master / Device (CM PtP) | -- | -- |
| **OPC UA** | -- | -- | -- | -- | Server / Client (port 4840) | -- | -- |
| **S7 Comm (PUT/GET)** | Client / Server (port 102) | Client / Server (port 102) | Peer (port 102) | via CP 243-1 | PUT/GET, BSEND/BRCV (port 102) | via CP 343-1 | via MPI/DP |
| **Open User Comm (TCP/UDP)** | -- | TCP / UDP / ISO-on-TCP | TCP / UDP / ISO-on-TCP | -- | TCP / UDP / ISO-on-TCP (+ Secure) | -- | -- |
| **Web Server** | HTTP/HTTPS | HTTPS (Web API) | -- | -- | HTTP/HTTPS (Web API) | -- | -- |
| **MPI** | -- | -- | -- | Built-in (all CPUs) | -- | Built-in (all CPUs) | Built-in (all CPUs) |
| **PPI** | -- | -- | Master / Slave | Built-in (default) | -- | -- | -- |
| **Freeport (Serial)** | -- | -- | XMT/RCV | XMT/RCV | via CM PtP | via CP 340/341 | via CP 440/441 |
| **USS (Drive)** | -- | -- | Master | Master | via CM PtP | -- | -- |
| **MQTT** | Client (AWS IoT) | -- | -- | -- | Publisher (CP 1545-1) | -- | -- |
| **NTP** | Client / Server | Client | -- | -- | Client | -- | -- |
| **SNMP** | -- | Client (V1) | -- | -- | Agent (V1/V3) | -- | -- |
| **IO-Link** | -- | -- | -- | -- | Master (CM 8x) | -- | -- |
| **PROFIsafe** | -- | -- | -- | -- | F-CPUs (SIL 3 / PL e) | -- | -- |

**Legend:** "--" = not supported or not documented in the available manuals. "via CP/CM/EM" = requires optional communication module.

## Key Communication Parameters

| Parameter | LOGO! 8 | S7-1200 G2 | S7-200 SMART | S7-200 | S7-1500 | S7-300 | S7-400 |
|-----------|---------|------------|--------------|--------|---------|--------|--------|
| Ethernet ports | 1 | 2 (PROFINET) | 1 | via CP | 2-3 (varies by CPU) | via CP | via CP |
| Max Modbus TCP connections | 10 (port 502-510) | Uses OUC pool | Uses OUC pool | N/A | Uses OUC pool | N/A | N/A |
| Max OUC connections | N/A | 78 dynamic pool | 8 active + 8 passive | N/A | 88-384 (by CPU) | N/A | N/A |
| Modbus TCP default port | 502 | 502 | 502 | N/A | 502 | N/A | N/A |
| S7 comm port | 102 | 102 | 102 | 102 (via CP) | 102 | 102 (via CP) | 102 (via CP) |
| Max PROFINET IO devices | N/A | 31 | 8 | N/A | Varies by CPU | N/A | N/A |
| Default IP | 192.168.0.1 | DHCP or manual | 192.168.2.1 | N/A | Manual or DHCP | N/A | N/A |

## PLC Generation Timeline

| Generation | PLC Family | Status | Primary Protocols |
|-----------|-----------|--------|-------------------|
| Current | S7-1500 / ET 200MP | Active production | PROFINET, OPC UA, Modbus TCP, S7, OUC, Web API |
| Current | S7-1200 G2 | Active production | PROFINET, Modbus TCP, S7, OUC, Web API |
| Current | LOGO! 8 | Active production | S7, Modbus TCP, Web Server, MQTT/AWS |
| Current | S7-200 SMART | Active production (Asia-Pacific) | Modbus TCP/RTU, PROFINET, GET/PUT, OUC |
| Legacy | S7-400 | Spare parts only | MPI, PROFIBUS DP, Ethernet (via CP) |
| Legacy | S7-300 | Spare parts only | MPI, PROFIBUS DP, Ethernet (via CP) |
| Legacy | S7-200 | Discontinued | PPI, MPI, PROFIBUS DP, Modbus RTU, Freeport |

## Extraction Metadata

- **Extraction date:** 2026-03-04
- **Tools:** PyMuPDF (fitz) 1.27.1, pdfplumber 0.11.9
- **Method:** Automated TOC-guided extraction with keyword-targeted page ranges
- **Pre-scan:** `prescan.json` contains per-PDF metadata (page counts, TOC, keyword hits)
- **Helpers:** `extract_helpers.py` provides shared extraction functions
