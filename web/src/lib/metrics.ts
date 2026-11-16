import raw from "@/data/metrics.json";

/** The few numbers the page shows, read from models/metrics.json (copied in before every build). */
export interface PageMetrics {
  prAuc: number;
  randomPrAuc: number;
  high: { precision: number; recall: number; caught: number; fakes: number; falseAlarms: number; genuine: number };
  warn: { precision: number; recall: number; caught: number };
  testSize: number;
  rowsAfterDedupe: number;
  synthetic: { scamFlagged: number; scamTotal: number; genuineFlagged: number; genuineTotal: number };
}

type Confusion = { precision: number; recall: number; tp: number; fp: number; tn: number; fn: number };

interface MetricsFile {
  dataset: { rows_after_dedupe: number; split_sizes: { test: number } };
  test: { tfidf_logreg: { pr_auc: number } };
  test_baselines: { random_pr_auc: number };
  test_chosen_at_thresholds: { warn: Confusion; high: Confusion };
  synthetic_india: {
    holdout: {
      scam: { combined: { flagged: number; total: number } };
      genuine: { combined: { flagged: number; total: number } };
    };
  };
}

export function pickMetrics(m: MetricsFile): PageMetrics {
  const high = m.test_chosen_at_thresholds.high;
  const warn = m.test_chosen_at_thresholds.warn;
  const holdout = m.synthetic_india.holdout;
  return {
    prAuc: m.test.tfidf_logreg.pr_auc,
    randomPrAuc: m.test_baselines.random_pr_auc,
    high: {
      precision: high.precision,
      recall: high.recall,
      caught: high.tp,
      fakes: high.tp + high.fn,
      falseAlarms: high.fp,
      genuine: high.tn + high.fp,
    },
    warn: { precision: warn.precision, recall: warn.recall, caught: warn.tp },
    testSize: m.dataset.split_sizes.test,
    rowsAfterDedupe: m.dataset.rows_after_dedupe,
    synthetic: {
      scamFlagged: holdout.scam.combined.flagged,
      scamTotal: holdout.scam.combined.total,
      genuineFlagged: holdout.genuine.combined.flagged,
      genuineTotal: holdout.genuine.combined.total,
    },
  };
}

export const metrics: PageMetrics = pickMetrics(raw as MetricsFile);

export const fmt = {
  decimal: (n: number, digits = 3) => n.toFixed(digits),
  int: (n: number) => n.toLocaleString("en-IN"),
  percent: (n: number) => `${Math.round(n * 100)}%`,
};
