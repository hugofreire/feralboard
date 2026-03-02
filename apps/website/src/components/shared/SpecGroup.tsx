import { motion } from "framer-motion";
import { renderChips } from "./ChipBadge";

interface SpecGroupProps {
  title: string;
  items: readonly string[];
  delay?: number;
}

const SpecGroup = ({ title, items, delay = 0 }: SpecGroupProps) => (
  <motion.div
    initial={{ opacity: 0, y: 12 }}
    whileInView={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.4 }}
    viewport={{ once: true }}
    className="mb-6 last:mb-0"
  >
    <h4 className="font-mono text-xs font-semibold uppercase tracking-[1.5px] text-primary mb-3 pb-1.5 border-b-2 border-tint-accent">
      {title}
    </h4>
    <div className="space-y-1.5">
      {items.map((item, i) => (
        <div key={i} className="flex items-start gap-2.5 text-sm leading-relaxed text-muted-foreground">
          <div className="w-1.5 h-1.5 min-w-[6px] bg-primary rounded-sm mt-[7px]" />
          <span>{renderChips(item)}</span>
        </div>
      ))}
    </div>
  </motion.div>
);

export default SpecGroup;
