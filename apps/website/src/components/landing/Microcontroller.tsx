import { Cpu } from "lucide-react";
import { useTranslation } from "react-i18next";
import SectionHead from "@/components/shared/SectionHead";
import InterfaceCard from "@/components/shared/InterfaceCard";
import { mcuCore, mcuSupervisory } from "@/data/product";

const Microcontroller = () => {
  const { t } = useTranslation();

  return (
    <section id="mcu" className="py-20 px-6">
      <div className="max-w-6xl mx-auto">
        <SectionHead icon={Cpu} label={t("mcu.label")} title={t("mcu.title")} />

        <div className="grid md:grid-cols-2 gap-4">
          <InterfaceCard name={mcuCore.name} items={mcuCore.items} delay={0} />
          <InterfaceCard name={mcuSupervisory.name} items={mcuSupervisory.items} delay={0.08} />
        </div>
      </div>
    </section>
  );
};

export default Microcontroller;
