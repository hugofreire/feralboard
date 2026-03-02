import { motion } from "framer-motion";
import { Code } from "lucide-react";
import { useTranslation } from "react-i18next";
import SectionHead from "@/components/shared/SectionHead";
import { renderChips } from "@/components/shared/ChipBadge";
import { firmwareLeft, firmwareRight } from "@/data/product";

const BulletList = ({ items, delay }: { items: readonly string[]; delay: number }) => (
  <motion.div
    initial={{ opacity: 0, y: 12 }}
    whileInView={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.4 }}
    viewport={{ once: true }}
    className="space-y-2"
  >
    {items.map((item, i) => (
      <div key={i} className="flex items-start gap-2.5 text-sm leading-relaxed text-muted-foreground">
        <div className="w-1.5 h-1.5 min-w-[6px] bg-primary rounded-sm mt-[7px]" />
        <span>{renderChips(item)}</span>
      </div>
    ))}
  </motion.div>
);

const FirmwareRuntime = () => {
  const { t } = useTranslation();

  return (
    <section id="firmware" className="py-20 px-6 bg-tint">
      <div className="max-w-6xl mx-auto">
        <SectionHead icon={Code} label={t("firmware.label")} title={t("firmware.title")} />

        <div className="grid md:grid-cols-2 gap-8">
          <BulletList items={firmwareLeft} delay={0} />
          <BulletList items={firmwareRight} delay={0.08} />
        </div>
      </div>
    </section>
  );
};

export default FirmwareRuntime;
