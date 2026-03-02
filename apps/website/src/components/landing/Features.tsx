import { motion } from "framer-motion";
import { Cpu, Zap, Wifi, Monitor, Shield, ThermometerSun } from "lucide-react";
import { useTranslation } from "react-i18next";
import { featureCards } from "@/data/product";

const iconMap = { Cpu, Zap, Wifi, Monitor, Shield, ThermometerSun } as const;

const Features = () => {
  const { t } = useTranslation();

  return (
    <section id="features" className="py-20 px-6 bg-tint">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="mb-12"
        >
          <p className="font-mono text-[10px] uppercase tracking-[3px] text-primary mb-2">{t("features.label")}</p>
          <h2 className="font-display text-3xl font-bold text-foreground">{t("features.title")}</h2>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {featureCards.map((f, i) => {
            const Icon = iconMap[f.icon as keyof typeof iconMap];
            const cardNum = i + 1;
            return (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.08, duration: 0.4 }}
                viewport={{ once: true }}
                className="bg-background border border-rule rounded-lg p-6 relative overflow-hidden group hover:border-primary/30 transition-colors"
              >
                <div className="absolute top-0 left-0 w-[3px] h-full bg-primary opacity-0 group-hover:opacity-100 transition-opacity" />
                <Icon className="w-5 h-5 text-primary mb-4" strokeWidth={1.5} />
                <h3 className="font-display text-sm font-semibold text-foreground mb-2">{t(`features.card${cardNum}.title`)}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{t(`features.card${cardNum}.desc`)}</p>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default Features;
