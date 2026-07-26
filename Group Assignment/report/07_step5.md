# Step 5: Hypothesis Test Decision — IT Basket Trading Range

Testing H0: μ ≤ 2.0% against Ha: μ > 2.0% at α = 0.05, on a fresh random sample of n = 40 IT-sector (Technology) sessions (seed 42, df = 39), gives a sample mean range_pct of 2.307% against the 2.0% benchmark.

**Critical value approach:** t_crit = 1.6849; observed t = 1.6670. Since 1.6670 < 1.6849, we **fail to reject H0**. In original units, the sample mean would have needed to exceed 2.3107% for rejection — ours came in just under that, at 2.307%.

**p-value approach:** the one-tailed p-value is 0.0518, marginally above α = 0.05, giving the identical decision: **fail to reject H0**. This p-value is the probability of observing a sample mean this far above 2.0% *if the 2.0% assumption were actually true* — it is not the probability that the assumption is true, and it should not be read as a 94.8% chance the desk's policy is correct.

Both methods agree, as they must: they are two views of the same t-distribution, one comparing statistics against a threshold statistic, the other comparing tail probability against α. A Wilcoxon signed-rank robustness check reaches the same conclusion (p = 0.1841, fail to reject), reinforcing that this result is not an artifact of the normality assumption.

**What the desk should take from this:** the data does not provide statistically significant evidence, at the 5% level, that the true average daily range exceeds 2.0%. However, this is a genuinely close call — the p-value of 0.052 sits just above the threshold, and the sample mean (2.307%) is well above 2.0% in absolute terms, missing significance mainly because n = 40 leaves considerable sampling uncertainty. The honest conclusion is not "the 2.0% assumption is confirmed," but "we lack sufficient evidence to overturn it yet, and this is close enough to warrant re-testing with a larger or more recent sample before treating the current stop-loss/margin policy as settled."
