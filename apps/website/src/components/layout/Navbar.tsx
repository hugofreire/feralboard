import { useEffect, useState, useCallback, useMemo } from "react";
import { useTranslation } from "react-i18next";
import { navItems } from "@/data/navigation";
import { useFeatureFlags } from "@/hooks/useFeatureFlags";
import { Menu, X } from "lucide-react";
import * as Icons from "lucide-react";
import type { LucideIcon } from "lucide-react";
import type { FeatureFlag } from "@/hooks/useFeatureFlags";

const iconMap: Record<string, LucideIcon> = {
  Star: Icons.Star,
  FileText: Icons.FileText,
  CircleDot: Icons.CircleDot,
  Globe: Icons.Globe,
  Code: Icons.Code,
  Monitor: Icons.Monitor,
  Zap: Icons.Zap,
  Cpu: Icons.Cpu,
  Laptop: Icons.Laptop,
  MonitorSmartphone: Icons.MonitorSmartphone,
  Cloud: Icons.Cloud,
  Shield: Icons.Shield,
  Tag: Icons.Tag,
  LayoutList: Icons.LayoutList,
  Wrench: Icons.Wrench,
};

const Navbar = () => {
  const { t, i18n } = useTranslation();
  const { isEnabled } = useFeatureFlags();
  const [activeId, setActiveId] = useState<string>("");
  const [isOpen, setIsOpen] = useState(false);

  const visibleItems = useMemo(
    () => navItems.filter((item) => !item.flag || isEnabled(item.flag as FeatureFlag)),
    [isEnabled],
  );

  // Scroll-spy via IntersectionObserver
  useEffect(() => {
    const ids = visibleItems.map((n) => n.id);
    const elements = ids.map((id) => document.getElementById(id)).filter(Boolean) as HTMLElement[];

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visible.length > 0) {
          setActiveId(visible[0].target.id);
        }
      },
      { rootMargin: "-80px 0px -60% 0px", threshold: 0 },
    );

    elements.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, [visibleItems]);

  const scrollTo = useCallback((id: string) => {
    const el = document.getElementById(id);
    if (el) {
      const offset = 64;
      const top = el.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({ top, behavior: "smooth" });
    }
    setIsOpen(false);
  }, []);

  const toggleLang = useCallback(() => {
    const next = i18n.language === "pt" ? "en" : "pt";
    i18n.changeLanguage(next);
    const url = new URL(window.location.href);
    url.searchParams.set("lang", next);
    window.history.replaceState(null, "", url.toString());
  }, [i18n]);

  const langLabel = i18n.language === "pt" ? "EN" : "PT";

  return (
    <nav className="sticky top-0 z-50 bg-background/90 backdrop-blur-sm border-b border-rule">
      {/* Desktop nav */}
      <div className="max-w-6xl mx-auto px-4 hidden md:flex items-center gap-1 h-12">
        {visibleItems.map((item) => {
          const Icon = iconMap[item.icon];
          return (
            <button
              key={item.id}
              onClick={() => scrollTo(item.id)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-mono tracking-wide transition-colors whitespace-nowrap
                ${activeId === item.id
                  ? "bg-primary/10 text-primary font-semibold"
                  : "text-muted-foreground hover:text-foreground hover:bg-tint"
                }`}
            >
              {Icon && <Icon className="w-3 h-3" strokeWidth={1.5} />}
              {t(`nav.${item.id}`)}
            </button>
          );
        })}
        <div className="flex-1" />
        <button
          onClick={toggleLang}
          className="px-2.5 py-1 rounded text-[10px] font-mono font-semibold tracking-wider uppercase border border-rule text-muted-foreground hover:text-foreground hover:bg-tint transition-colors"
        >
          {langLabel}
        </button>
      </div>

      {/* Mobile nav */}
      <div className="md:hidden flex items-center justify-between px-4 h-12">
        <span className="font-mono text-xs text-muted-foreground uppercase tracking-wider">
          {activeId ? t(`nav.${activeId}`) : "Navigation"}
        </span>
        <div className="flex items-center gap-2">
          <button
            onClick={toggleLang}
            className="px-2 py-1 rounded text-[10px] font-mono font-semibold tracking-wider uppercase border border-rule text-muted-foreground hover:text-foreground hover:bg-tint transition-colors"
          >
            {langLabel}
          </button>
          <button onClick={() => setIsOpen(!isOpen)} className="p-1.5 rounded hover:bg-tint">
            {isOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile dropdown */}
      {isOpen && (
        <div className="md:hidden border-t border-rule bg-background px-4 py-2 max-h-[60vh] overflow-y-auto">
          {visibleItems.map((item) => {
            const Icon = iconMap[item.icon];
            return (
              <button
                key={item.id}
                onClick={() => scrollTo(item.id)}
                className={`flex items-center gap-2.5 w-full px-3 py-2.5 rounded text-sm font-mono transition-colors
                  ${activeId === item.id
                    ? "bg-primary/10 text-primary font-semibold"
                    : "text-muted-foreground hover:text-foreground hover:bg-tint"
                  }`}
              >
                {Icon && <Icon className="w-4 h-4" strokeWidth={1.5} />}
                {t(`nav.${item.id}`)}
              </button>
            );
          })}
        </div>
      )}
    </nav>
  );
};

export default Navbar;
