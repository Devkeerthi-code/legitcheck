"use client";

import { useEffect, useRef, useState } from "react";
import { Icon } from "../Icon";
import { startDemo, type DemoController } from "./demo-script";

export function HeroDemo() {
  const root = useRef<HTMLDivElement>(null);
  const controller = useRef<DemoController | null>(null);
  const [paused, setPaused] = useState(false);

  useEffect(() => {
    if (!root.current) return;
    const c = startDemo(root.current);
    controller.current = c;
    return () => c.destroy();
  }, []);

  const togglePause = () => {
    const next = !paused;
    setPaused(next);
    controller.current?.setPaused(next);
  };
  const replay = () => {
    setPaused(false);
    controller.current?.replay();
  };

  return (
    <div className="demo" id="demo" ref={root} role="region" aria-labelledby="demoTitle">
      <div className="demo-top">
        <div className="status">
          <h2 id="demoTitle" className="sr-only">
            Live demo: checking a fictional offer message
          </h2>
          <ol className="stages" aria-hidden="true">
            <li data-stage="reading">Reading</li>
            <li data-stage="checking">Checking</li>
            <li data-stage="flagging" className="flag">
              Flagging
            </li>
          </ol>
        </div>
        <div className="demo-controls">
          <button className="icon-btn" type="button" onClick={togglePause} aria-label={paused ? "Resume demo" : "Pause demo"}>
            <Icon name={paused ? "play" : "pause"} />
          </button>
          <button className="icon-btn" type="button" onClick={replay} aria-label="Replay demo">
            <Icon name="replay" />
          </button>
        </div>
      </div>
      <div className="status-line">
        <span className="live">
          <span className="pulse" aria-hidden="true" />
          <span data-status aria-live="polite">
            Waiting to start
          </span>
        </span>
        <span className="tag-fiction">Fictional example</span>
      </div>

      <div className="doc">
        <div className="scanbar" data-scanbar aria-hidden="true" />
        <div className="ln dim">
          From: Nexora Talent Solutions &lt;
          <mark className="hl warn" data-flag="gmail">
            nexora.hr.team@gmail.com
          </mark>
          &gt;
        </div>
        <div className="ln dim">Subject: Selected for Work From Home Internship</div>
        <div className="ln">Dear Candidate, you are shortlisted for our Data Entry Internship. Stipend ₹25,000/month.</div>
        <div className="ln">
          To confirm your seat, pay a one-time{" "}
          <mark className="hl" data-flag="fee">
            registration fee of ₹1,999
          </mark>
          .
        </div>
        <div className="ln">
          For verification,{" "}
          <mark className="hl" data-flag="id">
            send Aadhaar and PAN
          </mark>{" "}
          photos today.
        </div>
        <div className="ln">
          For onboarding,{" "}
          <mark className="hl warn" data-flag="tg">
            contact HR on Telegram
          </mark>
          : @nexora_hr_desk
        </div>
        <div className="ln">
          Pay securely here:{" "}
          <mark className="hl warn" data-flag="link">
            bit.ly/nx-onboard
          </mark>
        </div>
        <div className="ln">
          This{" "}
          <mark className="hl warn" data-flag="urgent">
            offer valid only today
          </mark>
          . Seats are limited.
        </div>
      </div>

      <div className="flags" data-flags>
        <div className="flags-head">
          <span>Warning signs found</span>
          <span data-count>0</span>
        </div>
      </div>

      <div className="verdict-bar">
        <div className="stamp" data-stamp aria-hidden="true">
          <span className="dot" />
          High risk
        </div>
        <div className="score-mini">
          <div className="lbl">
            <span>Model score (example)</span>
            <span data-score>0.00</span>
          </div>
          <div className="meter" aria-hidden="true">
            <i data-meter />
          </div>
        </div>
        <div className="decide" data-decide>
          <Icon name="hand" />
          You decide
        </div>
      </div>
    </div>
  );
}
