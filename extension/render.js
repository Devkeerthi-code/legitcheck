// DOM builders for the popup. Everything from the API goes in through textContent, never innerHTML.

const SEVERITY_RANK = { high: 3, medium: 2, low: 1 };
const VERDICT_CHIP = { high_risk: "chip-high", warning: "chip-warn", consistent: "chip-ok" };
const NOTE = {
  high_risk: "This matches common scam patterns. You decide what to do next.",
  warning: "Some signs worth checking. Small companies sometimes do this too.",
  consistent: "No warning sign found. That doesn't prove it's real, so still run the checks below.",
};
const PREVIEW_CHARS = 260;
const SVG_NS = "http://www.w3.org/2000/svg";

export function el(tag, props = {}, children = []) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(props)) {
    if (value === undefined || value === null || value === false) continue;
    if (key === "text") node.textContent = value;
    else if (key === "className") node.className = value;
    else node.setAttribute(key, value === true ? "" : String(value));
  }
  for (const child of [].concat(children)) if (child) node.append(child);
  return node;
}

function icon(paths) {
  const svg = document.createElementNS(SVG_NS, "svg");
  svg.setAttribute("class", "icon");
  svg.setAttribute("viewBox", "0 0 24 24");
  svg.setAttribute("aria-hidden", "true");
  for (const d of paths) {
    const p = document.createElementNS(SVG_NS, "path");
    p.setAttribute("d", d);
    svg.append(p);
  }
  return svg;
}

export const ICONS = {
  arrow: () => icon(["M5 12h14M13 6l6 6-6 6"]),
  plus: () => icon(["M12 5v14M5 12h14"]),
  select: () => icon(["M4 7V5a1 1 0 011-1h2M17 4h2a1 1 0 011 1v2M20 17v2a1 1 0 01-1 1h-2M7 20H5a1 1 0 01-1-1v-2M9 12h6"]),
  offline: () => icon(["M3 3l18 18M8.5 16.5a5 5 0 017 0M5 12.5a10 10 0 015.2-2.8M19 12.5a10 10 0 00-2.4-1.7M12 20h.01"]),
};

/** Rules sorted by severity, highest first, keeping API order inside each level. */
export function topRules(rules, n = 3) {
  return rules
    .map((r, i) => ({ r, i }))
    .sort((a, b) => SEVERITY_RANK[b.r.severity] - SEVERITY_RANK[a.r.severity] || a.i - b.i)
    .slice(0, n)
    .map(({ r }) => r);
}

/** The start of the text with flagged phrases marked. Higher severity wins where phrases overlap. */
function previewNode(text, rules) {
  const shown = text.slice(0, PREVIEW_CHARS);
  const spans = rules
    .flatMap((r) => r.matches.filter((m) => m.source === "text" && m.start < shown.length).map((m) => ({ ...m, severity: r.severity })))
    .sort((a, b) => SEVERITY_RANK[b.severity] - SEVERITY_RANK[a.severity] || a.start - b.start);
  const taken = [];
  for (const s of spans) if (!taken.some((t) => s.start < t.end && s.end > t.start)) taken.push(s);
  taken.sort((a, b) => a.start - b.start);

  const p = el("p");
  let at = 0;
  for (const s of taken) {
    const end = Math.min(s.end, shown.length);
    p.append(shown.slice(at, s.start), el("mark", { className: s.severity === "high" ? "" : "w", text: shown.slice(s.start, end) }));
    at = end;
  }
  p.append(shown.slice(at) + (text.length > shown.length ? "…" : ""));
  return p;
}

export function selectionBox(text, rules, label) {
  return el("div", { className: "sel" }, [
    el("div", { className: "k" }, [el("span", { text: label }), el("span", { text: `${text.length.toLocaleString("en-IN")} chars` })]),
    rules ? previewNode(text, rules) : el("p", { text: text.slice(0, PREVIEW_CHARS) }),
  ]);
}

export function checklistBox(items) {
  const list = el(
    "ul",
    { className: "checks" },
    items.map((item) => {
      const body = el("span", { text: item.title });
      if (item.link) body.append(" (", el("a", { href: item.link, target: "_blank", rel: "noopener noreferrer", text: item.link_label || item.link }), ")");
      return el("li", {}, el("label", {}, [el("input", { type: "checkbox" }), body]));
    }),
  );
  const summary = el("summary", {}, [el("span", { text: `Before you reply: ${items.length} checks` })]);
  const plus = ICONS.plus();
  plus.setAttribute("class", "icon pm");
  summary.append(plus);
  return el("details", {}, [summary, list]);
}

export function openReportLink(href, label = "Open full report") {
  const a = el("a", { className: "open", href, target: "_blank", rel: "noopener noreferrer" }, [el("span", { text: label })]);
  a.append(ICONS.arrow());
  return a;
}

export function verdictView(result, text, reportHref) {
  const rules = topRules(result.rules);
  const count = result.rules.length;
  const chip = el("span", { className: `chip ${VERDICT_CHIP[result.verdict] || "chip-warn"}`, id: "chip" }, [el("span", { className: "dot" }), result.verdict_label]);
  const score = el("span", { className: "score" }, [el("b", { text: result.score.toFixed(2) }), "model score"]);
  const countText = count === 0 ? "No warning signs found." : `${count} warning sign${count === 1 ? "" : "s"}.`;
  const nodes = [
    selectionBox(text, result.rules, "Checked text"),
    el("div", { className: "verdict" }, [chip, score]),
    el("p", { className: "note" }, [el("strong", { text: countText }), ` ${NOTE[result.verdict] || ""}`]),
  ];
  if (result.model_note) nodes.push(el("p", { className: "model-note", text: result.model_note }));
  if (rules.length) {
    nodes.push(
      el("section", {}, [
        el("h2", { text: count > 3 ? `Top 3 of ${count} flags` : "Flags" }),
        el(
          "ol",
          { className: "flags" },
          rules.map((r, i) =>
            el("li", { className: r.severity === "high" ? "" : "warn" }, [
              el("span", { className: "n", "aria-hidden": "true", text: String(i + 1) }),
              el("span", {}, [el("b", { text: r.title }), r.matches[0] ? el("q", { text: r.matches[0].text }) : null]),
            ]),
          ),
        ),
      ]),
    );
  }
  nodes.push(openReportLink(reportHref), checklistBox(result.checklist), el("p", { className: "fine", text: result.disclaimer }));
  return nodes;
}

export function messageView({ iconName, title, body, problem = false, actions = [] }) {
  return el("div", { className: `empty${problem ? " problem" : ""}` }, [ICONS[iconName](), el("h3", { text: title }), body, ...actions]);
}
