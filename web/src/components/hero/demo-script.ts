import { prefersReducedMotion, spring } from "@/lib/spring";

/**
 * The hero scan animation. It drives the DOM directly (not React state) because it runs
 * frame-by-frame springs on many small nodes and must pause/resume without re-rendering.
 */
const RULES: Record<string, { title: string; tone: "high" | "warn" }> = {
  gmail: { title: "Company name, personal Gmail", tone: "warn" },
  fee: { title: "Asks you to pay a fee", tone: "high" },
  id: { title: "Wants Aadhaar/PAN early", tone: "high" },
  tg: { title: "HR only on Telegram", tone: "warn" },
  link: { title: "Shortened link hides destination", tone: "warn" },
  urgent: { title: "Pressure to decide today", tone: "warn" },
};
const FINAL_SCORE = 0.94;

export interface DemoController {
  replay: () => void;
  setPaused: (paused: boolean) => void;
  destroy: () => void;
}

export function startDemo(root: HTMLElement): DemoController {
  const q = <T extends Element>(sel: string) => root.querySelector<T>(sel)!;
  const qa = <T extends Element>(sel: string) => Array.from(root.querySelectorAll<T>(sel));
  const bar = q<HTMLElement>("[data-scanbar]");
  const flagsBox = q<HTMLElement>("[data-flags]");
  const statusEl = q<HTMLElement>("[data-status]");
  const countEl = q<HTMLElement>("[data-count]");
  const stamp = q<HTMLElement>("[data-stamp]");
  const decide = q<HTMLElement>("[data-decide]");
  const scoreVal = q<HTMLElement>("[data-score]");
  const scoreBar = q<HTMLElement>("[data-meter]");
  const lines = qa<HTMLElement>(".ln");

  const state = { run: 0, userPaused: false, offscreen: true, started: false, count: 0 };
  const paused = () => state.userPaused || state.offscreen || document.hidden;

  const wait = (ms: number, id: number) =>
    new Promise<boolean>((resolve) => {
      let left = ms;
      let last = performance.now();
      const tick = (now: number) => {
        if (id !== state.run) return resolve(false);
        if (!paused()) left -= now - last;
        last = now;
        if (left <= 0) return resolve(true);
        requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });

  const setStage = (stage: string, text: string) => {
    qa<HTMLElement>(".stages li").forEach((li) => {
      li.classList.toggle("on", li.dataset.stage === stage);
      li.classList.toggle("done", stage === "done");
    });
    statusEl.textContent = text;
  };

  const moveBar = (ln: HTMLElement) => {
    bar.style.opacity = "1";
    bar.style.height = `${ln.offsetHeight}px`;
    bar.style.transform = `translateY(${ln.offsetTop}px)`;
  };

  const addFlag = (mark: HTMLElement) => {
    const rule = RULES[mark.dataset.flag ?? ""];
    if (!rule) return;
    state.count++;
    const warn = rule.tone === "warn";
    const num = document.createElement("span");
    num.className = `num${warn ? " warn" : ""}`;
    num.textContent = String(state.count);
    num.setAttribute("aria-hidden", "true");
    mark.closest(".ln")?.appendChild(num);
    spring({ from: 0, to: 1, stiffness: 420, damping: 16, onUpdate: (p) => (num.style.transform = `scale(${Math.max(0, p)})`) });

    const row = document.createElement("div");
    row.className = `flag-row${warn ? " warn" : ""}`;
    const n = Object.assign(document.createElement("span"), { className: "n", textContent: String(state.count) });
    n.setAttribute("aria-hidden", "true");
    const t = Object.assign(document.createElement("span"), { className: "t", textContent: rule.title });
    t.appendChild(Object.assign(document.createElement("span"), { className: "q", textContent: `"${mark.textContent}"` }));
    const sev = Object.assign(document.createElement("span"), { className: "sev", textContent: warn ? "Warn" : "High" });
    row.append(n, t, sev);
    flagsBox.appendChild(row);
    countEl.textContent = String(state.count);
    spring({
      from: 0,
      to: 1,
      stiffness: 260,
      damping: 20,
      onUpdate: (p) => {
        row.style.opacity = String(Math.min(1, Math.max(0, p * 1.4)));
        row.style.transform = `translate(${((1 - p) * 28).toFixed(2)}px,${((1 - p) * 6).toFixed(2)}px) rotate(${((1 - p) * 2.5).toFixed(2)}deg)`;
      },
    });
  };

  const setScore = (v: number) => {
    scoreVal.textContent = v.toFixed(2);
    scoreBar.style.width = `${v * 100}%`;
    scoreBar.style.setProperty("--full", `${scoreBar.parentElement?.offsetWidth ?? 400}px`);
  };

  const showVerdict = () => {
    spring({
      from: 0,
      to: 1,
      stiffness: 320,
      damping: 14,
      onUpdate: (p) => {
        stamp.style.opacity = String(Math.min(1, p * 2));
        stamp.style.transform = `rotate(${(-3 + (1 - p) * -6).toFixed(2)}deg) scale(${(1.6 - 0.6 * p).toFixed(3)})`;
      },
    });
    decide.classList.add("on");
    root.classList.add("finished");
  };

  const reset = () => {
    state.count = 0;
    qa<HTMLElement>("mark.hl").forEach((m) => m.classList.remove("on"));
    qa<HTMLElement>(".num").forEach((n) => n.remove());
    qa<HTMLElement>(".flag-row").forEach((n) => n.remove());
    countEl.textContent = "0";
    stamp.style.opacity = "0";
    stamp.style.transform = "rotate(-3deg) scale(1.6)";
    decide.classList.remove("on");
    root.classList.remove("finished");
    bar.style.opacity = "0";
    setScore(0);
  };

  const doneText = () => `Done: ${state.count} warning signs. The decision is yours.`;

  const finalState = () => {
    state.run++;
    reset();
    qa<HTMLElement>("mark.hl").forEach((m) => {
      m.classList.add("on");
      addFlag(m);
    });
    setScore(FINAL_SCORE);
    showVerdict();
    setStage("done", doneText());
  };

  const run = async () => {
    const id = ++state.run;
    reset();
    for (const [i, ln] of lines.entries()) {
      setStage("reading", `Reading line ${i + 1} of ${lines.length}`);
      moveBar(ln);
      if (!(await wait(480, id))) return;
      setStage("checking", `Checking line ${i + 1} against the rules`);
      if (!(await wait(260, id))) return;
      for (const mark of Array.from(ln.querySelectorAll<HTMLElement>("mark.hl"))) {
        setStage("flagging", `Flagged: ${RULES[mark.dataset.flag ?? ""]?.title ?? ""}`);
        mark.classList.add("on");
        addFlag(mark);
        if (!(await wait(720, id))) return;
      }
    }
    bar.style.opacity = "0";
    setStage("checking", "Scoring the whole message with the model");
    const start = performance.now();
    for (;;) {
      if (!(await wait(16, id))) return;
      const p = Math.min(1, (performance.now() - start) / 900);
      setScore(FINAL_SCORE * (1 - Math.pow(1 - p, 3)));
      if (p >= 1) break;
    }
    showVerdict();
    setStage("done", doneText());
    if (await wait(7000, id)) void run();
  };

  const io = new IntersectionObserver(
    ([entry]) => {
      state.offscreen = !entry?.isIntersecting;
      if (entry?.isIntersecting && !state.started) {
        state.started = true;
        if (prefersReducedMotion()) finalState();
        else window.setTimeout(() => void run(), 500);
      }
    },
    { threshold: 0.25 },
  );
  io.observe(root);
  reset();

  return {
    replay: () => {
      state.userPaused = false;
      if (prefersReducedMotion()) finalState();
      else void run();
    },
    setPaused: (p) => {
      state.userPaused = p;
    },
    destroy: () => {
      state.run++;
      io.disconnect();
    },
  };
}
