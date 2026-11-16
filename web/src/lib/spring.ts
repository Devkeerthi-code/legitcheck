/**
 * Tiny damped-spring integrator (semi-implicit Euler). Real springs instead of eased fades,
 * so things land with weight and a little overshoot, and can be interrupted mid-flight.
 */
export interface SpringOptions {
  from: number;
  to: number;
  stiffness?: number;
  damping?: number;
  mass?: number;
  velocity?: number;
  onUpdate: (value: number) => void;
  onDone?: () => void;
}

export function prefersReducedMotion(): boolean {
  return typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export function hasFinePointer(): boolean {
  return typeof window !== "undefined" && window.matchMedia("(hover: hover) and (pointer: fine)").matches;
}

/** Runs a spring and returns a cancel function. Jumps straight to the end for reduced motion. */
export function spring({ from, to, stiffness = 200, damping = 18, mass = 1, velocity = 0, onUpdate, onDone }: SpringOptions) {
  if (prefersReducedMotion()) {
    onUpdate(to);
    onDone?.();
    return () => {};
  }
  let x = from;
  let v = velocity;
  let last = performance.now();
  let raf = 0;
  const step = (now: number) => {
    const dt = Math.min(0.032, (now - last) / 1000);
    last = now;
    v += ((-stiffness * (x - to) - damping * v) / mass) * dt;
    x += v * dt;
    onUpdate(x);
    if (Math.abs(v) < 0.005 && Math.abs(x - to) < 0.0005) {
      onUpdate(to);
      onDone?.();
      return;
    }
    raf = requestAnimationFrame(step);
  };
  raf = requestAnimationFrame(step);
  return () => cancelAnimationFrame(raf);
}

/** A 2D spring that keeps chasing a moving target. Used by magnetic buttons and tilt cards. */
export class Follower {
  private x = 0;
  private y = 0;
  private vx = 0;
  private vy = 0;
  private tx = 0;
  private ty = 0;
  private raf = 0;
  private last = 0;

  constructor(
    private readonly apply: (x: number, y: number) => void,
    private readonly k = 180,
    private readonly c = 16,
  ) {}

  set(tx: number, ty: number) {
    this.tx = tx;
    this.ty = ty;
    if (prefersReducedMotion()) {
      this.apply(0, 0);
      return;
    }
    if (!this.raf) {
      this.last = performance.now();
      this.raf = requestAnimationFrame(this.tick);
    }
  }

  stop() {
    cancelAnimationFrame(this.raf);
    this.raf = 0;
  }

  private tick = (now: number) => {
    const dt = Math.min(0.032, (now - this.last) / 1000);
    this.last = now;
    this.vx += (-this.k * (this.x - this.tx) - this.c * this.vx) * dt;
    this.vy += (-this.k * (this.y - this.ty) - this.c * this.vy) * dt;
    this.x += this.vx * dt;
    this.y += this.vy * dt;
    this.apply(this.x, this.y);
    const moving = Math.abs(this.vx) + Math.abs(this.vy) >= 0.01;
    const away = Math.abs(this.x - this.tx) + Math.abs(this.y - this.ty) >= 0.01;
    if (!moving && !away) {
      this.raf = 0;
      this.apply(this.tx, this.ty);
      return;
    }
    this.raf = requestAnimationFrame(this.tick);
  };
}
