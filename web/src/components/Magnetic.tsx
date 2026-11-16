"use client";

import { useRef, type AnchorHTMLAttributes, type ReactNode } from "react";
import { useMagnetic } from "@/lib/hooks";

/** A link that leans toward the cursor on desktop. Plain link everywhere else. */
export function MagneticLink({ children, className, ...rest }: AnchorHTMLAttributes<HTMLAnchorElement> & { children: ReactNode }) {
  const ref = useRef<HTMLAnchorElement>(null);
  useMagnetic(ref);
  return (
    <a ref={ref} className={`${className ?? ""} magnetic`} {...rest}>
      {children}
    </a>
  );
}
