# Model Selection Guide

This guide governs the modeling decision (Section 3.3 of the analysis plan and Section 8 of the
notebook): which model, how to select features, how to validate, and which metric to report. It
also supplies the concrete, leakage-safe implementation behind checkpoints CP-04 (data leakage)
and CP-05 (small-sample overfitting) — so those checkpoints flag the risk *and* point to code that
structurally prevents it. Read it before naming a model in a plan or generating any modeling code.

## Status

Added with the execution-layer merge (v0.3.0). The pipeline pattern, cross-validation scheme, and
metric choices below were run end to end on real scikit-learn against extracted radiomic features
(both a random forest and a logistic-regression path), and reproduced on the merged UPenn-GBM
proof-of-concept notebook. The guidance on choosing between models by sample size and outcome type
follows standard practice; the specific model for a given study is a decision to surface to the
researcher, not to apply silently.

## Choosing a model

Match the model to the outcome type, the sample size, and the class balance. Start simple —
complexity has to earn its place on a small cohort.

| Situation | Reasonable default | Why |
|---|---|---|
| Binary or multi-class outcome, small cohort (tens–low hundreds) | **Random forest** (`class_weight="balanced"`) | Robust, captures non-linear feature interactions, gives importances, tolerates correlated features |
| Binary outcome, signal likely roughly linear, want interpretability | **Logistic regression** (add **L1 / elastic-net** for built-in feature selection) | Interpretable coefficients; L1 selects features implicitly |
| Continuous outcome (e.g. survival *time* as regression) | `RandomForestRegressor` or `ElasticNet` | Same structure; swap scoring to `neg_mean_absolute_error` / `r2` |
| Time-to-event with censoring (true survival analysis) | Cox proportional hazards / Kaplan-Meier (via `lifelines`) | Classification/regression discard censoring; use survival models when follow-up is censored |

Do not reach for deep learning here. On the cohort sizes this skill targets it overfits, needs a
GPU, and is hard to interpret. Establish a radiomics + classical-ML baseline first.

## The leak-proof pipeline (this is CP-04's implementation)

The most common cause of falsely good radiomics results is fitting preprocessing on the whole
dataset before splitting. Prevent it structurally by bundling every data-dependent step with the
model in a scikit-learn `Pipeline`, so scaling and feature selection are refit inside each
cross-validation fold using training data only:

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.ensemble import RandomForestClassifier

model = Pipeline([
    ("scale",  StandardScaler()),                 # standardise features
    ("select", SelectKBest(f_classif, k=20)),     # keep the most informative K (guards small-N)
    ("clf",    RandomForestClassifier(n_estimators=300,
               class_weight="balanced", random_state=RANDOM_SEED, n_jobs=-1)),
])
```

Generated notebooks should build the model this way. Never scale or select features on the full
dataset before splitting — that is exactly the CP-04 failure, and wrapping the steps in a
`Pipeline` makes it impossible.

## Feature selection (this is part of CP-05's mitigation)

Radiomics almost always has more features than patients, so trimming is not optional:

- `SelectKBest` (simple, effective) inside the pipeline, or L1/elastic-net which selects implicitly.
- Drop constant / all-NaN columns first (no information; they break scaling).
- Keep `k` small on small cohorts (a handful to ~20). Report how many features fed the final model.

## Patient-level splitting

Split by **patient**, not by scan. If a patient contributes multiple scans, all must fall in the
same fold, or the model sees them on both sides of the split and the score inflates:

```python
from sklearn.model_selection import GroupKFold
cv = GroupKFold(n_splits=5)   # pass groups=patient_ids
```

When each row is already one patient (the usual radiomics case), stratified k-fold is fine.

## Validation and metrics (Section 3.4)

Estimate performance with **repeated stratified k-fold** cross-validation and report the spread,
not a single split:

```python
from sklearn.model_selection import RepeatedStratifiedKFold, cross_validate
cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=RANDOM_SEED)
scores = cross_validate(model, X, y, cv=cv, scoring=["roc_auc", "balanced_accuracy"])
print(scores["test_roc_auc"].mean(), "+/-", scores["test_roc_auc"].std())
```

- **ROC-AUC** — headline for imbalanced medical data; ranking quality, 0.5 = chance, 1.0 = perfect.
- **Balanced accuracy** — average per-class recall; a majority-class guesser cannot look good.
- Report **mean ± standard deviation**. A high mean with a large spread is unstable — say so.
- For out-of-fold ROC / confusion / calibration plots use a single `StratifiedKFold` with
  `cross_val_predict` (it needs a partition; repeated CV would place a patient in several test
  folds and error).

## Hyper-parameter tuning without leakage

Tuning on the same CV you report inflates the estimate. If you tune, use **nested CV**: an inner
`GridSearchCV` picks hyper-parameters within each outer-fold's training data; the outer CV reports
performance. On a small proof-of-concept cohort, sensible fixed defaults are more honest than
tuning on tens of patients.

## Small-sample instability (this is CP-05)

At tens of patients everything is noisy — which features are selected, the AUC, the top predictors.
Mitigations, all of which the checkpoint should recommend: aggressive feature selection, simple
models, repeated CV with reported spread, and resisting over-interpretation of any single feature
ranking. If the spread is large, the honest conclusion is "inconclusive at this sample size", not
the mean. Consider leave-one-out CV only for very small N, and confidence intervals on metrics.

## Always beat the baseline

Compare the imaging model against a **clinical-only** model (age and any standard clinical
variables). If radiomics does not improve on clinical variables alone, that is the finding —
report it. An imaging biomarker earns its place only by adding value over what is already known.

## Interpretation

Fit the pipeline once on all data **for interpretation only** (never for scoring) to read which
features survived selection and their importances/coefficients. State clearly that importance is
what the model *used*, not what is *causal*, and that correlated features swap ranks between runs.
