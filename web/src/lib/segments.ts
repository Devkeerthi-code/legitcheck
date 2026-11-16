import { SEVERITY_RANK } from "./severity";
import type { RuleHit, MatchSource, Severity } from "./types";

export interface Span {
  start: number;
  end: number;
  severity: Severity;
  ruleId: string;
  /** Position of the rule in the response, used as the tiebreak and for the footnote number. */
  order: number;
}

export interface Segment {
  start: number;
  end: number;
  text: string;
  /** The winning span for this piece of text, or null for plain text. */
  span: Span | null;
  /** Every rule that covers this piece, winner first. */
  ruleIds: string[];
  /** True when this piece ends where its winning span ends, so the footnote goes here once. */
  closesSpan: boolean;
}

/** Collects the match spans from one source (text, url or email) of the API response. */
export function spansFromRules(rules: RuleHit[], source: MatchSource): Span[] {
  return rules.flatMap((rule, order) =>
    rule.matches
      .filter((m) => m.source === source)
      .map((m) => ({ start: m.start, end: m.end, severity: rule.severity, ruleId: rule.id, order })),
  );
}

function outranks(a: Span, b: Span): boolean {
  const bySeverity = SEVERITY_RANK[a.severity] - SEVERITY_RANK[b.severity];
  if (bySeverity !== 0) return bySeverity > 0;
  if (a.order !== b.order) return a.order < b.order;
  return a.end - a.start > b.end - b.start;
}

function clampSpans(text: string, spans: Span[]): Span[] {
  return spans
    .map((s) => ({ ...s, start: Math.max(0, Math.floor(s.start)), end: Math.min(text.length, Math.floor(s.end)) }))
    .filter((s) => Number.isFinite(s.start) && Number.isFinite(s.end) && s.end > s.start);
}

/**
 * Splits text into non-overlapping segments. Where spans overlap, the higher severity wins
 * (then the earlier rule, then the longer span). Adjacent pieces with the same winner merge.
 */
export function buildSegments(text: string, rawSpans: Span[]): Segment[] {
  if (!text) return [];
  const spans = clampSpans(text, rawSpans);
  const cuts = new Set<number>([0, text.length]);
  for (const s of spans) {
    cuts.add(s.start);
    cuts.add(s.end);
  }
  const points = [...cuts].sort((a, b) => a - b);

  const segments: Segment[] = [];
  for (let i = 0; i < points.length - 1; i++) {
    const start = points[i]!;
    const end = points[i + 1]!;
    const covering = spans.filter((s) => s.start <= start && s.end >= end);
    covering.sort((a, b) => (outranks(a, b) ? -1 : outranks(b, a) ? 1 : 0));
    const winner = covering[0] ?? null;
    const ruleIds = [...new Set(covering.map((s) => s.ruleId))];
    const prev = segments[segments.length - 1];

    if (prev && prev.span === winner) {
      prev.end = end;
      prev.text = text.slice(prev.start, end);
      prev.ruleIds = [...new Set([...prev.ruleIds, ...ruleIds])];
    } else {
      segments.push({ start, end, text: text.slice(start, end), span: winner, ruleIds, closesSpan: false });
    }
  }
  for (const seg of segments) seg.closesSpan = seg.span !== null && seg.end === seg.span.end;
  return segments;
}
