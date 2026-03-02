import { motion } from "framer-motion";
import { useTranslation } from "react-i18next";

const NoteBox = () => {
  const { t } = useTranslation();

  return (
    <section className="py-12 px-6">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="bg-tint-accent border-l-[3px] border-primary rounded-r-md px-5 py-4 text-sm text-muted-foreground leading-relaxed"
        >
          <strong className="text-foreground">{t("noteBox.title")}</strong>{" "}
          {t("noteBox.text")}
        </motion.div>
      </div>
    </section>
  );
};

export default NoteBox;
