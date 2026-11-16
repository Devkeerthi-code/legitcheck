"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { postCheck } from "./api";
import type { ApiProblem } from "./errors";
import type { CheckResponse, Lang, SubmittedOffer } from "./types";

export type CheckStatus =
  | { kind: "idle" }
  | { kind: "loading"; startedAt: number }
  | { kind: "done"; result: CheckResponse; offer: SubmittedOffer }
  | { kind: "problem"; problem: ApiProblem; offer: SubmittedOffer; attempt: number };

/**
 * Owns one /check request at a time. A new submit aborts the previous request, so a slow
 * response can never overwrite a newer one.
 */
export function useCheck() {
  const [status, setStatus] = useState<CheckStatus>({ kind: "idle" });
  const controller = useRef<AbortController | null>(null);
  const failures = useRef(0);

  useEffect(() => () => controller.current?.abort(), []);

  const run = useCallback(async (offer: SubmittedOffer, lang: Lang): Promise<CheckStatus> => {
    controller.current?.abort();
    const ac = new AbortController();
    controller.current = ac;
    setStatus({ kind: "loading", startedAt: Date.now() });

    const res = await postCheck(
      { text: offer.text, url: offer.url || undefined, email: offer.email || undefined, lang, source: "web" },
      ac.signal,
    );
    if (ac.signal.aborted) return { kind: "idle" };

    let next: CheckStatus;
    if (res.ok) {
      failures.current = 0;
      next = { kind: "done", result: res.data, offer };
    } else {
      failures.current += 1;
      next = { kind: "problem", problem: res.problem, offer, attempt: failures.current };
    }
    controller.current = null;
    setStatus(next);
    return next;
  }, []);

  return { status, run, pending: status.kind === "loading" };
}

/** Seconds left until a timestamp, ticking once a second. 0 when it has passed. */
export function useCountdown(until: number | null): number {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    if (!until) return;
    const tick = () => {
      const t = Date.now();
      setNow(t);
      if (t >= until) window.clearInterval(id);
    };
    const first = window.setTimeout(tick, 0);
    const id = window.setInterval(tick, 500);
    return () => {
      window.clearTimeout(first);
      window.clearInterval(id);
    };
  }, [until]);
  return until ? Math.max(0, Math.ceil((until - now) / 1000)) : 0;
}
