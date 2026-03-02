import React from "react";

/**
 * Parses a string containing <ic>...</ic> and <signal>...</signal> markup
 * into React elements with styled chip badges.
 */
export function renderChips(text: string): React.ReactNode {
  const parts = text.split(/(<ic>.*?<\/ic>|<signal>.*?<\/signal>|<b>.*?<\/b>)/g);
  return parts.map((part, i) => {
    const icMatch = part.match(/^<ic>(.*?)<\/ic>$/);
    if (icMatch) {
      return <IcChip key={i} label={icMatch[1]} />;
    }
    const sigMatch = part.match(/^<signal>(.*?)<\/signal>$/);
    if (sigMatch) {
      return <SignalChip key={i} label={sigMatch[1]} />;
    }
    const boldMatch = part.match(/^<b>(.*?)<\/b>$/);
    if (boldMatch) {
      return <strong key={i} className="font-semibold text-foreground">{boldMatch[1]}</strong>;
    }
    return part;
  });
}

/** Green IC chip badge — for part numbers like ATmega4809 */
export const IcChip = ({ label }: { label: string }) => (
  <span className="inline-block font-mono text-[11px] font-semibold bg-success-light text-success px-1.5 py-px rounded align-baseline">
    {label}
  </span>
);

/** Gray signal chip — for signal names like SSR_A */
export const SignalChip = ({ label }: { label: string }) => (
  <span className="inline-block font-mono text-[11px] bg-tint text-mid px-1.5 py-px rounded align-baseline">
    {label}
  </span>
);

/** Isolated badge */
export const IsoBadge = ({ label = "Galvanic Isolated" }: { label?: string }) => (
  <span className="inline-block font-mono text-[10px] font-semibold bg-success-light text-success px-1.5 py-px rounded uppercase tracking-wider ml-2">
    {label}
  </span>
);
