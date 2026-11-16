import type { Severity, Verdict } from "./types";

export const SEVERITY_RANK: Record<Severity, number> = { high: 3, medium: 2, low: 1 };

/** Visual tone: the design system has two mark colours, red for high and amber for the rest. */
export type Tone = "high" | "warn";

export function toneOf(severity: Severity): Tone {
  return severity === "high" ? "high" : "warn";
}

export function severityLabel(severity: Severity): string {
  return { high: "High", medium: "Warning", low: "Low" }[severity];
}

export function verdictTone(verdict: Verdict): "high" | "warn" | "ok" {
  return { high_risk: "high", warning: "warn", consistent: "ok" }[verdict] as "high" | "warn" | "ok";
}
