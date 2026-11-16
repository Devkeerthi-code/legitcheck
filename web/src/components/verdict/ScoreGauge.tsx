"use client";

import { useEffect, useRef } from "react";
import { spring } from "@/lib/spring";

const CX = 66;
const CY = 70;
const R = 56;

function pointAt(fraction: number, radius: number) {
  const angle = Math.PI * (1 - fraction);
  return { x: CX + radius * Math.cos(angle), y: CY - radius * Math.sin(angle) };
}

function Tick({ at, label }: { at: number; label: string }) {
  const inner = pointAt(at, R + 6);
  const outer = pointAt(at, R + 12);
  return (
    <g>
      <line x1={inner.x} y1={inner.y} x2={outer.x} y2={outer.y} stroke="var(--ink-2)" strokeWidth="2" strokeLinecap="round" />
      <title>{label}</title>
    </g>
  );
}

interface Props {
  score: number;
  warn: number;
  high: number;
  tone: "high" | "warn" | "ok";
}

/** Half-circle gauge. The arc springs up to the score; ticks mark the warning and high-risk lines. */
export function ScoreGauge({ score, warn, high, tone }: Props) {
  const arc = useRef<SVGPathElement>(null);
  const label = useRef<SVGTextElement>(null);
  const value = Math.max(0, Math.min(1, score));

  useEffect(() => {
    return spring({
      from: 0,
      to: value,
      stiffness: 60,
      damping: 13,
      onUpdate: (v) => {
        const c = Math.max(0, Math.min(1, v));
        arc.current?.setAttribute("stroke-dashoffset", String(100 - c * 100));
        if (label.current) label.current.textContent = c.toFixed(2);
      },
    });
  }, [value]);

  const path = `M10 70 A56 56 0 0 1 122 70`;
  return (
    <svg className="gauge" viewBox="-4 -10 140 92" role="img" aria-label={`Model score ${value.toFixed(2)} out of 1. Warning from ${warn.toFixed(2)}, high risk from ${high.toFixed(2)}.`}>
      <path d={path} fill="none" stroke="var(--rule)" strokeWidth="10" strokeLinecap="round" />
      <path
        ref={arc}
        d={path}
        fill="none"
        stroke={`var(--${tone})`}
        strokeWidth="10"
        strokeLinecap="round"
        pathLength={100}
        strokeDasharray="100"
        strokeDashoffset="100"
      />
      <Tick at={warn} label={`Warning line, ${warn.toFixed(2)}`} />
      <Tick at={high} label={`High-risk line, ${high.toFixed(2)}`} />
      <text ref={label} x="66" y="64" textAnchor="middle" fontSize="22" fontWeight="600" fill="var(--ink)">
        0.00
      </text>
    </svg>
  );
}
