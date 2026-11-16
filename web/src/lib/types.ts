export type Verdict = "consistent" | "warning" | "high_risk";
export type Severity = "high" | "medium" | "low";
export type Lang = "en" | "hi" | "ta" | "kn" | "te";
export type MatchSource = "text" | "url" | "email";

export interface RuleMatch {
  start: number;
  end: number;
  text: string;
  source: MatchSource;
}

export interface RuleHit {
  id: string;
  severity: Severity;
  title: string;
  why: string;
  advice: string;
  matches: RuleMatch[];
}

export interface TopTerm {
  term: string;
  weight: number;
  direction: "towards_fake" | "towards_genuine";
}

export interface ChecklistItem {
  id: string;
  title: string;
  detail: string;
  link?: string | null;
  link_label?: string | null;
}

export interface CheckResponse {
  verdict: Verdict;
  verdict_label: string;
  reasons: string[];
  score: number;
  thresholds: { warn: number; high: number };
  rules: RuleHit[];
  top_terms: TopTerm[];
  checklist: ChecklistItem[];
  explanation: string;
  explanation_lang: Lang;
  llm_used: boolean;
  model_reliable: boolean;
  model_note: string | null;
  model_version: string;
  disclaimer: string;
}

export interface CheckRequest {
  text: string;
  url?: string;
  email?: string;
  lang: Lang;
  source: "web";
}

export interface HealthResponse {
  status: "ok";
  model_version: string;
  llm_available: boolean;
}

export interface StatsResponse {
  people: number;
  checks: number;
  by_verdict: Record<string, number>;
}

/** What the checker submitted, kept so offsets in the response line up with what we render. */
export interface SubmittedOffer {
  text: string;
  url: string;
  email: string;
}
