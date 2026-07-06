# Analysis Plan: Predicting Breast Cancer Recurrence from Imaging Features

Since you don't have a cohort selected yet, I'll lay out a general-purpose plan that you can adapt once you pick a data source. I'll flag the key decisions you'll need to make along the way and give you a realistic sense of sample size.

## 1. Define the Clinical Question Precisely

Before touching data, nail down:

- **Recurrence type**: Local recurrence, regional recurrence, distant metastasis, or any recurrence? These have different biology and different imaging correlates.
- **Time horizon**: 2-year recurrence? 5-year? 10-year? This determines your follow-up requirements and censoring approach.
- **Population**: All breast cancer, or a specific subtype (e.g., triple-negative, HER2+, ER+/HR+)? Recurrence biology differs substantially by subtype, and pooling subtypes without adjustment will confound your imaging signal.
- **Treatment context**: Pre-treatment imaging (prognostic biomarker) vs. post-neoadjuvant imaging (predicting residual disease/response) vs. surveillance imaging (detecting recurrence directly). These are fundamentally different prediction tasks.
- **Imaging modality**: Mammography, breast MRI, ultrasound, or multi-modal? Each has different feature extraction pipelines and different evidence bases for recurrence prediction.

For the rest of this plan I'll assume the most common framing in the literature: **pre-treatment breast MRI or mammography features predicting distant recurrence within 5 years**, since that's the most studied setup. Adjust as needed once you've scoped your actual question.

## 2. Cohort Identification and Expected Sample Size

You mentioned you don't have a cohort yet — this is the biggest open variable in the plan, so let's reason about it concretely.

**Public/consortium options to consider:**
- **TCGA-BRCA** (The Cancer Genome Imaging Archive companion to TCGA breast cohort): commonly cited as having genomic, clinical, and some imaging data for roughly **1,000–1,100 patients**, though only a subset (often cited around **130–150 patients**) have usable pre-treatment MRI in the associated imaging collections.
- **I-SPY 1/2 trials**: neoadjuvant breast MRI trials; I-SPY 1 enrolled approximately **230 patients**, and I-SPY 2 is an adaptive platform trial that has enrolled over **2,000 patients** cumulatively, though access typically requires a data use agreement and the "recurrence" endpoint specifically would need to be derived from linked outcomes data.
- **Institutional retrospective cohort**: if you're pulling from your own institution's PACS/EHR, a typical single-center retrospective study of breast cancer patients with pre-treatment imaging and 5-year follow-up might yield **200–800 patients**, depending on institution size and years covered, but you'd need to budget significant time for chart review and outcome curation.

**My honest caveat: I don't have verified, up-to-date enrollment numbers for these cohorts in front of me** — the figures above are approximate and based on general familiarity with these datasets, not a live lookup. Before finalizing your sample size assumptions, you should independently verify current cohort sizes and data availability (e.g., via TCIA's website, the I-SPY trial data portals, or your institution's data warehouse), since these numbers shift as data is released or embargoed.

**Expected usable sample size after exclusions:**
As a rule of thumb, expect significant attrition from the "enrolled" number to the "usable for this analysis" number:
- Exclude patients without baseline imaging in the modality of interest
- Exclude patients with insufficient follow-up (loss to follow-up before your time horizon)
- Exclude patients with missing recurrence/outcome annotation
- Exclude poor-quality or non-conforming imaging studies

A reasonable planning assumption is that you'll retain **50-70% of an initial candidate pool** after these exclusions. If recurrence events are the minority class (often only 15-25% of patients recur within 5 years in early-stage breast cancer), your **effective number of positive events** will be much smaller than your total N — this is the number that really constrains model complexity.

**Suggested target**: For a binary recurrence classifier with a handful of imaging features, aim for **at least 200-300 patients total** with **at least 30-50 recurrence events**, as a bare minimum for a stable model. For deep learning / radiomics approaches with many features, you'll want closer to **500+ patients** or you'll need to lean heavily on transfer learning, pretrained feature extractors, and aggressive regularization.

## 3. Data Elements Needed

| Category | Elements |
|---|---|
| Imaging | Baseline (and optionally follow-up) breast MRI or mammography, ideally DICOM with segmentation/ROI |
| Clinical | Age, menopausal status, tumor stage, grade, ER/PR/HER2 status, Ki-67 if available |
| Treatment | Surgery type, chemotherapy regimen, radiation, endocrine therapy |
| Outcome | Recurrence (yes/no), recurrence type, time to recurrence, time to last follow-up, vital status |
| Genomic (optional) | Oncotype DX / MammaPrint recurrence score if available, for comparison/calibration |

## 4. Feature Extraction Approach

Two broad tracks, often combined:

1. **Handcrafted radiomics**: shape, texture (GLCM, GLRLM), intensity histogram features extracted via a tool like PyRadiomics, following the IBSI (Image Biomarker Standardisation Initiative) guidelines for reproducibility.
2. **Deep learning features**: embeddings from a pretrained CNN (e.g., a model pretrained on a large mammography or natural-image corpus), either used directly or fine-tuned.

Recommend starting with radiomics for interpretability and a smaller data requirement, then exploring deep learning if sample size allows.

## 5. Modeling Plan

- **Primary endpoint**: Binary recurrence at fixed horizon (e.g., 5 years) OR time-to-event (recommend Cox proportional hazards or a survival-aware deep model if you have reliable censoring data — time-to-event is more statistically efficient than binarizing).
- **Baseline model**: Logistic regression / Cox model with clinical variables only (age, stage, grade, receptor status) — this is your benchmark.
- **Imaging model**: Clinical + radiomics features, with feature selection (e.g., LASSO) given likely high dimensionality relative to N.
- **Combined model**: Test whether imaging adds incremental value over clinical variables alone (this is often the actual scientific question reviewers care about).
- **Validation strategy**: 
  - Nested cross-validation if single-cohort (e.g., 5-fold outer, 3-fold inner for hyperparameter tuning)
  - External validation cohort if at all possible — single-cohort radiomics studies without external validation are a well-known reproducibility weak point in this literature
  - Report calibration (calibration plots, Brier score) in addition to discrimination (AUC/C-index)

## 6. Statistical Considerations

- Pre-register your primary endpoint and analysis plan if this is for publication, to avoid endpoint-shopping.
- Correct for multiple comparisons if testing many radiomic features individually.
- Given likely class imbalance (recurrence is the minority outcome), consider reporting AUPRC alongside AUROC, and avoid accuracy as a primary metric.
- Use DeLong's test or similar to compare AUCs between nested models (clinical-only vs. clinical+imaging).

## 7. Reporting Standards

Plan to write up using:
- **TRIPOD** (Transparent Reporting of a multivariable prediction model for Individual Prognosis Or Diagnosis) guidelines for the prediction model itself
- **METRICS** or **IBSI** guidelines if radiomics is central
- **CLEAR checklist** if this is a deep-learning-based radiomics study

## 8. Suggested Timeline (rough)

| Phase | Duration |
|---|---|
| Cohort finalization & IRB | 4-8 weeks |
| Data curation & QC | 4-8 weeks |
| Feature extraction | 2-4 weeks |
| Modeling & validation | 4-6 weeks |
| Write-up | 4 weeks |

## Open Questions for You

To tighten this plan into something concrete, I'd need you to clarify:
1. Which cohort(s) are you actually able to access (institutional, public, consortium)?
2. What's your imaging modality — MRI, mammography, ultrasound, or multiple?
3. Is this prognostic (pre-treatment) or about detecting recurrence directly on surveillance imaging?
4. Do you have existing follow-up/outcomes data, or does that need to be curated from scratch?
5. Is there an IRB/data use agreement already in place, or does that need to be initiated?

Once you have a candidate cohort, I can help you size the analysis more precisely and sanity-check whether the event count will support the model complexity you have in mind.
