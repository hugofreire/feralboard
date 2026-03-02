import { useMemo } from "react";

const VALID_FLAGS = ["cloud", "mcu", "assembly", "dsrev"] as const;
export type FeatureFlag = (typeof VALID_FLAGS)[number];

export function useFeatureFlags() {
  const enabled = useMemo(() => {
    const params = new URLSearchParams(window.location.search);
    const raw = params.get("flags") ?? "";
    const set = new Set(
      raw
        .split(",")
        .map((f) => f.trim().toLowerCase())
        .filter((f): f is FeatureFlag =>
          (VALID_FLAGS as readonly string[]).includes(f),
        ),
    );
    return set;
  }, []);

  return {
    isEnabled: (flag: FeatureFlag) => enabled.has(flag),
  };
}
