# Tabular Data Analysis Playbook

## What tabular data is
Rows are observations, columns are variables. Each row is independent. There
is no ordering relationship between rows (if there were, it would be time series).

## Step 1: Audit the data before any analysis

Run these checks first. Do not skip them.

```python
df.shape          # How many rows and columns
df.dtypes         # Are numeric columns actually numeric, or loaded as strings?
df.isnull().sum() # Which columns have missing values and how many
df.nunique()      # Cardinality — is "category" column actually categorical or a free-text field?
df.describe()     # Min/max/mean/std — look for impossible values (negative age, 999 as sentinel)
```

**Red flags to look for:**
- A column that should be numeric but loaded as object dtype — it has non-numeric values mixed in
- A date column that loaded as a string — parse it explicitly with pd.to_datetime
- Sentinel values used for missing data: -999, 0, "N/A" as a string — these must be replaced with NaN
- Cardinality that does not match expectations: "country" with 10,000 unique values is not categorical

## Step 2: Distributions

For each numeric column, look at the distribution before computing anything else.

```python
import matplotlib.pyplot as plt
df[numeric_col].hist(bins=30)
```

**What to look for:**
- Skewed distributions: median will be a better central tendency measure than mean
- Bimodal distributions: suggests two distinct populations are mixed — investigate
- Outliers: values beyond 3 standard deviations from the mean are candidates for investigation, not automatic removal

## Step 3: Correlations — with the outlier caveat

```python
df[numeric_columns].corr()  # Pearson correlation matrix
```

**The critical mistake**: computing Pearson correlation without first checking for outliers.
Pearson correlation is sensitive to outliers. A single extreme value can create a
strong apparent correlation that disappears when the outlier is removed.

Before trusting a correlation:
1. Plot a scatter plot of the two variables
2. Check if the correlation is driven by outliers
3. If the relationship is non-linear, Pearson correlation will understate the association

## Step 4: Groupby aggregations

Group by categorical columns and compute summary statistics for numeric columns.

```python
df.groupby("category_col")["numeric_col"].agg(["mean", "median", "std", "count"])
```

**The high-cardinality mistake**: do not groupby a column with thousands of unique values.
Limit groupby to columns with fewer than 30 unique values. For high-cardinality columns,
bin them first (e.g., cut continuous values into deciles) or select the top N categories.

## Step 5: What to report

A good tabular analysis report includes:
- Shape and completeness: how many rows, how many missing values per column
- Distribution summary for each numeric column: median, IQR, and whether it is skewed
- Top correlations (absolute value > 0.5) with scatter plots to verify
- Group-level comparison: how does the key outcome variable differ across categories
- Any anomalies found during Step 1 and how they were handled

## Common mistakes to avoid

1. **Dropping nulls without investigating why they are null.** Missingness is often structured
   — a column is null because of a business rule, not at random. Dropping changes your sample.

2. **Treating ordinal variables as continuous.** A rating of 1-5 is not a continuous variable.
   Do not compute the mean of star ratings without acknowledging this.

3. **Computing the mean of a heavily skewed distribution.** Report median and IQR instead.

4. **Forgetting to check for duplicate rows.** `df.duplicated().sum()` before any analysis.

5. **Calling a correlation "causation" in the output.** Never imply causation from observational data.
