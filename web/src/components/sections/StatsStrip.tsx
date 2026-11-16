import { fmt, metrics as m } from "@/lib/metrics";

interface Stat {
  label: string;
  value: string;
  unit?: string;
  note: string;
}

const STATS: Stat[] = [
  {
    label: "PR-AUC on held-out postings",
    value: fmt.decimal(m.prAuc),
    note: `How well the model ranks fake postings above real ones. 1.0 is perfect; guessing at random scores ${fmt.decimal(m.randomPrAuc)} here, because only about 1 in ${Math.round(1 / m.randomPrAuc)} postings is fake.`,
  },
  {
    label: "Fakes caught at High risk",
    value: `${m.high.caught}`,
    unit: `of ${m.high.fakes}`,
    note: `${fmt.percent(m.high.recall)} of the fake postings in the test set were marked High risk, and ${fmt.percent(m.high.precision)} of High risk marks were right.`,
  },
  {
    label: "False alarms at High risk",
    value: `${m.high.falseAlarms}`,
    unit: `of ${fmt.int(m.high.genuine)}`,
    note: "Genuine test postings wrongly marked High risk. Low on purpose, so a real offer is rarely scared off.",
  },
  {
    label: "Fakes reaching the warning level",
    value: fmt.percent(m.warn.recall),
    note: `The lower "Has warning signs" level catches ${m.warn.caught} of ${m.high.fakes} fakes, but only ${fmt.percent(m.warn.precision)} of those warnings are fakes. That's why a warning means "check", not "scam".`,
  },
];

export function StatsStrip() {
  const s = m.synthetic;
  return (
    <section className="section" aria-labelledby="statsTitle">
      <div className="wrap">
        <div className="section-head split">
          <div className="grid gap-4">
            <span className="eyebrow">How well it works</span>
            <h2 id="statsTitle">Measured on postings it never saw.</h2>
          </div>
          <p className="lede">
            {fmt.int(m.testSize)} job postings were held back from training (out of {fmt.int(m.rowsAfterDedupe)} after removing
            duplicates) and only used to score the final model. Each number says what it means in plain words.
          </p>
        </div>
        <div className="stats">
          {STATS.map((stat) => (
            <div className="stat" key={stat.label}>
              <span className="k">{stat.label}</span>
              <span className="stat-value">
                {stat.value}
                {stat.unit && <small>{stat.unit}</small>}
              </span>
              <p>{stat.note}</p>
            </div>
          ))}
        </div>
        <div className="stats-extra">
          <div className="stat-synthetic">
            <span className="tag-fiction">Synthetic examples written for testing</span>
            <p>
              <strong>
                {s.scamFlagged} of {s.scamTotal}
              </strong>{" "}
              Indian-style scam messages flagged, and{" "}
              <strong>
                {s.genuineFlagged} of {s.genuineTotal}
              </strong>{" "}
              genuine-style offers falsely flagged, on a held-out set written after the rules. These are invented messages, not real
              ones, so treat them as a sanity check rather than a score.
            </p>
          </div>
          <p className="stat-honest">
            The model learned from a public dataset of mostly US job postings from 2012 to 2014. Signs that are specific to India,
            like registration fees in rupees, Telegram HR and UPI requests, come from transparent rules you can read above.
          </p>
        </div>
      </div>
    </section>
  );
}
