import { LogoMark } from "../Icon";

/** A static, scaled-down picture of the popup so people know what they'd get. */
function PopupPreview() {
  return (
    <figure className="ext-preview" aria-label="Preview of the extension popup, with a fictional example">
      <div className="ext-top">
        <span className="logo ext-logo">
          <LogoMark size={20} />
          LegitCheck
        </span>
        <span className="tag-fiction">Fictional</span>
      </div>
      <div className="ext-body">
        <div className="ext-verdict">
          <span className="chip chip-high">
            <span className="dot" />
            High risk
          </span>
          <span className="ext-score">
            <b>0.94</b>model score
          </span>
        </div>
        <ol className="ext-flags">
          <li>
            <span className="n">1</span>
            <span>
              <b>Asks you to pay</b>
              <q>registration fee of ₹1,999</q>
            </span>
          </li>
          <li>
            <span className="n">2</span>
            <span>
              <b>Asks for ID or bank details early</b>
              <q>send Aadhaar and PAN</q>
            </span>
          </li>
          <li className="warn">
            <span className="n">3</span>
            <span>
              <b>Recruiter only on Telegram</b>
              <q>contact HR on Telegram</q>
            </span>
          </li>
        </ol>
        <span className="ext-open">Open full report</span>
      </div>
      <figcaption className="ext-foot">
        <span>Only the text you choose is checked.</span>
        <span className="ext-call">Paid? Call 1930</span>
      </figcaption>
    </figure>
  );
}

export function ExtensionSection() {
  return (
    <section className="section alt" id="extension" aria-labelledby="extTitle">
      <div className="wrap ext-grid">
        <div>
          <span className="eyebrow">Chrome extension</span>
          <h2 id="extTitle" className="mt-4">
            Check it where you found it.
          </h2>
          <p className="lede mt-4">
            On LinkedIn, Internshala, Gmail or WhatsApp Web, select the offer text and right-click. The popup shows the verdict and
            the top flags without leaving the page.
          </p>
          <ol className="ext-points">
            <li>
              <span>
                <b>Select the text</b> of the offer or posting.
              </span>
            </li>
            <li>
              <span>
                <b>Right-click, &quot;Check with LegitCheck&quot;.</b> Only the selected text is sent. Or click the toolbar icon to
                check the page you&apos;re on.
              </span>
            </li>
            <li>
              <span>
                <b>Read the verdict and top 3 flags,</b> then open the full report here if you want the details.
              </span>
            </li>
          </ol>
          <p className="fine mt-4">
            Desktop Chrome only, loaded from the project&apos;s extension folder (see the README). On your phone, paste into the
            checker above.
          </p>
        </div>
        <PopupPreview />
      </div>
    </section>
  );
}
