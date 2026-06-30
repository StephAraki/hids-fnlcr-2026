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

# CTDC-IDC Imaging ML Analysis Assistant

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
e, enhancing region, peri-tumoral margin.
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

