import { motion } from "framer-motion";
import { renderChips, IsoBadge } from "./ChipBadge";

interface InterfaceCardProps {
  name: string;
  isolated?: boolean;
  items?: { label: string; value: string }[];
  lines?: string[];
  delay?: number;
}

const InterfaceCard = ({ name, isolated, items, lines, delay = 0 }: InterfaceCardProps) => (
  <motion.div
    initial={{ opacity: 0, y: 12 }}
    whileInView={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.4 }}
    viewport={{ once: true }}
    className={`border border-rule rounded-lg p-4 relative overflow-hidden ${isolated ? "border-l-success" : ""}`}
  >
    <div className={`absolute top-0 left-0 w-[3px] h-full ${isolated ? "bg-success" : "bg-primary"}`} />
    <div className="font-mono text-xs font-semibold text-foreground uppercase tracking-wider mb-2">
      {name}
      {isolated && <IsoBadge />}
    </div>
    {items && (
      <div className="space-y-1 text-sm text-muted-foreground">
        {items.map((item) => (
          <div key={item.label}>
            <strong className="font-semibold text-foreground">{item.label}:</strong>{" "}
            {renderChips(item.value)}
          </div>
        ))}
      </div>
    )}
    {lines && (
      <div className="text-sm text-muted-foreground leading-relaxed">
        {lines.map((line, i) =>
          line === "" ? (
            <br key={i} />
          ) : (
            <span key={i}>
              {renderChips(line)}
              {i < lines.length - 1 && lines[i + 1] !== "" && <br />}
            </span>
          )
        )}
      </div>
    )}
  </motion.div>
);

export default InterfaceCard;
