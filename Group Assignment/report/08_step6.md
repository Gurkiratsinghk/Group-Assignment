# Step 6: Three t-Tests in Business Terms

## Test A: Does the IT basket's average range exceed the 2.0% policy level?

**Desk's belief:** current stop-losses and margin buffers, set at 2.0% of the opening price, are adequate for the IT basket.

**What the data says:** the sample mean IT range is 2.307%, meaningfully above 2.0% in absolute terms, but with n = 40 the test statistic (t = 1.667, p = 0.052) falls just short of the 5% significance threshold. This reproduces Step 5's result exactly.

**What changes:** nothing is proven wrong yet, but the desk should not read this as confirmation either. The gap between "2.307% observed" and "2.0% assumed" is real and sizeable; it just isn't statistically nailed down at this sample size. This is a borderline result that argues for re-testing with more data before the desk either raises its buffer or keeps it as-is with full confidence.

## Test B: Does IT trade with a wider daily range than Consumer Staples (FMCG)?

**Desk's belief:** if sector risk budgets are undifferentiated, the desk is implicitly assuming IT and FMCG carry comparable day-to-day range risk.

**What the data says:** Levene's test confirms the two sectors have statistically indistinguishable variances (p = 0.665), so the pooled t-test is the correct tool. On a fresh, independently drawn n = 40 sample per sector, IT's mean range (2.084%) sits 0.236 points **below** FMCG's (2.320%) — the opposite direction from an earlier, flawed pass — and it's nowhere near significant (t = -0.782, df = 78, p = 0.437, Cohen's d = -0.17). Mann-Whitney U agrees (p = 0.310); the 95% CI, [-0.836, 0.365], sits comfortably around zero. (An earlier draft accidentally reused Step 5's exact IT sample instead of drawing a fresh one, producing a misleading close-call result — see report/10_audit.md.)

**What changes:** nothing. This sample gives no evidence that IT and FMCG carry systematically different daily trading ranges — the effect is small, statistically insignificant, and even reverses sign from an earlier (buggy) pass. The desk should not differentiate sector risk budgets for IT vs FMCG on the basis of this variable; if anything, this result argues for treating the two books similarly until a much larger sample says otherwise.

## Test C: Is overnight gap risk or intraday move risk larger?

**Desk's belief:** an implicit assumption in many risk frameworks is that overnight gap risk — the risk accrued while the market is closed and positions can't be adjusted — is the primary driver of daily risk, since it can't be hedged in real time.

**What the data says:** this pairs both measurements on the same 40 ticker-days, which matters because overnight and intraday moves on the same session are correlated (a volatile day tends to show up in both legs) — treating the two columns as independent samples would inflate the standard error and blur a real within-day relationship. The paired test flatly contradicts the overnight-dominance assumption: mean intraday move (0.948%) is nearly double the mean overnight gap (0.505%), a highly significant difference (t = -3.108, p = 0.0035, Cohen's d = -0.49), confirmed by the Wilcoxon signed-rank robustness check (p = 0.0014). The equivalence check — running the paired test directly and as a one-sample t-test on the difference column — produced identical statistics, as it must.

**What changes:** this is the one test with a clear, decisive answer. The desk's real exposure on these names comes disproportionately from *during-session* trading, not the overnight gap. That argues for shifting risk-monitoring emphasis toward intraday limits and real-time systems rather than concentrating defensive measures on overnight gap buffers alone — the risk that can't be hedged (overnight) is, on this evidence, the smaller of the two.

## Taken together

Test A is a genuine close call that should be flagged as "watch, don't act yet." Test B is a clear null result — no evidence of a sector gap in range risk, so don't differentiate IT and FMCG on this basis. Test C gives the desk an actionable, statistically solid finding: intraday risk outweighs overnight risk on these names, and risk controls should be weighted accordingly.
