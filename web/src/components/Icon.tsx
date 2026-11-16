import type { CSSProperties } from "react";

const PATHS = {
  check: <path d="M5 12.5l4.5 4.5L19 7.5" />,
  cross: <path d="M6.5 6.5l11 11M17.5 6.5l-11 11" />,
  flag: <path d="M5 21V4M5 4h11l-2 4 2 4H5" />,
  lock: (
    <>
      <rect x="5" y="11" width="14" height="9" rx="2" />
      <path d="M8 11V8a4 4 0 018 0v3" />
    </>
  ),
  phone: <path d="M5 4h4l2 5-2.5 1.5a11 11 0 005 5L15 13l5 2v4a1 1 0 01-1 1A16 16 0 014 5a1 1 0 011-1z" />,
  arrow: <path d="M5 12h14M13 6l6 6-6 6" />,
  down: <path d="M12 5v14M6 13l6 6 6-6" />,
  play: <path d="M8 5.5v13l10-6.5z" />,
  pause: <path d="M8 5v14M16 5v14" />,
  replay: <path d="M4 12a8 8 0 108-8 8 8 0 00-6 2.7M4 4v4h4" />,
  sun: (
    <>
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
    </>
  ),
  moon: <path d="M20 14.5A8 8 0 019.5 4 8 8 0 1020 14.5z" />,
  hand: (
    <path d="M8 13V5.5a1.5 1.5 0 013 0V12M11 11V4.5a1.5 1.5 0 013 0V12M14 11.5V6a1.5 1.5 0 013 0v8a6 6 0 01-6 6h-.6a6 6 0 01-4.8-2.4L3.5 14.8a1.6 1.6 0 012.4-2.1L8 14.5" />
  ),
  info: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 11v5M12 8h.01" />
    </>
  ),
  pointer: <path d="M6 3l12 7-5.5 1.5L10 17z" />,
  external: <path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 01-1 1H5a1 1 0 01-1-1V7a1 1 0 011-1h5" />,
  plus: <path d="M12 5v14M5 12h14" />,
  wifiOff: <path d="M3 3l18 18M8.5 16.5a5 5 0 017 0M5 12.5a10 10 0 015.2-2.8M19 12.5a10 10 0 00-2.4-1.7M2 8.8a15 15 0 014.4-2.6M22 8.8A15 15 0 0012 5M12 20h.01" />,
  clock: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3 2" />
    </>
  ),
} as const;

export type IconName = keyof typeof PATHS;

export function Icon({ name, size, className, style }: { name: IconName; size?: number; className?: string; style?: CSSProperties }) {
  return (
    <svg
      className={`icon${className ? ` ${className}` : ""}`}
      viewBox="0 0 24 24"
      aria-hidden="true"
      focusable="false"
      style={size ? { width: size, height: size, ...style } : style}
    >
      {PATHS[name]}
    </svg>
  );
}

export function LogoMark({ size = 28 }: { size?: number }) {
  return (
    <svg className="logo-mark" width={size} height={size} viewBox="0 0 32 32" aria-hidden="true" focusable="false">
      <rect width="32" height="32" rx="8" fill="var(--ink)" />
      <rect x="8" y="9" width="16" height="2.5" rx="1.25" fill="var(--paper)" opacity=".55" />
      <rect x="6.5" y="14.2" width="19" height="4.2" rx="1.4" fill="#FFDF9E" />
      <rect x="8" y="21" width="11" height="2.5" rx="1.25" fill="var(--paper)" opacity=".55" />
    </svg>
  );
}
