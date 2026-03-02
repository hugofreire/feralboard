import { motion } from "framer-motion";
import type { LucideIcon } from "lucide-react";

interface SectionHeadProps {
  icon: LucideIcon;
  label: string;
  title: string;
  id?: string;
}

const SectionHead = ({ icon: Icon, label, title, id }: SectionHeadProps) => (
  <motion.div
    id={id}
    initial={{ opacity: 0 }}
    whileInView={{ opacity: 1 }}
    viewport={{ once: true }}
    className="mb-10"
  >
    <div className="flex items-center gap-3 mb-4">
      <div className="w-7 h-7 bg-primary rounded flex items-center justify-center shrink-0">
        <Icon className="w-3.5 h-3.5 text-primary-foreground" strokeWidth={2} />
      </div>
      <p className="font-mono text-[10px] uppercase tracking-[3px] text-primary">{label}</p>
      <div className="flex-1 h-px bg-rule" />
    </div>
    <h2 className="font-display text-3xl font-bold text-foreground">{title}</h2>
  </motion.div>
);

export default SectionHead;
