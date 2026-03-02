import { motion } from "framer-motion";

interface SystemBlockItem {
  label: string;
  value: string;
}

interface SystemBlockProps {
  tag: string;
  title: string;
  items: readonly SystemBlockItem[];
  singleCol?: boolean;
  delay?: number;
}

const SystemBlock = ({ tag, title, items, singleCol, delay = 0 }: SystemBlockProps) => (
  <motion.div
    initial={{ opacity: 0, y: 16 }}
    whileInView={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.4 }}
    viewport={{ once: true }}
    className="border-2 border-rule rounded-lg overflow-hidden"
  >
    <div className="bg-ink px-5 py-3 flex items-center gap-3">
      <span className="font-mono text-[10px] font-semibold bg-primary text-primary-foreground px-2.5 py-0.5 rounded uppercase tracking-wider">
        {tag}
      </span>
      <h3 className="font-display text-sm font-semibold text-white">{title}</h3>
    </div>
    <div className={`p-5 grid gap-3 ${singleCol ? "grid-cols-1" : "grid-cols-1 md:grid-cols-2"} gap-x-8`}>
      {items.map((item, i) => (
        <div key={i} className="flex items-start gap-2.5 text-sm text-muted-foreground leading-relaxed">
          <div className="w-1.5 h-1.5 min-w-[6px] rounded-full bg-primary mt-[7px]" />
          <span>
            <strong className="font-semibold text-foreground">{item.label}:</strong> {item.value}
          </span>
        </div>
      ))}
    </div>
  </motion.div>
);

export default SystemBlock;
