# Pre-registration: LLM second opinion

Written 2026-10-15 12:48 UTC, before any LLM call on test data. Committed to git before the run; the
commit timestamp is the evidence. Decisions are the team's (Q&A on 2026-10-15).

## Context

Baseline confidence labels (decision B, `reports/confidence_test.json`) put event type "trusted" on 69% of
2025 manufacturing reports at 92.8% accuracy (95% CI 91.6–93.9), just under the 93% target. This is a
**second look at the same test year**; the first result was 92.8%. Both are reported.

## Setup (fixed)

- **Sample:** 500 reports drawn at random (seed 2026) from 2025 manufacturing reports whose event code is
  classifiable. Baseline models: the ones from the confidence test (trained on 2024).
- **Model:** Gemma-4-31B-IT on AMD Token Factory. If it is unavailable, another Token Factory model is
  used and named in the report. Temperature 0.
- **Prompt:** the date-masked narrative, the baseline's top 5 event groups and top 5 source groups (with
  titles), and the 5 most similar 2024 reports (BM25) with their OSHA event and source groups. The LLM picks
  one event group and one source group from the candidates, as JSON.
- An unparseable answer or a code outside the candidates counts as disagreement.

## Rules compared

Baseline labels are unchanged for nature and part of body. For event type:

- **Rule A (primary):** trusted = baseline confidence ≥ the existing trusted threshold (0.6574) **and** the
  LLM picks the same group. Above the threshold but disagreeing → approximate. Human band unchanged.
- **Rule B:** trusted = not in the human band (confidence ≥ 0.560 and not a rare class) **and** the LLM
  picks the same group. Not in the human band but disagreeing → approximate.

Source is never trusted under either rule. When the LLM picks a different source candidate, that candidate is
shown first.

## Pass condition (per rule)

On the 500-report sample:

1. Accuracy of event "trusted" ≥ **0.93**, and
2. Share of event "trusted" ≥ **0.55**.

## Decision

- If Rule A passes, the product uses Rule A.
- Rule B replaces A only if B passes **and** its trusted share is larger than A's.
- If neither passes, the product keeps the baseline-only labels; the result is reported as is.
- The test is run once. No prompt, threshold or rule changes after seeing results.

## Also reported (no pass/fail)

Baseline-only labels on the same 500 reports; LLM-alone accuracy for event and source; how often the true
group is in the top 5 candidates; source top-1 accuracy before and after the LLM reorder; latency and
failed calls.

## Deviation (written 2026-10-15, after the strict result, before any re-scoring)

**What happened.** The single run finished: 500/500 reports answered (499 by Gemma-4-31B-IT, 1 by the
DeepSeek-V4-Flash fallback during a network outage). Network failures produced no answer and were retried
on the same model (see commit "Retry network failures..."). Under strict scoring, neither rule passed
(`reports/llm_second_opinion_strict.json`, decision "baseline only").

**Why a deviation.** In about 60% of answers Gemma copied the whole candidate line, e.g.
`"65: Struck by running powered equipment..."` instead of `"65"`. Strict scoring treated these as "outside
the candidates", although the answer names a candidate. This is a parsing problem in our scoring, not the
model choosing something else.

**Change (scoring only).** An answer is read as group `G` if it equals `G` or starts with `G` followed by
`:`, and `G` is one of the candidates. Everything else stays as pre-registered: same answers (no new
calls), same rules A/B, same thresholds, same pass condition and decision rule.

**Reporting.** Both results are reported: strict (pre-registered) and re-scored (this deviation). The
re-scored result is weaker evidence, because the scoring rule was fixed after seeing the strict result.
