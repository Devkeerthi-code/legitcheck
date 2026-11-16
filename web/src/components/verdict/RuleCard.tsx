"use client";

import { useEffect, useRef } from "react";
import { severityLabel, toneOf } from "@/lib/severity";
import { spring } from "@/lib/spring";
import type { RuleHit } from "@/lib/types";

const SOURCE_LABEL = { text: "", url: " (in the link)", email: " (in the email)" } as const;

export function RuleCard({ rule, index, total }: { rule: RuleHit; index: number; total: number }) {
  const ref = useRef<HTMLDivElement>(null);
  const tone = toneOf(rule.severity);

  // Springs in on every change of rule, so the card visibly answers the tap.
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    return spring({
      from: 0,
      to: 1,
      stiffness: 300,
      damping: 20,
      onUpdate: (p) => {
        el.style.transform = `translateY(${((1 - p) * 12).toFixed(2)}px) scale(${(0.98 + 0.02 * p).toFixed(4)})`;
        el.style.opacity = String(Math.min(1, 0.3 + p));
      },
    });
  }, [rule.id]);

  const quotes = [...new Map(rule.matches.map((m) => [`${m.source}:${m.text.toLowerCase()}`, m])).values()].slice(0, 4);

  return (
    <div ref={ref} className={`rule-card${tone === "warn" ? " warn" : ""}`} id="rule-card" tabIndex={-1} aria-live="polite">
      <div className="rc-head">
        <span className={`chip chip-${tone}`}>
          <span className="dot" />
          {severityLabel(rule.severity)}
        </span>
        <span className="rc-id">
          Flag {index + 1} of {total}
        </span>
      </div>
      <h3>{rule.title}</h3>
      <dl>
        <div>
          <dt>What we saw</dt>
          <dd className="rc-quotes">
            {quotes.map((m) => (
              <span key={`${m.source}-${m.start}`}>
                <q>{m.text}</q>
                {SOURCE_LABEL[m.source]}
              </span>
            ))}
          </dd>
        </div>
        <div>
          <dt>Why it matters</dt>
          <dd>{rule.why}</dd>
        </div>
        <div>
          <dt>What to do</dt>
          <dd>{rule.advice}</dd>
        </div>
      </dl>
    </div>
  );
}
