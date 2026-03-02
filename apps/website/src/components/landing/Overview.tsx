import { motion } from "framer-motion";
import { Star } from "lucide-react";
import { useTranslation } from "react-i18next";
import SectionHead from "@/components/shared/SectionHead";
import { renderChips } from "@/components/shared/ChipBadge";

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

const Overview = () => {
  const { t } = useTranslation();

  return (
    <section id="overview" className="py-20 px-6">
      <div className="max-w-6xl mx-auto md:grid md:grid-cols-[auto_1fr] md:gap-10 md:items-start">
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          whileInView={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="grid grid-cols-[1fr_1.4fr] grid-rows-2 gap-2 mb-8 md:mb-0 max-w-md aspect-[4/3]"
        >
          <img
            src="/feralboard-top.webp"
            alt="FeralBoard AIO-500 top view"
            className="row-span-2 w-full h-full object-cover rounded-xl"
          />
          <img
            src="/feralboard-board.webp"
            alt="FeralBoard AIO-500 board"
            className="w-full h-full object-cover rounded-xl"
          />
          <img
            src="/feralboard-render.webp"
            alt="FeralBoard AIO-500 marketing render"
            className="w-full h-full object-cover rounded-xl"
          />
        </motion.div>

        <div>
          <SectionHead icon={Star} label={t("overview.label")} title={t("overview.title")} />

          <motion.p
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-muted-foreground leading-relaxed max-w-4xl mb-6"
          >
            {renderChips(t("overview.description"))}
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.4 }}
            viewport={{ once: true }}
            className="flex flex-wrap gap-2"
          >
            {tagKeys.map((key, i) => (
              <motion.span
                key={key}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.15 + i * 0.04 }}
                viewport={{ once: true }}
                className="font-mono text-[11px] font-medium uppercase tracking-wider px-3 py-1.5 rounded bg-tint-accent text-primary-dark border border-primary/10"
              >
                {t(key)}
              </motion.span>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default Overview;
