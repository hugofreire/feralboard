import { motion } from "framer-motion";
import { useTranslation } from "react-i18next";

const items = [
  { val: "4\u00d7", labelKey: "highlights.tcChannels" },
  { val: "24", labelKey: "highlights.relayOutputs" },
  { val: "16", labelKey: "highlights.isolatedInputs" },
  { val: "2\u00d7", labelKey: "highlights.hBridgeMotors" },
  { val: "3\u00d7", labelKey: "highlights.ssrOutputs" },
  { val: "1\u00d7", labelKey: "highlights.rs485Port" },
];

const Highlights = () => {
  const { t } = useTranslation();

  return (
    <section id="highlights" className="border-b border-rule">
      <div className="max-w-6xl mx-auto grid grid-cols-3 sm:grid-cols-4 md:grid-cols-7">
        {items.map((item, i) => (
          <motion.div
            key={item.labelKey}
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.07, duration: 0.4 }}
            viewport={{ once: true }}
            className="py-6 px-4 text-center border-r border-rule last:border-r-0"
          >
            <div className="font-display text-2xl font-bold text-primary">{item.val}</div>
            <div className="font-mono text-[9px] uppercase tracking-[1.5px] text-muted-foreground mt-1">{t(item.labelKey)}</div>
          </motion.div>
        ))}
      </div>
    </section>
  );
};

export default Highlights;
