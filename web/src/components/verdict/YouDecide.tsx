"use client";

import { useState } from "react";
import { Icon } from "../Icon";
import { useToast } from "../Toasts";
import type { ChecklistItem, Verdict } from "@/lib/types";

const HEADINGS: Record<Verdict | "unknown", { title: string; why: string }> = {
  high_risk: {
    title: "We found serious warning signs. Whether to reply is your call.",
    why: "LegitCheck can be wrong in both directions. Five minutes with this checklist will tell you more than any score.",
  },
  warning: {
    title: "Some signs are worth checking before you go further.",
    why: "Small genuine companies sometimes do these things too. The checklist below is how you find out.",
  },
  consistent: {
    title: "No warning signs found. That isn't proof it's real.",
    why: "A careful scammer can write a clean message. Run these checks before you share documents or money.",
  },
  unknown: {
    title: "We couldn't check it right now. You can still check it yourself.",
    why: "These five checks catch most fake offers, with or without LegitCheck.",
  },
};

interface Props {
  verdict: Verdict | "unknown";
  checklist: ChecklistItem[];
  disclaimer?: string;
}

export function YouDecide({ verdict, checklist, disclaimer }: Props) {
  const toast = useToast();
  const [done, setDone] = useState<Set<string>>(() => new Set());
  const head = HEADINGS[verdict];

  const toggle = (id: string, checked: boolean) => {
    const next = new Set(done);
    if (checked) next.add(id);
    else next.delete(id);
    setDone(next);
    if (checked && next.size === checklist.length) toast("All checks done. You now know more than the message wanted you to.");
  };

  return (
    <div className="you-decide">
      <div>
        <span className="eyebrow">You decide</span>
        <h3 className="mt-3">{head.title}</h3>
        <p className="why">{head.why}</p>
        <div className="decide-actions">
          <button className="btn btn-primary btn-sm" type="button" onClick={() => toast("Good call. Check the company's own website before you reply.")}>
            I&apos;ll verify first
          </button>
          <a className="btn btn-ghost btn-sm" href="https://cybercrime.gov.in" target="_blank" rel="noopener noreferrer">
            Report it <Icon name="external" size={14} />
            <span className="sr-only">(opens in a new tab)</span>
          </a>
        </div>
        {disclaimer && <p className="fine disclaimer">{disclaimer}</p>}
      </div>
      <fieldset className="checklist">
        <legend className="sr-only">Verification checklist</legend>
        <div className="check-progress">
          <h4>Verification checklist</h4>
          <span aria-live="polite">
            {done.size} of {checklist.length} done
          </span>
        </div>
        {checklist.map((item) => (
          <label className="check-item" key={item.id}>
            <input type="checkbox" checked={done.has(item.id)} onChange={(e) => toggle(item.id, e.target.checked)} />
            <span>
              <span className="ct">{item.title}</span>
              <small>
                {item.detail}
                {item.link && (
                  <>
                    {" "}
                    <a href={item.link} target="_blank" rel="noopener noreferrer">
                      {item.link_label || item.link}
                    </a>
                    {item.id === "report" && (
                      <>
                        {" "}
                        or call <a href="tel:1930">1930</a>
                      </>
                    )}
                  </>
                )}
              </small>
            </span>
          </label>
        ))}
      </fieldset>
    </div>
  );
}
