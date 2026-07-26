import os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Rule 2: Set the random seed at the top of every script
RANDOM_SEED = 42
NUMERIC_VAR = "range_pct"
GROUP_VAR = "sector"
GROUP_A = "Technology"
BENCHMARK_VALUE = 2.0
ALPHA = 0.05
SAMPLE_SIZE_n = 40

np.random.seed(RANDOM_SEED)
rng = np.random.default_rng(RANDOM_SEED)

os.makedirs("data/processed", exist_ok=True)
os.makedirs("outputs/tables", exist_ok=True)
os.makedirs("outputs/figures", exist_ok=True)

print("================================================================================")
print("  STEP 07: HYPOTHESIS TEST DECISION (skill: hypothesis-test-decision-maker)      ")
print("================================================================================")

population_df = pd.read_csv("data/processed/population.csv")
it_pop_df = population_df[population_df[GROUP_VAR] == GROUP_A].reset_index(drop=True)
print(f"\nLoaded population: {len(population_df)} rows ({len(it_pop_df)} {GROUP_A} rows)")

# ------------------------------------------------------------------------------
# Draw the IT-sector sample, n = 40, seed = 42
# ------------------------------------------------------------------------------
print(f"\n[Setup] Drawing SRS without replacement, n={SAMPLE_SIZE_n}, seed={RANDOM_SEED}, from {GROUP_A} rows only...")

sample_indices = rng.choice(it_pop_df.index.values, size=SAMPLE_SIZE_n, replace=False)
sample_df = it_pop_df.loc[sample_indices].reset_index(drop=True)
sample_df.to_csv("data/processed/sample_it_n40.csv", index=False)
print(f"  Saved data/processed/sample_it_n40.csv ({len(sample_df)} rows)")

x = sample_df[NUMERIC_VAR].to_numpy(dtype=float)
n = len(x)
dof = n - 1
sample_mean = float(x.mean())
sample_std = float(x.std(ddof=1))
se = sample_std / np.sqrt(n)

print(f"  Sample mean = {sample_mean:.6f}, s = {sample_std:.6f}, SE = {se:.6f}, df = {dof}")

# ------------------------------------------------------------------------------
# H0: mu <= 2.0  vs  Ha: mu > 2.0  (upper-tailed test, per report/05_step3.md)
# ------------------------------------------------------------------------------
print(f"\nH0: mu <= {BENCHMARK_VALUE}   Ha: mu > {BENCHMARK_VALUE}   (one-tailed, upper tail)   alpha = {ALPHA}, df = {dof}")

# ------------------------------------------------------------------------------
# Approach 1: Critical value
# ------------------------------------------------------------------------------
print("\n[Approach 1] Critical value method...")

t_crit = float(stats.t.ppf(1 - ALPHA, df=dof))
t_obs = (sample_mean - BENCHMARK_VALUE) / se

print(f"  alpha = {ALPHA}, df = {dof}")
print(f"  Critical t value (upper tail): t_crit = {t_crit:.6f}")
print(f"  Observed test statistic: t = (x-bar - mu0) / (s/sqrt(n)) = ({sample_mean:.6f} - {BENCHMARK_VALUE}) / {se:.6f} = {t_obs:.6f}")
print(f"  Rejection region: reject H0 if t >= {t_crit:.6f}")
decision_cv = "REJECT H0" if t_obs >= t_crit else "FAIL TO REJECT H0"
print(f"  Decision: t = {t_obs:.6f} {'>=' if t_obs >= t_crit else '<'} t_crit = {t_crit:.6f}  ->  {decision_cv}")

x_crit = BENCHMARK_VALUE + t_crit * se
print(f"  Critical value in original units (critical sample mean): x_crit = mu0 + t_crit*SE = {x_crit:.6f}%")
print(f"  Manager-actionable version: if the sample mean range_pct exceeds {x_crit:.4f}%, reject the 2.0% assumption at alpha={ALPHA}.")

# ------------------------------------------------------------------------------
# Approach 2: p-value
# ------------------------------------------------------------------------------
print("\n[Approach 2] p-value method...")

p_value = float(stats.t.sf(t_obs, df=dof))
print(f"  One-tailed p-value = P(T >= {t_obs:.6f} | df={dof}) = {p_value:.6f}")
decision_pv = "REJECT H0" if p_value <= ALPHA else "FAIL TO REJECT H0"
print(f"  Decision: p = {p_value:.6f} {'<=' if p_value <= ALPHA else '>'} alpha = {ALPHA}  ->  {decision_pv}")
print(f"  Meaning: p = {p_value:.4f} is the probability of observing a sample mean at least this far above")
print(f"  2.0% IF H0 (mu<=2.0) were true. It is NOT the probability that H0 is true, and it is NOT the")
print(f"  probability that the 2.0% assumption is correct.")

# ------------------------------------------------------------------------------
# 1: Side-by-side decision table
# ------------------------------------------------------------------------------
print("\n[1] Side-by-side decision table...")

decision_table = pd.DataFrame([
    {"approach": "Critical value", "statistic": t_obs, "threshold": t_crit, "comparison": f"t {'>=' if t_obs>=t_crit else '<'} t_crit", "decision": decision_cv},
    {"approach": "p-value", "statistic": p_value, "threshold": ALPHA, "comparison": f"p {'<=' if p_value<=ALPHA else '>'} alpha", "decision": decision_pv},
])
print(decision_table.to_string(index=False))
print("\n  Both approaches reach the SAME decision because they are two readings of the identical")
print("  t-distribution: the critical-value method asks 'is my observed statistic past the threshold")
print("  statistic that corresponds to alpha', while the p-value method asks 'is the tail area beyond")
print("  my observed statistic smaller than alpha' -- t >= t_crit and P(T>=t) <= alpha are algebraically")
print("  the same statement, just expressed on the statistic axis versus the probability axis.")

# ------------------------------------------------------------------------------
# 2: Figure - t-distribution with rejection region, critical value, observed t, p-value area
# ------------------------------------------------------------------------------
print("\n[2] Plotting t-distribution with rejection region and p-value area...")

t_range = np.linspace(-4.5, 4.5, 1000)
t_pdf = stats.t.pdf(t_range, df=dof)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(t_range, t_pdf, color="black", linewidth=1.5, label=f"t-distribution (df={dof})")

reject_x = t_range[t_range >= t_crit]
ax.fill_between(reject_x, stats.t.pdf(reject_x, df=dof), color="red", alpha=0.3, label=f"Rejection region (alpha={ALPHA})")

pval_x = t_range[t_range >= t_obs]
ax.fill_between(pval_x, stats.t.pdf(pval_x, df=dof), color="orange", alpha=0.4, label=f"p-value area (p={p_value:.4f})")

ax.axvline(t_crit, color="red", linestyle="--", linewidth=2, label=f"t_crit = {t_crit:.3f}")
ax.axvline(t_obs, color="blue", linestyle="-", linewidth=2, label=f"observed t = {t_obs:.3f}")

ax.set_xlabel("t value")
ax.set_ylabel("Density")
ax.set_title(f"One-Tailed t-Test: Rejection Region vs p-Value Area (n={n}, df={dof})")
ax.legend()
fig.savefig("outputs/figures/07_ttest_rejection_pvalue.png", dpi=300, bbox_inches="tight")
plt.close(fig)
print("  Saved outputs/figures/07_ttest_rejection_pvalue.png")

# ------------------------------------------------------------------------------
# 3: Robustness check - Wilcoxon signed-rank test
# ------------------------------------------------------------------------------
print("\n[3] Robustness check: Wilcoxon signed-rank test (same sample, same benchmark)...")

wilcoxon_stat, wilcoxon_p_two_sided = stats.wilcoxon(x - BENCHMARK_VALUE, alternative="greater")
wilcoxon_decision = "REJECT H0" if wilcoxon_p_two_sided <= ALPHA else "FAIL TO REJECT H0"
print(f"  Wilcoxon signed-rank (one-tailed, alternative='greater'): W = {wilcoxon_stat:.6f}, p = {wilcoxon_p_two_sided:.6f}")
print(f"  Decision: p = {wilcoxon_p_two_sided:.6f} {'<=' if wilcoxon_p_two_sided<=ALPHA else '>'} alpha = {ALPHA}  ->  {wilcoxon_decision}")
if wilcoxon_decision == decision_pv:
    print(f"  Conclusion UNCHANGED: the non-parametric robustness check agrees with the t-test decision.")
else:
    print(f"  Conclusion CHANGES between the t-test and the Wilcoxon test -- flag for closer inspection.")

# ------------------------------------------------------------------------------
# 4: VERIFICATION - manual cross-check of scipy t-statistic and p-value
# ------------------------------------------------------------------------------
print("\n[4] VERIFICATION: manual cross-check via scipy.stats.t.sf / .ppf only...")

scipy_t_stat, scipy_p_two_sided = stats.ttest_1samp(x, popmean=BENCHMARK_VALUE, alternative="greater")
manual_t_stat = (np.sum(x) / n - BENCHMARK_VALUE) / (np.sqrt(np.sum((x - np.sum(x) / n) ** 2) / (n - 1)) / np.sqrt(n))
manual_p = float(stats.t.sf(manual_t_stat, df=dof))

print(f"  scipy.stats.ttest_1samp(alternative='greater'): t = {scipy_t_stat:.6f}, p = {scipy_p_two_sided:.6f}")
print(f"  Manual (explicit sum/(n-1) arithmetic + t.sf):   t = {manual_t_stat:.6f}, p = {manual_p:.6f}")
diff_t = abs(scipy_t_stat - manual_t_stat)
diff_p = abs(scipy_p_two_sided - manual_p)
flag_t = "  <-- MISMATCH >1e-9!" if diff_t > 1e-9 else ""
flag_p = "  <-- MISMATCH >1e-9!" if diff_p > 1e-9 else ""
print(f"  Diff (t): {diff_t:.2e}{flag_t}   Diff (p): {diff_p:.2e}{flag_p}")
print(f"  Tail direction used: UPPER tail (t.sf = P(T >= t), i.e. survival function), because Ha: mu > 2.0")
print(f"  requires the area to the RIGHT of the observed statistic, not the two-tailed value")
print(f"  (2*t.sf(|t|)) and not the lower tail (t.cdf).")

# ------------------------------------------------------------------------------
# Save results table (audit fix: this script previously saved no output table at all --
# every number in report/07_step5.md existed only as console output, violating Rule 1)
# ------------------------------------------------------------------------------
results_df = pd.DataFrame({
    "metric": [
        "n", "df", "sample_mean", "sample_std", "se", "t_crit", "t_observed",
        "critical_sample_mean_x_crit", "p_value", "decision",
        "wilcoxon_stat", "wilcoxon_p", "wilcoxon_decision"
    ],
    "value": [
        n, dof, sample_mean, sample_std, se, t_crit, t_obs,
        x_crit, p_value, decision_pv,
        wilcoxon_stat, wilcoxon_p_two_sided, wilcoxon_decision
    ]
})
results_df.to_csv("outputs/tables/07_hypothesis_test_results.csv", index=False)
print("\nSaved outputs/tables/07_hypothesis_test_results.csv")

print("\n================================================================================")
print("                              STEP 07 COMPLETE                                  ")
print("================================================================================")
