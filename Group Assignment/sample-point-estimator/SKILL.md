---
name: sample-point-estimator
description: Selects random samples and computes point estimates.
---
# Skill: sample-point-estimator
# Description: Selects random samples and computes point estimates.

## Core Logic & Formulas:
1. Parse the population array of numerical data.
2. Select a random sample of size n.
3. Compute point estimates:
   - Sample Mean (x_bar) = Sum(x_i) / n
   - Sample Standard Deviation (s) = sqrt( Sum(x_i - x_bar)^2 / (n-1) )
   - Sample Proportion (p_bar) = x / n (for binary categories)
4. Calculate standard errors:
   - Standard Error of Mean: s_x_bar = s / sqrt(n)
   - Standard Error of Proportion: s_p_bar = sqrt( p_bar * (1 - p_bar) / n )
