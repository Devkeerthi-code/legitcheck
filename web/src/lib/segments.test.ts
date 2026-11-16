import { describe, expect, it } from "vitest";
import { buildSegments, spansFromRules, type Span } from "./segments";
import type { RuleHit } from "./types";

const span = (start: number, end: number, severity: Span["severity"], ruleId: string, order = 0): Span => ({
  start,
  end,
  severity,
  ruleId,
  order,
});

const marked = (text: string, spans: Span[]) =>
  buildSegments(text, spans).map((s) => [s.text, s.span?.ruleId ?? null] as const);

describe("buildSegments", () => {
  it("returns the whole text as one plain segment when there are no spans", () => {
    expect(marked("hello world", [])).toEqual([["hello world", null]]);
  });

  it("returns nothing for empty text", () => {
    expect(buildSegments("", [span(0, 3, "high", "a")])).toEqual([]);
  });

  it("marks a single span and keeps the text around it", () => {
    expect(marked("pay the fee now", [span(4, 11, "high", "fee")])).toEqual([
      ["pay ", null],
      ["the fee", "fee"],
      [" now", null],
    ]);
  });

  it("lets the higher severity win where spans overlap", () => {
    const text = "join Telegram and pay fee";
    const result = marked(text, [span(0, 13, "medium", "chat", 0), span(5, 25, "high", "fee", 1)]);
    expect(result).toEqual([
      ["join ", "chat"],
      ["Telegram and pay fee", "fee"],
    ]);
  });

  it("splits a lower span around a higher span nested inside it", () => {
    const text = "aaaa HIGH bbbb";
    const result = marked(text, [span(0, 14, "low", "wide", 0), span(5, 9, "high", "inner", 1)]);
    expect(result).toEqual([
      ["aaaa ", "wide"],
      ["HIGH", "inner"],
      [" bbbb", "wide"],
    ]);
  });

  it("breaks severity ties by rule order", () => {
    const result = marked("abcdef", [span(0, 6, "medium", "second", 1), span(2, 4, "medium", "first", 0)]);
    expect(result).toEqual([
      ["ab", "second"],
      ["cd", "first"],
      ["ef", "second"],
    ]);
  });

  it("merges pieces with the same winner and keeps every covered rule", () => {
    const segs = buildSegments("join Telegram and pay fee", [span(0, 13, "medium", "chat", 0), span(5, 25, "high", "fee", 1)]);
    expect(segs[1]?.ruleIds).toEqual(["fee", "chat"]);
  });

  it("records every covering rule, winner first", () => {
    const segs = buildSegments("abcdef", [span(0, 6, "medium", "m", 0), span(2, 4, "high", "h", 1)]);
    expect(segs[1]?.ruleIds).toEqual(["h", "m"]);
  });

  it("marks closesSpan only on the piece where the winning span ends", () => {
    const segs = buildSegments("aaaa HIGH bbbb", [span(0, 14, "low", "wide", 0), span(5, 9, "high", "inner", 1)]);
    expect(segs.map((s) => s.closesSpan)).toEqual([false, true, true]);
  });

  it("merges identical duplicate spans", () => {
    expect(marked("fee fee", [span(0, 3, "high", "x"), span(0, 3, "high", "x")])).toEqual([
      ["fee", "x"],
      [" fee", null],
    ]);
  });

  it("clamps out-of-range offsets and drops empty spans", () => {
    expect(marked("short", [span(-4, 2, "high", "a"), span(3, 99, "low", "b"), span(4, 4, "high", "c")])).toEqual([
      ["sh", "a"],
      ["o", null],
      ["rt", "b"],
    ]);
  });

  it("reassembles to the original text", () => {
    const text = "Pay ₹1,999 on Telegram today\nthen send Aadhaar";
    const segs = buildSegments(text, [span(0, 10, "high", "a", 0), span(4, 22, "medium", "b", 1), span(39, 46, "high", "c", 2)]);
    expect(segs.map((s) => s.text).join("")).toBe(text);
  });
});

describe("spansFromRules", () => {
  it("keeps only matches from the requested source", () => {
    const rules: RuleHit[] = [
      {
        id: "personal_email",
        severity: "medium",
        title: "",
        why: "",
        advice: "",
        matches: [
          { start: 0, end: 5, text: "a@b.c", source: "email" },
          { start: 10, end: 15, text: "gmail", source: "text" },
        ],
      },
    ];
    expect(spansFromRules(rules, "text")).toEqual([{ start: 10, end: 15, severity: "medium", ruleId: "personal_email", order: 0 }]);
    expect(spansFromRules(rules, "email")).toHaveLength(1);
    expect(spansFromRules(rules, "url")).toHaveLength(0);
  });
});
