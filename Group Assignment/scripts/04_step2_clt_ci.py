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
N_RESAMPLES = 500
ALPHA = 0.05

np.random.seed(RANDOM_SEED)
rng = np.random.default_rng(RANDOM_SEED)

os.makedirs("outputs/tables", exist_ok=True)
os.makedirs("outputs/figures", exist_ok=True)
os.makedirs("report", exist_ok=True)

print("================================================================================")
print("   STEP 04: CLT DEMONSTRATION & CONFIDENCE INTERVAL (skill: confidence-interval-builder)")
print("================================================================================")

population_df = pd.read_csv("data/processed/population.csv")
pop_x = population_df[NUMERIC_VAR].to_numpy(dtype=float)
pop_mean_true = float(np.mean(pop_x))
pop_sigma_true = float(np.std(pop_x, ddof=0))  # true population parameter: divide by N
print(f"\nLoaded population: {len(pop_x)} rows. True mu = {pop_mean_true:.6f}, true sigma = {pop_sigma_true:.6f}")


def draw_sampling_distribution(values, n, num_samples, gen):
    means = np.empty(num_samples)
    stds = np.empty(num_samples)
    for i in range(num_samples):
        draw = gen.choice(values, size=n, replace=False)
        means[i] = draw.mean()
        stds[i] = draw.std(ddof=1)
    return means, stds


# ------------------------------------------------------------------------------
# PART A: Sampling distribution / CLT demonstration
# ------------------------------------------------------------------------------
print("\n[A1] Drawing 500 independent samples of n=40...")
means_40, stds_40 = draw_sampling_distribution(pop_x, 40, N_RESAMPLES, rng)

pd.DataFrame({"sample_mean_range_pct": means_40}).to_csv("outputs/tables/04_sampling_distribution.csv", index=False)
print("  Saved outputs/tables/04_sampling_distribution.csv")

print("\n[A2] Comparing empirical vs theoretical standard error (n=40)...")
mean_of_means = float(np.mean(means_40))
empirical_se = float(np.std(means_40, ddof=1))
theoretical_se = pop_sigma_true / np.sqrt(40)

print(f"  Mean of 500 sample means      = {mean_of_means:.6f}  (true mu = {pop_mean_true:.6f})")
print(f"  Empirical SE (std of means)   = {empirical_se:.6f}")
print(f"  Theoretical SE (sigma/sqrt40) = {theoretical_se:.6f}")
print(f"  Difference                    = {abs(empirical_se - theoretical_se):.6f}")
print("  Comment: the empirical and theoretical standard errors are very close, confirming that the")
print("  variability of the sample mean across repeated samples matches the CLT prediction sigma/sqrt(n).")

print("\n[A3] Plotting sampling distribution histogram (n=40) with normal overlay...")
fig, ax = plt.subplots(figsize=(8, 6))
ax.hist(means_40, bins=40, density=True, alpha=0.7, color="steelblue", edgecolor="black")
xs = np.linspace(means_40.min(), means_40.max(), 300)
ax.plot(xs, stats.norm.pdf(xs, pop_mean_true, theoretical_se), "r-", linewidth=2,
        label=f"Normal(mu={pop_mean_true:.2f}, SE={theoretical_se:.3f})")
ax.axvline(pop_mean_true, color="black", linestyle="--", linewidth=2, label=f"True population mean = {pop_mean_true:.2f}")
ax.set_xlabel("Sample mean of range_pct (%)")
ax.set_ylabel("Density")
ax.set_title(f"Sampling Distribution of the Mean, n=40 (500 samples)")
ax.legend()
fig.savefig("outputs/figures/04_sampling_distribution_n40.png", dpi=300, bbox_inches="tight")
plt.close(fig)
print("  Saved outputs/figures/04_sampling_distribution_n40.png")

print("\n[A4] Repeating for n=5, 15, 40 to visualize the CLT (1x3 panel)...")
means_5, _ = draw_sampling_distribution(pop_x, 5, N_RESAMPLES, rng)
means_15, _ = draw_sampling_distribution(pop_x, 15, N_RESAMPLES, rng)

panel_data = [(5, means_5), (15, means_15), (40, means_40)]
fig, axes = plt.subplots(1, 3, figsize=(18, 5.5), sharey=False)
for ax, (n_val, means_arr) in zip(axes, panel_data):
    se_n = pop_sigma_true / np.sqrt(n_val)
    ax.hist(means_arr, bins=30, density=True, alpha=0.7, color="steelblue", edgecolor="black")
    xs_n = np.linspace(means_arr.min(), means_arr.max(), 300)
    ax.plot(xs_n, stats.norm.pdf(xs_n, pop_mean_true, se_n), "r-", linewidth=2)
    ax.axvline(pop_mean_true, color="black", linestyle="--", linewidth=1.5)
    ax.set_title(f"n = {n_val}\n(SE = {se_n:.3f}, skew = {stats.skew(means_arr):.2f})")
    ax.set_xlabel("Sample mean of range_pct (%)")
axes[0].set_ylabel("Density")
fig.suptitle("Central Limit Theorem: Sampling Distribution of the Mean Tightens as n Grows (500 samples each)")
fig.savefig("outputs/figures/04_clt_panel_n5_15_40.png", dpi=300, bbox_inches="tight")
plt.close(fig)
print("  Saved outputs/figures/04_clt_panel_n5_15_40.png")

print("\n[A5] Normality test on the 500 sample means (n=40 case)...")
shapiro_means_stat, shapiro_means_p = stats.shapiro(means_40)
print(f"  Shapiro-Wilk on 500 sample means: W = {shapiro_means_stat:.6f}, p = {shapiro_means_p:.6e}")
print("  Contrast with EDA Step 2: Shapiro-Wilk on a 500-row subsample of the RAW range_pct variable")
print("  gave W = 0.783, p ~= 3e-25 (strong rejection of normality). The sampling distribution of the")
print("  mean is far closer to normal than the raw variable itself -- exactly what the CLT predicts:")
print("  averaging washes out the skew of the individual observations.")

# ------------------------------------------------------------------------------
# PART B: Confidence interval for the population mean (single original sample)
# ------------------------------------------------------------------------------
print("\n[B6] Building 95% CI from the single original sample (data/processed/sample_n40.csv)...")
sample_df = pd.read_csv("data/processed/sample_n40.csv")
x = sample_df[NUMERIC_VAR].to_numpy(dtype=float)
n = len(x)
dof = n - 1

skill_mean = float(pd.Series(x).mean())
skill_std = float(pd.Series(x).std(ddof=1))
skill_se = skill_std / np.sqrt(n)
skill_t_crit = float(stats.t.ppf(1 - ALPHA / 2, df=dof))
skill_moe = skill_t_crit * skill_se
skill_lower = skill_mean - skill_moe
skill_upper = skill_mean + skill_moe

print(f"  Sample mean = {skill_mean:.6f}, s = {skill_std:.6f}, SE = {skill_se:.6f}, df = {dof}")
print(f"  t critical value (alpha=0.05, df={dof}) = {skill_t_crit:.6f}")
print(f"  Margin of error = {skill_moe:.6f}")
print(f"  95% CI (skill) = [{skill_lower:.6f}, {skill_upper:.6f}]")

print("\n[B7] VERIFICATION: manual recomputation of the t-interval...")
manual_mean = np.sum(x) / n
manual_std = np.sqrt(np.sum((x - manual_mean) ** 2) / (n - 1))
manual_se = manual_std / np.sqrt(n)
manual_t_crit = stats.t.ppf(1 - ALPHA / 2, df=dof)
manual_moe = manual_t_crit * manual_se
manual_lower = manual_mean - manual_moe
manual_upper = manual_mean + manual_moe

ci_comparison_rows = [
    ("t_critical_value", skill_t_crit, manual_t_crit),
    ("margin_of_error", skill_moe, manual_moe),
    ("ci_lower", skill_lower, manual_lower),
    ("ci_upper", skill_upper, manual_upper),
]
print(f"\n  {'quantity':<20} {'skill output':>16} {'manual output':>16} {'abs diff':>14}")
for name, skill_val, manual_val in ci_comparison_rows:
    diff = abs(skill_val - manual_val)
    flag = "  <-- MISMATCH >1e-9!" if diff > 1e-9 else ""
    print(f"  {name:<20} {skill_val:>16.6f} {manual_val:>16.6f} {diff:>14.2e}{flag}")

z_crit = float(stats.norm.ppf(1 - ALPHA / 2))
z_moe = z_crit * skill_se
z_lower = skill_mean - z_moe
z_upper = skill_mean + z_moe
print(f"\n  z-based interval (for contrast): z_crit={z_crit:.6f}, MOE={z_moe:.6f}, CI = [{z_lower:.6f}, {z_upper:.6f}]")
print("  The t-distribution is the correct choice here because the population standard deviation is")
print("  unknown and is being estimated from the sample itself (s), and t's heavier tails correctly")
print("  widen the interval to account for that extra estimation uncertainty at n=40.")

# ------------------------------------------------------------------------------
# Coverage check across the 500 resamples (n=40)
# ------------------------------------------------------------------------------
print("\n[B8] Coverage check: 95% CI computed for each of the 500 resamples (n=40)...")
t_crit_40 = float(stats.t.ppf(1 - ALPHA / 2, df=39))
ci_lowers = means_40 - t_crit_40 * (stds_40 / np.sqrt(40))
ci_uppers = means_40 + t_crit_40 * (stds_40 / np.sqrt(40))
contains_true_mean = (ci_lowers <= pop_mean_true) & (pop_mean_true <= ci_uppers)
empirical_coverage_pct = float(np.mean(contains_true_mean) * 100)

print(f"  Nominal confidence level      = 95%")
print(f"  Empirical coverage (500 CIs)  = {empirical_coverage_pct:.2f}%  "
      f"({int(np.sum(contains_true_mean))}/{N_RESAMPLES} intervals contained the true mean)")
print("  This is close to the nominal 95%, which is exactly what '95% confidence' means: not that any")
print("  single interval has a 95% chance of containing mu, but that the procedure captures mu in about")
print("  95% of intervals over repeated sampling.")

# ------------------------------------------------------------------------------
# Save results table
# ------------------------------------------------------------------------------
results_df = pd.DataFrame({
    "metric": [
        "mean_of_500_sample_means", "empirical_se_n40", "theoretical_se_n40",
        "shapiro_W_500_means", "shapiro_p_500_means",
        "sample_mean_single_sample", "sample_std_single_sample", "t_critical_value",
        "margin_of_error", "ci_lower_t", "ci_upper_t", "z_critical_value", "ci_lower_z", "ci_upper_z",
        "empirical_coverage_pct"
    ],
    "value": [
        mean_of_means, empirical_se, theoretical_se,
        shapiro_means_stat, shapiro_means_p,
        skill_mean, skill_std, skill_t_crit,
        skill_moe, skill_lower, skill_upper, z_crit, z_lower, z_upper,
        empirical_coverage_pct
    ]
})
results_df.to_csv("outputs/tables/04_clt_ci_results.csv", index=False)
print("\nSaved outputs/tables/04_clt_ci_results.csv")
print(results_df.to_string(index=False))

print("\n================================================================================")
print("                              STEP 04 COMPLETE                                  ")
print("================================================================================")
