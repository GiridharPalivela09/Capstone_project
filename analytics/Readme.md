# Module 2 — Analytics Pipeline (`/analytics`)

One cohesive pipeline over the classic Titanic dataset, split into two notebooks that
share a single committed CSV:

| Notebook | Covers | Reads | Writes |
|---|---|---|---|
| `01_eda.ipynb` | Part A — profiling, cleaning, EDA, data story (Tasks 1–6) | `sns.load_dataset('titanic')` **once** | `titanic.csv` |
| `02_modeling.ipynb` | Part B — full predictive-modeling pipeline + regression side-task (Tasks 7–15) | `titanic.csv` (via `pd.read_csv`, no network) | `titanic_survival_pipeline.joblib` |

`02_modeling.ipynb` never re-fetches the dataset — it loads the exact CSV that
`01_eda.ipynb` cleaned and committed, which is the required behaviour: the dataset is
pulled from the network/cache exactly once across the whole module.

## How to run

1. Open `01_eda.ipynb` and **Run All**. This needs internet access on its first cell
   (to fetch Titanic via Seaborn) — after that it's fully offline. It produces the
   cleaned `titanic.csv` in this same folder.
2. Open `02_modeling.ipynb` and **Run All**. It reads `titanic.csv` from disk only —
   no network calls anywhere in this notebook. It produces
   `titanic_survival_pipeline.joblib`, the final fitted, end-to-end pipeline.

Both notebooks were executed top-to-bottom with no errors before delivery, so the
saved outputs (tables, charts, printed metrics) reflect a real run, not placeholders.

## `01_eda.ipynb` — Part A walkthrough

- **Task 1 — Load & profile.** Loads Titanic once via `sns.load_dataset`, prints
  `df.info()`, `df.describe()`, `df.shape`, and the missing-value percentage of every
  affected column, then immediately commits the raw DataFrame to `titanic.csv`.
- **Task 2 — Missing-value handling (per-column threshold rule).** Applies:
  **<5% missing → drop rows** (`embarked`, `embark_town`, 0.22% each — 2 rows),
  **5–30% missing → impute** (`age`, 19.87% missing → median, since age is only
  mildly right-skewed), **>30% missing → drop or "missing"-encode, justified**
  (`deck`, 77.22% missing → dropped, since imputing 4-in-5 values would be unreliable
  and `deck` isn't one of the six columns the correlation matrix requires). The
  cleaned data is re-saved over `titanic.csv`, which every later step — the rest of
  this notebook and all of `02_modeling.ipynb` — reads from.
- **Task 3 — Univariate analysis.** Histogram + box plot for `age` and `fare`,
  IQR-based (`[Q1-1.5·IQR, Q3+1.5·IQR]`) outlier counts for both, and a skewness
  discussion: `age` is close to symmetric (mean ≈ median), while `fare` is strongly
  right-skewed (mean > median > mode).
- **Task 4 — Bivariate analysis.** Survival rate by `sex`, by `pclass`, and by
  `sex`+`pclass` combined (via boolean masking); a 6×6 correlation heatmap restricted
  to exactly `survived, pclass, age, sibsp, parch, fare` (excluding the
  boolean-derived `adult_male`/`alone` and the redundant `class`/`who`); the two
  strongest off-diagonal correlations (`fare`↔`pclass` and `survived`↔`pclass`) are
  identified programmatically and interpreted in writing.
- **Task 5 — Multivariate "data story."** Four charts (grouped bar, KDE, box, bar) that
  build one argument together — sex is the dominant survival factor, amplified by
  class/fare, with secondary effects from age and family size — each with its own
  2–4 sentence interpretation.
- **Task 6 — EDA-stage z-score check.** Manually applies `z = (x-mean)/std` to `age`
  and `fare`, shows before/after distribution plots, and confirms both standardized
  columns land at ≈0 mean / ≈1 std. Explicitly **not** part of the modeling pipeline —
  `02_modeling.ipynb` fits its own `StandardScaler` train-only.

## `02_modeling.ipynb` — Part B walkthrough

- **Task 7 — Stratified split.** `train_test_split(..., stratify=survived)`, justified
  in writing by the ~62/38 survival class imbalance observed in Task 1.
- **Task 8 — Leak-free preprocessing.** A `ColumnTransformer` (median-impute + scale
  numeric columns, most-frequent-impute + one-hot encode `sex`/`embarked`) wrapped in
  a `Pipeline` with the final estimator, so every preprocessing step is fit on the
  training split only and only ever `.transform()`-ed on the test split.
- **Task 9 — Three classifiers.** Logistic Regression, Decision Tree (visualized with
  `plot_tree`, labeled features/classes), and Random Forest, all trained on the
  identical split.
- **Task 10 — Full evaluation.** Confusion matrix, accuracy, precision, recall, F1,
  and ROC/AUC for all three, plus a side-by-side ROC plot and a single comparison
  table.
- **Task 11 — Imbalance handling comparison.** Three variants on Random Forest —
  baseline, `class_weight='balanced'`, and SMOTE (applied to the training fold only,
  via an `imblearn` pipeline, to avoid leakage) — compared on precision/recall/F1 with
  a written conclusion.
- **Task 12 — Hyperparameter tuning.** `GridSearchCV` over the Random Forest's
  `n_estimators`, `max_depth`, `max_features`; refits a
  `RandomForestClassifier(oob_score=True, ...)` with the best params to report the
  out-of-bag score (only populated by construction, as required).
  **Result:** best params `{max_depth: 4, max_features: 'sqrt', n_estimators: 100}`,
  OOB score ≈ 0.821.
- **Task 13 — Regression side-task.** Multivariate linear regression predicting `fare`
  from the other features. **Result:** MAE ≈ 21.10, RMSE ≈ 41.70, R² ≈ 0.348,
  Adjusted R² ≈ 0.321; the residual plot shows a funnel shape, so the written
  conclusion is that the model **is heteroscedastic** (residual spread grows with
  predicted fare) — expected, since `fare` is right-skewed and untransformed here.
- **Task 14 — Model comparison table + recommendation.** Classifier metrics
  (accuracy/precision/recall/F1/AUC) and regression metrics (MAE/RMSE/R²/Adj. R²) are
  presented as two separate metric-column groups in one table, never implied to share
  a scale, with a 3–5 sentence final recommendation on which classifier to deploy.
- **Task 15 — Save the complete pipeline.** The best-performing full pipeline
  (preprocessing + tuned estimator together) is saved via
  `joblib.dump(full_pipeline, "titanic_survival_pipeline.joblib")`. A final cell
  reloads it with `joblib.load` and confirms it predicts correctly on raw,
  unprocessed sample input — verified during the actual run (see notebook output).

## Files in this folder

- `01_eda.ipynb`, `02_modeling.ipynb` — the two notebooks (already executed; outputs
  included).
- `titanic.csv` — the committed offline fallback (cleaned), produced by
  `01_eda.ipynb` and consumed by `02_modeling.ipynb`.
- `titanic_survival_pipeline.joblib` — the final saved, fitted, end-to-end pipeline
  from `02_modeling.ipynb`.

## Mapping to the acceptance criteria

Every bullet in the assignment's "Acceptance criteria" list is satisfied directly by
the task above it maps to — missing-value percentages and the threshold rule are
printed in Task 2, the six-column correlation heatmap and its two strongest pairs in
Task 4, the four data-story charts with interpretations in Task 5, the stratified
split and leak-free `Pipeline`/`ColumnTransformer` in Tasks 7–8, the full metric suite
for all three classifiers in Task 10, the three-way imbalance comparison in Task 11,
`GridSearchCV` best params + OOB score in Task 12, all four regression metrics and the
heteroscedasticity conclusion in Task 13, the merged-but-separate-scale comparison
table in Task 14, and the reloadable, end-to-end-usable saved pipeline in Task 15.