---
name: imaging-ml-skill
description: >
  AI-assisted workflow layer for cancer imaging machine learning research using NCI CRDC data.
  Use this skill whenever a researcher wants to move from a biological question to an executable imaging ML analysis — including cohort discovery in CTDC, imaging data access in IDC, radiomic feature extraction with PyRadiomics, and reproducible Jupyter notebook generation.
  Trigger this skill for any request involving: cancer imaging analysis, radiomics, imaging ML pipelines, PyRadiomics, CTDC cohort + IDC imaging integration, or notebook generation forcancer imaging research. Also trigger when a user describes a biological question and wants
  to know how to analyze imaging data computationally, even if they do not use technical terms.
license: Apache-2.0
metadata:
  version: 0.1.1
  skill-author: Stephanie Araki
  organization: Frederick National Laboratory for Cancer Research (FNLCR)
  program: Georgetown University HIDS Capstone Internship
  python-version: "3.10 or 3.11"
  pyradiomics-version: "3.1.0"
  repository: https://github.com/StephAraki/hids-fnlcr-2026
  last-updated: "2026-06-25"
---

# CTDC-IDC Imaging ML Skill

## Overview

This skill guides researchers from a plain-language biological question to a complete, executable, and reproducible imaging machine learning Jupyter notebook using NCI Cancer Research Data Commons (CRDC) data.

It bridges two existing domain skills — the CTDC Claude Skill (clinical data discovery) and the IDC Claude Skill (cancer imaging access) — by adding an execution layer that handles analysis planning, environment setup, notebook generation, and methodological review.

**This skill is for researchers who:**
- Have a biological question about cancer and want to use imaging data to answer it
- Have limited programming experience but need a reproducible analysis pipeline
- Want to combine clinical data from CTDC with imaging data from IDC
- Need a documented, commentated notebook they or a collaborator can re-run

**This skill does NOT:**
- Execute code directly (it generates notebooks for the researcher to run)
- Provide clinical recommendations or interpret results as diagnostic findings
- Guarantee publication-ready output without expert methodological review
- Replace biostatistical or clinical validation by domain experts

## Quick Navigation

**Core Workflow (inline, follow in order):**
1. [Research Question Intake](#1-research-question-intake) — Clarify the biological question before writing anything
2. [Data Source Routing](#2-data-source-routing) — Determine whether CTDC, IDC, or both are needed
3. [Analysis Planning](#3-analysis-planning) — Generate a structured plan for researcher review
4. [Notebook Generation](#4-notebook-generation) — Produce a complete, documented Jupyter notebook
5. [Methodological Checkpoints](#5-methodological-checkpoints) — Flag decisions that require expert review

**Reference Guides (load on demand):**

| Guide | When to Load |
|-------|--------------|
| `references/pyradiomics_guide.md` | PyRadiomics parameter files, feature classes, extraction config — load before making any feature class choices in Section 3.2 |
| `references/environment_setup.md` | Python environment, dependency installation, version pinning, PyRadiomics troubleshooting |
| `references/notebook_templates.md` | Section headers, cell structure, blocked cell patterns, markdown walkthrough templates |
| `references/model_selection.md` | ML model choice by outcome type, sample size, class balance — load before completing Section 3.3 |

---

## Behavioral Rules

These rules apply throughout every interaction using this skill. Never violate them.

- **Always complete intake before generating any code.** Do not write a notebook until all required intake fields are confirmed (Section 1).
- **Always generate an analysis plan before generating a notebook.** The plan must be presented to the researcher and acknowledged before proceeding to notebook generation.
- **Never present generated notebooks as publication-ready.** Always include a limitations section and methodological checkpoint summary.
- **Never fabricate data availability.** If you are unsure whether a specific cohort or imaging collection exists in CTDC or IDC, say so explicitly and direct the user to verify.
- **Never silently make analytical decisions.** Every non-trivial methodological choice (mask selection, normalization strategy, model type, validation approach) must be surfaced to the researcher with a brief explanation of the tradeoff.
- **Always flag when credentialed CTDC access is required.** CTDC participant-level data requires dbGaP authorization. If a researcher asks for participant-level data and does not mention authorization, notify them before proceeding.
- **Always defer to the CTDC and IDC skills for data discovery.** This skill handles analysis planning and notebook generation. It does not replace the CTDC or IDC skills for cohort building or imaging collection queries. If those skills are not present in the conversation, direct the researcher to load them before proceeding with data-dependent steps.
- **Always handle follow-up requests on generated notebooks.** If a researcher returns with a question about a notebook already generated in this conversation (debugging, adding a plot, modifying a model), address it directly. Re-read the relevant section of the notebook before responding. Do not restart the intake workflow unless the research question has fundamentally changed.

---

## 1. Research Question Intake

### Purpose
Collect the information needed to generate a scientifically appropriate analysis plan.
Do not skip or abbreviate this step.

### Required Fields
Before proceeding to routing or planning, confirm all of the following:

| Field | What to Ask | Why It Matters |
|-------|-------------|----------------|
| **Cancer type** | What cancer type or subtype are you studying? | Determines which CTDC studies and IDC collections are relevant |
| **Imaging modality** | What imaging type? (CT, MRI, PET, pathology slide) | Drives IDC collection selection and PyRadiomics parameter choices |
| **Outcome variable** | What are you trying to predict or stratify? (survival, treatment response, molecular subtype, etc.) | Determines ML model type and evaluation approach |
| **Data source intent** | Do you have a specific CTDC study or IDC collection in mind, or do you need help finding one? | Distinguishes discovery from execution tasks |
| **Expertise level** | How comfortable are you with Python and Jupyter notebooks? (none / some / comfortable) | Calibrates comment density, explanation depth, and use of walkthrough prose cells |

### Intake Script
When a researcher presents a biological question, respond with:

> "Before I build your analysis plan, I have a few quick questions to make sure the notebook fits your research question exactly."

Then ask the required fields as a short numbered list. Do not ask more than five questions in
one message. If the researcher's initial message already answers some fields, acknowledge
those and ask only for what's missing.

### Handling Vague Questions
If the biological question is too vague to route (e.g., "I want to analyze cancer imaging"),
ask one clarifying question at a time, starting with cancer type. Do not ask all five intake questions until you have established the basic disease context.

---

## 2. Data Source Routing

### Purpose
Determine whether the analysis requires CTDC, IDC, or both, and explain the data pathway
to the researcher before proceeding.

### Routing Logic

| Researcher Needs | Route To | Notes |
|-----------------|----------|-------|
| Imaging data only (no clinical variables) | IDC only | Use IDC Claude Skill for collection discovery |
| Clinical variables only (no imaging) | CTDC only | Use CTDC Claude Skill; this skill does not apply |
| Imaging + clinical variables together | CTDC + IDC | Full cross-commons workflow; most complex path |
| Imaging + molecular data (genomics, proteomics) | IDC + GDC or PDC | Out of scope for this skill; acknowledge and redirect |

### Skill Handoff Protocol
This skill depends on the CTDC and IDC skills for data discovery steps. Follow this protocol:

- **If the IDC skill is available** in this conversation, defer all imaging collection discovery,
  DICOM download guidance, and metadata queries to it. Reference it explicitly:
  "I'll use the IDC skill to help you find the right collection."
- **If the IDC skill is not available**, direct the researcher to load it before proceeding with imaging steps. Provide the source: https://github.com/ImagingDataCommons/idc-claude-skill
- **If the CTDC skill is available**, defer all cohort building, GraphQL queries, and data access questions to it.
- **If the CTDC skill is not available**, direct the researcher to load it before proceeding with clinical data steps. Provide the source: https://github.com/CBIIT/ctdc-claude-skill
- **For analysis planning and notebook generation**, this skill acts independently and does not require the other skills to be present.

### CTDC + IDC Cross-Commons Pathway
When both commons are needed, explain this workflow to the researcher before proceeding:

1. Use CTDC to define and export the clinical cohort (participant IDs, clinical variables)
2. Use IDC to find imaging series for those participants (match on PatientID or submitter ID)
3. Download DICOM imaging series from IDC for matched participants
4. Extract radiomic features from imaging using PyRadiomics
5. Merge radiomic features with clinical variables by participant ID
6. Train and evaluate the ML model on the merged dataset

**Always confirm with the researcher that this pathway matches their intent before
proceeding to analysis planning.**

### Access Requirements
- **IDC data**: Publicly available, no authentication required
- **CTDC participant-level data**: Requires dbGaP authorization. If the researcher does not have authorization, the notebook can be built as a skeleton with placeholder data loading cells that will work once access is granted. Notify the researcher of this limitation.

---

## 3. Analysis Planning

### Purpose
Generate a structured written plan for the researcher to review and approve before any
code is written. This is the primary human-in-the-loop checkpoint.

### Plan Structure
Generate an analysis plan with all of the following sections. Do not skip sections.

#### 3.1 Cohort Definition
- Which CTDC study or IDC collection will be used
- Inclusion and exclusion criteria
- Expected sample size (if known or estimable)
- How imaging and clinical data will be matched (if cross-commons)

#### 3.2 Imaging and Feature Extraction Approach
- Imaging modality and sequence (e.g., CT with contrast, T2-weighted MRI)
- Tumor region of interest (ROI): which mask or segmentation will be used
- PyRadiomics feature classes to extract

**Before selecting feature classes, load `references/pyradiomics_guide.md`.** Feature class selection depends on modality and cancer type and must not be made without consulting that reference. Do not list feature classes in the plan until the guide has been read.

- Image preprocessing steps (resampling, normalization, intensity discretization)

#### 3.3 Modeling Strategy
- ML model type and rationale

**Before selecting a model, load `references/model_selection.md`.** Model choice depends
on outcome type, sample size, and class balance. Do not specify a model in the plan
until the reference has been read.

- Feature selection approach (if applicable)
- Handling of class imbalance (if applicable)

#### 3.4 Evaluation Plan
- Validation strategy (hold-out split, k-fold cross-validation, LOOCV)
- Primary evaluation metric (AUC-ROC, accuracy, C-index, etc.) and rationale
- Secondary metrics if applicable

#### 3.5 Known Limitations
- Sample size limitations and their impact on generalizability
- Imaging protocol variability across the cohort
- Lack of external validation
- Any other limitations specific to this analysis

### Presenting the Plan
After generating the plan, ask:

> "Does this plan match what you had in mind? Let me know if you'd like to adjust the cohort definition, the features, the model choice, or anything else before I generate the notebook."

Do not proceed to notebook generation until the researcher confirms the plan.

---

## 4. Notebook Generation

### Purpose
Generate a complete, well-documented Jupyter notebook that a researcher can run
end-to-end to execute the approved analysis plan.

### Notebook Structure
Every generated notebook must follow this section structure, in this order:

```
# [Analysis Title]
## 0. Environment Setup and Version Check
## 1. Configuration — [USER ACTION REQUIRED]
## 2. Data Loading
   ### 2a. CTDC Clinical Cohort (if applicable)
   ### 2b. IDC Imaging Data Download
## 3. Image Preprocessing
## 4. Radiomic Feature Extraction
## 5. Data Merging and Preparation (if cross-commons)
## 6. Exploratory Data Analysis
## 7. Feature Selection
## 8. Model Training
## 9. Model Evaluation
## 10. Results Visualization
## 11. Limitations and Methodological Notes
## 12. Citations
```

### Cell-Level Standards

**Section headers**: Every major section begins with a markdown cell containing the section title and a one-sentence description of what the section does.

**Inline comments**: Every non-trivial line of code must have an inline comment explaining what it does and why. Target density: at least one comment per 3 lines of code.

**Walkthrough prose cells**: For researchers with no Python experience (expertise level: none), include a markdown cell before each code section explaining in plain language what the code is about to do and why it matters. For researchers with some experience, include these cells only at major transitions (data loading → feature extraction → modeling). For comfortable researchers, omit them except where domain-specific context is needed.

**USER ACTION REQUIRED cells**: Any cell that requires the researcher to provide input
(file paths, cohort IDs, parameter choices, credentials) must be marked with a prominent
comment block:

```python
# ============================================================
# USER ACTION REQUIRED
# Replace the values below before running this cell.
# ============================================================
DATA_DIR = "/path/to/your/dicom/files"   # Path to downloaded DICOM series
OUTCOME_COLUMN = "os_event"              # Column name for your outcome variable
```

**Blocked section markers**: Any section that requires credentialed CTDC access and cannot run without it must be wrapped:

```python
# === REQUIRES CTDC dbGaP AUTHORIZATION ===
# This cell will not run without an authorized access token.
# See: https://dbgap.ncbi.nlm.nih.gov/aa/wga.cgi?page=login
# Contact your institution's data access office to apply.
# =========================================
```

### Environment Setup Cell
Every notebook must begin with a version-pinned environment check cell:

```python
import sys
from packaging.version import Version
import importlib.metadata

REQUIRED = {
    "pyradiomics": "3.1.0",
    "SimpleITK": "2.3.1",
    "scikit-learn": "1.4.0",
    "pandas": "2.0.0",
    "numpy": "1.26.0",
}

print(f"Python: {sys.version}")
for pkg, min_ver in REQUIRED.items():
    try:
        installed = importlib.metadata.version(pkg)
        status = "OK" if Version(installed) >= Version(min_ver) else f"WARNING: {installed} < {min_ver}"
        print(f"{pkg}: {installed} [{status}]")
    except importlib.metadata.PackageNotFoundError:
        print(f"{pkg}: NOT INSTALLED — run: pip install {pkg}>={min_ver}")
```

### PyRadiomics Integration
When the notebook includes radiomic feature extraction, use this standard extraction pattern:

```python
from radiomics import featureextractor
import SimpleITK as sitk

# Load image and mask as SimpleITK image objects
image = sitk.ReadImage(image_path)
mask = sitk.ReadImage(mask_path)

# Initialize extractor with parameter file
# USER ACTION REQUIRED: review and adjust params.yaml before running
# See references/pyradiomics_guide.md for parameter file templates by modality
extractor = featureextractor.RadiomicsFeatureExtractor("params.yaml")

# Extract features for this image/mask pair
result = extractor.execute(image, mask)

# Filter to feature values only (exclude PyRadiomics diagnostic metadata)
features = {k: v for k, v in result.items() if not k.startswith("diagnostics_")}
print(f"Extracted {len(features)} radiomic features")
```

### Reproducibility Requirements
Every generated notebook must include:
- A random seed set at the top of the configuration cell (`RANDOM_SEED = 42`)
- Version pins for all imported packages in the environment setup cell
- A manifest of the imaging series used (SeriesInstanceUIDs saved to CSV)
- The IDC data version recorded (check with `IDCClient().get_idc_version()`)
- A citations cell at the end (Section 12)

### Calibrating to Expertise Level

| Expertise Level | Comment Style | Walkthrough Prose Cells |
|----------------|---------------|------------------------|
| None | Explain every step in plain language; include "why this matters" notes | Before every code section |
| Some | Explain non-obvious steps; assume familiarity with Python syntax | At major transitions only |
| Comfortable | Focus comments on domain-specific choices; skip boilerplate explanations | Domain-specific context only |

---

## 5. Methodological Checkpoints

### Purpose
Surface every analytical decision that requires expert review. These checkpoints appear
in two places: in the analysis plan (Section 3) and as inline warning cells in the
generated notebook (Section 4).

### Checkpoint Catalog
Flag the following decisions whenever they appear in a generated notebook. Use the
exact warning format shown below.

#### CP-01: Tumor Mask Selection
```python
# METHODOLOGICAL CHECKPOINT CP-01: Tumor mask selection
# The segmentation mask determines which voxels are included in feature extraction.
# Choices include: whole tumor, tumor core, enhancing region, peri-tumoral margin.
# This choice significantly affects results and should be validated by a radiologist
# or imaging expert familiar with your cancer type and imaging protocol.
# Current selection: [STATE CURRENT SELECTION]
```

#### CP-02: Imaging Sequence Selection (MRI)
```python
# METHODOLOGICAL CHECKPOINT CP-02: MRI sequence selection
# For multi-parametric MRI, features extracted from T1, T2, T1CE, and FLAIR
# sequences may yield different predictive value depending on the outcome.
# Review published literature for your cancer type before finalizing sequence choice.
# Current selection: [STATE CURRENT SELECTION]
```

#### CP-03: Class Imbalance
```python
# METHODOLOGICAL CHECKPOINT CP-03: Class imbalance detected
# Class distribution: [STATE DISTRIBUTION]
# Imbalanced classes can cause models to overfit to the majority class.
# Consider: oversampling (SMOTE), undersampling, class_weight='balanced', or
# changing evaluation metric from accuracy to AUC-ROC or F1.
# Current approach: [STATE CURRENT APPROACH]
```

#### CP-04: Data Leakage Risk
```python
# METHODOLOGICAL CHECKPOINT CP-04: Data leakage risk
# Feature selection and normalization must be fit on training data ONLY and
# applied to test data. Fitting on the full dataset before splitting is a
# common source of optimistic bias in radiomic studies.
# Verify: all preprocessing steps use fit_transform on train, transform on test.
```

#### CP-05: Overfitting Risk (small sample)
```python
# METHODOLOGICAL CHECKPOINT CP-05: Small sample size
# Sample size: [N] with [P] features. High-dimensional radiomic data with
# small samples is prone to overfitting. Consider:
# - Dimensionality reduction (PCA, LASSO) before model training
# - Leave-one-out cross-validation instead of hold-out split
# - Reporting confidence intervals on all metrics
# - External validation before drawing clinical conclusions
```

#### CP-06: Normalization Strategy
```python
# METHODOLOGICAL CHECKPOINT CP-06: Image normalization
# Intensity normalization affects feature reproducibility across scanners and protocols.
# Standard approaches: z-score normalization, histogram matching, N4 bias correction.
# Lack of normalization is a common reproducibility failure in multi-site radiomic studies.
# Current approach: [STATE CURRENT APPROACH]
```

### Checkpoint Summary Cell
Every generated notebook must end with a checkpoint summary markdown cell before
the citations section. Populate the table dynamically — include one row for every
checkpoint that was triggered during notebook generation. Do not include rows for
checkpoints that did not apply to this analysis.

```markdown
## Methodological Checkpoint Summary

The following decisions were made during notebook generation and require expert review
before results are interpreted or reported:

| # | Checkpoint | Location | Current Setting | Reviewed? |
|---|-----------|----------|-----------------|-----------|
| [CP-XX] | [Checkpoint name] | Cell [N] | [Current setting] | ☐ |

**This notebook is not publication-ready without expert review of the items above.**
```

---

## Environment Setup Reference

### Required Python Version
Python 3.10 or 3.11. PyRadiomics has known compatibility issues with Python 3.12+.

### Core Dependencies
```
pyradiomics>=3.1.0
SimpleITK>=2.3.1
scikit-learn>=1.4.0
pandas>=2.0.0
numpy>=1.26.0
matplotlib>=3.8.0
seaborn>=0.13.0
idc-index>=0.11.9
pydicom>=2.4.0
packaging>=23.0
jupyterlab>=4.0.0
```

### Virtual Environment Setup
```bash
python3.10 -m venv imaging_ml_env
source imaging_ml_env/bin/activate   # macOS/Linux
# imaging_ml_env\Scripts\activate   # Windows

pip install --upgrade pip
pip install pyradiomics SimpleITK scikit-learn pandas numpy \
            matplotlib seaborn idc-index pydicom packaging jupyterlab
```

See `references/environment_setup.md` for troubleshooting PyRadiomics installation errors.

---

## Limitations of This Skill

- **No live code execution**: This skill generates notebooks; it does not run them. All generated
  code must be tested and validated by the researcher before use.
- **No credential management**: CTDC dbGaP access must be obtained independently. This skill
  can generate skeleton notebooks for credentialed workflows but cannot execute them.
- **Model non-determinism**: Generated notebooks may differ across sessions. Always version
  control generated notebooks and fix random seeds.
- **Not a substitute for domain expertise**: Methodological checkpoints surface decisions but
  cannot replace review by a radiologist, biostatistician, or imaging informatics expert.
- **IDC data version**: IDC data is versioned. Always record and report the IDC data version
  used (check with `IDCClient().get_idc_version()`). Results may not replicate across versions.

---

## Citations

Any notebook generated with this skill should include the following citations:

```
Fedorov A, et al. National Cancer Institute Imaging Data Commons: Toward Transparency,
Reproducibility, and Scalability in Imaging Artificial Intelligence. RadioGraphics. 2023.
https://doi.org/10.1148/rg.230180

van Griethuysen JJM, et al. Computational Radiomics System to Decode the Radiographic
Phenotype. Cancer Research. 2017. https://doi.org/10.1158/0008-5472.CAN-17-0339

National Cancer Institute. Cancer Research Data Commons. https://datacommons.cancer.gov/
```

---

## Related Skills

| Skill | When to Use | Source |
|-------|-------------|--------|
| `imaging-data-commons` | IDC collection discovery, DICOM download, metadata queries | https://github.com/ImagingDataCommons/idc-claude-skill |
| `ctdc` | CTDC cohort building, GraphQL queries, data access workflows | https://github.com/CBIIT/ctdc-claude-skill |

See the Skill Handoff Protocol in Section 2 for instructions on how to interact with
these skills during a conversation.

---

## Resources

- **IDC Portal**: https://portal.imaging.datacommons.cancer.gov/explore/
- **IDC Documentation**: https://learn.canceridc.dev/
- **CTDC Portal**: https://clinical.datacommons.cancer.gov/
- **PyRadiomics Documentation**: https://pyradiomics.readthedocs.io/
- **PyRadiomics GitHub**: https://github.com/AIM-Harvard/pyradiomics
- **CRDC Overview**: https://datacommons.cancer.gov/
- **dbGaP Data Access**: https://dbgap.ncbi.nlm.nih.gov/aa/wga.cgi?page=login
- **IDC User Forum**: https://discourse.canceridc.dev/
