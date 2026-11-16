export type ApiErrorKind = "validation" | "too_large" | "rate_limited" | "asleep" | "server" | "aborted";

export interface ApiProblem {
  kind: ApiErrorKind;
  title: string;
  message: string;
  /** Which input the problem is about, when the API tells us. */
  field?: "text" | "url" | "email";
  retryAfterSec?: number;
}

/** What a failed request looked like, before we turn it into words. */
export type FailedRequest =
  | { type: "http"; status: number; body: unknown; retryAfter?: string | null }
  | { type: "network" }
  | { type: "aborted" };

type Field = NonNullable<ApiProblem["field"]>;

const DEFAULT_RETRY_AFTER = 60;
const FIELDS: readonly string[] = ["text", "url", "email"];

function isField(part: unknown): part is Field {
  return typeof part === "string" && FIELDS.includes(part);
}

function cleanPydanticMessage(msg: string): string {
  return msg.replace(/^Value error,\s*/i, "").trim();
}

function firstValidationDetail(body: unknown): { message: string; field?: Field } | null {
  if (!body || typeof body !== "object") return null;
  const detail = (body as { detail?: unknown }).detail;
  if (typeof detail === "string" && detail) return { message: detail };
  if (!Array.isArray(detail) || detail.length === 0) return null;
  const first = detail[0] as { msg?: unknown; loc?: unknown } | undefined;
  if (typeof first?.msg !== "string") return null;
  const loc: unknown[] = Array.isArray(first.loc) ? first.loc : [];
  return { message: cleanPydanticMessage(first.msg), field: loc.find(isField) };
}

function parseRetryAfter(value: string | null | undefined): number {
  const seconds = Number.parseInt(value ?? "", 10);
  return Number.isFinite(seconds) && seconds > 0 ? Math.min(seconds, 3600) : DEFAULT_RETRY_AFTER;
}

const ASLEEP: ApiProblem = {
  kind: "asleep",
  title: "The checker is waking up or offline",
  message:
    "It runs on free hosting that sleeps when nobody is using it. Waking up takes about 30 to 50 seconds. Your text is still here, so try again shortly.",
};

/** Turns any failed /check request into plain words a student can act on. */
export function describeFailure(failure: FailedRequest): ApiProblem {
  if (failure.type === "aborted") {
    return { kind: "aborted", title: "Check cancelled", message: "A newer check replaced this one." };
  }
  if (failure.type === "network") return ASLEEP;

  const { status, body } = failure;
  if (status === 422 || status === 400) {
    const detail = firstValidationDetail(body);
    return {
      kind: "validation",
      title: "Something in the form needs a fix",
      message: detail?.message || "Check the message, link and email, then try again.",
      field: detail?.field,
    };
  }
  if (status === 413) {
    return {
      kind: "too_large",
      title: "That's too much text",
      message: "Paste just the offer or the job posting, under 20,000 characters.",
      field: "text",
    };
  }
  if (status === 429) {
    const retryAfterSec = parseRetryAfter(failure.retryAfter);
    return {
      kind: "rate_limited",
      title: "Too many checks in a row",
      message: `To keep it free for everyone, each person gets a limited number of checks per minute. You can check again in ${retryAfterSec} seconds.`,
      retryAfterSec,
    };
  }
  if (status === 502 || status === 503 || status === 504) return ASLEEP;
  return {
    kind: "server",
    title: "The checker hit an error",
    message: `It returned an error (code ${status}). Nothing you pasted was saved. Try again in a moment.`,
  };
}

/** Suggested wait before retrying a sleeping API: grows with each failed attempt. */
export function wakeUpHintSeconds(attempt: number): number {
  return Math.min(60, 15 * 2 ** Math.max(0, attempt - 1));
}
