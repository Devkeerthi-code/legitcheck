import Link from "next/link";
import { LogoMark } from "@/components/Icon";

export default function NotFound() {
  return (
    <main className="not-found wrap">
      <LogoMark size={40} />
      <p className="eyebrow">404</p>
      <h1>
        This page doesn&apos;t exist. <span className="nf-mark">The checker does.</span>
      </h1>
      <p className="lede">The link may be old or mistyped. Nothing was lost: nothing you paste is ever stored.</p>
      <Link className="btn btn-primary" href="/">
        Go to the checker
      </Link>
    </main>
  );
}
