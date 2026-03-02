import { motion } from "framer-motion";
import { FileText } from "lucide-react";
import { useTranslation } from "react-i18next";
import SectionHead from "@/components/shared/SectionHead";
import { renderChips } from "@/components/shared/ChipBadge";
import { specifications } from "@/data/product";

const Specs = () => {
  const { t } = useTranslation();

  return (
    <section id="specs" className="py-20 px-6">
      <div className="max-w-3xl mx-auto">
        <SectionHead icon={FileText} label={t("specs.label")} title={t("specs.title")} />

        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="border border-rule rounded-lg overflow-hidden"
        >
          {specifications.map((s, i) => (
            <div
              key={s.label}
              className={`flex items-start gap-6 px-5 py-3.5 text-sm ${
                i % 2 === 0 ? "bg-tint" : "bg-background"
              }`}
            >
              <span className="font-mono text-xs uppercase tracking-wider text-foreground font-semibold w-40 shrink-0">
                {s.label}
              </span>
              <span className="text-muted-foreground">{renderChips(s.value)}</span>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

export default Specs;
