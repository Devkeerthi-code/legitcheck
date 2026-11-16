import { Checker } from "@/components/checker/Checker";
import { Hero } from "@/components/hero/Hero";
import { Compare } from "@/components/sections/Compare";
import { ExtensionSection } from "@/components/sections/ExtensionSection";
import { Faq } from "@/components/sections/Faq";
import { Footer, HelpBand } from "@/components/sections/HelpBand";
import { RuleTiles } from "@/components/sections/RuleTiles";
import { StatsStrip } from "@/components/sections/StatsStrip";
import { Steps } from "@/components/sections/Steps";
import { SiteHeader } from "@/components/SiteHeader";
import { ToastProvider } from "@/components/Toasts";

export default function Home() {
  return (
    <ToastProvider>
      <a className="skip" href="#main">
        Skip to content
      </a>
      <SiteHeader />
      <main id="main">
        <Hero />
        <Checker />
        <Compare />
        <RuleTiles />
        <StatsStrip />
        <Steps />
        <ExtensionSection />
        <Faq />
        <HelpBand />
      </main>
      <Footer />
    </ToastProvider>
  );
}
