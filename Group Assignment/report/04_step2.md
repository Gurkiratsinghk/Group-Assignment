# Step 2: CLT Demonstration & Confidence Interval

## The Central Limit Theorem in action

Drawing 500 independent samples of n = 40 from the population and recording each sample mean of range_pct produces an empirical standard error of 0.1717%, essentially matching the theoretical prediction sigma/√n = 0.1704%. The 1×3 panel (n = 5, 15, 40) shows the sampling distribution visibly tightening and losing skew as n grows, even though the underlying variable itself has skewness of 2.46. This is the CLT visualized directly: individual sessions are far from normal, but averages of them are not. A Shapiro-Wilk test on the 500 sample means gives W = 0.989, p = 0.0011 — still a formal rejection of exact normality, but nowhere near the extreme non-normality of the raw variable (W = 0.783, p ≈ 3×10⁻²⁵ on a comparable 500-row subsample). Averaging 40 skewed observations does not produce perfect normality here, but it moves the distribution dramatically closer to it.

## Confidence interval

The 95% t-interval for the population mean, built from the single original n = 40 sample, is [1.633%, 2.375%] (mean 2.004%, t-critical 2.023 on 39 df, margin of error 0.371%). Manual recomputation matched the skill output exactly (all differences 0.00e+00). The t-distribution, not z, is correct here because the population standard deviation is unknown and is being estimated from the sample itself; t's heavier tails widen the interval to price in that extra estimation uncertainty, whereas the z-interval [1.645%, 2.364%] is slightly and misleadingly narrower.

**Correct interpretation:** if we repeated this sampling procedure many times, about 95% of the resulting confidence intervals would contain the true population mean. This is a statement about the long-run behavior of the *procedure*, not about this one interval.

**WRONG interpretation:** "there is a 95% probability the true mean lies in this interval." This is wrong because the population mean is a fixed, unknown constant, not a random variable — it either does or does not lie in this specific interval, with no probability attached to it. The 95% describes how often the *method* succeeds across repeated samples, not our belief about this particular result.

The coverage check across the 500 resampled intervals supports this: 93.8% (469/500) contained the true mean, reasonably close to the nominal 95%, with the modest shortfall plausibly reflecting range_pct's strong right skew still influencing t-interval performance at n = 40.
