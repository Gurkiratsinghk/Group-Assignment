# Data Dictionary

| Column Name | Definition | Units | Formula / Calculation | Source |
| --- | --- | --- | --- | --- |
| `date` | Trading session calendar date | YYYY-MM-DD | Plain date from yfinance index | Yahoo Finance (NSE) |
| `ticker` | National Stock Exchange symbol | Categorical | Ticker string with `.NS` suffix | NSE India |
| `sector` | Broad industrial sector classification | Categorical | Mapped to `Technology` or `Consumer Staples` | Project Classification |
| `open` | Opening stock price for the trading session | INR (₹) | Raw unadjusted open price | Yahoo Finance (NSE) |
| `high` | Highest stock price during the session | INR (₹) | Raw unadjusted high price | Yahoo Finance (NSE) |
| `low` | Lowest stock price during the session | INR (₹) | Raw unadjusted low price | Yahoo Finance (NSE) |
| `close` | Closing stock price for the session | INR (₹) | Raw unadjusted close price | Yahoo Finance (NSE) |
| `adj_close` | Adjusted closing price (corporate action adjusted) | INR (₹) | Adjusted for dividends and stock splits | Yahoo Finance (NSE) |
| `volume` | Total shares traded during session | Count | Daily trading volume | Yahoo Finance (NSE) |
| `range_pct` | Relative daily price trading range | Percent (%) | `(high - low) / open * 100` | Derived (Primary Numeric Variable) |
| `daily_return_pct` | Session-to-session percentage price change | Percent (%) | `(close_t - close_{t-1}) / close_{t-1} * 100` | Derived |
| `overnight_gap_pct` | Percentage price gap between open and previous close | Percent (%) | `(open_t - close_{t-1}) / close_{t-1} * 100` | Derived |
| `intraday_move_pct` | Percentage price change within trading hours | Percent (%) | `(close_t - open_t) / open_t * 100` | Derived |
| `abs_overnight_gap_pct` | Absolute magnitude of overnight price gap | Percent (%) | `|overnight_gap_pct|` | Derived (Paired Variable 1) |
| `abs_intraday_move_pct` | Absolute magnitude of intraday price movement | Percent (%) | `|intraday_move_pct|` | Derived (Paired Variable 2) |
| `year` | Calendar year of trading date | Year | `date.year` | Derived |
| `month` | Calendar month of trading date | Month (1-12) | `date.month` | Derived |
| `weekday` | Day of week integer | Day (0=Mon...6=Sun) | `date.weekday` | Derived |

---

## Statistical Design Variable Mapping
- **Primary Numeric Variable of Interest (`NUMERIC_VAR`)**: `range_pct` (relative percentage trading range).
- **Categorical Grouping Variable (`GROUP_VAR`)**: `sector` (`Technology` [Group A] vs `Consumer Staples` [Group B]).
- **Paired-Sample Design Variables**:
  - `PAIR_VAR_1`: `abs_overnight_gap_pct` (absolute overnight gap percentage)
  - `PAIR_VAR_2`: `abs_intraday_move_pct` (absolute intraday movement percentage)
