# Wide Format Data Analysis Playbook

## What wide format data is
More columns than rows. Typically: measurements along one axis (samples, species,
time points) with many variables measured for each. Examples: gene expression matrices
(samples × genes), survey response matrices (respondents × questions), spectroscopy
readings (spectra × wavelengths).

The key problem: standard EDA assumes rows >> columns. When columns >> rows, correlation
matrices are rank-deficient, visualizations collapse under the number of variables,
and most statistical tests are invalid.

## Step 1: Understand the shape and what the axes mean

Before anything else, establish:
- What does each row represent?
- What does each column represent?
- Is there a target column (something you are trying to predict or explain)?
- Are all columns on the same scale, or do they need normalization?

```python
df.shape       # (n_rows, n_cols) — confirm you have wide data
df.describe()  # Range check — are columns on wildly different scales?
df.isnull().sum().sum()  # Total missing values across all cells
```

If columns are on different scales, normalize before any analysis:
```python
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
df_scaled = pd.DataFrame(scaler.fit_transform(df[numeric_cols]),
                         columns=numeric_cols, index=df.index)
```

## Step 2: Dimensionality reduction first — always

**Do not run standard EDA on wide data without reducing dimensions first.**
With 50 columns and 30 rows, a correlation matrix has 1,225 correlations.
Almost all of them will appear significant by chance (multiple comparisons problem).
A heatmap will be unreadable. Groupby will produce noise.

PCA (Principal Component Analysis) reduces many correlated columns into a small
number of uncorrelated components that capture most of the variance.

```python
from sklearn.decomposition import PCA
import numpy as np

# Choose number of components — explain 80-95% of variance
pca = PCA()
pca.fit(df_scaled[numeric_cols])
cumvar = np.cumsum(pca.explained_variance_ratio_)
n_components = np.argmax(cumvar >= 0.90) + 1
print(f"Components needed for 90% variance: {n_components}")

# Refit with that many components
pca = PCA(n_components=n_components)
components = pca.fit_transform(df_scaled[numeric_cols])
df_pca = pd.DataFrame(components, columns=[f"PC{i+1}" for i in range(n_components)])
```

Plot the scree (variance explained per component) to show the dimensionality structure:
```python
plt.plot(range(1, len(pca.explained_variance_ratio_) + 1),
         pca.explained_variance_ratio_, "o-")
plt.xlabel("Component")
plt.ylabel("Variance explained")
```

## Step 3: PCA biplot — what does each component mean?

Each principal component is a linear combination of the original columns.
The loadings (coefficients) tell you which original columns drive each component.

```python
loadings = pd.DataFrame(
    pca.components_.T,
    index=numeric_cols,
    columns=[f"PC{i+1}" for i in range(n_components)]
)
# Top drivers of PC1:
print(loadings["PC1"].abs().sort_values(ascending=False).head(10))
```

Name the component based on the dominant variables. If PC1 is driven by temperature,
humidity, and pressure, call it "atmospheric conditions."

## Step 4: Correlation heatmap — only after reducing

After PCA, the reduced component space is small enough for a readable correlation analysis.
If you have a target variable, correlate it against the PCA components.

```python
import seaborn as sns
corr = df_pca.corr()
plt.figure(figsize=(8, 6))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0)
plt.title("Component correlation matrix")
plt.tight_layout()
```

## Step 5: If there is a target column — feature importance

If the wide data has a label or target (class, outcome, value to predict):

```python
from sklearn.ensemble import RandomForestClassifier  # or Regressor
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(df_scaled[numeric_cols], df["target"])
importances = pd.Series(model.feature_importances_, index=numeric_cols)
importances.sort_values(ascending=False).head(20).plot(kind="bar")
plt.title("Top 20 features by importance")
plt.tight_layout()
```

Feature importance is more reliable than correlation for wide data because it accounts
for non-linear relationships and interactions between variables.

## Step 6: What to report

A good wide-format analysis report includes:
- Shape and completeness: n_rows × n_cols, missing value count
- Scree plot showing how many components capture 90% of variance
- Loadings for the top 2-3 components with human-readable names
- 2D scatter of samples in PC1 vs PC2 space (reveals clustering)
- Feature importance ranking if a target column exists

## Common mistakes to avoid

1. **Running a standard correlation matrix on all columns.** With 50+ columns,
   you will find hundreds of "significant" correlations by chance. Multiple
   comparisons invalidate standard p-value thresholds.

2. **Treating every column as independent.** Wide data is almost always highly
   correlated — that is why PCA works. Analyzing columns in isolation misses the structure.

3. **Using all components from PCA.** If PCA produces n_components components and you use
   all of them, you have done nothing — you still have n_cols worth of information.
   The point is reduction: pick the minimum number that preserves 90% of variance.

4. **Ignoring scale differences.** PCA is scale-sensitive. Always normalize to zero mean
   and unit variance before PCA. A column measured in kilometers will dominate a column
   measured in millimeters unless you standardize first.

5. **Confusing explained variance with predictive power.** A component that explains
   30% of total variance might explain 0% of the target variable. Dimensionality reduction
   and supervised feature selection are different goals.
