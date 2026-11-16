import { API_URL } from "./config";
import { describeFailure, type ApiProblem } from "./errors";
import type { CheckRequest, CheckResponse, HealthResponse, StatsResponse } from "./types";

export type CheckResult = { ok: true; data: CheckResponse } | { ok: false; problem: ApiProblem };

async function readJson(res: Response): Promise<unknown> {
  try {
    return await res.json();
  } catch {
    return null;
  }
}

function isAbort(error: unknown): boolean {
  return error instanceof DOMException && error.name === "AbortError";
}

export async function postCheck(body: CheckRequest, signal: AbortSignal): Promise<CheckResult> {
  try {
    const res = await fetch(`${API_URL}/check`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal,
    });
    const json = await readJson(res);
    if (res.ok && json) return { ok: true, data: json as CheckResponse };
    return {
      ok: false,
      problem: describeFailure({ type: "http", status: res.status, body: json, retryAfter: res.headers.get("Retry-After") }),
    };
  } catch (error) {
    return { ok: false, problem: describeFailure(isAbort(error) ? { type: "aborted" } : { type: "network" }) };
  }
}

async function getJson<T>(path: string, timeoutMs: number): Promise<T | null> {
  try {
    const res = await fetch(`${API_URL}${path}`, { signal: AbortSignal.timeout(timeoutMs) });
    return res.ok ? ((await res.json()) as T) : null;
  } catch {
    return null;
  }
}

export const getHealth = () => getJson<HealthResponse>("/health", 60_000);
export const getStats = () => getJson<StatsResponse>("/stats", 15_000);

const FIRST_USE_KEY = "lc_first_use_sent";

/** Counts this browser once. No identifiers are sent, only {source: "web"}. */
export async function sendFirstUseOnce(): Promise<void> {
  try {
    if (localStorage.getItem(FIRST_USE_KEY)) return;
    const res = await fetch(`${API_URL}/events/first-use`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source: "web" }),
      keepalive: true,
    });
    if (res.ok) localStorage.setItem(FIRST_USE_KEY, "1");
  } catch {
    // Storage blocked or API asleep: try again on a later visit.
  }
}
