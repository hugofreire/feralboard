const en = {
  // ── Nav ──
  "nav.highlights": "Highlights",
  "nav.overview": "Overview",
  "nav.outputs": "Outputs",
  "nav.inputs": "Inputs",
  "nav.firmware": "Firmware",
  "nav.comm": "Comms",
  "nav.power": "Power",
  "nav.mcu": "MCU",
  "nav.architecture": "Architecture",
  "nav.hmi": "HMI",
  "nav.cloud": "Cloud",
  "nav.features": "Features",
  "nav.applications": "Apps",
  "nav.specs": "Specs",
  "nav.io-summary": "I/O",
  "nav.assembly": "Assembly",

  // ── Hero ──
  "hero.datasheetLabel": "Product Datasheet",
  "hero.title": "FeralBoard AIO-500",
  "hero.subtitle": "All-in-One HMI + PLC Controller",
  "hero.description":
    "Embedded industrial controller combining a 7\u2033 HMI touchscreen with a high-density I/O PLC engine, optically isolated inputs, RS-485 communication, and remote control.",

  // ── Highlights ──
  "highlights.tcChannels": "TC Channels",
  "highlights.relayOutputs": "Relay Outputs",
  "highlights.isolatedInputs": "Isolated Inputs",
  "highlights.hBridgeMotors": "H-Bridge Motors",
  "highlights.ssrOutputs": "SSR Outputs",
  "highlights.rs485Port": "RS-485 Port",

  // ── Overview ──
  "overview.label": "Product Overview",
  "overview.title": "FeralBoard AIO-500",
  "overview.description":
    "The <b>FeralBoard AIO-500</b> is an integrated HMI+PLC platform for industrial process control, automation, and monitoring. It combines a real-time I/O controller (<ic>ATMEGA4809-AFR</ic>) with an embedded Linux-based HMI panel, MQTT-based communication, and a cloud management portal. The controller features a multi-rail on-board power supply accepting AC mains via an integrated transformer, with regulated 24V / 12V / 5V / 3.3V rails. A <ic>HT1232ARZ</ic> hardware watchdog supervisor ensures reliable unattended operation.",

  // ── Digital Outputs ──
  "digitalOutputs.label": "PLC Engine",
  "digitalOutputs.title": "Digital Outputs",
  "digitalOutputs.pwm": "PWM Outputs (2\u00d7 H-Bridge)",
  "digitalOutputs.dac": "DAC Output (1\u00d7)",
  "digitalOutputs.ssr": "SSR Outputs (3\u00d7)",
  "digitalOutputs.indicators": "Indicator & Alert Outputs",
  "digitalOutputs.relayBank": "Latched Relay Bank (24\u00d7)",

  // ── Inputs & Sensing ──
  "inputs.label": "PLC Engine",
  "inputs.title": "Inputs & Sensing",
  "inputs.colFunction": "Function",
  "inputs.colDetails": "Details",

  // ── Firmware ──
  "firmware.label": "Firmware",
  "firmware.title": "PLC Runtime",

  // ── Communication ──
  "comm.label": "Communication",
  "comm.title": "Interfaces",

  // ── Power Supply ──
  "power.label": "Power",
  "power.title": "On-Board Power Supply",
  "power.colRail": "Rail",
  "power.colRegulator": "Regulator IC",
  "power.colNotes": "Notes",

  // ── Microcontroller ──
  "mcu.label": "MCU",
  "mcu.title": "Microcontroller",

  // ── System Architecture ──
  "architecture.label": "System",
  "architecture.title": "Architecture",

  // ── HMI Panel ──
  "hmi.label": "HMI",
  "hmi.title": "Touchscreen Panel",

  // ── Cloud ──
  "cloud.label": "Cloud",
  "cloud.title": "Remote Management",

  // ── Features ──
  "features.label": "Capabilities",
  "features.title": "Built for the Factory Floor",
  "features.card1.title": "ATMEGA4809-AFR PLC Engine",
  "features.card1.desc":
    "Real-time I/O controller with CRC-8 protocol, EEPROM persistence, and HT1232ARZ hardware watchdog.",
  "features.card2.title": "High-Density I/O",
  "features.card2.desc":
    "24 relay outputs, 16 isolated inputs, 3 SSR drives, 2 H-bridge controllers \u2014 all in a single board.",
  "features.card3.title": "4-Channel Thermocouple",
  "features.card3.desc":
    "MAX31856MUD+T SPI converter supporting K/J/T/N/E/R/S/B types with fault monitoring.",
  "features.card4.title": "RS-485 + Cloud",
  "features.card4.desc":
    "One galvanically isolated port (ISO3088DWR), MQTT protocol.",
  "features.card5.title": "7\u2033 HMI Touchscreen",
  "features.card5.desc":
    "Raspberry Pi 4B powered capacitive display with Debian kiosk.",
  "features.card6.title": "Industrial-Grade Power",
  "features.card6.desc":
    "24VAC mains input from external transformer with regulated 24V / 12V / 5V / 3.3V rails, TVS protected.",

  // ── Applications ──
  "applications.label": "Applications",
  "applications.title": "Where It Fits",
  "applications.thermalProcess": "Thermal Process Control",
  "applications.hvac": "HVAC Systems",
  "applications.packaging": "Packaging Machinery",
  "applications.conveyor": "Conveyor & Handling",
  "applications.environmental": "Environmental Chambers",
  "applications.food": "Food Processing",
  "applications.water": "Water Treatment",
  "applications.oem": "Custom OEM",

  // ── Specs ──
  "specs.label": "Specifications",
  "specs.title": "Technical Overview",

  // ── I/O Summary ──
  "ioSummary.label": "I/O Summary",
  "ioSummary.title": "At a Glance",
  "ioSummary.outputs": "Outputs",
  "ioSummary.inputs": "Inputs",

  // ── NoteBox ──
  "noteBox.title":
    "DS Rev 1.1 \u2014 Grounded in hardware schematic (KiCad v9, PlacaControlo_v9).",
  "noteBox.text":
    "All I/O counts, IC references, and interface claims verified against actual board design. Contact Feralbyte for custom I/O configurations and OEM integration options.",

  // ── Board Base Assembly ──
  "assembly.label": "Assembly",
  "assembly.title": "Board Base Assembly",
  "assembly.description":
    "Default configuration of the base board. Optional subsystems can be populated for expanded I/O.",

  // ── Footer ──
  "footer.company": "Feralbyte Lda. \u2014 DS-AIO500-V5 R1.1",
} as const;

export default en;
