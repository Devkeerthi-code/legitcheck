"use client";

import { useEffect, useState } from "react";
import { getStats } from "@/lib/api";
import { fmt } from "@/lib/metrics";

const MIN_TO_SHOW = 10;

/** "Checked N offers so far", only once the real count is big enough to mean something. */
export function UsageLine() {
  const [checks, setChecks] = useState<number | null>(null);
  useEffect(() => {
    let alive = true;
    void getStats().then((s) => {
      if (alive && s && s.checks >= MIN_TO_SHOW) setChecks(s.checks);
    });
    return () => {
      alive = false;
    };
  }, []);
  if (checks === null) return null;
  return <p className="usage-line">Checked {fmt.int(checks)} offers so far.</p>;
}
