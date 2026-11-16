"use client";

import { useRef, useState, type KeyboardEvent, type ReactNode } from "react";
import { Icon } from "../Icon";
import { metrics as m, fmt } from "@/lib/metrics";

interface Qa {
  q: string;
  a: ReactNode;
}

const ext = { target: "_blank", rel: "noopener noreferrer" } as const;

const TABS: { id: string; label: string; urgent?: boolean; items: Qa[] }[] = [
  {
    id: "model",
    label: "About the model",
    items: [
      {
        q: "What does the score mean?",
        a: (
          <p>
            It is the model&apos;s estimate, from 0 to 1, of how much the wording resembles postings that were labelled fake. It is
            a likelihood, not proof. The flags underneath tell you why.
          </p>
        ),
      },
      {
        q: "What was it trained on?",
        a: (
          <>
            <p>
              A public dataset of {fmt.int(m.rowsAfterDedupe)} job postings labelled real or fake (after removing duplicates). Most
              of them are US postings from 2012 to 2014, so the model knows the general shape of a fake posting, not Indian
              WhatsApp scams.
            </p>
            <p>
              The signs specific to India, like registration fees, Telegram HR, UPI requests and task scams, come from hand-written
              rules. You can read each one in the warning-signs section. The rules explain; the model adds a second opinion.
            </p>
          </>
        ),
      },
      {
        q: "Why does a short message get a less reliable score?",
        a: (
          <p>
            The model learned from full job postings. For short messages under 60 words, its score counts for less and the verdict
            leans on the rules more. The report says so when this happens.
          </p>
        ),
      },
      {
        q: "Can it be wrong?",
        a: (
          <p>
            Yes, in both directions. A careful scammer can write a clean message, and a small genuine company can use a Gmail
            address. On held-out test postings, {fmt.percent(1 - m.high.recall)} of fakes were not marked High risk. Treat the
            report as a second pair of eyes, then verify.
          </p>
        ),
      },
      {
        q: 'Why is there no "all clear" verdict?',
        a: (
          <p>
            Reading one message can&apos;t prove a company is real. The best verdict is &quot;Looks consistent with genuine
            postings&quot;, which means no warning signs were found, not that there are none.
          </p>
        ),
      },
    ],
  },
  {
    id: "privacy",
    label: "Privacy",
    items: [
      {
        q: "Is what I paste stored?",
        a: (
          <p>
            No. The text is checked and thrown away. We only count that a check happened and which verdict it got, with no text,
            email or link attached. Each browser is also counted once, with no identifier, so we can say how many people used it.
          </p>
        ),
      },
      {
        q: "Does the extension read my pages?",
        a: (
          <p>
            Only when you ask it to: the text you select and right-click, or the page you&apos;re on when you click its icon. It
            does not read pages in the background, store anything, or track where you browse.
          </p>
        ),
      },
      {
        q: "Who writes the plain-language explanation?",
        a: (
          <p>
            When the optional Gemini key is set, Google&apos;s Gemini model rewrites the explanation, and translates it if you pick
            another language. It only gets the warning signs we found and the short phrases that triggered them (which can
            include a flagged email or link), not the whole message. Without the key, built-in English templates are used.
          </p>
        ),
      },
      { q: "Do I need an account?", a: <p>No. Open the page, paste, check.</p> },
    ],
  },
  {
    id: "paid",
    label: "If you've already paid",
    urgent: true,
    items: [
      {
        q: "I already paid a fee. What do I do?",
        a: (
          <>
            <p>
              <strong>Call 1930 immediately.</strong> It is the National Cyber Crime Helpline. The sooner you report, the better
              the chance the money can be held before it moves.
            </p>
            <p>
              Then file a complaint at{" "}
              <a href="https://cybercrime.gov.in" {...ext}>
                cybercrime.gov.in
              </a>
              .
            </p>
          </>
        ),
      },
      {
        q: "Should I contact my bank?",
        a: (
          <p>
            Yes. Call the number on the back of your card or in your bank&apos;s official app. Tell them it was a fraud payment and
            ask them to raise a dispute. Keep the UTR or transaction ID.
          </p>
        ),
      },
      {
        q: "I shared my Aadhaar, PAN or bank details.",
        a: (
          <p>
            Report it the same way, and tell your bank. You can lock your Aadhaar biometrics on the official UIDAI website or app.
            Watch for unexpected loan or OTP messages.
          </p>
        ),
      },
      {
        q: "What should I save as evidence?",
        a: (
          <p>
            Screenshots of the chat, the sender&apos;s number or handle, email addresses, UPI IDs, links and payment receipts.
            Don&apos;t delete the conversation.
          </p>
        ),
      },
    ],
  },
];

export function Faq() {
  const [active, setActive] = useState(0);
  const tabRefs = useRef<(HTMLButtonElement | null)[]>([]);

  const onKey = (e: KeyboardEvent, i: number) => {
    const last = TABS.length - 1;
    const next = { ArrowRight: i === last ? 0 : i + 1, ArrowLeft: i === 0 ? last : i - 1, Home: 0, End: last }[e.key];
    if (next === undefined) return;
    e.preventDefault();
    setActive(next);
    tabRefs.current[next]?.focus();
  };

  return (
    <section className="section" id="faq" aria-labelledby="faqTitle">
      <div className="wrap faq-grid">
        <div className="grid gap-4 faq-intro">
          <span className="eyebrow">Questions</span>
          <h2 id="faqTitle">Straight answers.</h2>
          <p className="lede">If you have already paid someone, go to the third tab now.</p>
        </div>
        <div>
          <div className="tabs" role="tablist" aria-label="FAQ categories">
            {TABS.map((t, i) => (
              <button
                key={t.id}
                ref={(el) => {
                  tabRefs.current[i] = el;
                }}
                className={`tab${t.urgent ? " urgent" : ""}`}
                role="tab"
                type="button"
                id={`tab-${t.id}`}
                aria-controls={`panel-${t.id}`}
                aria-selected={i === active}
                tabIndex={i === active ? 0 : -1}
                onClick={() => setActive(i)}
                onKeyDown={(e) => onKey(e, i)}
              >
                {t.label}
              </button>
            ))}
          </div>
          {TABS.map((t, i) => (
            <div key={t.id} className="tabpanel" role="tabpanel" id={`panel-${t.id}`} aria-labelledby={`tab-${t.id}`} tabIndex={0} hidden={i !== active}>
              {t.items.map((item, j) => (
                <details className="qa" key={item.q} open={j === 0 ? true : undefined}>
                  <summary>
                    {item.q}
                    <span className="pm" aria-hidden="true">
                      <Icon name="plus" size={14} />
                    </span>
                  </summary>
                  <div className="ans">{item.a}</div>
                </details>
              ))}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
