import os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Rule 2: Set the random seed at the top of every script
RANDOM_SEED = 42
GROUP_VAR = "sector"
GROUP_A = "Technology"
GROUP_B = "Consumer Staples"
NUMERIC_VAR = "range_pct"
PAIR_VAR_1 = "abs_overnight_gap_pct"
PAIR_VAR_2 = "abs_intraday_move_pct"
BENCHMARK_VALUE = 2.0
ALPHA = 0.05
SAMPLE_SIZE_n = 40

np.random.seed(RANDOM_SEED)
rng = np.random.default_rng(RANDOM_SEED)

os.makedirs("data/processed", exist_ok=True)
os.makedirs("outputs/tables", exist_ok=True)
os.makedirs("outputs/figures", exist_ok=True)

print("================================================================================")
print("        STEP 08: THREE t-TESTS (skill: two-population-t-tester, extended)       ")
print("================================================================================")

population_df = pd.read_csv("data/processed/population.csv")
print(f"\nLoaded population: {len(population_df)} rows")

consolidated_rows = []


def print_verify(label, skill_val, manual_val):
    diff = abs(skill_val - manual_val)
    flag = "  <-- MISMATCH >1e-9!" if diff > 1e-9 else ""
    print(f"    {label:<28} skill={skill_val:>14.6f}  manual={manual_val:>14.6f}  diff={diff:>10.2e}{flag}")


# ================================================================================
# TEST A: One-sample t-test (reproduces Step 5 exactly)
# ================================================================================
print("\n================================ TEST A: ONE-SAMPLE t-TEST ================================")
print("Variable: range_pct, IT-sector sample n=40, benchmark=2.0, one-tailed (upper), alpha=0.05.")
print("This is the SAME test as Step 5 (report/07_step5.md) -- reproduced here in standard format")
print("so this step stands alone. Reusing the exact sample saved at data/processed/sample_it_n40.csv.")

sample_a = pd.read_csv("data/processed/sample_it_n40.csv")
xa = sample_a[NUMERIC_VAR].to_numpy(dtype=float)
na = len(xa)
dof_a = na - 1
mean_a = float(xa.mean())
std_a = float(xa.std(ddof=1))
se_a = std_a / np.sqrt(na)

t_a_skill, p_a_skill = stats.ttest_1samp(xa, popmean=BENCHMARK_VALUE, alternative="greater")
manual_mean_a = np.sum(xa) / na
manual_std_a = np.sqrt(np.sum((xa - manual_mean_a) ** 2) / (na - 1))
manual_t_a = (manual_mean_a - BENCHMARK_VALUE) / (manual_std_a / np.sqrt(na))
manual_p_a = float(stats.t.sf(manual_t_a, df=dof_a))

t_crit_a = float(stats.t.ppf(1 - ALPHA, df=dof_a))
decision_a = "REJECT H0" if t_a_skill >= t_crit_a else "FAIL TO REJECT H0"

ci_t_a = float(stats.t.ppf(1 - ALPHA / 2, df=dof_a))
ci_a_lower = mean_a - ci_t_a * se_a
ci_a_upper = mean_a + ci_t_a * se_a

print(f"  n={na}, mean={mean_a:.6f}, s={std_a:.6f}, SE={se_a:.6f}, df={dof_a}")
print(f"  t={t_a_skill:.6f}, t_crit={t_crit_a:.6f}, p={p_a_skill:.6f}  ->  {decision_a}")
print(f"  95% CI for mean = [{ci_a_lower:.6f}, {ci_a_upper:.6f}]")
print("  VERIFICATION (skill vs manual):")
print_verify("t statistic", t_a_skill, manual_t_a)
print_verify("p-value", p_a_skill, manual_p_a)
print("  Assumptions: (1) independence -- questionable (volatility clustering, shared USD/INR & Nasdaq")
print("  driver across IT names; see report/05_step3.md); (2) ratio-scale data -- holds; (3) approx.")
print("  normality of the sampling distribution of the mean -- reasonably supported by the CLT at n=40")
print("  (see Step 2 findings), despite strong skew in the raw variable.")

consolidated_rows.append({
    "test": "A: One-sample t-test", "H0": "mu <= 2.0", "Ha": "mu > 2.0", "n": na,
    "statistic": t_a_skill, "df": dof_a, "p_value": p_a_skill, "decision": decision_a,
    "effect_size": (mean_a - BENCHMARK_VALUE) / std_a, "ci_95": f"[{ci_a_lower:.4f}, {ci_a_upper:.4f}]"
})

# ================================================================================
# TEST B: Two-independent-sample t-test (Technology vs Consumer Staples)
# ================================================================================
print("\n============================ TEST B: TWO-INDEPENDENT-SAMPLE t-TEST ============================")
print(f"Variable: range_pct. Groups: {GROUP_A} vs {GROUP_B}. n=40 each. Two-tailed, alpha=0.05.")

it_pop = population_df[population_df[GROUP_VAR] == GROUP_A].reset_index(drop=True)
fmcg_pop = population_df[population_df[GROUP_VAR] == GROUP_B].reset_index(drop=True)

# Audit fix: FMCG is drawn FIRST here so the IT draw is not the first call from a freshly
# seeded rng(42) -- drawing IT first would exactly reproduce Step 5/07's sample_it_n40.csv
# (same seed, same filter, same first-call rng.choice), silently making Test A and Test B's
# IT arm the same 40 rows instead of independent evidence. See report/10_audit.md finding.
idx_fmcg_b = rng.choice(fmcg_pop.index.values, size=SAMPLE_SIZE_n, replace=False)
sample_fmcg_b = fmcg_pop.loc[idx_fmcg_b].reset_index(drop=True)
sample_fmcg_b.to_csv("data/processed/sample_testB_fmcg_n40.csv", index=False)

idx_it_b = rng.choice(it_pop.index.values, size=SAMPLE_SIZE_n, replace=False)
sample_it_b = it_pop.loc[idx_it_b].reset_index(drop=True)
sample_it_b.to_csv("data/processed/sample_testB_it_n40.csv", index=False)
print("  Saved data/processed/sample_testB_fmcg_n40.csv and data/processed/sample_testB_it_n40.csv")

xb1 = sample_it_b[NUMERIC_VAR].to_numpy(dtype=float)
xb2 = sample_fmcg_b[NUMERIC_VAR].to_numpy(dtype=float)
n1, n2 = len(xb1), len(xb2)
mean1, mean2 = float(xb1.mean()), float(xb2.mean())
std1, std2 = float(xb1.std(ddof=1)), float(xb2.std(ddof=1))
mean_diff = mean1 - mean2

levene_stat, levene_p = stats.levene(xb1, xb2, center="median")
print(f"\n  Levene's test for equal variances: W={levene_stat:.6f}, p={levene_p:.6f}")
use_welch = levene_p <= ALPHA
print(f"  {'REJECT' if use_welch else 'FAIL TO REJECT'} equal variances at alpha={ALPHA} "
      f"-> {'Welch (unequal variance)' if use_welch else 'pooled (equal variance)'} t-test is the adopted approach.")

t_pooled, p_pooled = stats.ttest_ind(xb1, xb2, equal_var=True)
t_welch, p_welch = stats.ttest_ind(xb1, xb2, equal_var=False)
dof_pooled = n1 + n2 - 2
dof_welch = ((std1 ** 2 / n1 + std2 ** 2 / n2) ** 2) / (
    ((std1 ** 2 / n1) ** 2) / (n1 - 1) + ((std2 ** 2 / n2) ** 2) / (n2 - 1)
)

print(f"\n  Pooled t-test (equal_var=True):  t={t_pooled:.6f}, df={dof_pooled}, p={p_pooled:.6f}")
print(f"  Welch t-test  (equal_var=False): t={t_welch:.6f}, df={dof_welch:.4f}, p={p_welch:.6f}")

adopted_t, adopted_p, adopted_dof = (t_welch, p_welch, dof_welch) if use_welch else (t_pooled, p_pooled, dof_pooled)
decision_b = "REJECT H0" if adopted_p <= ALPHA else "FAIL TO REJECT H0"
print(f"  Adopted result: t={adopted_t:.6f}, df={adopted_dof:.4f}, p={adopted_p:.6f}  ->  {decision_b}")

pooled_sd = np.sqrt(((n1 - 1) * std1 ** 2 + (n2 - 1) * std2 ** 2) / (n1 + n2 - 2))
cohens_d_b = mean_diff / pooled_sd

se_welch = np.sqrt(std1 ** 2 / n1 + std2 ** 2 / n2)
t_crit_welch = float(stats.t.ppf(1 - ALPHA / 2, df=dof_welch))
ci_b_lower = mean_diff - t_crit_welch * se_welch
ci_b_upper = mean_diff + t_crit_welch * se_welch

print(f"\n  Group means: {GROUP_A}={mean1:.6f} (s={std1:.6f}), {GROUP_B}={mean2:.6f} (s={std2:.6f})")
print(f"  Mean difference ({GROUP_A} - {GROUP_B}) = {mean_diff:.6f}")
print(f"  95% CI for mean difference (Welch) = [{ci_b_lower:.6f}, {ci_b_upper:.6f}]")
print(f"  Cohen's d = {cohens_d_b:.6f}")

print("\n  VERIFICATION (skill vs manual, adopted test):")
manual_se_welch = np.sqrt(std1 ** 2 / n1 + std2 ** 2 / n2)
manual_t_welch = mean_diff / manual_se_welch
manual_se_pooled = pooled_sd * np.sqrt(1 / n1 + 1 / n2)
manual_t_pooled = mean_diff / manual_se_pooled
if use_welch:
    print_verify("t statistic (Welch)", t_welch, manual_t_welch)
else:
    print_verify("t statistic (pooled)", t_pooled, manual_t_pooled)

mwu_stat, mwu_p = stats.mannwhitneyu(xb1, xb2, alternative="two-sided")
mwu_decision = "REJECT H0" if mwu_p <= ALPHA else "FAIL TO REJECT H0"
print(f"\n  Robustness -- Mann-Whitney U: U={mwu_stat:.6f}, p={mwu_p:.6f}  ->  {mwu_decision}")
print(f"  Conclusion {'UNCHANGED' if mwu_decision == decision_b else 'CHANGES'} vs the adopted t-test.")

# Audit fix: Levene stat/p and raw group means/stds were previously printed but never saved
# to any output table -- only the adopted test's summary row made it into 08_ttest_results.csv.
group_stats_b_df = pd.DataFrame([{
    "group": GROUP_A, "n": n1, "mean": mean1, "std": std1,
    "levene_stat": levene_stat, "levene_p": levene_p, "adopted_test": "Welch" if use_welch else "pooled"
}, {
    "group": GROUP_B, "n": n2, "mean": mean2, "std": std2,
    "levene_stat": levene_stat, "levene_p": levene_p, "adopted_test": "Welch" if use_welch else "pooled"
}])
group_stats_b_df.to_csv("outputs/tables/08_testB_group_stats.csv", index=False)
print("  Saved outputs/tables/08_testB_group_stats.csv")

print("  Assumptions: (1) independence between and within groups -- between-sector independence is")
print("  reasonable (different tickers/business drivers), within-sector independence is weaker (shared")
print("  sector-level shocks); (2) ratio-scale data -- holds; (3) approx. normal sampling distributions")
print("  of each group mean -- supported by CLT at n=40 per Step 2, despite skewed raw data; (4) equal")
print(f"  variances -- {'violated' if use_welch else 'holds'} per Levene, hence the {'Welch' if use_welch else 'pooled'} test.")

consolidated_rows.append({
    "test": f"B: Two-sample t-test ({'Welch' if use_welch else 'pooled'})",
    "H0": "mu_IT = mu_FMCG", "Ha": "mu_IT != mu_FMCG", "n": f"{n1}+{n2}",
    "statistic": adopted_t, "df": round(adopted_dof, 2), "p_value": adopted_p, "decision": decision_b,
    "effect_size": cohens_d_b, "ci_95": f"[{ci_b_lower:.4f}, {ci_b_upper:.4f}]"
})

# ================================================================================
# TEST C: Paired t-test (overnight gap vs intraday move, same ticker-day)
# ================================================================================
print("\n================================ TEST C: PAIRED t-TEST ================================")
print(f"Variable pair: {PAIR_VAR_1} vs {PAIR_VAR_2}, n=40 ticker-days. Two-tailed, alpha=0.05.")
print("Genuinely paired because both measurements come from the SAME ticker-day session: treating")
print("them as independent samples would discard the within-day correlation between overnight and")
print("intraday risk and inflate the standard error, weakening the test's ability to detect a real")
print("difference.")

idx_c = rng.choice(population_df.index.values, size=SAMPLE_SIZE_n, replace=False)
sample_c = population_df.loc[idx_c].reset_index(drop=True)
sample_c.to_csv("data/processed/sample_testC_paired_n40.csv", index=False)
print("  Saved data/processed/sample_testC_paired_n40.csv")

xc1 = sample_c[PAIR_VAR_1].to_numpy(dtype=float)
xc2 = sample_c[PAIR_VAR_2].to_numpy(dtype=float)
nc = len(xc1)
dof_c = nc - 1
diff = xc1 - xc2
mean_c1, mean_c2 = float(xc1.mean()), float(xc2.mean())
mean_diff_c = float(diff.mean())
std_diff_c = float(diff.std(ddof=1))
se_diff_c = std_diff_c / np.sqrt(nc)

t_paired_skill, p_paired_skill = stats.ttest_rel(xc1, xc2)
t_onesample_skill, p_onesample_skill = stats.ttest_1samp(diff, popmean=0)

print(f"\n  Mean {PAIR_VAR_1} = {mean_c1:.6f}, Mean {PAIR_VAR_2} = {mean_c2:.6f}")
print(f"  Mean difference = {mean_diff_c:.6f}, s(diff) = {std_diff_c:.6f}, SE(diff) = {se_diff_c:.6f}, df={dof_c}")
print(f"  Paired t-test (scipy.stats.ttest_rel):        t={t_paired_skill:.6f}, p={p_paired_skill:.6f}")
print(f"  One-sample t-test on diff column (equivalence): t={t_onesample_skill:.6f}, p={p_onesample_skill:.6f}")
print_verify("t statistic (paired == 1-sample)", t_paired_skill, t_onesample_skill)
print_verify("p-value (paired == 1-sample)", p_paired_skill, p_onesample_skill)

decision_c = "REJECT H0" if p_paired_skill <= ALPHA else "FAIL TO REJECT H0"
t_crit_c = float(stats.t.ppf(1 - ALPHA / 2, df=dof_c))
ci_c_lower = mean_diff_c - t_crit_c * se_diff_c
ci_c_upper = mean_diff_c + t_crit_c * se_diff_c
cohens_d_c = mean_diff_c / std_diff_c

print(f"  Decision: p={p_paired_skill:.6f}  ->  {decision_c}")
print(f"  95% CI for mean difference = [{ci_c_lower:.6f}, {ci_c_upper:.6f}]")
print(f"  Cohen's d (paired) = mean_diff / s_diff = {cohens_d_c:.6f}")

manual_mean_diff = np.sum(diff) / nc
manual_std_diff = np.sqrt(np.sum((diff - manual_mean_diff) ** 2) / (nc - 1))
manual_t_c = manual_mean_diff / (manual_std_diff / np.sqrt(nc))
print("\n  VERIFICATION (skill vs manual arithmetic):")
print_verify("t statistic", t_paired_skill, manual_t_c)

wilcoxon_stat_c, wilcoxon_p_c = stats.wilcoxon(diff, alternative="two-sided")
wilcoxon_decision_c = "REJECT H0" if wilcoxon_p_c <= ALPHA else "FAIL TO REJECT H0"
print(f"\n  Robustness -- Wilcoxon signed-rank on differences: W={wilcoxon_stat_c:.6f}, p={wilcoxon_p_c:.6f}  ->  {wilcoxon_decision_c}")
print(f"  Conclusion {'UNCHANGED' if wilcoxon_decision_c == decision_c else 'CHANGES'} vs the paired t-test.")

print("  Assumptions: (1) independence of the DIFFERENCES across ticker-days -- weaker than i.i.d. for")
print("  the same reasons as Test A/B (volatility clustering); (2) ratio-scale differences -- holds;")
print("  (3) approx. normality of the sampling distribution of the mean difference -- reasonable at n=40")
print("  via CLT, though the differences inherit some right skew from both underlying variables.")

consolidated_rows.append({
    "test": "C: Paired t-test", "H0": "mu_diff = 0", "Ha": "mu_diff != 0", "n": nc,
    "statistic": t_paired_skill, "df": dof_c, "p_value": p_paired_skill, "decision": decision_c,
    "effect_size": cohens_d_c, "ci_95": f"[{ci_c_lower:.4f}, {ci_c_upper:.4f}]"
})

print("\n  Plotting paired slope plot and histogram of differences...")
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for i in range(nc):
    axes[0].plot([0, 1], [xc1[i], xc2[i]], color="gray", alpha=0.5, linewidth=1, marker="o", markersize=3)
axes[0].set_xticks([0, 1])
axes[0].set_xticklabels([PAIR_VAR_1, PAIR_VAR_2])
axes[0].set_ylabel("Value (%)")
axes[0].set_title(f"Paired Slope Plot (n={nc})")

axes[1].hist(diff, bins=20, color="steelblue", alpha=0.7, edgecolor="black")
axes[1].axvline(0, color="black", linestyle="--", linewidth=1.5, label="No difference")
axes[1].axvline(mean_diff_c, color="red", linestyle="-", linewidth=2, label=f"Mean diff = {mean_diff_c:.3f}")
axes[1].set_xlabel(f"{PAIR_VAR_1} - {PAIR_VAR_2} (%)")
axes[1].set_ylabel("Frequency")
axes[1].set_title(f"Histogram of Paired Differences (n={nc})")
axes[1].legend()

fig.savefig("outputs/figures/08_paired_slope_hist.png", dpi=300, bbox_inches="tight")
plt.close(fig)
print("  Saved outputs/figures/08_paired_slope_hist.png")

# ================================================================================
# Consolidated results table
# ================================================================================
print("\n================================ CONSOLIDATED RESULTS TABLE ================================")
consolidated_df = pd.DataFrame(consolidated_rows)
consolidated_df.to_csv("outputs/tables/08_ttest_results.csv", index=False)
print("Saved outputs/tables/08_ttest_results.csv")
print(consolidated_df.to_string(index=False))

print("\n================================================================================")
print("                              STEP 08 COMPLETE                                  ")
print("================================================================================")
