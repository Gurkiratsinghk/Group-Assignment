---
name: two-population-t-tester
description: Performs two-sample independent and paired t-tests.
---
# Skill: two-population-t-tester
# Description: Performs two-sample independent and paired t-tests.

## Core Logic & Formulas:
1. Input sample statistics for population 1 and 2 (n1, n2, mean1, mean2, s1, s2).
2. If independent samples, compute standard error:
   s_diff = sqrt( s1^2/n1 + s2^2/n2 )
3. Compute degrees of freedom (df) using Welch-Satterthwaite approximation.
4. Calculate t-statistic: t = (mean1 - mean2) / s_diff
5. Compare t against critical t or compute p-value to output reject/fail-to-reject H0.
