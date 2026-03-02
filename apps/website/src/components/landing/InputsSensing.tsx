import { motion } from "framer-motion";
import { Globe } from "lucide-react";
import { useTranslation } from "react-i18next";
import SectionHead from "@/components/shared/SectionHead";
import { renderChips, IsoBadge } from "@/components/shared/ChipBadge";
import { inputRows } from "@/data/product";

const InputsSensing = () => {
  const { t } = useTranslation();

  return (
    <section id="inputs" className="py-20 px-6">
      <div className="max-w-6xl mx-auto">
        <SectionHead icon={Globe} label={t("inputs.label")} title={t("inputs.title")} />

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="border border-rule rounded-lg overflow-hidden"
        >
          {/* Table header */}
          <div className="bg-ink grid grid-cols-[200px_1fr] md:grid-cols-[220px_1fr]">
            <div className="px-4 py-3 font-mono text-[10px] font-semibold uppercase tracking-[1.5px] text-white">
              {t("inputs.colFunction")}
            </div>
            <div className="px-4 py-3 font-mono text-[10px] font-semibold uppercase tracking-[1.5px] text-white">
              {t("inputs.colDetails")}
            </div>
          </div>

          {/* Table rows */}
          {inputRows.map((row, i) => (
            <div
              key={row.label}
              className={`grid grid-cols-[200px_1fr] md:grid-cols-[220px_1fr] text-sm ${
                i % 2 === 0 ? "bg-tint" : "bg-background"
              }`}
            >
              <div className="px-4 py-3 font-semibold text-foreground">
                {row.label}
                {row.badge && (
                  <>
                    <br />
                    <IsoBadge label={row.badge} />
                  </>
                )}
              </div>
              <div className="px-4 py-3 text-muted-foreground leading-relaxed">
                {renderChips(row.details)}
              </div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

export default InputsSensing;
