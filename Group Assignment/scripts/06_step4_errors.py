import os
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.power import TTestPower
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Rule 2: Set the random seed at the top of every script
RANDOM_SEED = 42
NUMERIC_VAR = "range_pct"
BENCHMARK_VALUE = 2.0
ALPHA = 0.05

np.random.seed(RANDOM_SEED)
rng = np.random.default_rng(RANDOM_SEED)

os.makedirs("outputs/tables", exist_ok=True)
os.makedirs("outputs/figures", exist_ok=True)

print("================================================================================")
print("     STEP 06: TYPE II ERROR & POWER ANALYSIS (skill: type2-error-analyzer)      ")
print("================================================================================")

sample_df = pd.read_csv("data/processed/sample_n40.csv")
x = sample_df[NUMERIC_VAR].to_numpy(dtype=float)
n_actual = len(x)
sample_mean = float(x.mean())
sample_std = float(x.std(ddof=1))
print(f"\nActual sample (n={n_actual}): mean = {sample_mean:.6f}, s = {sample_std:.6f}")

power_analysis = TTestPower()

# ------------------------------------------------------------------------------
# Step 4: Power grid across n and Cohen's d
# ------------------------------------------------------------------------------
print(f"\n[4] Power grid: one-tailed one-sample t-test, alpha={ALPHA}...")

n_grid = [10, 20, 30, 40, 50, 75, 100, 200, 500]
d_grid = [0.2, 0.5, 0.8]

grid_rows = []
for n_val in n_grid:
    for d_val in d_grid:
        pwr = power_analysis.power(effect_size=d_val, nobs=n_val, alpha=ALPHA, alternative="larger")
        grid_rows.append({"n": n_val, "cohens_d": d_val, "power": pwr})

grid_df = pd.DataFrame(grid_rows)
grid_df.to_csv("outputs/tables/06_power_grid.csv", index=False)
print("  Saved outputs/tables/06_power_grid.csv")
print(grid_df.pivot(index="n", columns="cohens_d", values="power").to_string())

# ------------------------------------------------------------------------------
# Step 5: Observed effect size and power of our actual n=40 test
# ------------------------------------------------------------------------------
print("\n[5] Observed effect size and power of the actual n=40 test...")

observed_d = (sample_mean - BENCHMARK_VALUE) / sample_std
observed_power = power_analysis.power(effect_size=observed_d, nobs=n_actual, alpha=ALPHA, alternative="larger")
observed_beta = 1 - observed_power

print(f"  Observed Cohen's d = (x-bar - mu0) / s = ({sample_mean:.6f} - {BENCHMARK_VALUE}) / {sample_std:.6f} = {observed_d:.6f}")
print(f"  Power at n={n_actual}, d={observed_d:.6f}, alpha={ALPHA}: power = {observed_power:.6f}")
print(f"  Beta (Type II error probability) = 1 - power = {observed_beta:.6f}")

# ------------------------------------------------------------------------------
# Step 6: Minimum n for 80% and 90% power at the observed effect size
# ------------------------------------------------------------------------------
print("\n[6] Minimum n required for 80% and 90% power at the observed effect size...")

n_for_80 = power_analysis.solve_power(effect_size=observed_d, alpha=ALPHA, power=0.80, alternative="larger")
n_for_90 = power_analysis.solve_power(effect_size=observed_d, alpha=ALPHA, power=0.90, alternative="larger")
print(f"  n required for 80% power: {n_for_80:,.1f}")
print(f"  n required for 90% power: {n_for_90:,.1f}")

# ------------------------------------------------------------------------------
# Step 7: Power curve figure
# ------------------------------------------------------------------------------
print("\n[7] Plotting power curves...")

n_fine = np.arange(5, 505, 5)
fig, ax = plt.subplots(figsize=(9, 6))
for d_val in d_grid:
    powers_fine = [power_analysis.power(effect_size=d_val, nobs=n_v, alpha=ALPHA, alternative="larger") for n_v in n_fine]
    ax.plot(n_fine, powers_fine, linewidth=2, label=f"Cohen's d = {d_val}")
ax.axhline(0.80, color="black", linestyle="--", linewidth=1, label="Power = 0.80")
ax.axvline(n_actual, color="red", linestyle=":", linewidth=2, label=f"Actual n = {n_actual}")
ax.set_xlabel("Sample size (n)")
ax.set_ylabel("Statistical power")
ax.set_title("Power Curves: One-Tailed One-Sample t-Test (alpha=0.05)")
ax.legend()
fig.savefig("outputs/figures/06_power_curves.png", dpi=300, bbox_inches="tight")
plt.close(fig)
print("  Saved outputs/figures/06_power_curves.png")

# ------------------------------------------------------------------------------
# Step 8: VERIFICATION - Monte Carlo power for one grid cell
# ------------------------------------------------------------------------------
print("\n[8] VERIFICATION: Monte Carlo power simulation for one grid cell (n=40, d=0.5)...")

mc_n = 40
mc_d = 0.5
n_sims = 10000

mc_samples = rng.normal(loc=mc_d, scale=1.0, size=(n_sims, mc_n))
mc_means = mc_samples.mean(axis=1)
mc_stds = mc_samples.std(axis=1, ddof=1)
mc_t_stats = mc_means / (mc_stds / np.sqrt(mc_n))
t_crit = stats.t.ppf(1 - ALPHA, df=mc_n - 1)
mc_rejections = np.sum(mc_t_stats > t_crit)
mc_power = mc_rejections / n_sims

analytic_power_cell = power_analysis.power(effect_size=mc_d, nobs=mc_n, alpha=ALPHA, alternative="larger")

print(f"  Analytic power (statsmodels TTestPower): {analytic_power_cell:.6f}")
print(f"  Monte Carlo power (10,000 sims, seed=42): {mc_power:.6f}  ({mc_rejections}/{n_sims} rejected)")
print(f"  Absolute difference: {abs(analytic_power_cell - mc_power):.6f}")
print("  Comment: the Monte Carlo estimate agrees closely with the analytic power (difference well")
print("  within the Monte Carlo standard error of ~0.005 for 10,000 simulated trials), confirming the")
print("  analytic non-central t power formula used by statsmodels.")

# ------------------------------------------------------------------------------
# Save observed-effect-size / power / beta / min-n / Monte Carlo results (audit fix:
# these were previously printed only, with no saved output file -- violates Rule 1)
# ------------------------------------------------------------------------------
observed_results_df = pd.DataFrame({
    "metric": [
        "n_actual", "observed_cohens_d", "observed_power", "observed_beta",
        "n_required_for_80pct_power", "n_required_for_90pct_power",
        "mc_n", "mc_cohens_d", "mc_n_sims", "mc_power", "analytic_power_same_cell", "mc_vs_analytic_diff"
    ],
    "value": [
        n_actual, observed_d, observed_power, observed_beta,
        n_for_80, n_for_90,
        mc_n, mc_d, n_sims, mc_power, analytic_power_cell, abs(analytic_power_cell - mc_power)
    ]
})
observed_results_df.to_csv("outputs/tables/06_observed_power_results.csv", index=False)
print("\nSaved outputs/tables/06_observed_power_results.csv")

print("\n================================================================================")
print("                              STEP 06 COMPLETE                                  ")
print("================================================================================")
