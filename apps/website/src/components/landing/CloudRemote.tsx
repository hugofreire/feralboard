import { Cloud } from "lucide-react";
import { useTranslation } from "react-i18next";
import SectionHead from "@/components/shared/SectionHead";
import SystemBlock from "@/components/shared/SystemBlock";
import { cloudItems } from "@/data/product";

const CloudRemote = () => {
  const { t } = useTranslation();

  return (
    <section id="cloud" className="py-20 px-6 bg-tint">
      <div className="max-w-6xl mx-auto">
        <SectionHead icon={Cloud} label={t("cloud.label")} title={t("cloud.title")} />
        <SystemBlock
          tag="Cloud"
          title="Remote Configuration & Monitoring Portal"
          items={cloudItems}
          singleCol
        />
      </div>
    </section>
  );
};

export default CloudRemote;
