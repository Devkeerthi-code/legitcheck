"use client";

import { useMemo, type KeyboardEvent } from "react";
import { buildSegments, spansFromRules } from "@/lib/segments";
import { toneOf } from "@/lib/severity";
import type { MatchSource, RuleHit } from "@/lib/types";
import { hasFinePointer } from "@/lib/spring";

interface Props {
  text: string;
  source: MatchSource;
  rules: RuleHit[];
  selectedId: string | null;
  onSelect: (ruleId: string, reveal: boolean) => void;
}

/** The submitted text with each flagged phrase as a control that opens its rule card. */
export function HighlightedText({ text, source, rules, selectedId, onSelect }: Props) {
  const segments = useMemo(() => buildSegments(text, spansFromRules(rules, source)), [text, rules, source]);
  const titleOf = (id: string) => rules.find((r) => r.id === id)?.title ?? "";

  return segments.map((seg) => {
    if (!seg.span) return <span key={seg.start}>{seg.text}</span>;
    const { ruleId, order, severity } = seg.span;
    const tone = toneOf(severity);
    const others = seg.ruleIds.filter((id) => id !== ruleId).map(titleOf);
    const label = `Warning sign ${order + 1}: ${titleOf(ruleId)}${others.length ? `. Also: ${others.join(", ")}` : ""}. Show details`;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        onSelect(ruleId, true);
      }
    };
    return (
      <span
        key={seg.start}
        role="button"
        tabIndex={0}
        className={`rule-mark${tone === "warn" ? " warn" : ""}`}
        aria-pressed={selectedId === ruleId}
        aria-label={`${seg.text}. ${label}`}
        onClick={() => onSelect(ruleId, true)}
        onKeyDown={onKey}
        onMouseEnter={() => {
          if (hasFinePointer() && selectedId !== ruleId) onSelect(ruleId, false);
        }}
      >
        {seg.text}
        {seg.closesSpan && <sup aria-hidden="true">{order + 1}</sup>}
      </span>
    );
  });
}
