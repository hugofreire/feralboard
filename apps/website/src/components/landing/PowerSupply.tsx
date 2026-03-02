import { motion } from "framer-motion";
import { Zap } from "lucide-react";
import { useTranslation } from "react-i18next";
import SectionHead from "@/components/shared/SectionHead";
import { renderChips } from "@/components/shared/ChipBadge";
import { powerRails } from "@/data/product";

const PowerSupply = () => {
  const { t } = useTranslation();

  return (
    <section id="power" className="py-20 px-6 bg-tint">
      <div className="max-w-6xl mx-auto">
        <SectionHead icon={Zap} label={t("power.label")} title={t("power.title")} />

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="border border-rule rounded-lg overflow-hidden"
        >
          {/* Table header */}
          <div className="bg-ink grid grid-cols-[140px_1fr_1fr] md:grid-cols-[160px_1fr_1fr]">
            <div className="px-4 py-3 font-mono text-[10px] font-semibold uppercase tracking-[1.5px] text-white">
              {t("power.colRail")}
            </div>
            <div className="px-4 py-3 font-mono text-[10px] font-semibold uppercase tracking-[1.5px] text-white">
              {t("power.colRegulator")}
            </div>
            <div className="px-4 py-3 font-mono text-[10px] font-semibold uppercase tracking-[1.5px] text-white">
              {t("power.colNotes")}
            </div>
          </div>

          {/* Table rows */}
          {powerRails.map((rail, i) => (
            <div
              key={rail.rail}
              className={`grid grid-cols-[140px_1fr_1fr] md:grid-cols-[160px_1fr_1fr] text-sm ${
                i % 2 === 0 ? "bg-tint" : "bg-background"
              }`}
            >
              <div className="px-4 py-3 font-semibold text-foreground">{rail.rail}</div>
              <div className="px-4 py-3 text-muted-foreground">{renderChips(rail.regulator)}</div>
              <div className="px-4 py-3 text-muted-foreground">{rail.notes}</div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

export default PowerSupply;
