"use client";

import { useCallback, useEffect, useRef, useState, type FormEvent } from "react";
import { Icon } from "../Icon";
import { useToast } from "../Toasts";
import { VerdictView } from "../verdict/VerdictView";
import { EmptyReport, LoadingReport, ProblemReport } from "./ResultStates";
import { getHealth, sendFirstUseOnce } from "@/lib/api";
import { LANGUAGES, MAX_TEXT, MIN_TEXT, SHORT_MESSAGE_WORDS } from "@/lib/config";
import { SAMPLES, type Sample } from "@/lib/samples";
import { countWords, lengthProblem, normaliseOffer } from "@/lib/text";
import type { Lang, SubmittedOffer } from "@/lib/types";
import { useCheck, useCountdown, type CheckStatus } from "@/lib/useCheck";

type FieldErrors = Partial<Record<"text" | "url" | "email", string>>;

const LENGTH_MESSAGES = {
  empty: "Paste the message first. Copy the whole offer, including who sent it.",
  too_short: `That's too short to check. Paste at least ${MIN_TEXT} characters, ideally the whole message.`,
  too_long: `That's over ${MAX_TEXT.toLocaleString("en-IN")} characters. Paste just the offer or the posting.`,
} as const;

/** Reads #text=... (from the extension's "Open full report"). The text never touches a URL query or server log. */
function takeHashText(): string | null {
  const hash = window.location.hash;
  if (!hash.startsWith("#text=")) return null;
  let text: string | null = null;
  try {
    text = decodeURIComponent(hash.slice("#text=".length));
  } catch {
    text = null;
  }
  history.replaceState(null, "", window.location.pathname + window.location.search);
  return text;
}

function scrollIntoViewIfBelow(id: string) {
  const el = document.getElementById(id);
  if (!el) return;
  const r = el.getBoundingClientRect();
  if (r.top > window.innerHeight * 0.6 || r.top < 0) {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    el.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
  }
}

function successMessage(status: CheckStatus): string | null {
  if (status.kind !== "done") return null;
  const n = status.result.rules.length;
  return `Report ready: ${status.result.verdict_label}. ${n === 0 ? "No warning-sign rules fired." : `${n} warning sign${n === 1 ? "" : "s"} found.`}`;
}

export function Checker() {
  const toast = useToast();
  const { status, run, pending } = useCheck();
  const [text, setText] = useState("");
  const [email, setEmail] = useState("");
  const [url, setUrl] = useState("");
  const [lang, setLang] = useState<Lang>("en");
  const [errors, setErrors] = useState<FieldErrors>({});
  const [llmAvailable, setLlmAvailable] = useState<boolean | null>(null);
  const [cooldownUntil, setCooldownUntil] = useState<number | null>(null);
  const cooldownLeft = useCountdown(cooldownUntil);
  const textRef = useRef<HTMLTextAreaElement>(null);

  const submit = useCallback(
    async (offer: SubmittedOffer, language: Lang) => {
      const next = await run(offer, language);
      const ok = successMessage(next);
      if (ok) {
        toast(ok, "success");
        requestAnimationFrame(() => scrollIntoViewIfBelow("report"));
        return;
      }
      if (next.kind !== "problem") return;
      const { problem } = next;
      if (problem.field) setErrors({ [problem.field]: problem.message });
      if (problem.retryAfterSec) setCooldownUntil(Date.now() + problem.retryAfterSec * 1000);
      toast(problem.title, "error");
      requestAnimationFrame(() => scrollIntoViewIfBelow("report"));
    },
    [run, toast],
  );

  const validateAndSend = (raw: { text: string; email: string; url: string }, language: Lang) => {
    const offer: SubmittedOffer = { text: normaliseOffer(raw.text), email: raw.email.trim(), url: raw.url.trim() };
    const problem = lengthProblem(offer.text);
    if (problem) {
      setErrors({ text: LENGTH_MESSAGES[problem] });
      textRef.current?.focus();
      return;
    }
    setErrors({});
    void submit(offer, language);
  };

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (pending || cooldownLeft > 0) return;
    validateAndSend({ text, email, url }, lang);
  };

  const loadSample = (sample: Sample) => {
    setText(sample.text);
    setEmail(sample.email);
    setUrl(sample.url);
    setErrors({});
    textRef.current?.focus();
  };

  useEffect(() => {
    void sendFirstUseOnce();
    let alive = true;
    void getHealth().then((h) => {
      if (alive && h) setLlmAvailable(h.llm_available);
    });
    return () => {
      alive = false;
    };
  }, []);

  // Deep link from the extension: prefill and check once, then forget the hash.
  const submitRef = useRef(submit);
  useEffect(() => {
    submitRef.current = submit;
  }, [submit]);
  useEffect(() => {
    const fromHash = () => {
      const incoming = takeHashText();
      if (incoming === null) return;
      const offer = { text: normaliseOffer(incoming), email: "", url: "" };
      setText(incoming);
      setEmail("");
      setUrl("");
      document.getElementById("check")?.scrollIntoView({ block: "start" });
      if (lengthProblem(offer.text)) {
        setErrors({ text: LENGTH_MESSAGES[lengthProblem(offer.text)!] });
        return;
      }
      setErrors({});
      void submitRef.current(offer, "en");
    };
    const id = window.setTimeout(fromHash, 0);
    window.addEventListener("hashchange", fromHash);
    return () => {
      window.clearTimeout(id);
      window.removeEventListener("hashchange", fromHash);
    };
  }, []);

  const trimmedLength = normaliseOffer(text).length;
  const words = countWords(text);
  const langDisabled = llmAvailable === false;
  const retry = () => {
    if (status.kind === "problem") void submit(status.offer, lang);
  };

  return (
    <section className="section" id="check" aria-labelledby="checkTitle">
      <div className="wrap">
        <div className="section-head split">
          <div className="grid gap-4">
            <span className="eyebrow">Check an offer</span>
            <h2 id="checkTitle">Paste the offer you got.</h2>
          </div>
          <p className="lede">
            The whole message works best: the text, who sent it and any link. Nothing you paste is stored. You get every warning
            sign with the words that triggered it, a model score, and a checklist.
          </p>
        </div>

        <form className="paste-card checker-form" onSubmit={onSubmit} noValidate aria-describedby="checkerPrivacy">
          <div className={`field field-text${errors.text ? " err" : ""}`}>
            <label htmlFor="offerText">Offer message or job posting</label>
            <textarea
              id="offerText"
              ref={textRef}
              name="offer"
              value={text}
              onChange={(e) => {
                setText(e.target.value);
                if (errors.text) setErrors((x) => ({ ...x, text: undefined }));
              }}
              placeholder="Paste the full message here, including who sent it…"
              aria-invalid={errors.text ? true : undefined}
              aria-describedby="offerHelp offerErr"
              maxLength={MAX_TEXT + 2000}
              spellCheck={false}
            />
            <span className="help" id="offerHelp">
              {trimmedLength.toLocaleString("en-IN")} characters · {words} words
              {words > 0 && words < SHORT_MESSAGE_WORDS && " · short messages lean more on the rules"}
            </span>
            <span className="err-msg" id="offerErr" role="alert">
              {errors.text && (
                <>
                  <Icon name="info" size={16} />
                  <span>{errors.text}</span>
                </>
              )}
            </span>
          </div>

          <div className="checker-side">
            <div className={`field${errors.email ? " err" : ""}`}>
              <label htmlFor="offerEmail">
                Recruiter&apos;s email <span className="optional">(optional)</span>
              </label>
              <input
                id="offerEmail"
                type="email"
                inputMode="email"
                autoComplete="off"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="hr@company.com"
                aria-invalid={errors.email ? true : undefined}
                aria-describedby="emailErr"
              />
              <span className="err-msg" id="emailErr" role="alert">
                {errors.email}
              </span>
            </div>
            <div className={`field${errors.url ? " err" : ""}`}>
              <label htmlFor="offerUrl">
                Link in the offer <span className="optional">(optional)</span>
              </label>
              <input
                id="offerUrl"
                type="url"
                inputMode="url"
                autoComplete="off"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://… or bit.ly/…"
                aria-invalid={errors.url ? true : undefined}
                aria-describedby="urlErr"
              />
              <span className="err-msg" id="urlErr" role="alert">
                {errors.url}
              </span>
            </div>
            <div className="field">
              <label htmlFor="offerLang">Explanation language</label>
              <select
                id="offerLang"
                value={langDisabled ? "en" : lang}
                onChange={(e) => setLang(e.target.value as Lang)}
                disabled={langDisabled}
                aria-describedby={langDisabled ? "langNote" : undefined}
              >
                {LANGUAGES.map((l) => (
                  <option key={l.value} value={l.value}>
                    {l.label}
                  </option>
                ))}
              </select>
              {langDisabled && (
                <span className="help" id="langNote">
                  Translations need the optional Gemini key; English explanation shown.
                </span>
              )}
            </div>
            <div className="samples">
              <span>No message handy?</span>
              <button className="btn btn-ghost btn-sm" type="button" onClick={() => loadSample(SAMPLES.scam)}>
                Try a fictional scam
              </button>
              <button className="btn btn-ghost btn-sm" type="button" onClick={() => loadSample(SAMPLES.genuine)}>
                Try a fictional genuine offer
              </button>
            </div>
            <div className="paste-actions">
              <span className="counts" id="checkerPrivacy">
                <Icon name="lock" size={14} /> Checked, then thrown away
              </span>
              <button className={`btn btn-accent${pending ? " pending" : ""}`} type="submit" disabled={pending || cooldownLeft > 0} aria-disabled={pending || cooldownLeft > 0}>
                <span className="spinner" aria-hidden="true" />
                <span>{pending ? "Checking…" : cooldownLeft > 0 ? `Wait ${cooldownLeft}s` : "Check this offer"}</span>
              </button>
            </div>
          </div>
        </form>

        <div className="result-region" id="report" aria-busy={pending}>
          {status.kind === "idle" && <EmptyReport />}
          {status.kind === "loading" && <LoadingReport />}
          {status.kind === "done" && <VerdictView key={status.result.explanation + status.offer.text} result={status.result} offer={status.offer} />}
          {status.kind === "problem" && <ProblemReport problem={status.problem} attempt={status.attempt} cooldownLeft={cooldownLeft} onRetry={retry} />}
        </div>
      </div>
    </section>
  );
}
