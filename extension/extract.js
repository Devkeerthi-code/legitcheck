// Runs INSIDE the page via chrome.scripting.executeScript, so it must be self-contained:
// no imports, no outer variables. Returns the selection, else the page's main readable text.
export function extractPageText(maxChars) {
  const clean = (s) => (s || "").replace(/[ \t ]+/g, " ").replace(/\s*\n\s*\n\s*/g, "\n\n").trim();
  const SKIP = "nav, header, footer, aside, script, style, noscript, [role=navigation], [role=banner], [role=contentinfo]";

  const selection = clean(String(window.getSelection ? window.getSelection() : ""));
  if (selection.length >= 20) return { text: selection.slice(0, maxChars), from: "selection" };

  // innerText keeps line breaks between blocks; then drop the text of any page chrome inside.
  const readable = (el) => {
    let text = el.innerText || el.textContent || "";
    el.querySelectorAll(SKIP).forEach((n) => {
      const skipped = n.innerText || "";
      if (skipped.trim()) text = text.replace(skipped, "");
    });
    return clean(text);
  };

  const preferred = document.querySelector("article, main, [role=main]");
  if (preferred) {
    const text = readable(preferred);
    if (text.length >= 200) return { text: text.slice(0, maxChars), from: "main" };
  }

  // Score each container by the paragraph-like text directly inside it; the best one is the body copy.
  const scores = new Map();
  document.querySelectorAll("p, li, pre, blockquote, td").forEach((node) => {
    if (node.closest(SKIP)) return;
    const parent = node.parentElement;
    if (!parent) return;
    scores.set(parent, (scores.get(parent) || 0) + clean(node.textContent).length);
  });
  let best = null;
  let bestScore = 0;
  scores.forEach((score, el) => {
    if (score > bestScore) {
      best = el;
      bestScore = score;
    }
  });
  const text = best && bestScore >= 200 ? readable(best) : readable(document.body);
  return { text: text.slice(0, maxChars), from: "page" };
}
