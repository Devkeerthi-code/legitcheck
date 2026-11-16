"use client";

import { createContext, useCallback, useContext, useRef, useState, type ReactNode } from "react";
import { Icon } from "./Icon";
import { spring } from "@/lib/spring";

type ToastTone = "success" | "error" | "info";
interface ToastItem {
  id: number;
  message: string;
  tone: ToastTone;
}

const ToastContext = createContext<(message: string, tone?: ToastTone) => void>(() => {});

export function useToast() {
  return useContext(ToastContext);
}

function Toast({ item, onGone }: { item: ToastItem; onGone: (id: number) => void }) {
  const attach = useCallback(
    (el: HTMLDivElement | null) => {
      if (!el) return;
      spring({
        from: 0,
        to: 1,
        stiffness: 320,
        damping: 22,
        onUpdate: (p) => {
          el.style.transform = `translateY(${(1 - p) * 24}px)`;
          el.style.opacity = String(Math.min(1, p * 1.5));
        },
      });
      window.setTimeout(() => {
        spring({
          from: 1,
          to: 0,
          stiffness: 300,
          damping: 30,
          onUpdate: (p) => {
            el.style.opacity = String(Math.max(0, p));
            el.style.transform = `translateY(${(1 - p) * 12}px)`;
          },
          onDone: () => onGone(item.id),
        });
      }, 4200);
    },
    [item.id, onGone],
  );
  const icon = item.tone === "error" ? "info" : "check";
  return (
    <div ref={attach} className={`toast toast-${item.tone}`}>
      <Icon name={icon} />
      <span>{item.message}</span>
    </div>
  );
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([]);
  const nextId = useRef(1);
  const show = useCallback((message: string, tone: ToastTone = "success") => {
    const id = nextId.current++;
    setItems((list) => [...list.slice(-2), { id, message, tone }]);
  }, []);
  const remove = useCallback((id: number) => setItems((list) => list.filter((t) => t.id !== id)), []);
  return (
    <ToastContext.Provider value={show}>
      {children}
      <div className="toasts" aria-live="polite">
        {items.map((item) => (
          <Toast key={item.id} item={item} onGone={remove} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}
