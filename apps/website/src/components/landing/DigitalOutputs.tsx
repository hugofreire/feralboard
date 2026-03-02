import { CircleDot } from "lucide-react";
import { useTranslation } from "react-i18next";
import SectionHead from "@/components/shared/SectionHead";
import SpecGroup from "@/components/shared/SpecGroup";
import { pwmOutputSpecs, dacOutputSpecs, ssrOutputSpecs, indicatorSpecs, relayBankSpecs } from "@/data/product";

const DigitalOutputs = () => {
  const { t } = useTranslation();

  return (
    <section id="outputs" className="py-20 px-6 bg-tint">
      <div className="max-w-6xl mx-auto">
        <SectionHead icon={CircleDot} label={t("digitalOutputs.label")} title={t("digitalOutputs.title")} />

        <div className="grid md:grid-cols-2 gap-x-12 gap-y-2">
          <div>
            <SpecGroup title={t("digitalOutputs.pwm")} items={pwmOutputSpecs} delay={0} />
            <SpecGroup title={t("digitalOutputs.dac")} items={dacOutputSpecs} delay={0.04} />
            <SpecGroup title={t("digitalOutputs.ssr")} items={ssrOutputSpecs} delay={0.08} />
          </div>
          <div>
            <SpecGroup title={t("digitalOutputs.indicators")} items={indicatorSpecs} delay={0.04} />
            <SpecGroup title={t("digitalOutputs.relayBank")} items={relayBankSpecs} delay={0.12} />
          </div>
        </div>
      </div>
    </section>
  );
};

export default DigitalOutputs;
