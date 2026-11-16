"use client";

import { useEffect, useRef, useState, type CSSProperties, type ReactNode, type RefObject } from "react";
import { prefersReducedMotion } from "@/lib/spring";

const STEPS: { title: string; body: string; mini: ReactNode }[] = [
  {
    title: "Paste",
    body: "Copy the whole message, including the sender's email and any link. On desktop, select it and use the extension.",
    mini: (
      <>
        &quot;Dear Candidate, you are shortlisted…&quot;
        <br />
        nexora.hr.team@gmail.com
      </>
    ),
  },
  {
    title: "We check",
    body: "Rules look for known scam patterns. A model trained on labelled postings gives a second opinion.",
    mini: (
      <>
        rules + 1 model
        <br />
        about 2 seconds
      </>
    ),
  },
  {
    title: "Read the flags",
    body: "Each flag quotes the words that triggered it and explains why it matters.",
    mini: (
      <>
        <span className="chip chip-high">Asks you to pay</span>
        <br />
        &quot;registration fee of ₹1,999&quot;
      </>
    ),
  },
  {
    title: "Verify",
    body: 'Official careers page, email domain, a quick search for the company name plus "scam".',
    mini: (
      <>
        [x] careers page
        <br />[ ] email domain
      </>
    ),
  },
  {
    title: "Decide",
    body: "Reply, ask questions, walk away or report. We don't make the call for you.",
    mini: (
      <>
        Report: cybercrime.gov.in
        <br />
        Helpline: 1930
      </>
    ),
  },
];

/** Fills the track as you scroll through the section, lighting each step in turn. */
function useScrollProgress(ref: RefObject<HTMLDivElement | null>) {
  const [progress, setProgress] = useState(0);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    let ticking = false;
    const update = () => {
      ticking = false;
      if (prefersReducedMotion()) return setProgress(1);
      const r = el.getBoundingClientRect();
      const vh = window.innerHeight;
      setProgress(Math.max(0, Math.min(1, (vh * 0.75 - r.top) / (r.height + vh * 0.25))));
    };
    const onScroll = () => {
      if (!ticking) {
        ticking = true;
        requestAnimationFrame(update);
      }
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    onScroll();
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
    };
  }, [ref]);
  return progress;
}

export function Steps() {
  const ref = useRef<HTMLDivElement>(null);
  const p = useScrollProgress(ref);
  const active = Math.min(STEPS.length - 1, Math.floor(p * STEPS.length));
  return (
    <section className="section alt" id="how" aria-labelledby="howTitle">
      <div className="wrap">
        <div className="section-head split">
          <div className="grid gap-4">
            <span className="eyebrow">How to check an offer</span>
            <h2 id="howTitle">Five steps. The last one is yours.</h2>
          </div>
          <p className="lede">From &quot;this looks too good&quot; to a decision you can explain, in about two minutes.</p>
        </div>
        <div className="steps-wrap" ref={ref}>
          <div className="steps-track" aria-hidden="true" style={{ "--p": p.toFixed(3) } as CSSProperties}>
            <i />
          </div>
          <ol className="steps">
            {STEPS.map((s, i) => (
              <li key={s.title} className={`step${p > 0.02 && i <= active ? " on" : ""}`}>
                <span className="step-dot" aria-hidden="true">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <div className="step-body">
                  <h3>{s.title}</h3>
                  <p>{s.body}</p>
                  <div className="step-mini" aria-hidden="true">
                    {s.mini}
                  </div>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </div>
    </section>
  );
}
