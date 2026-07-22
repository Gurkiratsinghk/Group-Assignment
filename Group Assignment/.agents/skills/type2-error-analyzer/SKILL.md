---
name: type2-error-analyzer
description: Calculates Type II error probability (beta) and statistical power.
Skill: type2-error-analyzer
Description: Calculates Type II error probability (beta) and statistical power.
---
# Skill: type2-error-analyzer
# Description: Calculates Type II error probability (beta) and statistical power.

## Core Logic & Formulas:
1. Input baseline mean (mu0), hypothesized mean (mu1), sigma, sample size (n), and alpha.
2. For an upper-tailed test, calculate critical mean (x_crit) under H0:
   x_crit = mu0 + z_alpha * (sigma / sqrt(n))
3. Calculate z-value for critical mean under the alternative mean mu1:
   z = (x_crit - mu1) / (sigma / sqrt(n))
4. Compute beta = P(Z < z).
5. Compute Power of the Test = 1 - beta.
