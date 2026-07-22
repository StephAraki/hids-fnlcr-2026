# PyRadiomics Guide

This guide governs two decisions the skill must not make blindly: which feature classes to
extract (Section 3.2 of the analysis plan) and what parameter file to extract them with
(Section 4 of the notebook). Read it before listing feature classes in a plan and before
generating any extraction code. It also documents the bundled, tested extraction component so
generated notebooks call a known-good implementation instead of re-deriving one each time.

## Status

This guide was added when the skill's execution layer was merged in (v0.3.0). Its parameter
settings ship as `scripts/radiomics_params.yaml` and its extraction logic as
`scripts/extract_radiomics.py`; both have been run end to end on real PyRadiomics 3.0.1
(numpy 1.26.4) against synthetic image/mask pairs, producing ~107 original-image features per
case with no errors. The feature-class recommendations by modality below follow published
radiomics practice and the IBSI standard, but the "best feature set for a given cancer type" is
ultimately an empirical, literature-guided choice — treat the tables here as sensible defaults to
surface to the researcher, not settled truth to apply silently.

## What a radiomic feature is (for the plain-language walkthrough)

A radiomic feature is one number describing the tumor region marked by the mask: how large it is,
how bright, how textured. PyRadiomics computes these in families. The point of extracting many is
that they are used together downstream, the way several lab values are read together rather than
one in isolation.

## Feature classes

| Class | Enables (`enableFeatureClassByName`) | What it measures |
|---|---|---|
| Shape | `shape` | Geometry of the mask alone: volume, surface area, sphericity, elongation, diameters. Intensity-independent. |
| First order | `firstorder` | Distribution of intensities inside the ROI: mean, median, energy, entropy, skewness, kurtosis, percentiles. |
| GLCM | `glcm` | Gray-level co-occurrence: contrast, correlation, homogeneity of adjacent intensity pairs. |
| GLRLM | `glrlm` | Run lengths of consecutive same-intensity voxels: coarse vs fine texture. |
| GLSZM | `glszm` | Sizes of connected same-intensity zones. |
| GLDM | `gldm` | How many neighbours match a voxel's intensity (dependence). |
| NGTDM | `ngtdm` | Neighbouring gray-tone difference: coarseness, busyness, contrast. |

The "non-uniformity" and "entropy" texture features quantify tumor heterogeneity, which is a
recurring signal in oncology imaging and usually worth including.

## Choosing feature classes by modality and question

Surface this choice to the researcher (it is a Section 3.2 decision), with a brief rationale:

- **Default starting set (most cancers, CT or MRI):** `shape`, `firstorder`, and all five texture
  families on the **original image only**. This yields ~100 features — enough signal for a
  proof of concept and small enough to defend against overfitting on a typical radiomics cohort.
- **CT (absolute Hounsfield units):** set `normalize: false`. HU are already comparable across
  scanners, so normalizing throws away real signal.
- **MRI (arbitrary intensity units):** set `normalize: true`. Without it, the model can learn the
  scanner instead of the biology. This is the single most important MRI-specific setting.
- **When shape is uninformative or the mask is unreliable:** you may drop `shape`, but say why.
- **Multi-parametric MRI (T1, T1CE, T2, FLAIR):** extract per sequence and concatenate features
  with a per-sequence prefix. Flag this as CP-02 (sequence selection) — different sequences carry
  different predictive value for different outcomes.

## Image types (filters) and the feature-count explosion

PyRadiomics can compute every family on filtered images too:

- `LoG` (Laplacian of Gaussian) at several sigmas — edge/blob emphasis at chosen scales.
- `Wavelet` (8 sub-bands) — texture at multiple frequency scales.

Enabling these multiplies the count into the hundreds to ~1500. On the small cohorts this skill
targets, that invites overfitting and demands aggressive selection. **Default to original-image
features only.** Only enable filters with a larger cohort and the leakage-safe selection scheme in
`references/model_selection.md`, and surface it to the researcher when you do — it is a
methodological choice, not a free upgrade.

## The parameter file (Section 4 extraction settings)

Generated notebooks should use the bundled `scripts/radiomics_params.yaml` rather than inlining a
different set of settings. Its choices, and why:

- `normalize: true`, `normalizeScale: 100` — standardise MRI intensities (turn off for CT).
- `binWidth: 25` — intensity-bin width for the texture matrices; a common default *after*
  normalization. Too small makes sparse noisy matrices; too large washes texture out. Keep it
  fixed across all patients.
- `resampledPixelSpacing: null` — set (e.g. `[1, 1, 1]`) if voxel spacing varies across the cohort,
  since texture depends on spacing. Leave null for already-standardised derivatives.
- `label: 1` — the mask value that marks the ROI. Change for multi-segment masks (CP-01).
- `geometryTolerance` / `correctMask: true` — tolerate and repair tiny image/mask grid mismatches.

## The bundled extraction component (use this in Section 4)

Do not hand-write a per-patient extraction loop in each generated notebook. Call the tested
component instead:

```python
# Batch extraction over a cohort manifest (patient_id, image_path, mask_path columns)
from extract_radiomics import extract_cohort   # scripts/extract_radiomics.py
features_df, failures = extract_cohort(cohort_df, params_path="scripts/radiomics_params.yaml")
```

or from the command line:

```bash
python scripts/extract_radiomics.py cohort_manifest.csv features.csv \
    --params scripts/radiomics_params.yaml
```

It handles per-case failures (an empty or misaligned mask does not sink the batch), keeps only the
real `original_`-prefixed features (dropping PyRadiomics `diagnostics_*` bookkeeping), and writes a
sidecar failures CSV. Section 4's markdown should still explain, at the researcher's expertise
level, what extraction is doing — see `references/notebook_structure.md`.

## Robustness caveat (state it in the notebook)

Radiomic features are sensitive to acquisition (scanner, protocol) and especially to the
**segmentation** — redraw the mask slightly and some features move a lot. This is why CP-01 (mask
selection) and CP-06 (normalization) exist. Serious studies quantify feature stability
(test–retest or multi-segmentation, via the intraclass correlation coefficient) and keep only
robust features. At minimum, a single-segmentation feature set is fragile; say so when reporting.

## Environment note

PyRadiomics 3.0.1 must run under **NumPy 1.x**. Its compiled C extension is NumPy-1.x ABI and
fails to import under NumPy 2.x, even after a source rebuild. See `references/environment_setup.md`
for the verified configuration and the reproduced failure.
