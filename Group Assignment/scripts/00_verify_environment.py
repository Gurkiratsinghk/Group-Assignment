import sys
import random
import numpy as np

# Set random seed
random.seed(42)
np.random.seed(42)

libraries = ['yfinance', 'pandas', 'numpy', 'scipy', 'statsmodels', 'matplotlib']

print("=== Environment Verification ===")
for lib in libraries:
    try:
        mod = __import__(lib)
        version = getattr(mod, '__version__', 'Installed (no version attribute)')
        print(f"{lib}: {version}")
    except Exception as e:
        print(f"{lib}: IMPORT ERROR -> {e}")
