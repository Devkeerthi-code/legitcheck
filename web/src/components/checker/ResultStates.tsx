"use client";

import { useEffect, useState } from "react";
import { Icon } from "../Icon";
import { YouDecide } from "../verdict/YouDecide";
import { OFFLINE_CHECKLIST } from "@/lib/checklist";
import { wakeUpHintSeconds, type ApiProblem } from "@/lib/errors";

export function EmptyReport() {
  return (
    <div className="result-empty">
      <svg viewBox="0 0 120 96" aria-hidden="true">
        <rect x="18" y="8" width="72" height="84" rx="8" fill="var(--surface)" stroke="var(--line-2)" strokeWidth="1.5" />
        <rect x="28" y="22" width="44" height="5" rx="2.5" fill="var(--line)" />
        <rect x="26" y="34" width="56" height="9" rx="3" fill="var(--warn-mark)" />
        <rect x="28" y="50" width="38" height="5" rx="2.5" fill="var(--line)" />
        <rect x="28" y="62" width="48" height="5" rx="2.5" fill="var(--line)" />
        <circle cx="88" cy="66" r="16" fill="none" stroke="var(--ink)" strokeWidth="3" />
        <path d="M99 78l12 12" stroke="var(--ink)" strokeWidth="4" strokeLinecap="round" />
      </svg>
      <h3>Your report appears here</h3>
      <p>Paste a message and press Check. Each warning sign shows up with the exact words highlighted.</p>
    </div>
  );
}

const SLOW_AFTER_MS = 6000;

/** Skeleton in the shape of the report, plus a note if a sleeping server is taking its time. */
export function LoadingReport() {
  const [slow, setSlow] = useState(false);
  useEffect(() => {
    const id = window.setTimeout(() => setSlow(true), SLOW_AFTER_MS);
    return () => window.clearTimeout(id);
  }, []);
  return (
    <div className="verdict-screen loading-report" aria-busy="true">
      <div className="vs-top">
        <div className="skel skel-row">
          <i style={{ width: 120, height: 32, borderRadius: 999 }} />
          <i style={{ width: 160 }} />
        </div>
      </div>
      <div className="vs-grid">
        <div className="vs-doc skel">
          <i style={{ width: "55%" }} />
          <i />
          <i style={{ width: "92%" }} />
          <i style={{ width: "80%" }} />
          <i style={{ width: "88%" }} />
          <i style={{ width: "60%" }} />
        </div>
        <div className="vs-side skel">
          <i style={{ height: 150, borderRadius: 16 }} />
          <i style={{ height: 76, width: "70%" }} />
          <i style={{ height: 12 }} />
          <i style={{ height: 12, width: "80%" }} />
        </div>
      </div>
      <p className="loading-note" role="status">
        {slow
          ? "Still working. If the checker was asleep (free hosting), waking it takes about 30 to 50 seconds. Keep this tab open."
          : "Checking against the rules and the model…"}
      </p>
    </div>
  );
}

interface ProblemProps {
  problem: ApiProblem;
  attempt: number;
  cooldownLeft: number;
  onRetry: () => void;
}

export function ProblemReport({ problem, attempt, cooldownLeft, onRetry }: ProblemProps) {
  const canRetry = problem.kind === "asleep" || problem.kind === "server" || problem.kind === "rate_limited";
  const icon = problem.kind === "asleep" ? "wifiOff" : problem.kind === "rate_limited" ? "clock" : "info";
  return (
    <div className="problem-wrap">
      <div className={`problem problem-${problem.kind}`} role="alert">
        <span className="problem-icon">
          <Icon name={icon} />
        </span>
        <div className="problem-body">
          <h3>{problem.title}</h3>
          <p>{problem.message}</p>
          {problem.kind === "asleep" && attempt > 1 && (
            <p className="fine">
              Attempt {attempt}. Give it about {wakeUpHintSeconds(attempt)} seconds before the next try.
            </p>
          )}
          {canRetry && (
            <button className="btn btn-primary btn-sm" type="button" onClick={onRetry} disabled={cooldownLeft > 0}>
              <Icon name="replay" size={16} />
              {cooldownLeft > 0 ? `Try again in ${cooldownLeft}s` : "Try again"}
            </button>
          )}
        </div>
      </div>
      <div className="verdict-screen">
        <YouDecide verdict="unknown" checklist={OFFLINE_CHECKLIST} />
      </div>
    </div>
  );
}
