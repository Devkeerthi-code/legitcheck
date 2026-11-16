import { API_URL, MAX_TEXT, MIN_TEXT, WEB_APP_URL } from "./config.js";
import { extractPageText } from "./extract.js";
import { checklistBox, el, messageView, openReportLink, selectionBox, verdictView } from "./render.js";

// Shown when the API can't be reached, so the checklist is always there.
const OFFLINE_CHECKLIST = [
  { title: "Find the company's official careers page" },
  { title: "Never pay to get a job" },
  { title: "Check the HR email domain" },
  { title: 'Search the company name with "scam"' },
  { title: "Report fraud", link: "https://cybercrime.gov.in", link_label: "cybercrime.gov.in" },
];

const body = document.getElementById("body");
const siteEl = document.getElementById("site");
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
let lastText = "";

if (new URLSearchParams(location.search).has("window")) document.documentElement.classList.add("in-window");

/* ---------- theme: light by default, toggle lasts for this popup only ---------- */
const themeBtn = document.getElementById("theme");
themeBtn.addEventListener("click", () => {
  const dark = document.documentElement.dataset.theme !== "dark";
  if (dark) document.documentElement.dataset.theme = "dark";
  else delete document.documentElement.dataset.theme;
  themeBtn.setAttribute("aria-label", dark ? "Switch to light mode" : "Switch to dark mode");
});

/* ---------- springs (same constants as the web app) ---------- */
function spring(onUpdate, { stiffness = 280, damping = 20, delay = 0 } = {}) {
  if (reduceMotion) return onUpdate(1);
  let x = 0;
  let v = 0;
  let last = performance.now();
  const t0 = last;
  const step = (now) => {
    if (now - t0 < delay) {
      last = now;
      return requestAnimationFrame(step);
    }
    const dt = Math.min(0.032, (now - last) / 1000);
    last = now;
    v += (-stiffness * (x - 1) - damping * v) * dt;
    x += v * dt;
    onUpdate(x);
    if (Math.abs(v) < 0.005 && Math.abs(x - 1) < 0.0005) return onUpdate(1);
    requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

function animateResult() {
  const chip = document.getElementById("chip");
  if (chip) {
    spring((p) => (chip.style.transform = p >= 1 ? "none" : `scale(${(1.35 - 0.35 * p).toFixed(3)}) rotate(${((1 - p) * -4).toFixed(2)}deg)`), {
      stiffness: 320,
      damping: 14,
    });
  }
  body.querySelectorAll(".flags li").forEach((li, i) => {
    li.style.opacity = reduceMotion ? "1" : "0";
    spring(
      (p) => {
        li.style.opacity = String(Math.min(1, p * 1.4));
        li.style.transform = p >= 1 ? "none" : `translateY(${((1 - p) * 10).toFixed(2)}px)`;
      },
      { delay: 120 + i * 70 },
    );
  });
}

/* ---------- views ---------- */
function show(nodes, busy = false) {
  body.replaceChildren(...[].concat(nodes));
  body.setAttribute("aria-busy", String(busy));
}

function reportHref(text) {
  return `${WEB_APP_URL}#text=${encodeURIComponent(text)}`;
}

function showLoading(text) {
  show(
    [
      selectionBox(text, null, "Checking this text"),
      el("div", { className: "skel", "aria-label": "Checking" }, [
        el("i", { style: "width:55%;height:30px;border-radius:999px" }),
        el("i", { style: "height:46px" }),
        el("i", { style: "height:46px" }),
        el("i", { style: "height:46px" }),
      ]),
      el("p", { className: "status", role: "status", text: "Checking against the rules and the model…" }),
    ],
    true,
  );
  return window.setTimeout(() => {
    const status = body.querySelector(".status");
    if (status) status.textContent = "Still working. A sleeping server takes 30 to 50 seconds to wake up.";
  }, 6000);
}

function showNothing(reason) {
  const pasteLink = openReportLink(WEB_APP_URL + "#check", "Paste text in the web app instead");
  pasteLink.className = "btn btn-ghost";
  show([
    messageView({
      iconName: "select",
      title: "Nothing to check here",
      body: el("p", {}, [
        reason,
        " Select the offer on the page, then right-click and choose ",
        el("span", { className: "kbd", text: "Check with LegitCheck" }),
        ".",
      ]),
      actions: [pasteLink],
    }),
  ]);
}

function showProblem(title, message, text, canRetry) {
  const actions = [];
  if (canRetry) {
    const retry = el("button", { className: "btn", type: "button", text: "Try again" });
    retry.addEventListener("click", () => void check(text));
    actions.push(retry);
  }
  show([
    messageView({ iconName: "offline", title, body: el("p", { text: message }), problem: true, actions }),
    checklistBox(OFFLINE_CHECKLIST),
  ]);
  body.querySelector("details")?.setAttribute("open", "");
}

/* ---------- API ---------- */
function describeHttp(status, json, retryAfter) {
  if (status === 422 || status === 400) {
    const msg = Array.isArray(json?.detail) ? json.detail[0]?.msg : json?.detail;
    return ["That text can't be checked", String(msg || "Check the text and try again.").replace(/^Value error,\s*/i, ""), false];
  }
  if (status === 413) return ["That's too much text", "Select just the offer or the posting.", false];
  if (status === 429) return ["Too many checks in a row", `Try again in about ${Number(retryAfter) || 60} seconds.`, true];
  if (status >= 502 && status <= 504) return asleep();
  return ["The checker hit an error", `It returned code ${status}. Nothing was saved.`, true];
}

function asleep() {
  return [
    "The checker is waking up or offline",
    "It runs on free hosting that sleeps when idle. Waking takes about 30 to 50 seconds, then try again.",
    true,
  ];
}

async function check(text) {
  lastText = text;
  const slowTimer = showLoading(text);
  try {
    const res = await fetch(`${API_URL}/check`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, source: "extension" }),
    });
    const json = await res.json().catch(() => null);
    if (text !== lastText) return;
    if (!res.ok || !json) {
      const [title, message, retry] = describeHttp(res.status, json, res.headers.get("Retry-After"));
      return showProblem(title, message, text, retry);
    }
    show(verdictView(json, text, reportHref(text)));
    animateResult();
  } catch {
    if (text === lastText) showProblem(...asleep().slice(0, 2), text, true);
  } finally {
    window.clearTimeout(slowTimer);
  }
}

/* ---------- where the text comes from ---------- */
function takePendingSelection() {
  return new Promise((resolve) => {
    try {
      chrome.runtime.sendMessage({ type: "legitcheck:take-pending" }, (reply) => {
        void chrome.runtime.lastError;
        resolve(reply?.text || null);
      });
    } catch {
      resolve(null);
    }
  });
}

async function readActiveTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id) return { error: "No page is open." };
  try {
    if (tab.url) siteEl.textContent = new URL(tab.url).hostname;
  } catch {
    // URL not available for this tab.
  }
  try {
    const [injection] = await chrome.scripting.executeScript({ target: { tabId: tab.id }, func: extractPageText, args: [MAX_TEXT] });
    return injection?.result || { error: "This page has no readable text." };
  } catch {
    return { error: "Chrome doesn't let extensions read this kind of page (for example chrome:// pages or the Web Store)." };
  }
}

function normalise(text) {
  return (text || "").replace(/[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]/g, "").trim().slice(0, MAX_TEXT);
}

async function start() {
  const pending = normalise(await takePendingSelection());
  if (pending) {
    siteEl.textContent = "selected text";
    if (pending.length < MIN_TEXT) return showNothing(`The selection is too short (${pending.length} characters; at least ${MIN_TEXT} needed).`);
    return check(pending);
  }
  const page = await readActiveTab();
  if (page.error) return showNothing(page.error);
  const text = normalise(page.text);
  if (text.length < MIN_TEXT) return showNothing("There isn't enough text on this page to check.");
  if (page.from === "selection") siteEl.textContent = "selected text";
  return check(text);
}

void start();
