---
name: hypothesis-test-decision-maker
description: Evaluates hypothesis tests using p-value and critical value rules.
Skill: hypothesis-test-decision-maker
Description: Evaluates hypothesis tests using p-value and critical value rules.
---
# Skill: hypothesis-test-decision-maker
# Description: Evaluates hypothesis tests using p-value and critical value rules.

## Core Logic & Formulas:
1. Input test statistic value (z or t) and test type (one-tailed/two-tailed).
2. Input significance level (alpha).
3. Compute the p-value:
   - Upper-tailed: P(Z >= z)
   - Lower-tailed: P(Z <= z)
   - Two-tailed: 2 * P(Z >= |z|)
4. Apply Decision Rules:
   - Rule 1 (p-value): If p-value <= alpha, Reject H0. Else, Fail to Reject H0.
   - Rule 2 (critical value): If |z| >= z_crit, Reject H0. Else, Fail to Reject H0.
5. Output the formal decision and statistical explanation.
