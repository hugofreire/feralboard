import { motion } from "framer-motion";
import { useTranslation } from "react-i18next";

const Hero = () => {
  const { t } = useTranslation();

  return (
    <section id="hero" className="relative overflow-hidden bg-[#0d0d14]">
      <div className="absolute top-0 right-0 w-1/3 h-full bg-gradient-to-br from-[#6c3dd1] to-[#4a1fa0]"
           style={{ clipPath: "polygon(30% 0, 100% 0, 100% 100%, 0 100%)" }} />

      <div className="relative z-10 max-w-6xl mx-auto px-8 py-10 md:py-14">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 border-2 border-[#8b6ce0] rounded-md flex items-center justify-center font-mono font-bold text-[#8b6ce0] text-sm">
                FB
              </div>
              <span className="font-display font-bold text-xl tracking-wider text-white uppercase">
                FERAL<span className="font-light text-[#8b6ce0]">BYTE</span>
              </span>
            </div>
            <span className="font-mono text-[10px] tracking-[4px] uppercase text-[#8b6ce0]/80">
              {t("hero.datasheetLabel")}
            </span>
          </div>

          <h1 className="font-display text-3xl md:text-4xl font-extrabold text-white tracking-tight leading-tight mb-2">
            {t("hero.title")}
          </h1>

          <p className="font-mono text-[10px] tracking-[3px] uppercase text-[#8b6ce0]/70 mb-4">
            {t("hero.subtitle")}&nbsp;&nbsp;&middot;&nbsp;&nbsp;HW Rev V5&nbsp;&nbsp;&middot;&nbsp;&nbsp;DS Rev 1.1
          </p>

          <p className="text-gray-400 max-w-xl text-sm leading-relaxed">
            {t("hero.description")}
          </p>
        </motion.div>
      </div>
    </section>
  );
};

export default Hero;
