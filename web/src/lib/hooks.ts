"use client";

import { useEffect, useState, type RefObject } from "react";
import { Follower, hasFinePointer } from "./spring";

/** Pulls an element a few pixels toward the cursor, then springs back. Desktop pointers only. */
export function useMagnetic<T extends HTMLElement>(ref: RefObject<T | null>) {
  useEffect(() => {
    const el = ref.current;
    if (!el || !hasFinePointer()) return;
    const f = new Follower(
      (x, y) => {
        el.style.setProperty("--bx", `${x.toFixed(2)}px`);
        el.style.setProperty("--by", `${y.toFixed(2)}px`);
      },
      220,
      14,
    );
    const move = (e: PointerEvent) => {
      const r = el.getBoundingClientRect();
      const dx = e.clientX - (r.left + r.width / 2);
      const dy = e.clientY - (r.top + r.height / 2);
      f.set(Math.max(-8, Math.min(8, dx * 0.22)), Math.max(-6, Math.min(6, dy * 0.3)));
    };
    const leave = () => f.set(0, 0);
    el.addEventListener("pointermove", move);
    el.addEventListener("pointerleave", leave);
    return () => {
      f.stop();
      el.removeEventListener("pointermove", move);
      el.removeEventListener("pointerleave", leave);
    };
  }, [ref]);
}

/** Tilts a card toward the cursor with a spring return. Desktop pointers only. */
export function useTilt<T extends HTMLElement>(ref: RefObject<T | null>) {
  useEffect(() => {
    const el = ref.current;
    if (!el || !hasFinePointer()) return;
    const f = new Follower(
      (x, y) => {
        el.style.setProperty("--ry", `${x.toFixed(2)}deg`);
        el.style.setProperty("--rx", `${y.toFixed(2)}deg`);
      },
      160,
      14,
    );
    const move = (e: PointerEvent) => {
      const r = el.getBoundingClientRect();
      f.set(((e.clientX - r.left) / r.width - 0.5) * 6, -((e.clientY - r.top) / r.height - 0.5) * 6);
    };
    const leave = () => f.set(0, 0);
    el.addEventListener("pointermove", move);
    el.addEventListener("pointerleave", leave);
    return () => {
      f.stop();
      el.removeEventListener("pointermove", move);
      el.removeEventListener("pointerleave", leave);
    };
  }, [ref]);
}

/** True once the element has scrolled into view (and stays true). */
export function useSeenOnce<T extends HTMLElement>(ref: RefObject<T | null>, threshold = 0.2) {
  const [seen, setSeen] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el || seen) return;
    const io = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) {
          setSeen(true);
          io.disconnect();
        }
      },
      { threshold },
    );
    io.observe(el);
    return () => io.disconnect();
  }, [ref, seen, threshold]);
  return seen;
}
