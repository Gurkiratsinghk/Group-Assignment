import os
import numpy as np
import pandas as pd

# Rule 2: Set the random seed at the top of every script
RANDOM_SEED = 42
NUMERIC_VAR = "range_pct"
SAMPLE_SIZE_n = 40

np.random.seed(RANDOM_SEED)
rng = np.random.default_rng(RANDOM_SEED)

os.makedirs("data/processed", exist_ok=True)
os.makedirs("outputs/tables", exist_ok=True)
os.makedirs("report", exist_ok=True)

print("================================================================================")
print("       STEP 03: SIMPLE RANDOM SAMPLE & POINT ESTIMATES (skill: sample-point-estimator)")
print("================================================================================")

population_df = pd.read_csv("data/processed/population.csv")
print(f"\nLoaded population: {len(population_df)} rows")

# ------------------------------------------------------------------------------
# Step 1: Draw ONE simple random sample without replacement, n = 40, seed = 42
# ------------------------------------------------------------------------------
print(f"\n[1] Drawing simple random sample without replacement (n={SAMPLE_SIZE_n}, seed={RANDOM_SEED})...")

sample_indices = rng.choice(population_df.index.values, size=SAMPLE_SIZE_n, replace=False)
sample_df = population_df.loc[sample_indices].reset_index(drop=True)
sample_df.to_csv("data/processed/sample_n40.csv", index=False)
print(f"  Saved data/processed/sample_n40.csv ({len(sample_df)} rows)")

x = sample_df[NUMERIC_VAR].to_numpy(dtype=float)
n = len(x)
dof = n - 1

# ------------------------------------------------------------------------------
# Step 2: Point estimates via the sample-point-estimator skill formulas
# ------------------------------------------------------------------------------
print("\n[2] Computing point estimates (skill: sample-point-estimator)...")

skill_mean = float(pd.Series(x).mean())
skill_std = float(pd.Series(x).std(ddof=1))
skill_se = skill_std / np.sqrt(n)

print(f"  Sample mean (x-bar)          = {skill_mean:.6f}")
print(f"  Sample std dev (s, ddof=1)   = {skill_std:.6f}")
print(f"  Standard error (s/sqrt(n))   = {skill_se:.6f}")
print(f"  n                            = {n}")
print(f"  Degrees of freedom (n-1)     = {dof}")

# ------------------------------------------------------------------------------
# Step 3: VERIFICATION - recompute from first principles, plain numpy arithmetic
# ------------------------------------------------------------------------------
print("\n[3] VERIFICATION: recomputing from first principles (plain numpy, no pandas convenience)...")

manual_mean = np.sum(x) / n
manual_std_ddof1 = np.sqrt(np.sum((x - manual_mean) ** 2) / (n - 1))
manual_std_ddof0 = np.sqrt(np.sum((x - manual_mean) ** 2) / n)
manual_se = manual_std_ddof1 / np.sqrt(n)
manual_dof = n - 1

comparison_rows = [
    ("sample_mean (x-bar)", skill_mean, manual_mean),
    ("sample_std (s, ddof=1)", skill_std, manual_std_ddof1),
    ("standard_error (s/sqrt(n))", skill_se, manual_se),
    ("n", float(n), float(n)),
    ("degrees_of_freedom (n-1)", float(dof), float(manual_dof)),
]

print(f"\n  {'quantity':<28} {'skill output':>16} {'manual output':>16} {'abs diff':>14}")
for name, skill_val, manual_val in comparison_rows:
    diff = abs(skill_val - manual_val)
    flag = "  <-- MISMATCH >1e-9!" if diff > 1e-9 else ""
    print(f"  {name:<28} {skill_val:>16.6f} {manual_val:>16.6f} {diff:>14.2e}{flag}")

print("\n  --- ddof=0 vs ddof=1 trap ---")
print(f"  std with ddof=1 (sample, Bessel-corrected): {manual_std_ddof1:.6f}")
print(f"  std with ddof=0 (population formula):       {manual_std_ddof0:.6f}")
print("  CORRECT CHOICE: ddof=1. This is a SAMPLE of size 40 drawn from a larger population, not the")
print("  full population itself. Dividing by (n-1) instead of n corrects the downward bias that arises")
print("  because the sample mean is itself estimated from the data and is closer, on average, to the")
print("  sample points than the true population mean would be. Using ddof=0 here would understate the")
print("  true variability and produce a standard error that is too small.")

# ------------------------------------------------------------------------------
# Step 4: True population values (only knowable because we constructed the population)
# ------------------------------------------------------------------------------
print("\n[4] TRUE population values (for context only)...")

pop_x = population_df[NUMERIC_VAR].to_numpy(dtype=float)
pop_mean_true = float(np.mean(pop_x))
pop_std_true = float(np.std(pop_x, ddof=1))
sampling_error = skill_mean - pop_mean_true

print(f"  TRUE population mean (mu)     = {pop_mean_true:.6f}")
print(f"  TRUE population std dev       = {pop_std_true:.6f}")
print(f"  Sampling error (x-bar - mu)   = {sampling_error:.6f}")
print("  NOTE: In a real study mu is unknowable from a single sample. We can only state it here")
print("  because we built the full population ourselves from downloaded market data.")

# ------------------------------------------------------------------------------
# Step 5: Save results table
# ------------------------------------------------------------------------------
results_df = pd.DataFrame({
    "metric": [
        "n", "degrees_of_freedom", "sample_mean", "sample_std_ddof1", "sample_std_ddof0",
        "standard_error_of_mean", "population_mean_true", "population_std_true", "sampling_error"
    ],
    "value": [
        n, dof, skill_mean, manual_std_ddof1, manual_std_ddof0,
        skill_se, pop_mean_true, pop_std_true, sampling_error
    ]
})
results_df.to_csv("outputs/tables/03_point_estimates.csv", index=False)
print("\nSaved outputs/tables/03_point_estimates.csv")
print(results_df.to_string(index=False))

print("\n================================================================================")
print("                              STEP 03 COMPLETE                                  ")
print("================================================================================")
