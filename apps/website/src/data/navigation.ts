export interface NavItem {
  id: string;
  label: string;
  icon: string;
  flag?: string;
}

export const navItems: NavItem[] = [
  { id: "outputs", label: "Outputs", icon: "CircleDot" },
  { id: "inputs", label: "Inputs", icon: "Globe" },
  { id: "firmware", label: "Firmware", icon: "Code" },
  { id: "comm", label: "Comms", icon: "Monitor" },
  { id: "power", label: "Power", icon: "Zap" },
  { id: "mcu", label: "MCU", icon: "Cpu", flag: "mcu" },
  { id: "architecture", label: "Architecture", icon: "Laptop" },
  { id: "hmi", label: "HMI", icon: "MonitorSmartphone" },
  { id: "cloud", label: "Cloud", icon: "Cloud", flag: "cloud" },
  { id: "features", label: "Features", icon: "Shield" },
  { id: "applications", label: "Apps", icon: "Tag" },
  { id: "specs", label: "Specs", icon: "FileText" },
  { id: "io-summary", label: "I/O", icon: "LayoutList" },
  { id: "assembly", label: "Assembly", icon: "Wrench", flag: "assembly" },
];
