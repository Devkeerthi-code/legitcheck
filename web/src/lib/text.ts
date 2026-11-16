import { MAX_TEXT, MIN_TEXT } from "./config";

// Mirrors the API's validator so match offsets index into exactly what we keep for highlighting.
const CONTROL_CHARS = /[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]/g;

export function normaliseOffer(raw: string): string {
  return raw.replace(CONTROL_CHARS, "").trim();
}

export function countWords(text: string): number {
  const trimmed = text.trim();
  return trimmed ? trimmed.split(/\s+/).length : 0;
}

export type LengthProblem = "empty" | "too_short" | "too_long" | null;

export function lengthProblem(text: string): LengthProblem {
  if (text.length === 0) return "empty";
  if (text.length < MIN_TEXT) return "too_short";
  if (text.length > MAX_TEXT) return "too_long";
  return null;
}
