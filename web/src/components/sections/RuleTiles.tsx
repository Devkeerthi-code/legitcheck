"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";
import { Icon } from "../Icon";
import { useTilt } from "@/lib/hooks";
import { hasFinePointer, prefersReducedMotion } from "@/lib/spring";

function Tile({ tone, title, body, wide, children }: { tone: "high" | "warn"; title: string; body: string; wide?: boolean; children: ReactNode }) {
  const ref = useRef<HTMLElement>(null);
  useTilt(ref);
  return (
    <article ref={ref} className={`tile${wide ? " w2" : ""}`}>
      <span className={`chip chip-${tone} sev-tag`}>
        <span className="dot" />
        {tone === "high" ? "High" : "Warning"}
      </span>
      <h3>{title}</h3>
      <p>{body}</p>
      {children}
    </article>
  );
}

const START_SECONDS = 29 * 60 + 59;

/** The ticking earnings counter and countdown that make the "task scam" and "pressure" tiles feel live. */
function useTicker() {
  const [tick, setTick] = useState(0);
  useEffect(() => {
    if (prefersReducedMotion()) return;
    const id = window.setInterval(() => {
      if (!document.hidden) setTick((t) => t + 1);
    }, 1000);
    return () => window.clearInterval(id);
  }, []);
  const seconds = START_SECONDS - (tick % (START_SECONDS + 1));
  const earned = 50 + (tick % 19) * 50;
  return {
    timer: `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`,
    earned: `₹${earned.toLocaleString("en-IN")}`,
  };
}

/** On touch screens there is no hover, so the short link flips to its real destination on its own. */
function useAutoFlip() {
  const [flipped, setFlipped] = useState(false);
  useEffect(() => {
    if (hasFinePointer() || prefersReducedMotion()) return;
    const id = window.setInterval(() => setFlipped((f) => !f), 2200);
    return () => window.clearInterval(id);
  }, []);
  return flipped;
}

export function RuleTiles() {
  const { timer, earned } = useTicker();
  const flipped = useAutoFlip();
  return (
    <section className="section" aria-labelledby="rulesTitle">
      <div className="wrap">
        <div className="section-head split">
          <div className="grid gap-4">
            <span className="eyebrow">The rules it checks</span>
            <h2 id="rulesTitle">Each warning sign is a rule you can read.</h2>
          </div>
          <p className="lede">No black box. Every flag in a report comes from one of these checks, and each one quotes the words that triggered it.</p>
        </div>
        <div className="bento">
          <Tile tone="high" wide title="Asks you to pay to get the job" body='Registration fees, training kits, "refundable" deposits. Real employers pay you, not the other way round.'>
            <div className="mock">
              <div className="mock-row">
                <span>
                  To confirm your seat, pay a <span className="x">registration fee of ₹1,999</span>
                </span>
              </div>
              <div className="mock-row mt-1.5">
                <span>Also matches</span>
                <span>
                  <b>training fee</b> · <b>security deposit</b> · <b>kit charges</b>
                </span>
              </div>
            </div>
          </Tile>
          <Tile tone="warn" title="HR only on Telegram or WhatsApp" body="No office, no company number, just a chat handle.">
            <div className="mock mock-chat">
              <span className="bubble">Hi, is this the HR team?</span>
              <span className="bubble me">
                Yes. Continue on <span className="y">Telegram @hr_desk</span>
              </span>
            </div>
          </Tile>
          <Tile tone="warn" title="Company name, personal email" body="The sender's domain should match the company's website.">
            <div className="mock">
              <div className="mock-row">
                <span className="okc">careers@nexora.in</span>
                <Icon name="check" size={14} style={{ color: "var(--ok)" }} />
              </div>
              <div className="mock-row">
                <span>
                  nexora.hr.team@<span className="y">gmail.com</span>
                </span>
                <Icon name="flag" size={14} style={{ color: "var(--warn)" }} />
              </div>
            </div>
          </Tile>
          <Tile tone="high" title={'"Like videos and earn"'} body={'Paid tasks that start small and end with a deposit to "unlock" more.'}>
            <div className="mock">
              <div className="mock-row">
                <span>Task earnings</span>
                <b className="tick-count">{earned}</b>
              </div>
              <div className="mock-row">
                <span>To withdraw</span>
                <span className="x">deposit ₹500</span>
              </div>
            </div>
          </Tile>
          <Tile tone="high" title="Early ID or bank details" body="Aadhaar, PAN, bank account or OTP before any interview.">
            <div className="mock">
              <div>
                Aadhaar <span className="redact" style={{ width: 72 }} /> <span className="redact" style={{ width: 34 }} />
              </div>
              <div>
                PAN <span className="redact" style={{ width: 88 }} />
              </div>
              <div className="mt-1">
                <span className="x">Send by 6 PM</span>
              </div>
            </div>
          </Tile>
          <Tile tone="warn" title="Short or lookalike links" body="Short links hide where they really go. Lookalike domains copy a real name.">
            <div className={`mock${flipped ? " auto" : ""}`}>
              <span className="link-swap" role="img" aria-label="bit.ly/nx-onboard really goes to nex0ra-careers.co/pay">
                <span aria-hidden="true">bit.ly/nx-onboard</span>
                <span aria-hidden="true">
                  <span className="y">nex0ra</span>-careers.co/pay
                </span>
              </span>
              <div className="mt-1">zero, not the letter o</div>
            </div>
          </Tile>
          <Tile tone="warn" title="Pressure to decide fast" body="Deadlines in minutes so you don't stop to check.">
            <div className="mock mock-row">
              <span>Reply within</span>
              <span className="timer" role="img" aria-label="A countdown timer, example">
                {timer}
              </span>
            </div>
          </Tile>
        </div>
      </div>
    </section>
  );
}
