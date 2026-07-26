import os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Rule 2: Set the random seed at the top of every script
np.random.seed(42)
rng = np.random.default_rng(42)

NUMERIC_VAR = "range_pct"
GROUP_VAR = "sector"
GROUP_A = "Technology"
GROUP_B = "Consumer Staples"

os.makedirs("outputs/tables", exist_ok=True)
os.makedirs("outputs/figures", exist_ok=True)

print("================================================================================")
print("                    STEP 02: EXPLORATORY DATA ANALYSIS (EDA)                    ")
print("================================================================================")

df = pd.read_csv("data/processed/population.csv")
print(f"\nLoaded data/processed/population.csv: {len(df)} rows")

# ------------------------------------------------------------------------------
# Step 1: Summary statistics (Rule 3: dual computation - library vs raw formula)
# ------------------------------------------------------------------------------
print("\n[1] Computing summary statistics for range_pct (overall + by sector)...")


def summary_row(x, label):
    x = np.asarray(x, dtype=float)
    n = len(x)

    mean_lib = float(pd.Series(x).mean())
    mean_raw = float(np.sum(x) / n)

    std_lib = float(pd.Series(x).std(ddof=1))
    std_raw = float(np.sqrt(np.sum((x - mean_raw) ** 2) / (n - 1)))

    skew_lib = float(stats.skew(x, bias=False))
    skew_raw = float((n / ((n - 1) * (n - 2))) * np.sum(((x - mean_raw) / std_raw) ** 3))

    kurt_lib = float(stats.kurtosis(x, fisher=True, bias=False))
    kurt_raw = float(
        ((n * (n + 1)) / ((n - 1) * (n - 2) * (n - 3))) * np.sum(((x - mean_raw) / std_raw) ** 4)
        - (3 * (n - 1) ** 2) / ((n - 2) * (n - 3))
    )

    print(f"\n  -- {label} (n={n}) --")
    for nm, lib, raw in [("mean", mean_lib, mean_raw), ("std", std_lib, std_raw),
                         ("skewness", skew_lib, skew_raw), ("kurtosis", kurt_lib, kurt_raw)]:
        diff = abs(lib - raw)
        flag = "  <-- MISMATCH >1e-9!" if diff > 1e-9 else ""
        print(f"    {nm}: library={lib:.10f}  raw={raw:.10f}  diff={diff:.2e}{flag}")

    return {
        "group": label, "n": n, "mean": mean_lib, "median": float(np.median(x)), "std": std_lib,
        "min": float(np.min(x)), "q1": float(np.percentile(x, 25)), "q3": float(np.percentile(x, 75)),
        "max": float(np.max(x)), "skewness": skew_lib, "excess_kurtosis": kurt_lib
    }


rows = [summary_row(df[NUMERIC_VAR], "Overall")]
for g in [GROUP_A, GROUP_B]:
    rows.append(summary_row(df.loc[df[GROUP_VAR] == g, NUMERIC_VAR], g))

summary_df = pd.DataFrame(rows)
summary_df.to_csv("outputs/tables/02_summary_stats.csv", index=False)
print("\nSaved outputs/tables/02_summary_stats.csv")
print(summary_df.to_string(index=False))

# ------------------------------------------------------------------------------
# Step 2: Figures
# ------------------------------------------------------------------------------
print("\n[2] Generating figures...")

x = df[NUMERIC_VAR].values
mu, sigma = x.mean(), x.std(ddof=1)

fig, ax = plt.subplots(figsize=(8, 6))
ax.hist(x, bins=50, density=True, alpha=0.7, color="steelblue", edgecolor="black")
xs = np.linspace(x.min(), x.max(), 300)
ax.plot(xs, stats.norm.pdf(xs, mu, sigma), "r-", linewidth=2, label=f"Normal(μ={mu:.2f}, σ={sigma:.2f})")
ax.set_xlabel("range_pct (%)")
ax.set_ylabel("Density")
ax.set_title(f"Distribution of range_pct with Normal Overlay (n={len(x)})")
ax.legend()
fig.savefig("outputs/figures/02_hist_range_pct.png", dpi=300, bbox_inches="tight")
plt.close(fig)
print("  Saved outputs/figures/02_hist_range_pct.png")

fig, ax = plt.subplots(figsize=(8, 6))
stats.probplot(x, dist="norm", plot=ax)
ax.set_title(f"Q-Q Plot of range_pct vs Normal Distribution (n={len(x)})")
fig.savefig("outputs/figures/02_qq_range_pct.png", dpi=300, bbox_inches="tight")
plt.close(fig)
print("  Saved outputs/figures/02_qq_range_pct.png")

group_a_vals = df.loc[df[GROUP_VAR] == GROUP_A, NUMERIC_VAR].values
group_b_vals = df.loc[df[GROUP_VAR] == GROUP_B, NUMERIC_VAR].values

fig, ax = plt.subplots(figsize=(8, 6))
ax.boxplot([group_a_vals, group_b_vals], tick_labels=[GROUP_A, GROUP_B])
ax.set_ylabel("range_pct (%)")
ax.set_title(f"range_pct by Sector (n={len(df)})")
fig.savefig("outputs/figures/02_box_range_pct_by_sector.png", dpi=300, bbox_inches="tight")
plt.close(fig)
print("  Saved outputs/figures/02_box_range_pct_by_sector.png")

y = df["daily_return_pct"].values
mu2, sigma2 = y.mean(), y.std(ddof=1)

fig, ax = plt.subplots(figsize=(8, 6))
ax.hist(y, bins=50, density=True, alpha=0.7, color="seagreen", edgecolor="black")
ys = np.linspace(y.min(), y.max(), 300)
ax.plot(ys, stats.norm.pdf(ys, mu2, sigma2), "r-", linewidth=2, label=f"Normal(μ={mu2:.2f}, σ={sigma2:.2f})")
ax.set_xlabel("daily_return_pct (%)")
ax.set_ylabel("Density")
ax.set_title(f"Distribution of daily_return_pct with Normal Overlay (n={len(y)})")
ax.legend()
fig.savefig("outputs/figures/02_hist_daily_return_pct.png", dpi=300, bbox_inches="tight")
plt.close(fig)
print("  Saved outputs/figures/02_hist_daily_return_pct.png")

# ------------------------------------------------------------------------------
# Step 3: Formal normality checks on range_pct
# ------------------------------------------------------------------------------
print("\n[3] Formal normality checks on range_pct...")

print(f"  Full population n = {len(x)} exceeds scipy's recommended/reliable Shapiro-Wilk sample size "
      f"(~5000); at large n Shapiro-Wilk is over-powered and rejects normality for trivially small, "
      f"practically irrelevant deviations. Running Shapiro-Wilk on a random subsample of 500 (seed 42) instead.")

subsample = rng.choice(x, size=500, replace=False)
shapiro_stat, shapiro_p = stats.shapiro(subsample)
print(f"  Shapiro-Wilk (n=500 subsample): W = {shapiro_stat:.6f}, p = {shapiro_p:.6e}")

dagostino_stat, dagostino_p = stats.normaltest(x)
print(f"  D'Agostino K^2 (full n={len(x)}): K2 = {dagostino_stat:.6f}, p = {dagostino_p:.6e}")

anderson_result = stats.anderson(x, dist="norm")
print(f"  Anderson-Darling (full n={len(x)}): A2 = {anderson_result.statistic:.6f}")
for sig, crit in zip(anderson_result.significance_level, anderson_result.critical_values):
    verdict = "REJECT normality" if anderson_result.statistic > crit else "fail to reject"
    print(f"    significance level {sig:>5}%  critical value = {crit:.4f}  -> {verdict}")

normality_results = pd.DataFrame([
    {"test": "Shapiro-Wilk (n=500 subsample, seed=42)", "statistic": shapiro_stat, "p_value": shapiro_p},
    {"test": "D'Agostino K^2 (full population)", "statistic": dagostino_stat, "p_value": dagostino_p},
    {"test": "Anderson-Darling (full population)", "statistic": anderson_result.statistic,
     "p_value": np.nan},
])

# ------------------------------------------------------------------------------
# Step 4: Levene's test for equality of variances between sectors
# ------------------------------------------------------------------------------
print("\n[4] Levene's test for equality of variances (Technology vs Consumer Staples)...")

var_a_lib = float(np.var(group_a_vals, ddof=1))
var_a_raw = float(np.sum((group_a_vals - group_a_vals.mean()) ** 2) / (len(group_a_vals) - 1))
var_b_lib = float(np.var(group_b_vals, ddof=1))
var_b_raw = float(np.sum((group_b_vals - group_b_vals.mean()) ** 2) / (len(group_b_vals) - 1))

print(f"  {GROUP_A} variance: library={var_a_lib:.10f}  raw={var_a_raw:.10f}  diff={abs(var_a_lib - var_a_raw):.2e}")
print(f"  {GROUP_B} variance: library={var_b_lib:.10f}  raw={var_b_raw:.10f}  diff={abs(var_b_lib - var_b_raw):.2e}")

levene_stat, levene_p = stats.levene(group_a_vals, group_b_vals, center="median")
print(f"  Levene's test (center=median): W = {levene_stat:.6f}, p = {levene_p:.6e}")

levene_results = pd.DataFrame([{
    "test": "Levene (center=median)", "statistic": levene_stat, "p_value": levene_p,
    f"variance_{GROUP_A}": var_a_lib, f"variance_{GROUP_B}": var_b_lib
}])

normality_variance_df = pd.concat([normality_results, levene_results], ignore_index=True)
normality_variance_df.to_csv("outputs/tables/02_normality_variance_tests.csv", index=False)
print("\nSaved outputs/tables/02_normality_variance_tests.csv")

print("\n================================================================================")
print("                              STEP 02 COMPLETE                                  ")
print("================================================================================")
