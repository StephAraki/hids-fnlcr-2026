# Notebook Structure Guide

This guide defines the shape of each section: what markdown goes where, what a
well-formed code cell looks like, and how prose changes by expertise level. It does not
own the domain-specific content of every section. Where a section's actual code depends
on another reference guide, this file shows the structural pattern and points to that
guide rather than duplicating its content:

- Section 0's version-check code lives in `references/environment_setup.md`.
- Section 4's feature-class and parameter choices live in `references/pyradiomics_guide.md`.
- Section 8's model selection depends on `references/model_selection.md`.

Duplicating those elsewhere risks the same problem already found and fixed once in this
project: two copies of the same fact drifting apart. This guide shows structure only for
those three sections.

## Status

This guide has not been tested end to end through an actual notebook generation run.
A manual self-test (generating a sample notebook by hand against this guide's rules)
found and fixed two gaps: no convention existed for skipping a non-applicable section
(now added), and the expertise-tier walkthrough rule only had one worked example and no
explicit list of which sections it applies to (now added). Those two fixes are reflected
below, but neither has been confirmed against a real Claude Code run yet. The remaining
templates follow the 13-section structure and cell-level standards already defined in
SKILL.md, but are otherwise still unverified against real generated output.

---

## Cell-Level Standards (Reference Copy)

These rules are also stated in SKILL.md; they are repeated here because every template
below depends on them directly.

**Section headers**: every major section begins with a markdown cell containing the
section title and a one-sentence description of what the section does.

**Inline comments**: every non-trivial line of code has an inline comment explaining
what it does and why. Target density: at least one comment per 3 lines of code.

**USER ACTION REQUIRED cells**: any cell requiring researcher input is marked:

```python
# ============================================================
# USER ACTION REQUIRED
# Replace the values below before running this cell.
# ============================================================
DATA_DIR = "/path/to/your/dicom/files"   # Path to downloaded DICOM series
OUTCOME_COLUMN = "os_event"              # Column name for your outcome variable
```

**Blocked section markers**: any section requiring credentialed CTDC access that cannot
run without it:

```python
# === REQUIRES CTDC dbGaP AUTHORIZATION ===
# This cell will not run without an authorized access token.
# See: https://dbgap.ncbi.nlm.nih.gov/aa/wga.cgi?page=login
# Contact your institution's data access office to apply.
# =========================================
```

**Skipped section markers**: any section marked "if applicable" or "if cross-commons"
that does not apply to a given analysis (for example, Section 2a or Section 5 in an
IDC-only analysis) must still appear in the notebook, in its numbered place, rather than
being silently omitted. Use this exact markdown cell in place of the section's normal
content:

```markdown
### 2a. CTDC Clinical Cohort

**Not applicable to this analysis.** This is an IDC-only workflow; no CTDC cohort was
defined in the analysis plan.
```

Keeping the numbered header with a one-line "not applicable" note, rather than deleting
the section outright, keeps the notebook's section numbering consistent across
different analyses and makes it clear the omission was deliberate rather than an error.

---

## Section Templates

### Section 0: Environment Setup and Version Check

```markdown
## 0. Environment Setup and Version Check

This cell checks that your Python environment matches the versions this notebook was
built and tested against, since a mismatched version (particularly PyRadiomics) can
fail silently or produce different results.
```

Code cell: use the version-check pattern documented in `references/environment_setup.md`
exactly as written there. Do not reconstruct a different version of this check here.

### Section 1: Configuration -- USER ACTION REQUIRED

```markdown
## 1. Configuration

Set the values below before running the rest of this notebook. Each one is explained
inline.
```

```python
# ============================================================
# USER ACTION REQUIRED
# Replace the values below before running this notebook.
# ============================================================
RANDOM_SEED = 42                          # Fixed for reproducibility -- do not change unless intentional
DEMO_MODE = True                           # True = run offline on synthetic data (no download); False = real IDC data
CTDC_STUDY_NAME = "REPLACE_ME"             # Confirmed CTDC study name, from Section 3.1 of the analysis plan
IDC_COLLECTION_ID = "REPLACE_ME"           # Confirmed IDC collection id, from Section 3.1 of the analysis plan
OUTCOME_COLUMN = "REPLACE_ME"              # Column name for the outcome variable defined in intake
DATA_DIR = "./data"                        # Local directory for downloaded imaging and clinical data
```

Include a `DEMO_MODE` flag in the configuration of every generated notebook. When `True`, Section 2
builds a synthetic cohort with `scripts/make_synthetic_cohort.py` (no download, runs in seconds) so
the researcher can confirm the pipeline works before committing to a real IDC download; when
`False`, Section 2 downloads real data. Both paths must produce the same cohort table shape
(one row per patient: `patient_id`, `image_path`, `mask_path`, plus the outcome column), so every
section after data loading is identical in both modes.

Use literal `REPLACE_ME` placeholders for any value not yet confirmed against a live
query, not a plausible-sounding invented name. A researcher should never mistake a
placeholder for a real identifier.

### Section 2: Data Loading

```markdown
## 2. Data Loading

This section retrieves the clinical cohort (if applicable) and the matching imaging
data for this analysis.
```

#### 2a. CTDC Clinical Cohort (if applicable)

Follow "CTDC Query Constraints" in SKILL.md for the actual query syntax. If this
analysis does not use CTDC, use the "Skipped section markers" convention above instead
of the template below. Structural pattern for this subsection when CTDC applies:

```markdown
### 2a. CTDC Clinical Cohort

Queries CTDC for the participant cohort defined in the analysis plan.
```

```python
# See "CTDC Query Constraints" in SKILL.md for verified query syntax.
# Do not use a filter: object or assume a participants resolver exists.
```

#### 2b. IDC Imaging Data Download

Follow "IDC Download Constraints" in SKILL.md for the actual method signatures.
Structural pattern:

```markdown
### 2b. IDC Imaging Data Download

Downloads matching imaging series from IDC using idc-index.
```

```python
from idc_index import IDCClient

client = IDCClient()
print(f"IDC data version: {client.get_idc_version()}")  # Always record this
```

### Section 3: Image Preprocessing

```markdown
## 3. Image Preprocessing

Prepares downloaded images for feature extraction: resampling, normalization, and mask
alignment.
```

```python
# METHODOLOGICAL CHECKPOINT CP-06: Image normalization
# See "Methodological Checkpoints" in SKILL.md for the full checkpoint text.
```

### Section 4: Radiomic Feature Extraction

```markdown
## 4. Radiomic Feature Extraction

Extracts radiomic features from the preprocessed images using PyRadiomics.
```

Code cell: do not generate until `references/pyradiomics_guide.md` has been read for
this analysis's modality and cancer type, per SKILL.md's existing gating rule. The
feature classes and parameter file must come from that guide, not from this one.

Call the bundled, tested component rather than writing a fresh extraction loop:

```python
# scripts/extract_radiomics.py + scripts/radiomics_params.yaml (see pyradiomics_guide.md)
from extract_radiomics import extract_cohort
features_df, failures = extract_cohort(cohort_df, params_path="scripts/radiomics_params.yaml")
print(f"{features_df.shape[0]} patients x {features_df.shape[1]} features; {len(failures)} failures")
```

### Section 5: Data Merging and Preparation (if cross-commons)

If this analysis is single-commons (IDC-only or CTDC-only), use the "Skipped section
markers" convention above in place of this section's content. Structural pattern when
cross-commons applies:

```markdown
## 5. Data Merging and Preparation

Merges radiomic features with clinical variables by participant ID, if this analysis
uses both CTDC and IDC.
```

```python
# Confirm the join key actually maps between CTDC and IDC identifiers for this specific
# cohort before trusting the merge. Do not assume the join succeeds silently -- report
# the resulting row count and compare it against the expected cohort size from Section 3.1.
merged_df = clinical_df.merge(features_df, left_on="participant_id", right_on="PatientID", how="inner")
print(f"Merged cohort size: {len(merged_df)}")
```

### Section 6: Exploratory Data Analysis

```markdown
## 6. Exploratory Data Analysis

Examines the outcome distribution and basic feature properties before modeling.
```

```python
import matplotlib.pyplot as plt

print(merged_df[OUTCOME_COLUMN].value_counts())

# METHODOLOGICAL CHECKPOINT CP-03: Class imbalance
# Class distribution: [STATE DISTRIBUTION]
# See "Methodological Checkpoints" in SKILL.md for the full checkpoint text and options.
```

### Section 7: Feature Selection

```markdown
## 7. Feature Selection

Reduces the radiomic feature set before modeling, since feature count typically exceeds
sample size in radiomics cohorts.
```

```python
# METHODOLOGICAL CHECKPOINT CP-04: Data leakage risk
# Fit any feature selector on training data only. See SKILL.md for the full checkpoint text.
from sklearn.feature_selection import VarianceThreshold

selector = VarianceThreshold(threshold=0.01)
```

### Section 8: Model Training

```markdown
## 8. Model Training

Trains the model type selected in the analysis plan.
```

Code cell: do not select or hard-code a model type here without having consulted
`references/model_selection.md` in Section 3.3 of the analysis plan first. This section
implements the plan's decision; it does not make that decision itself.

### Section 9: Model Evaluation

```markdown
## 9. Model Evaluation

Evaluates the trained model using the validation strategy and metrics defined in the
analysis plan.
```

```python
# Report the metric decided in Section 3.4 of the analysis plan.
# Do not substitute a different metric here without noting the change and why.
```

### Section 10: Results Visualization

```markdown
## 10. Results Visualization

Visualizes model performance and, where relevant, feature importance.
```

```python
import matplotlib.pyplot as plt

# Keep this section's plots limited to what the evaluation plan actually calls for.
# Do not add exploratory visualizations here that were not part of the approved plan.
```

### Section 11: Limitations and Methodological Notes

```markdown
## 11. Limitations and Methodological Notes

**This notebook is not publication-ready without expert review of the items below.**
```

Populate this section with the Checkpoint Summary Cell format defined in SKILL.md's
"Methodological Checkpoints" section, including only the checkpoints actually triggered
during this notebook's generation.

### Section 12: Citations

```markdown
## 12. Citations
```

Use the citation block from SKILL.md's "Citations" section verbatim. Do not paraphrase
or shorten the citations.

---

## Walkthrough Prose by Expertise Level

SKILL.md's calibration table states the rule but does not say which sections it applies
to. Here is the explicit mapping, so this isn't left to guesswork per notebook:

- **None**: a walkthrough cell before every one of the 13 sections, not just some of them.
- **Some**: a walkthrough cell only at three points: before Section 2 (Data Loading),
  before Section 4 (Radiomic Feature Extraction), and before Section 8 (Model Training).
  These are the three "major transitions" the calibration table refers to. No other
  section gets a walkthrough cell at this tier.
- **Comfortable**: a walkthrough cell only where a methodological checkpoint (CP-01
  through CP-06) is present in that section, since that is the "domain-specific context"
  the calibration table refers to. Sections with no checkpoint get no walkthrough cell.

The examples below cover Section 4 at all three tiers, plus Section 2 and Section 8 at
the "Some" tier, since that tier's other two transition points had no worked example
before this revision. Apply the same tone pattern to any other cell that needs one.

### Section 4 (Radiomic Feature Extraction) -- all three tiers

#### Expertise: None

```markdown
### Before we extract features

Right now we have a CT image and a mask that marks the tumor region. A "radiomic
feature" is just a number that describes something about that region -- how bright it
is, how textured it looks, what shape it has. We are about to calculate a few hundred
of these numbers per patient. You do not need to understand each one individually; the
next section will use them together, the same way a doctor might use several lab
values together rather than looking at just one.
```

#### Expertise: Some

```markdown
### Feature extraction

This cell runs PyRadiomics on each image/mask pair using the feature classes and
parameter file selected in the analysis plan. If you are unfamiliar with any specific
feature class, the PyRadiomics documentation linked in Section 12 describes each one.
```

#### Expertise: Comfortable

```markdown
### Feature extraction

Standard PyRadiomics extraction using the plan's selected feature classes and params
file. See Section 3.2 of the analysis plan for the extraction rationale.
```

### Section 2 (Data Loading) -- Expertise: Some

```markdown
### Loading the data

The next two cells retrieve the imaging data (and clinical data, if this analysis uses
CTDC) needed for this analysis. This is a good point to confirm the cohort size printed
below matches what was estimated in the analysis plan before continuing.
```

### Section 8 (Model Training) -- Expertise: Some

```markdown
### Training the model

This cell trains the model type selected in Section 3.3 of the analysis plan. If you
want to compare it against a different model type, that is a change worth discussing
with a collaborator first, since model choice here was tied to your sample size and
outcome type, not an arbitrary default.
```

Note the tone pattern across tiers: "None" explains the concept and why it matters
before showing code. "Some" explains what the cell does and where to look something up
or double check, without re-explaining Python or statistics fundamentals. "Comfortable"
states what the cell does and defers to the plan document rather than re-explaining it.