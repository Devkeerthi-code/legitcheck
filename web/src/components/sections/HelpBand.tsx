import { Icon } from "../Icon";

export function HelpBand() {
  return (
    <section className="wrap help-wrap" aria-labelledby="helpTitle">
      <div className="help-band">
        <div>
          <h2 id="helpTitle">Already paid someone? Call 1930 now.</h2>
          <p>
            The National Cyber Crime Helpline. Reporting within the first hours gives the best chance of stopping the money. Then
            file at cybercrime.gov.in and call your bank.
          </p>
        </div>
        <div className="btns">
          <a className="btn btn-call" href="tel:1930">
            <Icon name="phone" />
            Call 1930
          </a>
          <a className="btn btn-out" href="https://cybercrime.gov.in" target="_blank" rel="noopener noreferrer">
            cybercrime.gov.in <Icon name="external" size={16} />
            <span className="sr-only">(opens in a new tab)</span>
          </a>
        </div>
      </div>
    </section>
  );
}

export function Footer() {
  return (
    <footer>
      <div className="wrap foot">
        <span>LegitCheck. Helps you read an offer. Does not certify any company.</span>
        <span>Nothing you paste is stored.</span>
      </div>
    </footer>
  );
}
