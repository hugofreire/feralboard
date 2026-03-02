// ── Highlights bar items ──
export const highlights = [
  { val: "4×", label: "TC Channels" },
  { val: "24", label: "Relay Outputs" },
  { val: "16", label: "Isolated Inputs" },
  { val: "4×", label: "PWM Outputs" },
  { val: "3×", label: "SSR Outputs" },
  { val: "1×", label: "RS-485 Port" },
  { val: "1×", label: "DAC Output" },
] as const;

// ── Application tags ──
export const applicationTags = [
  "Thermal Process Control",
  "HVAC Systems",
  "Packaging Machinery",
  "Conveyor & Handling",
  "Environmental Chambers",
  "Food Processing",
  "Water Treatment",
  "Custom OEM",
] as const;

// ── Digital Outputs — PWM Outputs ──
export const pwmOutputSpecs = [
  "2 PWM outputs (24VDC maximum) via <ic>TB67H451AFNG,EL</ic> H-bridge drivers",
  "Allows for independent control of 2 DC motors with variable speed and direction",
] as const;

// ── Digital Outputs — DAC Output ──
export const dacOutputSpecs = [
  "Analog speed ref via <ic>MCP4725A0T-E/CH</ic> 12-bit DAC (10 levels) + <ic>OPA192IDR</ic> conditioning (0-10V)",
] as const;

export const ssrOutputSpecs = [
  "3× solid-state relay drive: <signal>SSR_A</signal> <signal>SSR_B</signal> <signal>SSR_C</signal>",
  "Driven via <ic>BXT420N03M</ic> MOSFETs",
  "Firmware PWM available (1 Hz, duty 0–100%) for proportional control",
] as const;

export const indicatorSpecs = [
  "On-board status LEDs (Red / Blue)",
  "Internal piezo buzzer (<ic>CPI-148-24-90T-67</ic>) — vol 0–255, patterns: single → quintuple, interval & continuous",
] as const;

export const relayBankSpecs = [
  "3× <ic>TPIC6C595DG4</ic> cascaded shift registers driving 24× <ic>HF49FD/024-1H12T</ic> relays",
  "4× common bus sections with independent power feeds",
  "Switches relays, contactors, solenoids, fans, horns, valves, indicators",
  "Fused/protected wiring to screw terminal connectors",
] as const;

// ── Inputs & Sensing table ──
export interface InputRow {
  label: string;
  badge?: string;
  details: string;
}

export const inputRows: InputRow[] = [
  {
    label: "Digital Inputs (16×)",
    badge: "Isolated",
    details:
      "16-ch via <ic>CD74HCT4067M</ic> analog MUX. Front-end: 4× <ic>TLP293-4(GBTPR,E</ic> quad optocouplers (galvanic isolation). 4 groups × 4 inputs (IN0–IN3), each with independent common (COM-0 … COM-3). ESD/TVS protected.",
  },
  {
    label: "Thermocouple (4×)",
    details:
      "<ic>MAX31856MUD+T</ic> SPI converter via <ic>CD74HC4052PWR</ic> 4-ch TC MUX. 1 primary + 3 auxiliary channels. DRDY & FAULT monitored. K/J/T/N/E/R/S/B types. Level-shifted via <ic>TXS0108EPWR</ic> (5V ↔ 3.3V).",
  },
  {
    label: "Board Temperature",
    details: "Firmware-reported internal PCB ambient temperature.",
  },
];

// ── Firmware & PLC Runtime ──
export const firmwareLeft = [
  "CRC-8 framed serial protocol for reliable host ↔ controller comms",
  "Persistent EEPROM configuration (survives power cycles)",
  "Configurable I/O mapping and threshold parameters",
] as const;

export const firmwareRight = [
  "Real-time fault/status telemetry — continuous health reporting",
  "Hardware watchdog supervisor (<ic>HT1232ARZ</ic>) for unattended reliability",
  "UPDI programming interface",
] as const;

// ── Communication Interfaces ──
export const rs485SharedNote =
  "The same communication bus is used between the microcontroller and both RS-485 ICs which means they cannot be used at the same time";

export interface RS485Port {
  name: string;
  isolated: boolean;
  ic: string;
  isolation: string;
  speed: string;
  extra: string;
}

export const rs485Ports: RS485Port[] = [
  {
    name: "RS-485",
    isolated: true,
    ic: "ISO3088DWR",
    isolation: "R1SE-0505 isolated DC-DC",
    speed: "9600 bps (default)",
    extra: "Half-duplex, DE control, multi-drop",
  },
  {
    name: "RS-485",
    isolated: false,
    ic: "ST485EBDR",
    isolation: "Non-isolated",
    speed: "9600 bps (default)",
    extra: "Half-duplex, standard RS-485",
  },
];

export interface CommCard {
  name: string;
  lines: string[];
}

export const commCards: CommCard[] = [
  {
    name: "UART × 2",
    lines: ["<b>UART0</b> (Debug)", "Up to 921600 bps", "", "<b>UART1</b> (Aux)", "9600 bps default"],
  },
  {
    name: "I²C Bus",
    lines: ["On-board <ic>MCP4725A0T-E/CH</ic> DAC", "", "Extensible for sensors, displays, EEPROM"],
  },
  {
    name: "SPI Bus",
    lines: [
      "On-board <ic>MAX31856MUD+T</ic> via <ic>TXS0108EPWR</ic>",
      "",
      "3× <ic>TPIC6C595DG4</ic> shift-reg latch",
    ],
  },
];

// ── Power Supply table ──
export interface PowerRail {
  rail: string;
  regulator: string;
  notes: string;
}

export const powerRails: PowerRail[] = [
  { rail: "24VAC Input", regulator: "External transformer + <ic>744290103</ic> common mode choke", notes: "Varistor + TVS protected input stage" },
  { rail: "24VDC", regulator: "<ic>LMR51430XDDCR</ic> buck", notes: "Main bus for relays & PWM drivers" },
  { rail: "12VDC", regulator: "<ic>LMR51430XDDCR</ic> buck", notes: "Supplementary loads & 12V relays (if used)" },
  { rail: "5VDC", regulator: "<ic>LMR51450SDRRR</ic> buck", notes: "MCU, peripherals, dedicated RPi supply" },
  { rail: "3.3VDC", regulator: "<ic>K7803M-1000R3</ic> buck", notes: "MAX31856MUD+T, TXS0108EPWR level shifters" },
  { rail: "Isolated 5VDC", regulator: "<ic>R1SE-0505</ic> isolated DC-DC", notes: "Galvanic isolation domain for RS-485" },
];

// ── Microcontroller cards ──
export const mcuCore = {
  name: "MCU Core",
  items: [
    { label: "IC", value: "<ic>ATMEGA4809-AFR</ic>" },
    { label: "Package", value: "TQFP-48" },
    { label: "UART Ports", value: "3× (UART0, UART1, UART3→RS-485)" },
    { label: "Programming", value: "UPDI interface" },
  ],
};

export const mcuSupervisory = {
  name: "Supervisory",
  items: [
    { label: "Watchdog", value: "<ic>HT1232ARZ</ic> external supervisor" },
    { label: "Reset", value: "Dedicated RESET-PIN line" },
    { label: "Protection", value: "ESD/TVS on all I/O buses" },
    { label: "Connector", value: "2× JST-NSH (3 & 6 pin)" },
  ],
};

// ── System Architecture nodes ──
export const archNodes = [
  { id: "psu", label: "24VAC Input\n→ On-Board\nPSU", sub: "External Transformer", variant: "psu" as const },
  { id: "plc", label: "AIO-500\nPLC Engine", sub: "ATmega4809", variant: "controller" as const },
  { id: "hmi", label: "HMI Touch\nPanel", sub: "Raspberry Pi 4B", variant: "hmi" as const },
  { id: "cloud", label: "Cloud Portal\n& Web Access", sub: "Remote Config", variant: "cloud" as const },
] as const;

export const archArrows = [
  { top: "24V/12V/5V", bottom: "3.3V" },
  { top: "RS-485 / UART", bottom: "MQTT" },
  { top: "HTTPS / VPN", bottom: "OTA Updates" },
] as const;

// ── HMI Panel items ──
export const hmiItems = [
  { label: "SBC", value: "Raspberry Pi 4B + RTC module" },
  { label: "Display", value: "7″ capacitive touchscreen" },
  { label: "OS", value: "Debian-based Linux, kiosk mode" },
  { label: "Vision", value: "Camera with YOLOv11 object detection" },
  { label: "Protocol", value: "MQTT broker — full bidirectional I/O control" },
  { label: "Telemetry", value: "Real-time data acquisition & logging" },
  { label: "Remote", value: "VNC server for remote desktop access" },
  { label: "Updates", value: "OTA — software + firmware over-the-air" },
] as const;

// ── HMI Hardware & Connectivity (RPi 4B) ──
export const hmiHardwareItems = [
  { label: "Ethernet", value: "Gigabit Ethernet (RJ45) — primary network / cloud uplink" },
  { label: "USB", value: "2× USB 3.0 + 2× USB 2.0 — peripherals, storage, pen updates" },
  { label: "GPIO", value: "40-pin header — spare I/O, 1-Wire sensors, additional SPI/I²C/UART" },
  { label: "Wi-Fi", value: "802.11ac dual-band (2.4 / 5 GHz) — wireless connectivity" },
  { label: "Bluetooth", value: "Bluetooth 5.0 + BLE — wireless peripherals & beacons" },
  { label: "Camera (CSI)", value: "MIPI CSI-2 port — YOLOv11 vision pipeline input" },
  { label: "Display (DSI)", value: "MIPI DSI port — 7″ capacitive touchscreen interface" },
  { label: "Storage", value: "microSD slot — OS, application data, local logging" },
] as const;

// ── Cloud & Remote items ──
export const cloudItems = [
  { label: "Web Portal", value: "Browser-based access to edit SBC configuration, application logic, and parameters remotely" },
  { label: "Telemetry Dashboard", value: "Cloud-hosted monitoring of process data, alarms, and device health" },
  { label: "Pen Updates", value: "USB-based offline update capability for field deployments without network access" },
] as const;

// ── Specifications table ──
export const specifications = [
  { label: "Model", value: "AIO-500-V5" },
  { label: "Input Voltage", value: "24VAC via external transformer" },
  { label: "Internal Rails", value: "24V / 12V / 5V / 3.3V (all regulated) + isolated 5V domain" },
  { label: "Operating Temp", value: "0 °C to +50 °C" },
  { label: "Digital Outputs", value: "24× latched relay (<ic>HF49FD/024-1H12T</ic>) + 3× SSR + 2× H-bridge" },
  { label: "Digital Inputs", value: "16× optically isolated (<ic>TLP293-4(GBTPR,E</ic>)" },
  { label: "Analog Inputs", value: "4× thermocouple (<ic>MAX31856MUD+T</ic>, types K/J/T/N/E/R/S/B) + PCB temp" },
  { label: "Communication", value: "RS-485 (1 isolated + 1 not isolated) + 2× UART + I²C + SPI" },
  { label: "MCU", value: "<ic>ATMEGA4809-AFR</ic> + <ic>HT1232ARZ</ic> hardware watchdog" },
  { label: "HMI", value: "7″ capacitive touch, Raspberry Pi 4B, Debian Linux, MQTT" },
  { label: "Enclosure Rating", value: "TBD" },
  { label: "Certifications", value: "CE (pending) — designed with EMC best practices" },
] as const;

// ── I/O Summary ──
export const ioOutputs = [
  { count: "24×", desc: "Latched relay outputs (HF49FD)" },
  { count: "3×", desc: "SSR drive outputs (MOSFET)" },
  { count: "2×", desc: "Bidirectional H-bridge motors" },
  { count: "1×", desc: "DAC analog output (12-bit)" },
  { count: "1×", desc: "Piezo buzzer (programmable)" },
  { count: "2×", desc: "Status LEDs (Red / Blue)" },
] as const;

export const ioInputs = [
  { count: "16×", desc: "Optically isolated digital (24V)" },
  { count: "4×", desc: "Thermocouple channels" },
  { count: "1×", desc: "PCB ambient temperature" },
] as const;

// ── Feature cards ──
export const featureCards = [
  {
    icon: "Cpu" as const,
    title: "ATMEGA4809-AFR PLC Engine",
    desc: "Real-time I/O controller with CRC-8 protocol, EEPROM persistence, and HT1232ARZ hardware watchdog.",
  },
  {
    icon: "Zap" as const,
    title: "High-Density I/O",
    desc: "24 relay outputs, 16 isolated inputs, 3 SSR drives, 2 H-bridge controllers — all in a single board.",
  },
  {
    icon: "ThermometerSun" as const,
    title: "4-Channel Thermocouple",
    desc: "MAX31856MUD+T SPI converter supporting K/J/T/N/E/R/S/B types with fault monitoring.",
  },
  {
    icon: "Wifi" as const,
    title: "RS-485 + Cloud",
    desc: "One galvanically isolated port (ISO3088DWR), MQTT protocol, and remote cloud management portal.",
  },
  {
    icon: "Monitor" as const,
    title: "7″ HMI Touchscreen",
    desc: "Raspberry Pi 4B powered capacitive display with Debian kiosk, YOLOv11 vision, and OTA updates.",
  },
  {
    icon: "Shield" as const,
    title: "Industrial-Grade Power",
    desc: "24VAC mains input from external transformer with regulated 24V / 12V / 5V / 3.3V rails, TVS protected.",
  },
] as const;

// ── Board Base Assembly notes ──
export const boardBaseAssemblyItems = [
  "12V rail is not soldered, only 24V and 5V",
  "10 soldered output relays that can be expanded to 24",
  "4 AC inputs and 4 DC inputs that can be expanded to 16",
  "1 thermocouple channel that can be expanded to 4",
  "SSR outputs are not soldered",
  "DAC analog output is not soldered",
  "RS-485 with galvanic isolation is not soldered",
  "<ic>K7803M-1000R3</ic> is not soldered — +3V3 comes from Raspberry regulator",
] as const;
