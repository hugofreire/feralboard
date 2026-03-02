import { motion } from "framer-motion";
import { Wrench } from "lucide-react";
import { useTranslation } from "react-i18next";
import SectionHead from "@/components/shared/SectionHead";
import { renderChips } from "@/components/shared/ChipBadge";
import { boardBaseAssemblyItems } from "@/data/product";

const BoardBaseAssembly = () => {
  const { t } = useTranslation();

  return (
    <section id="assembly" className="py-20 px-6">
      <div className="max-w-6xl mx-auto">
        <SectionHead icon={Wrench} label={t("assembly.label")} title={t("assembly.title")} />

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="bg-tint-accent border border-primary/20 rounded-lg p-6"
        >
          <p className="text-sm text-muted-foreground mb-4">
            {t("assembly.description")}
          </p>
          <div className="grid md:grid-cols-2 gap-2">
            {boardBaseAssemblyItems.map((item, i) => (
              <div key={i} className="flex items-start gap-2.5 text-sm leading-relaxed text-muted-foreground">
                <div className="w-1.5 h-1.5 min-w-[6px] bg-primary rounded-sm mt-[7px]" />
                <span>{renderChips(item)}</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default BoardBaseAssembly;
