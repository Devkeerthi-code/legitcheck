import { describe, expect, it } from "vitest";
import { describeFailure, wakeUpHintSeconds } from "./errors";

describe("describeFailure", () => {
  it("shows the pydantic message in plain words and names the field", () => {
    const problem = describeFailure({
      type: "http",
      status: 422,
      body: {
        detail: [{ type: "value_error", loc: ["body", "email"], msg: "Value error, That doesn't look like an email address." }],
      },
    });
    expect(problem).toMatchObject({ kind: "validation", field: "email", message: "That doesn't look like an email address." });
  });

  it("falls back to a generic validation message when the body is not the FastAPI shape", () => {
    const problem = describeFailure({ type: "http", status: 422, body: "<html>" });
    expect(problem.kind).toBe("validation");
    expect(problem.message).toMatch(/try again/i);
    expect(problem.field).toBeUndefined();
  });

  it("accepts a string detail", () => {
    expect(describeFailure({ type: "http", status: 400, body: { detail: "Bad input." } }).message).toBe("Bad input.");
  });

  it("maps 413 to a too-large problem on the text field", () => {
    expect(describeFailure({ type: "http", status: 413, body: { detail: "Request too large." } })).toMatchObject({
      kind: "too_large",
      field: "text",
    });
  });

  it("reads Retry-After on 429, with a sane default and cap", () => {
    expect(describeFailure({ type: "http", status: 429, body: null, retryAfter: "17" }).retryAfterSec).toBe(17);
    expect(describeFailure({ type: "http", status: 429, body: null, retryAfter: null }).retryAfterSec).toBe(60);
    expect(describeFailure({ type: "http", status: 429, body: null, retryAfter: "nonsense" }).retryAfterSec).toBe(60);
    expect(describeFailure({ type: "http", status: 429, body: null, retryAfter: "99999" }).retryAfterSec).toBe(3600);
  });

  it("treats network errors and gateway errors as a sleeping API", () => {
    expect(describeFailure({ type: "network" }).kind).toBe("asleep");
    expect(describeFailure({ type: "http", status: 503, body: null }).kind).toBe("asleep");
  });

  it("reports other statuses as a server error with the code", () => {
    const problem = describeFailure({ type: "http", status: 500, body: null });
    expect(problem.kind).toBe("server");
    expect(problem.message).toContain("500");
  });

  it("recognises aborted requests", () => {
    expect(describeFailure({ type: "aborted" }).kind).toBe("aborted");
  });

  it("never claims anything is safe", () => {
    const all = [
      describeFailure({ type: "network" }),
      describeFailure({ type: "http", status: 429, body: null }),
      describeFailure({ type: "http", status: 500, body: null }),
    ];
    for (const p of all) expect(`${p.title} ${p.message}`.toLowerCase()).not.toContain("safe");
  });
});

describe("wakeUpHintSeconds", () => {
  it("grows with attempts and caps at a minute", () => {
    expect([1, 2, 3, 4].map(wakeUpHintSeconds)).toEqual([15, 30, 60, 60]);
  });
});
