---
name: confidence-interval-builder
description: Automatically builds confidence intervals for means and proportions.
---
# Skill: confidence-interval-builder
# Description: Automatically builds confidence intervals for means and proportions.

## Core Logic & Formulas:
1. Input sample stats: n, mean, standard deviation (s or sigma), and confidence level (1-alpha).
2. If population standard deviation (sigma) is KNOWN:
   - Use Standard Normal z-distribution: z_alpha_2
   - Interval = mean +/- z_alpha_2 * (sigma / sqrt(n))
3. If population standard deviation is UNKNOWN:
   - Use Student's t-distribution: t_alpha_2 with df = n-1
   - Interval = mean +/- t_alpha_2 * (s / sqrt(n))
4. Output the margin of error and lower/upper confidence bounds.
