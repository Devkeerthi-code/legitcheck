"use client";

import { useRef, type CSSProperties } from "react";
import { Icon } from "../Icon";
import { useSeenOnce } from "@/lib/hooks";

const SCAM_SIGNS: [string, string?][] = [
  ['You pay before you start: a registration, training or "security deposit" fee', '"pay ₹1,999 to confirm your seat"'],
  ["HR only talks on Telegram or WhatsApp, with no company number or office", '"contact HR on Telegram: @hr_desk"'],
  ["A Gmail or Yahoo address claiming to be a company", "company.hr.team@gmail.com"],
  ['You get paid to like videos, rate hotels or "complete tasks"', '"earn ₹50 per like"'],
  ["Aadhaar, PAN or bank details asked for before any interview"],
  ["Shortened or lookalike links that hide where they go", "bit.ly/..., nex0ra-careers.co"],
  ["Pressure to decide now", '"offer valid only today", "reply in 30 minutes"'],
];

const GENUINE_SIGNS: [string, string?][] = [
  ["You never pay. The company pays you."],
  ["There was a real interview or test with named people"],
  ["Email comes from the company's own domain, the same one as its website", "careers@company.com"],
  ["The role is listed on the company's official careers page"],
  ["ID and bank details are asked for only after a signed offer, through an HR portal"],
  ["Links go to the company's own website, in full"],
  ["You get time to read the offer and ask questions"],
];

function SignList({ items, icon }: { items: [string, string?][]; icon: "cross" | "check" }) {
  return (
    <ul className="cmp-list">
      {items.map(([text, example], i) => (
        <li key={text} style={{ "--i": i } as CSSProperties}>
          <span className="mk">
            <Icon name={icon} />
          </span>
          <span>
            {text}
            {example && <small>{example}</small>}
          </span>
        </li>
      ))}
    </ul>
  );
}

export function Compare() {
  const ref = useRef<HTMLDivElement>(null);
  const seen = useSeenOnce(ref);
  return (
    <section className="section alt" id="signs" aria-labelledby="cmpTitle">
      <div className="wrap">
        <div className="section-head split">
          <div className="grid gap-4">
            <span className="eyebrow">What to look for</span>
            <h2 id="cmpTitle">Scam offers repeat the same few moves.</h2>
          </div>
          <p className="lede">
            Most fake internships in India follow a script: an exciting stipend, then a fee, a chat app and a deadline. Genuine
            offers look boring by comparison, and that is a good sign.
          </p>
        </div>
        <div className={`compare${seen ? " in" : ""}`} ref={ref}>
          <article className="cmp-card bad">
            <header>
              <h3>Signs of a scam</h3>
              <span className="chip chip-high">
                <span className="dot" />
                Warning signs
              </span>
            </header>
            <SignList items={SCAM_SIGNS} icon="cross" />
          </article>
          <article className="cmp-card good">
            <header>
              <h3>Signs of a genuine offer</h3>
              <span className="chip chip-ok">
                <span className="dot" />
                Consistent
              </span>
            </header>
            <SignList items={GENUINE_SIGNS} icon="check" />
          </article>
        </div>
        <p className="cmp-note">
          <Icon name="info" />A clean-looking message can still be a scam, and an odd-looking one can still be real. That is why
          LegitCheck never gives an all-clear. It shows you what it found and leaves the call to you.
        </p>
      </div>
    </section>
  );
}
