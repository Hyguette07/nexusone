"use client";

import { DISCLAIMER } from "@/lib/labels";

export function DisclaimerBanner({ compact = false }: { compact?: boolean }) {
  return (
    <p
      className={`rounded-lg border border-signal/40 bg-signal/10 text-signal ${
        compact ? "px-3 py-2 text-[11px] tracking-wide" : "px-4 py-3 text-xs"
      }`}
      role="note"
    >
      {DISCLAIMER}
    </p>
  );
}
