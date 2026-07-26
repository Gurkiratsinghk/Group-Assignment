# Step 3: Hypothesis Framing — IT Basket Daily Trading Range

## 1. Parameter and benchmark

The parameter of interest is **μ**, the population mean of `range_pct` for the six large-cap Indian IT tickers (Technology sector). The benchmark is **μ₀ = 2.0%**, the desk's existing stop-loss/margin policy level, fixed before this data was examined — it is not derived from the sample and cannot be adjusted after seeing the result.

## 2. Hypotheses

- **H0: μ ≤ 2.0%** — the desk's claim as stated ("at most 2.0%"). This is the status quo, so it is the null: the burden of proof sits on the data to overturn it, not on the desk to re-justify an existing, already-budgeted policy.
- **Ha: μ > 2.0%** — the risk-relevant direction. Only this direction changes the decision: if the true average range is below 2.0%, current stops/margins are already adequate; the desk only needs to act if the true average exceeds 2.0%, since that means stops and margins are undersized relative to actual volatility.

## 3. Tail and rejection region

**One-tailed, upper-tailed.** The desk revises policy only if evidence points toward understated risk (μ > 2.0). A two-tailed test wastes power on a direction that triggers no action. Rejection region: right tail of the t-distribution.

## 4. Significance level

**α = 0.05.** A false alarm here (tightening stops/margins when 2.0% was already adequate) costs some capital efficiency but is cheap and fully reversible — unlike a clinical trial, where a false positive can put patients on an ineffective or harmful treatment and typically demands α = 0.01 or stricter. A missed true signal (Type II error), conversely, leaves the desk under-margined against real volatility. α = 0.05 is a conventional, defensible balance for a reversible, capital-allocation decision of this kind.

## 5. Test choice

**Primary test: one-sample t-test** (n = 40 per project design). Justification from the EDA (`02_eda_findings.md`): the raw `range_pct` variable is heavily right-skewed (population skewness 2.46; Technology-sector skewness ≈2.51, excess kurtosis ≈12.77) and fails Shapiro-Wilk, D'Agostino K², and Anderson-Darling decisively. The t-test does not require the *raw variable* to be normal — it requires the *sampling distribution of the mean* to be approximately normal, and the CLT demonstration in Step 2 confirmed this holds reasonably well by n = 40: Shapiro-Wilk on 500 resampled means gave W = 0.989 versus W = 0.783 for the raw variable, and empirical CI coverage (93.8%) sat close to the nominal 95%. This licenses the t-test as primary. **Robustness check: Wilcoxon signed-rank test**, run given the residual skew and imperfect CLT convergence at this n; it does not assume normality of the mean's sampling distribution.

## 6. Assumptions, assessed honestly

- **Scale of measurement:** `range_pct` is continuous, ratio-scale — appropriate for a t-test.
- **Approximate normality of the sampling distribution:** reasonably supported (see above), though not perfect at n = 40 given the strength of the skew.
- **Independence:** this is the weak assumption here, and it should not be glossed over. Ticker-day observations are **not** fully independent: volatility clusters in time (today's range is correlated with yesterday's), the six IT names share common drivers — the rupee-dollar rate and overnight Nasdaq moves, since these are USD-revenue exporters tracking global tech sentiment — and quarterly results cluster into the same few weeks each quarter across all six names simultaneously. **Consequence:** the effective sample size is smaller than the nominal n = 40, so the standard error computed under an i.i.d. assumption is understated, making the test mildly **anti-conservative** — the true false-positive rate is somewhat higher than the stated 5%.
