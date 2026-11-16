import { Fragment, type CSSProperties } from "react";
import { Icon } from "../Icon";
import { MagneticLink } from "../Magnetic";
import { HeroDemo } from "./HeroDemo";
import { UsageLine } from "./UsageLine";

const HEADLINE = ["Read", "it", "before", "you"];
const MARKED = ["pay", "for", "it."];

/** Each word is its own span so CSS can drop them in one after another (no JS needed). */
function Words({ words, offset }: { words: string[]; offset: number }) {
  return words.map((w, idx) => (
    <Fragment key={w}>
      {idx > 0 && " "}
      <span className="w" style={{ "--i": offset + idx } as CSSProperties} aria-hidden="true">
        {w}
      </span>
    </Fragment>
  ));
}

function Headline() {
  return (
    <h1 id="heroTitle" aria-label="Read it before you pay for it.">
      <Words words={HEADLINE} offset={0} />{" "}
      <span className="pay">
        <span className="pay-w">
          <Words words={MARKED} offset={HEADLINE.length} />
        </span>
      </span>
    </h1>
  );
}

export function Hero() {
  return (
    <section className="hero" aria-labelledby="heroTitle">
      <div className="wrap hero-grid">
        <div className="hero-copy">
          <span className="eyebrow">For students checking internship and job offers</span>
          <Headline />
          <p className="lede">
            Paste an offer message or posting. LegitCheck points out each warning sign, such as a registration fee, HR who only
            talks on Telegram, or a Gmail address posing as a company, and shows you the exact words that triggered it. Then you
            decide.
          </p>
          <div className="hero-ctas">
            <MagneticLink className="btn btn-primary" href="#check">
              Check an offer <Icon name="arrow" />
            </MagneticLink>
            <a className="btn btn-ghost" href="#signs">
              See the warning signs
            </a>
          </div>
          <a className="demo-jump" href="#demo">
            <Icon name="down" size={16} />
            Watch it check a fictional offer
          </a>
          <div className="hero-meta">
            <span>
              <Icon name="lock" />
              Nothing you paste is stored
            </span>
            <span>
              <Icon name="check" />
              No account needed
            </span>
            <span>
              <Icon name="check" />
              Free
            </span>
          </div>
          <UsageLine />
        </div>
        <HeroDemo />
      </div>
    </section>
  );
}
