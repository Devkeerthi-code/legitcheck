import { describe, expect, it } from "vitest";
import { fmt, metrics } from "./metrics";

describe("metrics from models/metrics.json", () => {
  it("derives counts from the confusion matrix instead of hand-typed numbers", () => {
    expect(metrics.high.caught).toBeLessThanOrEqual(metrics.high.fakes);
    expect(metrics.high.fakes + metrics.high.genuine).toBe(metrics.testSize);
    expect(metrics.prAuc).toBeGreaterThan(metrics.randomPrAuc);
  });

  it("formats numbers the way the page shows them", () => {
    expect(fmt.decimal(0.879219)).toBe("0.879");
    expect(fmt.int(2352)).toBe("2,352");
    expect(fmt.percent(0.792453)).toBe("79%");
  });
});
