import { Monitor } from "lucide-react";
import { useTranslation } from "react-i18next";
import SectionHead from "@/components/shared/SectionHead";
import SystemBlock from "@/components/shared/SystemBlock";
import { hmiItems, hmiHardwareItems } from "@/data/product";

const HMIPanel = () => {
  const { t } = useTranslation();

  return (
    <section id="hmi" className="py-20 px-6">
      <div className="max-w-6xl mx-auto">
        <SectionHead icon={Monitor} label={t("hmi.label")} title={t("hmi.title")} />
        <SystemBlock
          tag="HMI"
          title="7\u2033 Capacitive Touchscreen \u2014 Debian-Based Kiosk System"
          items={hmiItems}
        />
        <div className="mt-6" />
        <SystemBlock
          tag="Hardware"
          title="Raspberry Pi 4B \u2014 Connectivity & I/O"
          items={hmiHardwareItems}
          delay={0.1}
        />
      </div>
    </section>
  );
};

export default HMIPanel;
