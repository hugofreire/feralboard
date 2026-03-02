import { useTranslation } from "react-i18next";

const Footer = () => {
  const { t } = useTranslation();

  return (
    <footer id="contact" className="bg-ink py-12 px-6">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 border-2 border-primary-light rounded flex items-center justify-center font-mono font-bold text-primary-light text-xs">
            FB
          </div>
          <span className="font-display font-bold text-sm tracking-wider text-primary-foreground uppercase">
            FERAL<span className="font-light text-primary-light">BYTE</span>
          </span>
        </div>
        <p className="font-mono text-[10px] tracking-wider text-primary-foreground/40 uppercase">
          {t("footer.company")}
        </p>
      </div>
    </footer>
  );
};

export default Footer;
