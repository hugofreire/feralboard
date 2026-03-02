const pt = {
  // ── Nav ──
  "nav.highlights": "Destaques",
  "nav.overview": "Vis\u00e3o Geral",
  "nav.outputs": "Sa\u00eddas",
  "nav.inputs": "Entradas",
  "nav.firmware": "Firmware",
  "nav.comm": "Comms",
  "nav.power": "Energia",
  "nav.mcu": "MCU",
  "nav.architecture": "Arquitetura",
  "nav.hmi": "HMI",
  "nav.cloud": "Cloud",
  "nav.features": "Recursos",
  "nav.applications": "Aplica\u00e7\u00f5es",
  "nav.specs": "Espec.",
  "nav.io-summary": "I/O",
  "nav.assembly": "Montagem",

  // ── Hero ──
  "hero.datasheetLabel": "Ficha T\u00e9cnica",
  "hero.title": "FeralBoard AIO-500",
  "hero.subtitle": "Controlador HMI + PLC Tudo-em-Um",
  "hero.description":
    "Controlador industrial embebido que combina um ecr\u00e3 t\u00e1til HMI de 7\u2033 com um motor PLC de I/O de alta densidade, entradas opticamente isoladas, comunica\u00e7\u00e3o RS-485 e controlo remoto.",

  // ── Highlights ──
  "highlights.tcChannels": "Canais TC",
  "highlights.relayOutputs": "Sa\u00eddas Rel\u00e9",
  "highlights.isolatedInputs": "Entradas Isoladas",
  "highlights.hBridgeMotors": "Motores H-Bridge",
  "highlights.ssrOutputs": "Sa\u00eddas SSR",
  "highlights.rs485Port": "Porta RS-485",

  // ── Overview ──
  "overview.label": "Vis\u00e3o Geral do Produto",
  "overview.title": "FeralBoard AIO-500",
  "overview.description":
    "O <b>FeralBoard AIO-500</b> \u00e9 uma plataforma integrada HMI+PLC para controlo de processos industriais, automa\u00e7\u00e3o e monitoriza\u00e7\u00e3o. Combina um controlador de I/O em tempo real (<ic>ATMEGA4809-AFR</ic>) com um painel HMI baseado em Linux embebido, comunica\u00e7\u00e3o via MQTT e um portal de gest\u00e3o na cloud. O controlador disp\u00f5e de uma fonte de alimenta\u00e7\u00e3o multi-rail integrada que aceita alimenta\u00e7\u00e3o AC via transformador integrado, com rails regulados de 24V / 12V / 5V / 3.3V. Um supervisor watchdog de hardware <ic>HT1232ARZ</ic> assegura opera\u00e7\u00e3o fi\u00e1vel sem supervis\u00e3o.",

  // ── Digital Outputs ──
  "digitalOutputs.label": "Motor PLC",
  "digitalOutputs.title": "Sa\u00eddas Digitais",
  "digitalOutputs.pwm": "Sa\u00eddas PWM (2\u00d7 H-Bridge)",
  "digitalOutputs.dac": "Sa\u00edda DAC (1\u00d7)",
  "digitalOutputs.ssr": "Sa\u00eddas SSR (3\u00d7)",
  "digitalOutputs.indicators": "Sa\u00eddas de Indica\u00e7\u00e3o e Alerta",
  "digitalOutputs.relayBank": "Banco de Rel\u00e9s com Reten\u00e7\u00e3o (24\u00d7)",

  // ── Inputs & Sensing ──
  "inputs.label": "Motor PLC",
  "inputs.title": "Entradas e Sensores",
  "inputs.colFunction": "Fun\u00e7\u00e3o",
  "inputs.colDetails": "Detalhes",

  // ── Firmware ──
  "firmware.label": "Firmware",
  "firmware.title": "Runtime PLC",

  // ── Communication ──
  "comm.label": "Comunica\u00e7\u00e3o",
  "comm.title": "Interfaces",

  // ── Power Supply ──
  "power.label": "Energia",
  "power.title": "Fonte de Alimenta\u00e7\u00e3o Integrada",
  "power.colRail": "Rail",
  "power.colRegulator": "IC Regulador",
  "power.colNotes": "Notas",

  // ── Microcontroller ──
  "mcu.label": "MCU",
  "mcu.title": "Microcontrolador",

  // ── System Architecture ──
  "architecture.label": "Sistema",
  "architecture.title": "Arquitetura",

  // ── HMI Panel ──
  "hmi.label": "HMI",
  "hmi.title": "Painel T\u00e1til",

  // ── Cloud ──
  "cloud.label": "Cloud",
  "cloud.title": "Gest\u00e3o Remota",

  // ── Features ──
  "features.label": "Capacidades",
  "features.title": "Constru\u00eddo para o Ch\u00e3o de F\u00e1brica",
  "features.card1.title": "Motor PLC ATMEGA4809-AFR",
  "features.card1.desc":
    "Controlador de I/O em tempo real com protocolo CRC-8, persist\u00eancia EEPROM e watchdog de hardware HT1232ARZ.",
  "features.card2.title": "I/O de Alta Densidade",
  "features.card2.desc":
    "24 sa\u00eddas rel\u00e9, 16 entradas isoladas, 3 drives SSR, 2 controladores H-bridge \u2014 tudo numa \u00fanica placa.",
  "features.card3.title": "Termopar de 4 Canais",
  "features.card3.desc":
    "Conversor SPI MAX31856MUD+T com suporte para tipos K/J/T/N/E/R/S/B e monitoriza\u00e7\u00e3o de falhas.",
  "features.card4.title": "RS-485 + Cloud",
  "features.card4.desc":
    "Uma porta com isolamento galv\u00e2nico (ISO3088DWR), protocolo MQTT.",
  "features.card5.title": "Ecr\u00e3 T\u00e1til HMI de 7\u2033",
  "features.card5.desc":
    "Display capacitivo alimentado por Raspberry Pi 4B com quiosque Debian.",
  "features.card6.title": "Alimenta\u00e7\u00e3o de Grau Industrial",
  "features.card6.desc":
    "Entrada de 24VAC via transformador externo com rails regulados de 24V / 12V / 5V / 3.3V, protegido por TVS.",

  // ── Applications ──
  "applications.label": "Aplica\u00e7\u00f5es",
  "applications.title": "Onde Se Encaixa",
  "applications.thermalProcess": "Controlo de Processos T\u00e9rmicos",
  "applications.hvac": "Sistemas AVAC",
  "applications.packaging": "M\u00e1quinas de Embalagem",
  "applications.conveyor": "Transporte e Manuseamento",
  "applications.environmental": "C\u00e2maras Ambientais",
  "applications.food": "Processamento Alimentar",
  "applications.water": "Tratamento de \u00c1gua",
  "applications.oem": "OEM Personalizado",

  // ── Specs ──
  "specs.label": "Especifica\u00e7\u00f5es",
  "specs.title": "Vis\u00e3o T\u00e9cnica",

  // ── I/O Summary ──
  "ioSummary.label": "Resumo I/O",
  "ioSummary.title": "Num Relance",
  "ioSummary.outputs": "Sa\u00eddas",
  "ioSummary.inputs": "Entradas",

  // ── NoteBox ──
  "noteBox.title":
    "DS Rev 1.1 \u2014 Baseado no esquem\u00e1tico de hardware (KiCad v9, PlacaControlo_v9).",
  "noteBox.text":
    "Todas as contagens de I/O, refer\u00eancias de IC e especifica\u00e7\u00f5es de interfaces verificadas contra o design real da placa. Contacte a Feralbyte para configura\u00e7\u00f5es de I/O personalizadas e op\u00e7\u00f5es de integra\u00e7\u00e3o OEM.",

  // ── Board Base Assembly ──
  "assembly.label": "Montagem",
  "assembly.title": "Montagem Base da Placa",
  "assembly.description":
    "Configura\u00e7\u00e3o padr\u00e3o da placa base. Subsistemas opcionais podem ser instalados para expandir I/O.",

  // ── Footer ──
  "footer.company": "Feralbyte Lda. \u2014 DS-AIO500-V5 R1.1",
} as const;

export default pt;
