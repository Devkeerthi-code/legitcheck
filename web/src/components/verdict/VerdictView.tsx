"use client";

import { useState } from "react";
import { Icon } from "../Icon";
import { HighlightedText } from "./HighlightedText";
import { RuleCard } from "./RuleCard";
import { ScoreGauge } from "./ScoreGauge";
import { TopTerms } from "./TopTerms";
import { YouDecide } from "./YouDecide";
import { verdictTone } from "@/lib/severity";
import type { CheckResponse, SubmittedOffer } from "@/lib/types";

function revealCard() {
  const card = document.getElementById("rule-card");
  if (!card) return;
  const r = card.getBoundingClientRect();
  if (r.top < 64 || r.bottom > window.innerHeight) {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    card.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "nearest" });
  }
}

function MetaLine({ label, value, offer, result, selectedId, onSelect }: {
  label: string;
  value: string;
  offer: "email" | "url";
  result: CheckResponse;
  selectedId: string | null;
  onSelect: (id: string, reveal: boolean) => void;
}) {
  if (!value) return null;
  return (
    <span>
      {label}:{" "}
      <HighlightedText text={value} source={offer} rules={result.rules} selectedId={selectedId} onSelect={onSelect} />
    </span>
  );
}

export function VerdictView({ result, offer }: { result: CheckResponse; offer: SubmittedOffer }) {
  const rules = result.rules;
  const [selectedId, setSelectedId] = useState<string | null>(rules[0]?.id ?? null);
  const tone = verdictTone(result.verdict);
  const selectedIndex = Math.max(0, rules.findIndex((r) => r.id === selectedId));
  const selected = rules[selectedIndex];
  const count = rules.length;

  const select = (id: string, reveal: boolean) => {
    setSelectedId(id);
    if (reveal) requestAnimationFrame(revealCard);
  };

  return (
    <article className="verdict-screen" aria-labelledby="verdictTitle">
      <div className="vs-top">
        <div className="left">
          <h3 id="verdictTitle" className={`chip chip-${tone} chip-lg`}>
            <span className="dot" />
            {result.verdict_label}
          </h3>
          <span className="vs-count">
            {count === 0 ? "No warning-sign rules fired" : `${count} warning sign${count === 1 ? "" : "s"}`} · checked just now
          </span>
        </div>
        <span className="fine">Model {result.model_version}</span>
      </div>

      <div className="vs-grid">
        <div className="vs-doc">
          {(offer.email || offer.url) && (
            <div className="meta">
              <MetaLine label="Email" value={offer.email} offer="email" result={result} selectedId={selectedId} onSelect={select} />
              <MetaLine label="Link" value={offer.url} offer="url" result={result} selectedId={selectedId} onSelect={select} />
            </div>
          )}
          <div className="vs-text">
            <HighlightedText text={offer.text} source="text" rules={rules} selectedId={selectedId} onSelect={select} />
          </div>
          {count > 0 && (
            <p className="vs-hint">
              <Icon name="pointer" />
              Tap or focus a highlighted phrase to see which rule it triggered.
            </p>
          )}
          <div className="explain" lang={result.explanation_lang}>
            <h4>In plain words</h4>
            <p>{result.explanation}</p>
          </div>
        </div>

        <div className="vs-side">
          {selected ? (
            <div>
              <RuleCard rule={selected} index={selectedIndex} total={count} />
              {count > 1 && (
                <div className="rule-nav" role="group" aria-label="Warning signs">
                  {rules.map((r, i) => (
                    <button
                      key={r.id}
                      type="button"
                      className={r.severity === "high" ? "sev-high" : "sev-warn"}
                      aria-pressed={r.id === selected.id}
                      aria-label={`Warning sign ${i + 1}: ${r.title}`}
                      onClick={() => select(r.id, false)}
                    >
                      {i + 1}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="no-rules">
              <Icon name="check" />
              <p>
                <strong>None of the warning-sign rules fired.</strong> No fee, chat-only HR, personal email, early ID request or
                pressure wording was found. The score below is the model&apos;s second opinion.
              </p>
            </div>
          )}

          <div className="score-block">
            <ScoreGauge score={result.score} warn={result.thresholds.warn} high={result.thresholds.high} tone={tone} />
            <p className="lbl">
              <strong>Model score: {result.score.toFixed(2)}</strong>
              How much the wording looks like fake postings the model learned from, from 0 to 1. A likelihood, not proof. Marks
              show the warning ({result.thresholds.warn.toFixed(2)}) and high-risk ({result.thresholds.high.toFixed(2)}) lines.
            </p>
          </div>
          {result.model_note && (
            <p className="model-note" role="note">
              <Icon name="info" />
              {result.model_note}
            </p>
          )}

          {result.reasons.length > 0 && (
            <div className="reasons">
              <h4>Why this verdict</h4>
              <ul>
                {result.reasons.map((r) => (
                  <li key={r}>{r}</li>
                ))}
              </ul>
            </div>
          )}

          <TopTerms terms={result.top_terms} />
        </div>
      </div>

      <YouDecide verdict={result.verdict} checklist={result.checklist} disclaimer={result.disclaimer} />
    </article>
  );
}
