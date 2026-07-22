# Project Brief & Constants

## Rules for Every Step of the Project
1. Never simulate, fabricate, or hand-edit data. Every number in the final report must be traceable to a script in `/scripts/` and a file in `/outputs/`.
2. Set the random seed at the top of every script.
3. Every statistic must be computed twice — once via library/skill, once from the raw formula — and both values printed. Flag any disagreement beyond 1e-9 loudly.
4. Save every result table as CSV in `/outputs/tables/` and every figure as PNG in `/outputs/figures/`.
5. Print, don't summarise: show me the actual numeric output of each script.

## Project Constants
RANDOM_SEED = 42
POPULATION_FILE = data/processed/population.csv
NUMERIC_VAR = range_pct
GROUP_VAR = sector
GROUP_A = Technology
GROUP_B = Consumer Staples
PAIR_VAR_1 = abs_overnight_gap_pct
PAIR_VAR_2 = abs_intraday_move_pct
BENCHMARK_VALUE = 2.0
ALPHA = 0.05
SAMPLE_SIZE_n = 40
N_RESAMPLES = 500
