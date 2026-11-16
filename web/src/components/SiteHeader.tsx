"use client";

import { useEffect, useState } from "react";
import { Icon, LogoMark } from "./Icon";
import { MagneticLink } from "./Magnetic";
import { useTheme } from "@/lib/theme";

function ThemeToggle() {
  const [theme, setTheme] = useTheme();
  const dark = theme === "dark";
  return (
    <button
      className="theme-toggle"
      type="button"
      aria-label={dark ? "Switch to light mode" : "Switch to dark mode"}
      onClick={() => setTheme(dark ? "light" : "dark")}
    >
      <Icon name="sun" className="sun" />
      <Icon name="moon" className="moon" />
    </button>
  );
}

export function SiteHeader() {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header className={`site-header${scrolled ? " scrolled" : ""}`} id="top">
      <nav className="wrap nav" aria-label="Main">
        <a className="logo" href="#top" aria-label="LegitCheck, back to top">
          <LogoMark />
          LegitCheck
        </a>
        <ul className="nav-links">
          <li>
            <a href="#check">Checker</a>
          </li>
          <li>
            <a href="#signs">Warning signs</a>
          </li>
          <li>
            <a href="#how">How it works</a>
          </li>
          <li>
            <a href="#faq">FAQ</a>
          </li>
        </ul>
        <div className="nav-actions">
          <a className="btn btn-ghost btn-sm hide-sm" href="#extension">
            Chrome extension
          </a>
          <MagneticLink className="btn btn-primary btn-sm" href="#check">
            Check an offer
          </MagneticLink>
          <ThemeToggle />
        </div>
      </nav>
    </header>
  );
}
