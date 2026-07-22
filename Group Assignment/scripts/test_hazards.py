import yfinance as yf
import pandas as pd
import numpy as np

tickers = ['TCS.NS', 'INFY.NS', 'HCLTECH.NS', 'WIPRO.NS', 'TECHM.NS', 'PERSISTENT.NS', 'HINDUNILVR.NS', 'ITC.NS', 'NESTLEIND.NS', 'BRITANNIA.NS', 'DABUR.NS', 'MARICO.NS']

data_list = []
for t in tickers:
    df = yf.download(t, start='2024-01-01', end='2026-01-01', auto_adjust=False, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df['ticker'] = t
    df['date'] = df.index
    data_list.append(df)

combined = pd.concat(data_list)
print('Combined shape:', combined.shape)

# Check Close vs Adj Close ratio discontinuity per ticker
combined['adj_ratio'] = combined['Close'] / combined['Adj Close']
print("\n--- Corporate Action Discontinuity Check ---")
for t, group in combined.groupby('ticker'):
    group = group.sort_values('date')
    ratio_diff = group['adj_ratio'].pct_change().abs()
    step_dates = group[ratio_diff > 0.01]
    if len(step_dates) > 0:
        print(f'Discontinuity in {t}:')
        for idx, row in step_dates.iterrows():
            prev_row = group.loc[:idx].iloc[-2]
            print(f'  Date: {idx.strftime("%Y-%m-%d")}, Prev Ratio: {prev_row["adj_ratio"]:.4f}, Curr Ratio: {row["adj_ratio"]:.4f}')
    else:
        print(f'No ratio discontinuity step >1% in {t}')

# Check range_pct == 0
combined['range_pct'] = (combined['High'] - combined['Low']) / combined['Open'] * 100
zero_range = combined[combined['range_pct'] <= 0.01]
print(f"\n--- Range Pct Zero / Near Zero Check (count: {len(zero_range)}) ---")
if len(zero_range) > 0:
    for idx, row in zero_range.iterrows():
        print(f"  Ticker: {row['ticker']}, Date: {row['date'].strftime('%Y-%m-%d')}, Open: {row['Open']}, High: {row['High']}, Low: {row['Low']}, Range%: {row['range_pct']:.4f}")

# Check aggregate volume per date for Diwali Muhurat trading
daily_vol = combined.groupby('date')['Volume'].sum()
med_vol = daily_vol.median()
low_vol_dates = daily_vol[daily_vol < 0.3 * med_vol]
print(f"\n--- Low Volume Special Session Check (Median Daily Volume across 12 tickers: {med_vol:,.0f}) ---")
for d, v in low_vol_dates.items():
    print(f'  Date: {d.strftime("%Y-%m-%d")}, Total Vol: {v:,}, Ratio to Median: {v/med_vol:.2%}')
