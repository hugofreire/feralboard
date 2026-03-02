import { motion } from "framer-motion";
import { Laptop } from "lucide-react";
import { useTranslation } from "react-i18next";
import SectionHead from "@/components/shared/SectionHead";
import { archNodes, archArrows } from "@/data/product";

const nodeStyles: Record<string, string> = {
  psu: "bg-amber-50 border-2 border-amber-400 text-amber-900",
  controller: "bg-ink border-2 border-primary text-white",
  hmi: "bg-primary-dark text-white",
  cloud: "bg-background border-2 border-rule text-foreground",
};

const SystemArchitecture = () => {
  const { t } = useTranslation();

  return (
    <section id="architecture" className="py-20 px-6 bg-tint">
      <div className="max-w-6xl mx-auto">
        <SectionHead icon={Laptop} label={t("architecture.label")} title={t("architecture.title")} />

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="border border-rule rounded-lg bg-background p-6 md:p-8"
        >
          {/* Horizontal flow on desktop, vertical on mobile */}
          <div className="flex flex-col md:flex-row items-center justify-center gap-4 md:gap-2">
            {archNodes.map((node, i) => (
              <div key={node.id} className="contents">
                {/* Node */}
                <div
                  className={`${nodeStyles[node.variant]} rounded-lg px-5 py-4 font-mono text-xs font-semibold uppercase tracking-wider text-center min-w-[140px] leading-relaxed`}
                >
                  {node.label.split("\n").map((line, j) => (
                    <span key={j}>
                      {line}
                      {j < node.label.split("\n").length - 1 && <br />}
                    </span>
                  ))}
                  <br />
                  <span className="text-[10px] opacity-60 normal-case">{node.sub}</span>
                </div>

                {/* Arrow (not after last node) */}
                {i < archNodes.length - 1 && (
                  <div className="flex flex-col md:flex-row items-center gap-1 py-2 md:py-0 md:px-1">
                    {/* Vertical arrow for mobile */}
                    <div className="md:hidden flex flex-col items-center gap-0.5">
                      <span className="font-mono text-[9px] text-light uppercase tracking-wider">
                        {archArrows[i].top}
                      </span>
                      <div className="w-0.5 h-6 bg-primary relative">
                        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-full border-l-[5px] border-l-transparent border-r-[5px] border-r-transparent border-t-[6px] border-t-primary" />
                      </div>
                      <span className="font-mono text-[9px] text-light uppercase tracking-wider mt-1">
                        {archArrows[i].bottom}
                      </span>
                    </div>

                    {/* Horizontal arrow for desktop */}
                    <div className="hidden md:flex flex-col items-center gap-0.5">
                      <span className="font-mono text-[9px] text-light uppercase tracking-wider">
                        {archArrows[i].top}
                      </span>
                      <div className="w-10 h-0.5 bg-primary relative">
                        <div className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-full border-t-[5px] border-t-transparent border-b-[5px] border-b-transparent border-l-[6px] border-l-primary" />
                      </div>
                      <span className="font-mono text-[9px] text-light uppercase tracking-wider">
                        {archArrows[i].bottom}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default SystemArchitecture;
