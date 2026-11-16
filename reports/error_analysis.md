# Error analysis

All cases come from the **validation** set, so the test set stays a clean final check.
The raw cases (score, top terms, a text snippet, automatic tags) are in
[error_analysis_cases.md](error_analysis_cases.md), regenerated with
`python -m legitcheck.model.error_analysis`.

At the validation thresholds, 8 of 2,246 genuine postings scored above **High risk** and
10 of 106 fake postings scored below **Has warning signs**.

## Genuine postings flagged as fake (false positives)

| Pattern | Examples | Why it happens |
|---|---|---|
| **Job type is being used as evidence** | Receptionist, Office Manager, Clerical, Data entry, Front desk | In this dataset the fakes cluster in admin and data-entry roles, so words like `receptionist` (+1.06) and `office manager` (+0.87) push the score up on their own. The model learned "what kind of job scammers advertise", not just "how scams are written". This is a topic bias and the biggest source of false alarms. |
| **Industry prior** | Offshore oil & gas project manager (`offshore` +0.76) | Oil and gas postings are heavily over-represented among the fakes, so a genuine engineering role inherits that prior. |
| **Contact-heavy staffing posts** | Jr. Java Developer for OPT candidates (`link urltoken` +0.91, `emailtoken`, `phonetoken`) | Consultancy posts that list many links, emails and phones look like the staffing-agency fakes in the data. |
| **Possibly mislabelled** | "Casual/Part-Time... We give a work for everybody. $430 per a week", no company profile, no logo | This reads like a scam (broken English, vague company, weekly pay) but is labelled genuine. Some "false positives" are probably label noise, so precision is likely slightly understated. |

## Fake postings missed (false negatives)

| Pattern | Examples | Why it happens |
|---|---|---|
| **Fakes written in professional language** | "Our client is an award winning High-Frequency Prop. Trading firm..." | Recruiter-style wording (`our client` -0.27) is common in genuine agency posts. Text alone can't separate a well-copied fake from the real thing. |
| **Signal is in the metadata, not the text** | Almost every missed fake has *no company profile* and *no logo* | The gradient-boosting model with structured features uses exactly these signals (see `figures/gbm_importance_val.png`), but a pasted message has no such fields, so the served model can't use them. |
| **Junk text** | "Normal 0 false false EN-US X-NONE ... mso-style-name" | Word-pasted CSS survived cleaning. A preprocessing gap: strip `mso-` style blocks before vectorising. |
| **Almost no text** | "Sales Executive Sales Executive...", "Northwestern Hospital build a website" | There is nothing to judge. The verdict layer now treats texts under 60 words as low-confidence for the model, and the UI says so. |

## What changed because of this

1. **Short-message rule.** The synthetic India set showed the same short-text problem, much worse: the model alone put 19 of 26 short genuine messages above the warning level (see `synthetic_india_before_short_text_rule` in `models/metrics.json`). Below 60 words the model can no longer raise a warning on its own; only the high threshold and the rules count. On the holdout synthetic set this cut false alarms from 7/10 to 0/10 and missed one scam that had no rule-detectable sign (13/14 caught instead of 14/14).
2. **The rules layer is not optional.** The model catches about half of the synthetic Indian scams on its own (7/14 on holdout), because fees, Telegram HR and Aadhaar requests barely appear in the training data. The rules catch 13/14.

## Next fixes I'd make

- Remove role and industry words from the vocabulary, or reweight by job function, then measure how much PR-AUC that costs versus the drop in admin-role false alarms.
- Strip Office/HTML style junk in `text.clean_text`.
- Drop currency tokens (`rs`, `inr`). All 15 training postings containing `rs` are genuine, so
  the model learned "rupee amount = genuine" (weight about -0.7), the opposite of what an
  India-facing tool needs.
- Collect real (consented, anonymised) Indian offer messages to replace the synthetic set.
