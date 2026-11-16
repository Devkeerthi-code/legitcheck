# Model card: LegitCheck text model v1.0.0

All numbers come from [`models/metrics.json`](models/metrics.json); the full report is
[`reports/evaluation.md`](reports/evaluation.md).

## What it is

A calibrated **TF-IDF (word 1-2 grams) + logistic regression** classifier that scores how much
the wording of a job posting or offer message resembles fake postings in its training data.
In the app it is **one input** to a verdict, next to a set of hand-written rules for Indian
scam patterns. It never produces the verdict on its own, and there is no "safe" verdict.

| | |
|---|---|
| Output | Probability in 0-1, sigmoid-calibrated with 5-fold cross-validation |
| Thresholds | warn 0.046 (90% recall on validation); high 0.485 (90% precision on validation) |
| Explanations | Exact per-term contribution to the logit: coefficient × tf-idf value |
| Size / speed | 1.2 MB artifact; under 10 ms per check (score, explanation and rules) on one CPU core |
| Code | `legitcheck/model/train.py` (fixed seed 42, pinned dependencies) |

## Training data

- **[Real / Fake Job Posting Prediction](https://www.kaggle.com/datasets/shivamb/real-or-fake-fake-jobposting-prediction)**
  (Kaggle, Shivam Bansal), from the EMSCAD dataset by the University of the Aegean.
  Licence **CC0: Public Domain**. 17,880 postings from 2012-2014, mostly US and English.
- 2,200 exact duplicate postings were removed **before** splitting to avoid train/test leakage,
  leaving 15,680 postings (4.5% fake). Split: 70 / 15 / 15, stratified.
- Emails, URLs and phone numbers are replaced with tokens (`emailtoken`...). The dataset had
  already anonymised them, so whether a contact is present is the signal, never its value.
- The **synthetic India set** (`data/synthetic/india_offers.jsonl`, 64 messages written for this
  project, fictional companies) is used **only** for evaluation and rule tests. Training asserts
  none of it leaks in.

## Performance (test set, evaluated once)

| Metric | Value | What it means |
|---|---|---|
| PR-AUC | **0.879** | Random scoring would get 0.045 here |
| Recall at 90% precision | **0.802** | Tuned on validation, 0.792 at the saved threshold |
| At the *high* threshold | precision 0.903, recall 0.792 | 84 of 106 fakes caught, 9 false alarms among 2,246 genuine |
| At the *warn* threshold | precision 0.480, recall 0.906 | 96 of 106 caught, 104 false alarms |
| Brier score | 0.0116 | Probabilities track observed rates (see the calibration plot) |

Alternatives compared on the same split (test PR-AUC): gradient boosting on engineered text
features 0.337; gradient boosting with structured fields 0.525 (can't be served on pasted text);
average of LR and text GBM 0.850.

**SYNTHETIC India holdout** (14 scams, 10 genuine; written by the project, not real messages):
the model alone flags 7/14 scams **and 7/10 genuine** messages. Combined with the rules and the
short-message policy, the app flags 13/14 scams and 0/10 genuine messages.

## Intended use

- A **second opinion** for students and job seekers deciding whether an internship or job
  offer needs more checking, always shown with a verification checklist.
- Teaching and portfolio purposes: an honest, inspectable baseline.

## Must not be used for

- Declaring any offer or company **safe or genuine**. A low score only means the wording
  resembles genuine postings from 2012-14.
- Accusing, blacklisting or reporting a named company or person automatically.
- Screening applicants, moderating a job board, or any decision about people without human
  review.
- Legal evidence of fraud.

## Limitations and biases

- **Domain shift.** Trained on long, mostly US English postings. Short WhatsApp-style messages,
  Hinglish and Indian scam types (registration fees, Telegram HR, task scams, Aadhaar requests)
  are barely represented. Below 60 words the app ignores the model's warning threshold and
  relies on the rules plus the high threshold.
- **Topic bias.** It learned which *jobs* scammers advertise. Admin, receptionist,
  data-entry and oil-and-gas roles score higher even when genuine (see
  [error analysis](reports/error_analysis.md)). Students applying for those roles will see more
  false alarms.
- **Short-text bias.** In the training data very short postings are often fake, so brevity
  itself raises the score.
- **Rupee bias.** Only 204 training postings are located in India (3 fake), and all 15 that
  mention `rs` are genuine, so the word `rs` pushes the score *towards genuine* (about -0.7 on
  the logit). An Indian scam that quotes a fee in "Rs" gets a slightly lower model score. The
  payment rule catches fee requests regardless, and the next retrain should drop currency
  tokens from the vocabulary.
- **Easy to evade.** A scammer who copies a real company's posting text will score low. That
  is why rules check the email domain, links and payment requests separately.
- **Label noise.** Some genuine-labelled postings read like scams, so reported precision is
  probably slightly understated.
- **Age.** Scam language changes. The model should be retrained on recent, consented data.

## Ethical considerations

- No submitted text is stored or logged. Only daily counts per verdict are kept.
- The optional Gemini step receives only the verdict and the matched phrases, never the full
  message, and cannot change the verdict.
- The UI always ends with "You decide" and the 1930 helpline / cybercrime.gov.in, so a
  wrong score never leaves a student without a next step.
