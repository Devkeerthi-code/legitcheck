import type { CSSProperties } from "react";
import type { TopTerm } from "@/lib/types";

/** Words the model weighed most. Shown as a list with bars, never highlighted in the text. */
export function TopTerms({ terms }: { terms: TopTerm[] }) {
  if (terms.length === 0) return null;
  const max = Math.max(...terms.map((t) => Math.abs(t.weight))) || 1;
  return (
    <div className="words">
      <h4>Words the model weighed most</h4>
      <ul className="term-list">
        {terms.map((t) => {
          const fake = t.direction === "towards_fake";
          return (
            <li key={t.term} className={`word ${fake ? "to-fake" : "to-genuine"}`}>
              <code title={t.term}>{t.term}</code>
              <span className="bar" aria-hidden="true">
                <i style={{ "--w": `${Math.round((Math.abs(t.weight) / max) * 100)}%` } as CSSProperties} />
              </span>
              <span className="dir">{fake ? "toward fake" : "toward genuine"}</span>
            </li>
          );
        })}
      </ul>
      <p className="fine">Lowercased words and pairs from your text. [a link], [an email address] and [a phone number] stand in for any link, email or number.</p>
    </div>
  );
}
