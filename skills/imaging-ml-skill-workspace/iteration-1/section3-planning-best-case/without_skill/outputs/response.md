# Analysis Plan: Predicting pCR from Pre-Treatment DCE-MRI Radiomics in Breast Cancer

This is a well-posed radiomics problem with a natural cohort to anchor it: **ACRIN-6698 (I-SPY 2 sub-study)** was specifically designed to evaluate quantitative DCE-MRI and DWI metrics as early predictors of pathologic complete response (pCR) to neoadjuvant chemotherapy in breast cancer. Pairing the imaging with clinical/treatment-response variables is exactly the right approach, since pCR is determined at surgery and needs to be pulled from the clinical data side, not the imaging side.

Below is an end-to-end plan, organized the way I'd actually execute it.

---

## 1. Define the cohort and endpoint

- **Population:** Breast cancer patients enrolled in ACRIN-6698 who underwent neoadjuvant chemotherapy (NAC) and had baseline (pre-treatment) DCE-MRI.
- **Outcome:** Pathologic complete response (pCR), defined per the trial's pathology criteria (typically ypT0/Tis ypN0, i.e., no residual invasive disease in breast or axillary nodes). Treat this as binary: pCR vs. non-pCR (residual disease, RD).
- **Timepoint of interest:** Only the **pre-treatment (baseline, T0)** MRI exam is in scope per your question — note that ACRIN-6698 collected multiple timepoints (baseline, after 1 cycle, after all cycles before surgery), so you'll need to filter to the baseline visit only when pulling images.

**Open question for you:** Do you want pCR defined strictly at the breast level, or breast + nodal (ypN0)? This affects how you derive the label from CTDC fields, and I don't want to assume which convention your downstream comparison (e.g., to I-SPY 2 publications) expects.

---

## 2. Data acquisition

### 2a. Imaging data (IDC)
- Use the `idc-index` Python package to query and download the ACRIN-6698 collection.
- Filter to baseline timepoint DCE-MRI series (you'll need to inspect the series descriptions, e.g., "VOLSER" or early/late post-contrast phase labels — ACRIN-6698 includes multiple DCE phases per timepoint, so identify which series corresponds to pre-contrast and peak/early post-contrast).
- Download as DICOM, then convert to NIfTI or a volumetric array format for processing (e.g., via `dcm2niix` or `pydicom` + manual volume assembly, since DCE series can have non-trivial sorting by acquisition time/phase).

**I want to flag clearly: I do not have verified, up-to-date knowledge of the exact current series-naming conventions, total patient count, or download size for ACRIN-6698 as hosted in IDC.** IDC's collection contents and metadata schemas are periodically updated, and I can't confirm from memory what the live `idc-index` query will return. Please run a metadata query first (see code below) and inspect the actual series descriptions before assuming my guesses about phase labeling are correct.

### 2b. Clinical / treatment-response data (CTDC)
- Pull patient-level clinical variables: age, hormone receptor (ER/PR) status, HER2 status, baseline tumor stage, treatment arm/regimen, and the pCR outcome variable itself.
- **Critical step:** identify the correct patient/case identifier that lets you join CTDC records to IDC `PatientID`/`StudyInstanceUID`. ACRIN trials typically use a consistent case ID across CRDC commons, but the exact field names in CTDC's data model I cannot state with confidence from memory — you'll need to inspect the CTDC schema directly (e.g., via its GraphQL API or data dictionary) to find the matching key.

**Open question for you:** Do you already know the join key CTDC uses for ACRIN-6698 cases, or do you need help discovering it? This is often the single biggest practical blocker in these federated-commons workflows, and I'd rather you verify it against the live schema than have me guess a field name that turns out to be wrong.

---

## 3. Preprocessing pipeline

1. **DICOM → volume conversion:** Assemble the DCE series into a 3D (or 4D, if keeping multiple post-contrast phases) array per patient, per timepoint.
2. **Tumor segmentation:** You need a tumor ROI/mask to extract radiomics features.
   - Check whether ACRIN-6698 in IDC ships with annotation/segmentation data (some IDC collections include expert-drawn or qualitative-image-analysis-derived segmentations). If not, you'll need to either find a published segmentation method/model for this dataset or perform manual/semi-automated segmentation — this is a major scope decision and worth discussing before you proceed, since it materially affects timeline.
   - If segmentations exist in IDC as a companion SEG/RTSTRUCT object, load and align them with the source DCE series.
3. **Intensity normalization:** DCE-MRI signal intensities are not directly comparable across scanners/sites (ACRIN-6698 is multi-site). Consider normalizing using a reference tissue or z-scoring within-patient before feature extraction, or working with derived parametric maps (e.g., percent enhancement, washout) rather than raw intensities if available.
4. **Resampling:** Resample to isotropic voxel spacing for radiomics feature reproducibility (per IBSI — Image Biomarker Standardisation Initiative — recommendations).

---

## 4. Radiomics feature extraction

- Use **PyRadiomics**, the standard, IBSI-aligned open-source library, to extract features from the tumor ROI on the pre-treatment DCE volume:
  - Shape features (volume, sphericity, surface area)
  - First-order intensity statistics (mean, skewness, kurtosis, entropy)
  - Texture features (GLCM, GLRLM, GLSZM, GLDM, NGTDM)
- If you have multiple DCE phases, you can extract features per phase and/or derive kinetic features (e.g., signal enhancement ratio, time-to-peak) — kinetic/pharmacokinetic-style features are particularly relevant here since ACRIN-6698's original hypothesis centered on functional tumor volume and quantitative kinetic parameters as response predictors, not just static texture.
- Apply a fixed bin width/count for intensity discretization per IBSI guidelines, and document your parameter file (PyRadiomics uses a YAML params file) for reproducibility.

---

## 5. Feature selection and dimensionality reduction

Given a likely small-to-moderate sample size (neoadjuvant imaging trial cohorts are typically in the low hundreds of patients at most, and after baseline-imaging-availability and quality filtering the usable N is often smaller), radiomics feature counts (~100+) will vastly exceed sample size. This is the most important methodological risk in the whole plan.

- **I don't have a reliable, verifiable number for the exact enrolled/evaluable patient count in ACRIN-6698** — please pull this from the CTDC cohort query directly rather than relying on a figure I might state, since I can't confirm it precisely from memory and don't want to give you a wrong number to plan around.
- Use the CTDC query and IDC availability join to get your **actual** usable N before deciding on a feature selection strategy. As a rule of thumb for this kind of problem:
  - With N in the 50–150 range, plan for aggressive dimensionality reduction (e.g., top-k via mRMR or LASSO-embedded selection) down to single-digit-to-low-teens features before modeling.
  - Use nested cross-validation so that feature selection happens only within training folds, never leaking into the held-out fold.

---

## 6. Modeling

Given intermediate Python skill and a likely small N, I'd recommend starting simple and adding complexity only if justified:

1. **Baseline:** Logistic regression with L1/L2 regularization (LASSO/Ridge) on selected radiomics features ± clinical covariates (HR/HER2 status, tumor stage). This is interpretable and a reasonable first benchmark.
2. **Tree-based:** Random Forest or gradient boosting (XGBoost/LightGBM) as a comparison — often more robust to feature redundancy.
3. **Combined model:** Radiomics + clinical features together, compared against radiomics-only and clinical-only models, to assess incremental value of imaging.

**Validation strategy:**
- Given likely small N, use **nested stratified k-fold cross-validation** (e.g., 5-fold outer, 5-fold inner for hyperparameter tuning) rather than a single train/test split, to get a more stable performance estimate.
- Stratify folds by pCR status to preserve class balance, and check for site/scanner imbalance across folds if that metadata is available (multi-site harmonization can matter for DCE-MRI radiomics).
- Report AUC-ROC, sensitivity/specificity at a clinically reasonable threshold, and calibration — not just accuracy, since pCR rates are typically well below 50%, so the classes will be imbalanced.

---

## 7. Evaluation and reporting

- Primary metric: **AUC-ROC** with 95% CI (bootstrap).
- Secondary: sensitivity, specificity, PPV/NPV at a chosen operating point; calibration plot.
- Compare radiomics-only vs. clinical-only vs. combined models with DeLong's test or bootstrap comparison of AUCs.
- Report feature importance / selected features for interpretability, and sanity-check whether selected features have plausible biological correspondence (e.g., texture heterogeneity, enhancement kinetics) rather than treating it as a pure black box.

---

## Open items I need from you before this is fully executable

1. **pCR definition** — breast-only vs. breast+nodal (ypN0)?
2. **CTDC join key** — do you already know how ACRIN-6698 case IDs map between CTDC and IDC, or should we investigate the schema together?
3. **Segmentation availability** — do you know if IDC hosts tumor segmentations for this collection, or do you have access to/plan to create your own?
4. **Actual cohort size** — I'd rather you run the CTDC/IDC queries and report back the real evaluable N than have me plan around a guessed number.

---

## Suggested next step

Run a metadata-only query first (no large downloads) against both IDC and CTDC to confirm: (a) how many ACRIN-6698 patients have baseline DCE-MRI in IDC, (b) how many have a recorded pCR outcome in CTDC, and (c) the overlap between the two. That intersection is your real working sample size, and it should drive every downstream decision (especially feature selection aggressiveness) rather than planning around an assumed number.

```python
# Step 0: Environment setup
# pip install idc-index pyradiomics pydicom SimpleITK scikit-learn pandas numpy requests

from idc_index import IDCClient

client = IDCClient()

# Inspect what's available for ACRIN-6698 — confirm collection id naming before relying on it
collections = client.get_collections()
print([c for c in collections if "acrin" in c.lower() or "6698" in c.lower()])
```

```python
# Step 1: Query series-level metadata for the collection (adjust collection_id once confirmed above)
collection_id = "ACRIN-6698"  # confirm exact string from the query above before downloading

series_df = client.sql_query(f"""
    SELECT PatientID, StudyInstanceUID, SeriesInstanceUID, Modality, SeriesDescription
    FROM index
    WHERE collection_id = '{collection_id.lower()}'
""")
print(series_df.head())
print(series_df['SeriesDescription'].unique())  # inspect before assuming baseline-phase naming
```

```python
# Step 2 (placeholder): once you've confirmed which SeriesDescription values correspond to
# the pre-treatment baseline DCE acquisition, filter and download only those series.
baseline_series = series_df[series_df['SeriesDescription'].str.contains(
    "REPLACE_WITH_CONFIRMED_BASELINE_LABEL", case=False, na=False
)]

client.download_from_selection(
    seriesInstanceUID=baseline_series['SeriesInstanceUID'].tolist(),
    downloadDir="./acrin6698_baseline_dce"
)
```

```python
# Step 3: CTDC clinical data — pseudocode, since exact GraphQL schema fields need to be
# confirmed against the live CTDC API/data dictionary rather than assumed here.
import requests

CTDC_GRAPHQL_ENDPOINT = "https://CONFIRM_ACTUAL_ENDPOINT"  # verify current endpoint

query = """
{
  # Replace with confirmed node/field names from the CTDC data model
  # for ACRIN-6698 cases: case_id, pCR/pathologic_response field,
  # ER/PR/HER2 status, treatment arm, etc.
}
"""
# response = requests.post(CTDC_GRAPHQL_ENDPOINT, json={"query": query})
# clinical_df = pd.json_normalize(response.json())
```

```python
# Step 4: Join imaging and clinical cohorts on the (to-be-confirmed) shared case identifier
# merged_df = baseline_series.merge(clinical_df, left_on="PatientID", right_on="case_id", how="inner")
# print(f"Usable cohort size after join: {merged_df['PatientID'].nunique()}")
```

```python
# Step 5: Radiomics extraction (once images + segmentation masks are in hand)
import radiomics
from radiomics import featureextractor

params = {
    "binWidth": 25,
    "resampledPixelSpacing": [1, 1, 1],
    "interpolator": "sitkBSpline",
}
extractor = featureextractor.RadiomicsFeatureExtractor(**params)

# for each patient:
# result = extractor.execute(image_path, mask_path)
# features[patient_id] = {k: v for k, v in result.items() if not k.startswith("diagnostics")}
```

```python
# Step 6: Modeling with nested cross-validation
import numpy as np
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.metrics import roc_auc_score

# X = feature_df.values, y = pCR_labels (0/1)

outer_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
inner_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

pipe = Pipeline([
    ("scale", StandardScaler()),
    ("select", SelectKBest(score_func=f_classif)),
    ("clf", LogisticRegression(penalty="l1", solver="liblinear", max_iter=5000)),
])

param_grid = {
    "select__k": [5, 10, 15],
    "clf__C": [0.01, 0.1, 1, 10],
}

outer_scores = []
# for train_idx, test_idx in outer_cv.split(X, y):
#     X_train, X_test = X[train_idx], X[test_idx]
#     y_train, y_test = y[train_idx], y[test_idx]
#     grid = GridSearchCV(pipe, param_grid, scoring="roc_auc", cv=inner_cv)
#     grid.fit(X_train, y_train)
#     preds = grid.predict_proba(X_test)[:, 1]
#     outer_scores.append(roc_auc_score(y_test, preds))

# print(f"Nested CV AUC: {np.mean(outer_scores):.3f} +/- {np.std(outer_scores):.3f}")
```

This code is scaffolding, not a finished pipeline — several pieces (collection ID string, series description filters, CTDC endpoint/schema, segmentation source) need to be confirmed against the live systems before they'll run correctly. I'd rather hand you a structurally sound plan with explicit verification points than a pipeline that silently runs on wrong assumptions about field names or sample sizes.
