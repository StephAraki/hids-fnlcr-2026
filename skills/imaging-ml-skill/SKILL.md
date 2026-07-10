---
name: imaging-ml-skill
description: AI-assisted workflow layer for cancer imaging machine learning research using NCI CRDC data. Use this skill whenever a researcher wants to move from a biological question to an executable imaging ML analysis — including cohort discovery in CTDC, imaging data access in IDC, radiomic feature extraction with PyRadiomics, and reproducible Jupyter notebook generation. Trigger this skill for any request involving cancer imaging analysis, radiomics, imaging ML pipelines, PyRadiomics, CTDC cohort + IDC imaging integration, or notebook generation for cancer imaging research. Also trigger when a user describes a biological question and wants to know how to analyze imaging data computationally, even if they do not use technical terms.
license: Apache-2.0
metadata:
  version: 0.2.2
  skill-author: Stephanie Araki
  organization: Frederick National Laboratory for Cancer Research (FNLCR)
  program: Georgetown University HIDS Capstone Internship
  python-version: "3.9"
  pyradiomics-version: "3.0.1"
  repository: https://github.com/StephAraki/hids-fnlcr-2026
  last-updated: 2026-07-10
---
 
# CTDC-IDC Imaging ML Skill
 
## Status

This skill's overall architecture and behavioral rules are complete. As of this version,
functional testing has been completed for Research Question Intake (Section 1) and for
the environment setup path: both `environment.yml` and `references/environment_setup.md`
have been tested end to end on a real machine, including a fresh install from scratch,
not just written. Data Source Routing, Analysis Planning, Notebook Generation, and
Methodological Checkpoints are written but not yet validated end-to-end.

Of the four planned reference guides, two are written: `references/environment_setup.md`
(tested, see above) and `references/notebook_templates.md` (written, not yet tested
against an actual generated notebook). `references/pyradiomics_guide.md` and
`references/model_selection.md` are still planned but not yet implemented. Treat this
skill as a working draft until that testing is complete; do not assume untested sections
behave exactly as written when used for the first time.
 
## Overview
 
This skill guides researchers from a plain-language biological question to a complete,
executable, and reproducible imaging machine learning Jupyter notebook using NCI Cancer
Research Data Commons (CRDC) data.
 
It builds on two existing domain skills — the CTDC skill (clinical data discovery) and
the IDC skill (cancer imaging access) — by adding an execution layer that handles
analysis planning, environment setup, notebook generation, and methodological review.
This skill does not call those skills as functions. It adopts their documented behaviors
at the appropriate workflow stage. See "Working With the CTDC and IDC Skills" below.
 
**This skill is for researchers who:**
 
- Have a biological question about cancer and want to use imaging data to answer it
- Have limited programming experience but need a reproducible analysis pipeline
- Want to combine clinical data from CTDC with imaging data from IDC
- Need a documented, commented notebook they or a collaborator can re-run
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
|---|---|
| `references/pyradiomics_guide.md` | Before making any feature class or parameter-file choice in Section 3.2, and before generating any PyRadiomics extraction code in Section 4 |
| `references/environment_setup.md` | Python environment, dependency installation, version pinning, PyRadiomics troubleshooting |
| `references/notebook_templates.md` | Section headers, cell structure, blocked cell patterns, markdown walkthrough templates |
| `references/model_selection.md` | Before selecting a model in Section 3.3 |
 
---
 
## Working With the CTDC and IDC Skills
 
This skill does not have a mechanism to detect whether another skill is "loaded" or
"available" in a conversation, and it cannot call another skill as a function or receive
a return value from one. There is no handshake between skills. What this skill can do is
instruct Claude to adopt the documented behavior of the CTDC or IDC skill at the point in
the workflow where that behavior is needed — the same way Claude would behave if the
researcher had asked a CTDC- or IDC-specific question directly.
 
Follow these rules instead of checking for "availability":
 
- **For any CTDC cohort discovery, GraphQL query construction, portal workflow guidance,
  or citation generation step**, follow the CTDC skill's documented patterns exactly,
  including its query syntax, authoritative endpoints, and access-tier guidance. Do not
  improvise GraphQL syntax. See "CTDC Query Constraints" below before writing or
  describing any query.
- **For any IDC collection discovery, metadata query, DICOM download, or visualization
  step**, follow the IDC skill's documented `idc-index` patterns exactly, including its
  method signatures and version-check requirement. See "IDC Download Constraints" below
  before generating any download cell.
- **If the researcher's conversation does not already contain CTDC or IDC skill content**
  and a data-dependent step is needed, tell the researcher directly: "This step needs the
  CTDC skill" (or IDC skill) "added to this project so I can follow its query patterns
  correctly. You can find it at [correct source link below]." Do not attempt to
  reconstruct CTDC or IDC query syntax from general knowledge once you have flagged this
  — wait for the skill to be added, or for the researcher to confirm they want you to
  proceed without it and accept the risk of unverified syntax.
- **For analysis planning and notebook generation**, this skill acts independently and
  does not depend on the CTDC or IDC skill being present, except for the data-access
  steps named above.
### CTDC Query Constraints
 
The CTDC skill's deployed schema does not match the generic Bento `filter:` object
pattern. Before writing or describing any CTDC GraphQL query in an analysis plan or
notebook cell:
 
- Do not write `participants(filter: { field: { eq: ... } })`. CTDC uses positional
  list-of-string arguments directly on resolvers, e.g.
  `participantOverview(ctep_disease_term: ["Breast Cancer"])`.
- Do not assume a top-level `participants` or `studies` resolver exists. Consult the
  CTDC skill's `graphql_patterns.md` for the verified list of root query fields.
- Do not reference a `fileCount` field on `participantOverview`; it does not exist.
- Treat any field or resolver not explicitly confirmed in the CTDC skill's reference
  files as unverified, and say so rather than guessing.
- For questions about CTDC submission requirements or portal page text, defer entirely
  to the CTDC skill rather than answering from memory.
### IDC Download Constraints
 
The IDC skill's `idc-index` package has two download methods with different argument
order. Before generating any IDC download cell:
 
- `client.download_from_selection(downloadDir, **filter_kwargs)` takes `downloadDir` as
  the first positional argument and accepts filter keyword arguments
  (`collection_id`, `seriesInstanceUID` as a list, etc.) — it does not accept a
  DataFrame directly.
- `client.download_dicom_series(seriesInstanceUID, downloadDir)` takes
  `seriesInstanceUID` as the first positional argument — the reverse order from
  `download_from_selection`.
- Always call `client.get_idc_version()` (or run the IDC skill's version-check script)
  at the start of the notebook, before any query, and record the result.
- When extracting UIDs from a query result for download, extract them as a list
  (`list(df['SeriesInstanceUID'].values)`) before passing to either download method.
---
 
## Behavioral Rules
 
These rules apply throughout every interaction using this skill. Never violate them.
 
- **Always complete intake before generating any code.** Do not write a notebook until all required intake fields are confirmed (Section 1).
- **Always generate an analysis plan before generating a notebook.** The plan must be presented to the researcher and acknowledged before proceeding to notebook generation.
- **Never present generated notebooks as publication-ready.** Always include a limitations section and methodological checkpoint summary.
- **Never fabricate data availability.** If you are unsure whether a specific cohort or imaging collection exists in CTDC or IDC, say so explicitly and direct the user to verify, following the CTDC and IDC skills' own guidance on not fabricating counts or fields.
- **Never silently make analytical decisions.** Every non-trivial methodological choice (mask selection, normalization strategy, model type, validation approach) must be surfaced to the researcher with a brief explanation of the tradeoff.
- **Always flag when credentialed CTDC access is required.** CTDC participant-level data requires dbGaP authorization. If a researcher asks for participant-level data and does not mention authorization, notify them before proceeding.
- **Always defer to the CTDC and IDC skills' documented behavior for data discovery steps**, per "Working With the CTDC and IDC Skills" above. This skill handles analysis planning and notebook generation; it does not reconstruct CTDC or IDC query and download logic independently.
- **Never write a CTDC GraphQL query without checking it against "CTDC Query Constraints."** Never write an IDC download cell without checking it against "IDC Download Constraints."
- **Always handle follow-up requests on generated notebooks.** If a researcher returns with a question about a notebook already generated in this conversation (debugging, adding a plot, modifying a model), address it directly. Re-read the relevant section of the notebook before responding. Do not restart the intake workflow unless the research question has fundamentally changed.
---
 
## 1. Research Question Intake
 
### Purpose
 
Collect the information needed to generate a scientifically appropriate analysis plan.
Do not skip or abbreviate this step.
 
### Required Fields
 
Before proceeding to routing or planning, confirm all of the following:
 
| Field | What to Ask | Why It Matters |
|---|---|---|
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
ask one clarifying question at a time, starting with cancer type. Do not ask all five intake
questions until you have established the basic disease context.
 
---
 
## 2. Data Source Routing
 
### Purpose
 
Determine whether the analysis requires CTDC, IDC, or both, and explain the data pathway
to the researcher before proceeding.
 
### Routing Logic
 
| Researcher Needs | Route To | Notes |
|---|---|---|
| Imaging data only (no clinical variables) | IDC only | Follow the IDC skill's documented patterns for collection discovery |
| Clinical variables only (no imaging) | CTDC only | Follow the CTDC skill's documented patterns; this skill's notebook generation still applies if the researcher wants a non-imaging analysis notebook |
| Imaging + clinical variables together | CTDC + IDC | Full cross-commons workflow; most complex path |
| Imaging + molecular data (genomics, proteomics) | IDC + GDC or PDC | Out of scope for this skill; acknowledge and redirect |
 
### CTDC + IDC Cross-Commons Pathway
 
When both commons are needed, explain this workflow to the researcher before proceeding:
 
1. Use CTDC to define and export the clinical cohort (participant IDs, clinical variables), following the CTDC skill's documented query patterns
2. Use IDC to find imaging series for those participants (match on PatientID or submitter ID), following the IDC skill's documented query patterns
3. Download DICOM imaging series from IDC for matched participants, following the method signatures in "IDC Download Constraints"
4. Extract radiomic features from imaging using PyRadiomics, after consulting `references/pyradiomics_guide.md`
5. Merge radiomic features with clinical variables by participant ID
6. Train and evaluate the ML model on the merged dataset
**Always confirm with the researcher that this pathway matches their intent before
proceeding to analysis planning.**
 
### Access Requirements
 
- **IDC data**: Publicly available, no authentication required.
- **CTDC participant-level data**: Requires dbGaP authorization. If the researcher does not
  have authorization, the notebook can be built as a skeleton with placeholder data loading
  cells that will work once access is granted. Notify the researcher of this limitation.
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
If this section involves describing or sketching a CTDC query, follow "CTDC Query
Constraints" above; do not write a `filter:` object or assume a `participants` resolver.
 
#### 3.2 Imaging and Feature Extraction Approach
 
- Imaging modality and sequence (e.g., CT with contrast, T2-weighted MRI)
- Tumor region of interest (ROI): which mask or segmentation will be used
- PyRadiomics feature classes to extract
**Before selecting feature classes, load `references/pyradiomics_guide.md`.** Feature class
selection depends on modality and cancer type and must not be made without consulting
that reference. Do not list feature classes in the plan until the guide has been read.
 
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
 
**Section headers**: Every major section begins with a markdown cell containing the section
title and a one-sentence description of what the section does.
 
**Inline comments**: Every non-trivial line of code must have an inline comment explaining
what it does and why. Target density: at least one comment per 3 lines of code.
 
**Walkthrough prose cells**: For researchers with no Python experience (expertise level: none),
include a markdown cell before each code section explaining in plain language what the code
is about to do and why it matters. For researchers with some experience, include these cells
only at major transitions (data loading → feature extraction → modeling). For comfortable
researchers, omit them except where domain-specific context is needed.
 
**USER ACTION REQUIRED cells**: Any cell that requires the researcher to provide input
(file paths, cohort IDs, parameter choices, credentials) must be marked with a prominent
comment block:
 
```
# ============================================================
# USER ACTION REQUIRED
# Replace the values below before running this cell.
# ============================================================
DATA_DIR = "/path/to/your/dicom/files"   # Path to downloaded DICOM series
OUTCOME_COLUMN = "os_event"              # Column name for your outcome variable
```
 
**Blocked section markers**: Any section that requires credentialed CTDC access and cannot
run without it must be wrapped:
 
```
# === REQUIRES CTDC dbGaP AUTHORIZATION ===
# This cell will not run without an authorized access token.
# See: https://dbgap.ncbi.nlm.nih.gov/aa/wga.cgi?page=login
# Contact your institution's data access office to apply.
# =========================================
```
 
### Environment Setup Cell

Every notebook must begin with a version-pinned environment check cell. Use the exact
code in `references/notebook_templates.md` (Section 0 template), which in turn follows
the version-check pattern verified in `references/environment_setup.md`. Do not write a
different version of this check directly in a notebook.

If the notebook includes IDC data access, also call `client.get_idc_version()` in this
cell (or immediately after) and print the result, per "IDC Download Constraints" above.

### PyRadiomics Integration

**Do not generate this section's code until `references/pyradiomics_guide.md` has been
read for this analysis's modality and cancer type.** The feature classes and parameter
file must be the ones determined in Section 3.2, not a default. See the Section 4
template in `references/notebook_templates.md` for the structural pattern this code
should follow once those choices are made.

### IDC Download Cell Pattern

When generating a cell that downloads IDC data, follow "IDC Download Constraints" above
exactly. See the Section 2b template in `references/notebook_templates.md` for the
structural pattern.

### Reproducibility Requirements

Every generated notebook must include:

- A random seed set at the top of the configuration cell (`RANDOM_SEED = 42`)
- Version pins for all imported packages in the environment setup cell
- A manifest of the imaging series used (SeriesInstanceUIDs saved to CSV)
- The IDC data version recorded (`client.get_idc_version()`)
- A citations cell at the end (Section 12)
### Calibrating to Expertise Level
 
| Expertise Level | Comment Style | Walkthrough Prose Cells |
|---|---|---|
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
 
```
## Methodological Checkpoint Summary
 
The following decisions were made during notebook generation and require expert review
before results are interpreted or reported:
 
| # | Checkpoint | Location | Current Setting | Reviewed? |
|---|-----------|----------|-----------------|-----------|
| [CP-XX] | [Checkpoint name] | Cell [N] | [Current setting] | [ ] |
 
**This notebook is not publication-ready without expert review of the items above.**
```
 
---
 
## Environment Setup Reference
 
### Required Python Version
 
Python 3.9, verified with pyradiomics 3.0.1. Do not use Python 3.10+ or pyradiomics
3.1.0 — see `references/environment_setup.md` for the reproduced failure mode.
 
### Core Dependencies
 
```
pyradiomics==3.0.1
SimpleITK==2.5.3
scikit-learn==1.6.1
pandas==2.3.3
numpy==2.0.2
scipy==1.13.1
matplotlib==3.9.4
seaborn==0.13.2
PyYAML==6.0.3
jupyterlab==4.5.6
notebook==7.5.5
ipykernel==6.31.0
openpyxl==3.1.5
```
 
`idc-index` is intentionally not pinned here yet. Current PyPI idc-index (0.12.3)
requires `pandas<=2.2.4`, which conflicts with the verified `pandas==2.3.3` above.
This has not been tested together. See `references/environment_setup.md` before
adding idc-index to any notebook's dependency list.
 
`pydicom` was previously listed here but is not part of the verified environment and
its actual usage in this skill's generated code has not been confirmed. Do not assume
it is needed until a specific cell requires it.
 
### Virtual Environment Setup
 
```bash
python3.9 -m venv imaging_ml_env
source imaging_ml_env/bin/activate   # macOS/Linux
# imaging_ml_env\Scripts\activate    # Windows
 
pip install --upgrade pip
pip install pyradiomics==3.0.1 SimpleITK==2.5.3 scikit-learn==1.6.1 \
            pandas==2.3.3 numpy==2.0.2 scipy==1.13.1 matplotlib==3.9.4 \
            seaborn==0.13.2 PyYAML==6.0.3 jupyterlab==4.5.6 notebook==7.5.5 \
            ipykernel==6.31.0 openpyxl==3.1.5
```
 
Or, using conda to manage the interpreter and pip for packages:
 
```bash
conda env create -f environment.yml
conda activate imaging-ml-env
```
 
See `references/environment_setup.md` for troubleshooting PyRadiomics installation errors
and the current idc-index compatibility status.
 
---
 
## Limitations of This Skill
 
- **No live code execution**: This skill generates notebooks; it does not run them. All generated code must be tested and validated by the researcher before use.
- **No credential management**: CTDC dbGaP access must be obtained independently. This skill can generate skeleton notebooks for credentialed workflows but cannot execute them.
- **No live skill-to-skill handoff**: This skill cannot detect or call the CTDC or IDC skill programmatically. It instructs Claude to adopt their documented behavior at the right workflow stage; see "Working With the CTDC and IDC Skills." If those skills' content is not present in the conversation, data-dependent steps should be flagged rather than improvised.
- **Model non-determinism**: Generated notebooks may differ across sessions. Always version control generated notebooks and fix random seeds.
- **Not a substitute for domain expertise**: Methodological checkpoints surface decisions but cannot replace review by a radiologist, biostatistician, or imaging informatics expert.
- **IDC data version**: IDC data is versioned. Always record and report the IDC data version used (`client.get_idc_version()`). Results may not replicate across versions.
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
|---|---|---|
| `imaging-data-commons` | IDC collection discovery, DICOM download, metadata queries | https://github.com/ImagingDataCommons/imaging-data-commons-skill |
| `ctdc-skill` | CTDC cohort building, GraphQL queries, data access workflows | https://github.com/CBIIT/ctdc-claude-skill |
 
See "Working With the CTDC and IDC Skills" above for how this skill interacts with these
two skills during a conversation. There is no live handoff mechanism between skills; this
skill adopts their documented behavior directly rather than calling out to them.
 
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