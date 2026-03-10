# SATO Label Printer Specifications

Reference extracted from SATO operator manuals and programming references.

---

## WT4 (WT4-AXB Series)

**Category:** Industrial Thermal Printer

| Property | Specification |
| --- | --- |
| Print Method | Direct Thermal / Thermal Transfer |
| Resolution | 203 dpi (8 dots/mm) / 300 dpi (12 dots/mm) |
| Max Print Speed | 2-8 ips (203 dpi) / 2-6 ips (300 dpi) |
| Max Print Width | 104 mm |
| Max Printable Length | 2500 mm (203 dpi) / 1500 mm (300 dpi) |
| Memory | 128 MB DRAM, 128 MB Flash |
| CPU | 32-bit RISC microprocessor |
| Display | 3.5" Color LCD |
| Dimensions | 265.5 mm (W) x 235 mm (H) x 293.5 mm (D) |
| Weight | 11.5 kg |
| Power | AC 100-240V, 50/60 Hz |
| Operating Temp | 4-40 C, 30-80% RH (non-condensing) |

### Interfaces

| Interface | Details |
| --- | --- |
| USB 2.0 (Type A) | 2 ports (host) |
| USB 2.0 (Type B) | 1 port (device) |
| RS-232C | DB9 serial, baud rates 2400-115200 bps, 7/8 data bits, flow control: XON/XOFF / RTS / Status |
| Ethernet (LAN) | 10BASE-T / 100BASE-TX, RJ-45 |
| Bluetooth 5.0 | Optional. BLE only (no Classic). 1 client connection. Peripheral and central modes. |
| WLAN | Optional. IEEE 802.11 b/g/n, 2.4 GHz. Infrastructure mode. WEP/WPA/WPA2-Personal/Enterprise. |

### Communication Protocols

- SBPL command framing: STX \<A\> ... \<Z\> ETX
- Serial protocols: READY/BUSY, XON/XOFF, Status (bidirectional)
- LAN protocols: TCP/IP socket, DHCP, SNMP, IPv4/IPv6
- Default socket port: configurable via web settings tool
- Web configuration tool built into firmware (HTTP via LAN)

### Programming Languages / Emulations

| Language | Notes |
| --- | --- |
| SBPL | Native SATO language. Full barcode and font support. |
| SZPL (PPLZ) | Zebra ZPL compatible emulation. Fonts A-H plus AGFA scalable. |
| SIPL | Intermec IPL compatible emulation. 15 internal fonts. |

### Media

- Label width: 22-112 mm (25-115 mm including liner)
- Media types: Direct thermal label, direct thermal tag, roll paper, fanfold paper
- Paper thickness: 0.08-0.19 mm
- Max roll OD: 203.2 mm (8") on 76 mm (3") core; 177.8 mm (7") on 38 mm (1.5") core
- Ribbon: max 450 m length, 82 mm OD, wax/wax-resin/resin

### Options

Cutter kit, dispenser kit, external rewinder (RWG500, RW350), external supply (UW200EF, UWC400)

---

## WS2 (WS208 / WS212)

**Category:** Compact Desktop Printer

| Property | WS208 | WS212 |
| --- | --- | --- |
| Print Method | Direct Thermal | Direct Thermal |
| Resolution | 203 dpi (8 dots/mm) | 300 dpi (12 dots/mm) |
| Max Print Speed | 2-7 ips (2-3 ips peel-off) | 2-5 ips (2-3 ips peel-off) |
| Max Print Width | 54.1 mm | 56.8 mm |
| Max Print Length | 2540 mm (100") | 1270 mm (50") |
| Memory (Flash) | 16 MB (8 MB user) | 16 MB (8 MB user) |
| Memory (SDRAM) | 32 MB | 32 MB |
| CPU | 32-bit RISC | 32-bit RISC |
| Dimensions | 116 mm (W) x 170 mm (H) x 215 mm (D) | same |
| Weight | 1.05 kg | 1.05 kg |
| Power | AC 100-240V, 50/60 Hz | same |
| Operating Temp | 5-40 C | same |

### Interfaces

| Interface | Details |
| --- | --- |
| USB (Type A) | Host port |
| USB (Type B) | Device port |
| Ethernet (LAN) | 10BASE-T / 100BASE-TX, RJ-45, auto-detecting |
| Bluetooth 4.2 | Optional. Class 2. SPP and GATT profiles. 10 m range. Slave mode only. |
| WLAN | Optional. IEEE 802.11 b/g/n, 2.4 GHz. Infrastructure and Ad Hoc modes. |

**Note:** No RS-232C serial port on WS2.

### Communication Protocols

- LAN: TCP/IP socket, LPR, DHCP, IPv4/IPv6, SNMP
- LAN ports: RJ-45 with Auto-MDIX, Auto-Negotiation
- Socket mode: TCP Server/Client, UDP Client
- WLAN security: WEP (64/128 bit), WPA (TKIP), WPA2 (AES), 802.1x enterprise (PEAP, TLS, TTLS, LEAP, EAP-FAST)

### Programming Languages / Emulations

| Language | Notes |
| --- | --- |
| SDPL | Datamax DPL compatible. 9 internal fonts + 6 ASD smooth fonts. |
| SEPL | Eltron EPL compatible. 5 internal fonts. |
| SZPL | Zebra ZPL compatible. Fonts A-H plus AGFA scalable. |

### Media

- Label width: 12-60 mm
- Label length: 10-2540 mm (WS208) / 10-1270 mm (WS212)
- Thickness: 0.06-0.2 mm
- Max roll OD: 127 mm (5") on 25.4/38 mm core; 115 mm (4.5") on 12.7 mm core
- Media types: Direct thermal label, direct thermal tag, roll paper, fanfold paper
- USB storage: up to 32 GB (FAT32)

### Options

Peeler, full cutter

---

## CL4NX Plus / CL6NX Plus

**Category:** Industrial Printer (shared programming reference)

| Property | CL4NX Plus | CL6NX Plus |
| --- | --- | --- |
| Print Method | Direct Thermal / Thermal Transfer | Direct Thermal / Thermal Transfer |
| Resolution | 203 dpi / 305 dpi / 609 dpi | 203 dpi / 305 dpi |
| Max Print Speed (203/305 dpi) | 2-14 ips | 2-14 ips |
| Max Print Speed (609 dpi) | 2-6 ips | N/A |
| Max Print Width (203 dpi) | ~104 mm (832 dots) | ~156 mm (1248 dots at 203 dpi) |
| Max Print Width (305 dpi) | ~104 mm (1248 dots) | ~156 mm (1872 dots at 305 dpi) |
| Memory | 2.95 MB receive buffer | 2.95 MB receive buffer |
| Display | LCD with icon status display | LCD with icon status display |

### Interfaces

| Interface | Details |
| --- | --- |
| USB 2.0 (Type A) | Host port |
| USB 2.0 (Type B) | Device, High-speed. Protocols: Status4, Status5. |
| RS-232C | DB9 female. Baud rates 2400-115200 bps. Protocols: READY/BUSY, XON/XOFF, Status3/4/5. |
| IEEE 1284 (Parallel) | Amphenol 36-pin. ECP/Compatible mode. Protocols: Status4, Status5. |
| Ethernet (LAN) | 10BASE-T / 100BASE-TX, RJ-45, up to 100 m cable. |
| Bluetooth 3.0+EDR | Standard. Class 2, SPP profile, 10 m range. Master/Slave. PIN auth. CRC optional. |
| NFC | Standard. Type 2 Tag. Tag mode (power off) + pass-through mode (power on). |
| WLAN | Optional. IEEE 802.11 a/b/g/n, 2.4/5 GHz. Infrastructure and Ad Hoc. Wi-Fi Direct. WPS 2.0. |
| External Signal | Amphenol 14-pin. For connecting peripheral devices. |

### Communication Protocols

- LAN/WLAN: TCP/IP (IPv4/IPv6), LPR (RFC1179), FTP (RFC959), HTTP/HTTPS, DHCP, SNMP (v1/v2c/v3), NTP
- LAN socket ports: 1024, 1025, 9100 (configurable)
- LAN/WLAN switching: AUTO / LAN / Wi-Fi (cannot use simultaneously)
- Serial: READY/BUSY, XON/XOFF, Status3, Status4, Status5
- Bidirectional status: ENQ/CAN/DLE/DC1 commands with STX...ETX framing
- WLAN security: WEP, WPA/WPA2 Personal (PSK), Enterprise 802.1x (FAST, LEAP, PEAP, TLS, TTLS, CCKM)

### Programming Language

| Language | Notes |
| --- | --- |
| SBPL | Native SATO language. Full command set with RFID support (optional). |

---

## CT4-LX

**Category:** Compact Desktop Printer

| Property | Specification |
| --- | --- |
| Print Method | Direct Thermal / Thermal Transfer |
| Resolution | 203 dpi (8 dots/mm) / 305 dpi (12 dots/mm) |
| Max Print Speed | 2-8 ips (203 dpi) / 2-6 ips (305 dpi) |
| Max Print Width | ~104 mm (832 dots at 203 dpi / 1248 dots at 305 dpi) |
| Memory | 2.95 MB receive buffer |
| Display | Screen with status icons |

### Interfaces

| Interface | Details |
| --- | --- |
| USB 2.0 (Type A) | 2 ports (back x1, front x1). Host. Mass storage and HID class. |
| USB 2.0 (Type B) | Device, High-speed. Protocols: Status4, Status5. |
| Ethernet (LAN) | 10BASE-T / 100BASE-TX / 1000BASE-T (Gigabit), RJ-45, up to 100 m. |
| NFC | Standard. NFC Forum Type 2 Tag. Tag mode + pass-through mode. 888 bytes tag memory. |
| RS-232C | Optional. DB9 female. Baud rates 2400-115200 bps. Protocols: READY/BUSY, XON/XOFF, Status3/4/5. |
| Bluetooth 4.1 | Optional. SPP, HID, HSP, HFP profiles. Master/Slave. 10 m range. PIN auth. CRC optional. |
| WLAN | Optional. IEEE 802.11 a/b/g/n/ac, 2.4/5 GHz. Infrastructure and Ad Hoc. Wi-Fi Direct. WPS 2.0. |

### Communication Protocols

- LAN/WLAN: TCP/IP (IPv4/IPv6), LPR (RFC1179), FTP (RFC959), HTTP/HTTPS, DHCP, SNMP (v1/v2c/v3), NTP
- LAN socket ports: 1024, 1025, 9100 (configurable)
- LAN supports 1000BASE-T (Gigabit) -- unique among these SATO models
- LAN and WLAN can be used simultaneously (same segment only)
- Serial: READY/BUSY, XON/XOFF, Status3, Status4, Status5
- Bidirectional status: ENQ/CAN/DLE/DC1 commands with STX...ETX framing
- WLAN security: WEP, WPA/WPA2 Personal (PSK), Enterprise 802.1x (FAST, LEAP, PEAP, TLS, TTLS, CCKM)
- WLAN supports 802.11ac (up to 433.3 Mbps theoretical)

### Programming Language

| Language | Notes |
| --- | --- |
| SBPL | Native SATO language. Full command set with optional RFID (UHF M6e) support. |

### USB Device ID Compatibility

The CT4-LX can emulate CT4i series USB identifiers for backward compatibility:

| Mode | 203 dpi PnP Name | 305 dpi PnP Name |
| --- | --- | --- |
| Default | CT4-LX 203dpi | CT4-LX 305dpi |
| L'espritV/CT4i compat | CT408i | CT412i |
| ETER400/CT4i compat | CT408i | CT412i |

---

## Interface Comparison Matrix

| Feature | WT4 | WS2 | CL4NX Plus | CT4-LX |
| --- | --- | --- | --- | --- |
| **Print Method** | DT / TT | DT only | DT / TT | DT / TT |
| **Resolution (dpi)** | 203, 300 | 203 (WS208), 300 (WS212) | 203, 305, 609 | 203, 305 |
| **Max Print Speed** | 8 ips | 7 ips | 14 ips | 8 ips |
| **Max Print Width** | 104 mm | 54-57 mm | ~104 mm (4") / ~156 mm (6") | ~104 mm |
| **USB Type A (host)** | 2 ports | 1 port | 1 port | 2 ports |
| **USB Type B (device)** | 1 port | 1 port | 1 port | 1 port |
| **RS-232C Serial** | Standard | -- | Standard | Optional |
| **IEEE 1284 Parallel** | -- | -- | Standard | -- |
| **Ethernet** | 10/100 Mbps | 10/100 Mbps | 10/100 Mbps | 10/100/1000 Mbps |
| **Bluetooth** | 5.0 (optional, BLE) | 4.2 (optional) | 3.0+EDR (standard) | 4.1 (optional) |
| **WLAN** | 802.11 b/g/n (optional) | 802.11 b/g/n (optional) | 802.11 a/b/g/n (optional) | 802.11 a/b/g/n/ac (optional) |
| **NFC** | -- | -- | Standard | Standard |
| **External Signal I/O** | -- | -- | Standard (14-pin) | -- |
| **SBPL** | Yes | -- | Yes | Yes |
| **SZPL (ZPL compat)** | Yes | Yes | -- | -- |
| **SDPL (DPL compat)** | -- | Yes | -- | -- |
| **SEPL (EPL compat)** | -- | Yes | -- | -- |
| **SIPL (IPL compat)** | Yes | -- | -- | -- |
| **Web Config Tool** | Yes (built-in) | -- | -- | -- |
| **RFID Support** | -- | -- | -- | Optional (UHF M6e) |
| **Socket Ports (default)** | Configurable | Configurable | 1024, 1025, 9100 | 1024, 1025, 9100 |
| **LPR** | -- | -- | Yes (RFC1179) | Yes (RFC1179) |
| **FTP** | -- | -- | Yes (RFC959) | Yes (RFC959) |
| **SNMP** | -- | Yes | Yes (v1/v2c/v3) | Yes (v1/v2c/v3) |
| **IPv6** | Yes | -- | Yes | Yes |
| **Weight** | 11.5 kg | 1.05 kg | N/A (industrial) | N/A (compact) |
| **Dimensions** | 265x235x294 mm | 116x170x215 mm | N/A | N/A |

### Protocol Support Detail

All models with Ethernet support TCP/IP sockets for sending SBPL print data. The bidirectional status protocol (Status3/4/5) enables the host to monitor printer state (online/offline, errors, buffer status, ribbon/label near-end) via ENQ polling.

| Protocol | RS-232C | USB | LAN | Bluetooth | WLAN | NFC |
| --- | --- | --- | --- | --- | --- | --- |
| READY/BUSY | CL4NX, CT4-LX | -- | -- | -- | -- | -- |
| XON/XOFF | CL4NX, CT4-LX | -- | -- | -- | -- | -- |
| Status3 | CL4NX, CT4-LX | -- | CL4NX, CT4-LX | -- | -- | -- |
| Status4 | CL4NX, CT4-LX | CL4NX, CT4-LX | CL4NX, CT4-LX | CL4NX, CT4-LX | CL4NX, CT4-LX | -- |
| Status5 | CL4NX, CT4-LX | CL4NX, CT4-LX | CL4NX, CT4-LX | CL4NX | CT4-LX | -- |
| Multiple buffer (NFC) | -- | -- | -- | -- | -- | CL4NX, CT4-LX |

### Serial Port Settings (RS-232C) Comparison

| Setting | WT4 | CL4NX Plus | CT4-LX |
| --- | --- | --- | --- |
| Baud Rate | 2400-115200 | 2400-115200 | 2400-115200 |
| Data Bits | 7, 8 | 7, 8 | 7, 8 |
| Parity | None, Odd, Even | None, Odd, Even | None, Odd, Even |
| Stop Bits | 1, 2 | 1, 2 | 1, 2 |
| Flow Control | XON/XOFF, RTS, Status | READY/BUSY, XON/XOFF, Status3/4/5 | READY/BUSY, XON/XOFF, Status3/4/5 |
| Connector | DB9 | DB9 female | DB9 female |
| Max Cable | 5 m | 5 m | 5 m |

---

*Sources: sato_wt4_operator_manual.pdf, sato_ws2_operator_manual.pdf, sato_cl4nx_plus_programming_ref.pdf, sato_ct4lx_programming_ref.pdf, sato_wt4_web_setting_manual.pdf*
