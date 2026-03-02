import { motion } from "framer-motion";
import { MonitorSmartphone } from "lucide-react";
import { useTranslation } from "react-i18next";
import SectionHead from "@/components/shared/SectionHead";
import InterfaceCard from "@/components/shared/InterfaceCard";
import { rs485SharedNote, rs485Ports, commCards } from "@/data/product";

const CommInterfaces = () => {
  const { t } = useTranslation();

  return (
    <section id="comm" className="py-20 px-6">
      <div className="max-w-6xl mx-auto">
        <SectionHead icon={MonitorSmartphone} label={t("comm.label")} title={t("comm.title")} />

        {/* RS-485 Ports */}
        <motion.h4
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="font-mono text-xs font-semibold uppercase tracking-[1.5px] text-primary mb-2"
        >
          RS-485
        </motion.h4>
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-sm text-muted-foreground mb-4 italic"
        >
          {rs485SharedNote}
        </motion.p>
        <div className="grid md:grid-cols-2 gap-4 mb-8">
          {rs485Ports.map((port, i) => (
            <InterfaceCard
              key={`${port.name}-${port.isolated}`}
              name={port.name}
              isolated={port.isolated}
              items={[
                { label: "IC", value: `<ic>${port.ic}</ic>` },
                { label: "Isolation", value: port.isolated ? `<ic>${port.isolation.split(" ")[0]}</ic> isolated DC-DC` : port.isolation },
                { label: "Speed", value: port.speed },
              ]}
              lines={[port.extra]}
              delay={i * 0.08}
            />
          ))}
        </div>

        {/* UART / I²C / SPI */}
        <motion.h4
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="font-mono text-xs font-semibold uppercase tracking-[1.5px] text-primary mb-3"
        >
          UART · I²C · SPI
        </motion.h4>
        <div className="grid md:grid-cols-3 gap-4">
          {commCards.map((card, i) => (
            <InterfaceCard key={card.name} name={card.name} lines={card.lines} delay={i * 0.08} />
          ))}
        </div>
      </div>
    </section>
  );
};

export default CommInterfaces;
