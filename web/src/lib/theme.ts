"use client";

import { useSyncExternalStore } from "react";

export type Theme = "light" | "dark";
const KEY = "lc-theme";

/**
 * Runs in <head> before paint. Light is the default whatever the OS says; dark only applies
 * when the visitor chose it with the toggle (stored in localStorage).
 */
export const THEME_BOOT_SCRIPT = `try{if(localStorage.getItem("${KEY}")==="dark")document.documentElement.dataset.theme="dark"}catch(e){}`;

function read(): Theme {
  return document.documentElement.dataset.theme === "dark" ? "dark" : "light";
}

function subscribe(onChange: () => void) {
  const mo = new MutationObserver(onChange);
  mo.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  return () => mo.disconnect();
}

export function useTheme(): [Theme, (t: Theme) => void] {
  const theme = useSyncExternalStore(subscribe, read, () => "light" as Theme);
  const setTheme = (t: Theme) => {
    if (t === "dark") document.documentElement.dataset.theme = "dark";
    else delete document.documentElement.dataset.theme;
    try {
      localStorage.setItem(KEY, t);
    } catch {
      // Private mode or storage blocked: the choice lasts for this page view only.
    }
  };
  return [theme, setTheme];
}
