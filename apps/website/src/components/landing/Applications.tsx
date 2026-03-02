import { motion } from "framer-motion";
import { useTranslation } from "react-i18next";

const tagKeys = [
  "applications.thermalProcess",
  "applications.hvac",
  "applications.packaging",
  "applications.conveyor",
  "applications.environmental",
  "applications.food",
  "applications.water",
  "applications.oem",
] as const;

const Applications = () => {
  const { t } = useTranslation();

  return (
    <section id="applications" className="py-16 px-6">
      <div className="max-w-4xl mx-auto text-center">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
        >
          <p className="font-mono text-[10px] uppercase tracking-[3px] text-primary mb-2">{t("applications.label")}</p>
          <h2 className="font-display text-3xl font-bold text-foreground mb-8">{t("applications.title")}</h2>
          <div className="flex flex-wrap justify-center gap-3">
            {tagKeys.map((key, i) => (
              <motion.span
                key={key}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.05 }}
                viewport={{ once: true }}
                className="font-mono text-xs uppercase tracking-wider px-4 py-2 rounded-md bg-tint-accent text-primary-dark border border-primary/10"
              >
                {t(key)}
              </motion.span>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default Applications;
