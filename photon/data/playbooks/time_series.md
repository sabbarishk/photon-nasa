# Time Series Analysis Playbook

## What time series data is
Rows are observations ordered by time. The ordering relationship between rows
matters — the sequence is the structure. This is fundamentally different from
tabular data where rows are independent and interchangeable.

## Step 1: Establish the time axis

Parse the datetime column and set it as the index.

```python
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").set_index("date")
```

Then check for gaps and irregularity:
```python
df.index.freq           # Is the data evenly spaced?
df.index.duplicated().sum()  # Are there duplicate timestamps?
```

**If the data is irregular** (not evenly spaced), decide whether to resample to a regular
frequency before any analysis. Irregular spacing breaks most time series methods.

```python
df_daily = df.resample("D").mean()  # Resample to daily, fill with mean
```

## Step 2: Plot the raw series first — always

Do this before computing anything else. The plot will tell you:
- Whether the series has an obvious trend
- Whether there is visible seasonality
- Whether there are clear outliers or discontinuities (instrument failures, data gaps)
- Whether the variance is changing over time (heteroscedasticity)

```python
df["value"].plot(figsize=(12, 4), title="Raw time series")
plt.tight_layout()
```

## Step 3: Check for stationarity before computing trends

**This is the most commonly skipped step and the source of most time series mistakes.**

A stationary series has constant mean, variance, and autocorrelation over time.
Most statistical methods assume stationarity. If you compute the trend or correlation
of a non-stationary series, the results are meaningless — a "strong correlation" between
two trending series often disappears entirely after differencing.

```python
from statsmodels.tsa.stattools import adfuller
result = adfuller(df["value"].dropna())
p_value = result[1]
# p_value < 0.05: stationary (safe to proceed)
# p_value >= 0.05: non-stationary — difference the series before analysis
```

If the series is non-stationary, apply first differencing:
```python
df["value_diff"] = df["value"].diff()
```

## Step 4: Rolling statistics — use them for context, not as the primary analysis

Rolling averages smooth noise and reveal the underlying trend.

```python
window = 7  # 7-day rolling average for daily data
df["rolling_mean"] = df["value"].rolling(window=window).mean()
df["rolling_std"] = df["value"].rolling(window=window).std()
```

**The rolling average mistake**: plotting only the rolling average and calling it
"the trend." The rolling average is not the trend — it is a smoothed version of
the original data. It cannot be used to forecast beyond the data range.

## Step 5: Seasonal decomposition (for regular frequencies)

If you suspect seasonal patterns (daily, weekly, annual), decompose the series:

```python
from statsmodels.tsa.seasonal import seasonal_decompose
decomp = seasonal_decompose(df["value"].dropna(), model="additive", period=12)
decomp.plot()
plt.tight_layout()
```

This separates the series into: trend + seasonal + residual.
The residual should look like white noise. If it has structure, the model missed something.

## Step 6: What to report

A good time series report includes:
- The raw series plot with key events annotated if known
- Stationarity test result and whether differencing was applied
- The decomposition showing trend and seasonal components separately
- The magnitude of seasonal variation relative to trend
- Any detected anomalies (values beyond 3 sigma from rolling mean)

## Common mistakes to avoid

1. **Reading trend from a non-stationary series.** If the ADF test says non-stationary,
   the apparent trend is a statistical artifact, not a real finding.

2. **Computing the mean of a time series as its "typical value."** The mean of a trending
   series is meaningless — the series never spends time near its mean.

3. **Confusing rolling average with forecasting.** Rolling average is backward-looking only.

4. **Ignoring seasonality when comparing point-in-time values.** July vs. December
   temperatures are not comparable without seasonal adjustment.

5. **Treating time-correlated errors as independent.** Standard regression assumes
   independent errors. Time series residuals are usually autocorrelated — use Durbin-Watson
   or plot ACF to check.
