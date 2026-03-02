import { motion } from "framer-motion";
import { LayoutList } from "lucide-react";
import { useTranslation } from "react-i18next";
import SectionHead from "@/components/shared/SectionHead";
import { ioOutputs, ioInputs } from "@/data/product";

const IOSummary = () => {
  const { t } = useTranslation();

  return (
    <section id="io-summary" className="py-16 px-6 bg-tint">
      <div className="max-w-4xl mx-auto">
        <SectionHead icon={LayoutList} label={t("ioSummary.label")} title={t("ioSummary.title")} />

        <div className="grid md:grid-cols-2 gap-6">
          <motion.div
            initial={{ opacity: 0, x: -12 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="border-2 border-primary rounded-lg p-6"
          >
            <p className="font-mono text-[10px] uppercase tracking-[2px] text-primary font-semibold mb-4">
              {t("ioSummary.outputs")}
            </p>
            <div className="space-y-2">
              {ioOutputs.map((o) => (
                <div key={o.desc} className="flex gap-3 text-sm">
                  <span className="font-semibold text-foreground w-8">{o.count}</span>
                  <span className="text-muted-foreground">{o.desc}</span>
                </div>
              ))}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 12 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="border-2 border-success rounded-lg p-6"
          >
            <p className="font-mono text-[10px] uppercase tracking-[2px] text-success font-semibold mb-4">
              {t("ioSummary.inputs")}
            </p>
            <div className="space-y-2">
              {ioInputs.map((inp) => (
                <div key={inp.desc} className="flex gap-3 text-sm">
                  <span className="font-semibold text-foreground w-8">{inp.count}</span>
                  <span className="text-muted-foreground">{inp.desc}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default IOSummary;
