# Week 1 Observations
**Dates:** June 8–13, 2026  

---

## Setup Log

- [x] GitHub repo created: `StephAraki/hids-fnlcr-2026`
- [x] VS Code installed with Python, Jupyter, Claude Code extensions
- [x] Virtual environment created (Python 3.12, venv)
- [x] CTDC skill cloned: `skills/ctdc-claude-skill/` (v0.2.2)
- [x] IDC skill cloned: `skills/idc-claude-skill/`
- [x] Python dependencies installed (`requirements.txt` generated)
- [x] OpenAI API key obtained and verified loading correctly
- [x] All work committed and pushed to GitHub

---

## Background: What The CTDC Claude Skill Is

Before running experiments it was important to understand what the skill actually 
is. A Claude skill is a markdown text file (SKILL.md) that Claude reads as 
instructions" it defines what Claude knows, what it should and shouldn't do, 
and when to load additional reference files. It is not running code or calling 
an API autonomously; it is a knowledge and navigation layer that guides Claude's 
responses.

The CTDC skill (v0.2.2) teaches Claude to:
- Answer factual questions about CTDC scope and structure
- Compose GraphQL queries against the CTDC API
- Walk users through portal workflows
- Generate proper data citations
- Recommend the correct data access path
- Refuse confidently when a question is out of scope

---

## Experiment 1: CTDC Skill — Baseline Navigation Test

**Date:** June 11, 2026  
**Tool:** Claude Code extension in VS Code  
**Skill loaded:** `skills/ctdc-claude-skill/SKILL.md`

**Question asked:**
> "I'm a researcher studying glioblastoma. I want to analyze brain MRI data 
> to predict IDH mutation status and understand whether it affects patient 
> survival. Can you help me find the right imaging data, retrieve radiomic 
> features, train a model to predict IDH status, and generate a survival 
> analysis? I'd like a Jupyter notebook with the results."

**What happened:**
The skill ran a live GraphQL query against the CTDC production endpoint and 
returned real data:

```
Total participants: 248
Disease breakdown:
- Plasma Cell Myeloma: 64
- Non-Small Cell Lung Carcinoma: 52
- Colorectal Carcinoma: 50
- Melanoma: 45
- Prostate Carcinoma: 12
- Small Cell Lung Carcinoma: 10
- Acute Myeloid Leukemia NOS: 8
- Adenocarcinoma of the Gastroesophageal Junction: 7
```

The skill correctly:
- Ran a real query (no hallucinated counts)
- Confirmed zero GBM patients in CTDC
- Identified that IDH status is not a queryable GraphQL field
- Explained that molecular data lives in controlled-access VCF files
- Redirected to IDC/TCIA as the appropriate resource for this question
- Offered to invoke the IDC skill for next steps

**What the skill could NOT do:**
- Retrieve imaging data
- Extract radiomic features
- Train a classifier
- Generate a notebook
- Produce a scientific finding

**Key finding:**
> The CTDC skill is an excellent navigation and knowledge tool. It correctly 
> grounds answers in real data and refuses to fabricate. But it stops at the 
> boundary of data discovery — it cannot execute the scientific workflow a 
> researcher actually needs.

**Implication for project:**
This confirmed that a cross-commons execution layer is needed. 

---

## Experiment 2: Cross-Skill Handoff — IDC Skill Invoked

**Date:** June 11, 2026  
**Tool:** Claude Code extension in VS Code  
**Skills loaded:** CTDC skill → IDC skill (handoff)

**Question asked:**
> "Yes, invoke the IDC skill"

**What happened:**
Claude Code loaded the IDC skill and generated a complete Jupyter notebook 
(`notebooks/02_upenn_gbm_idh_radiomics_survival.ipynb`) covering:

1. UPenn-GBM clinical data retrieval via idc-index (671 patients, 19 IDH-mutant)
2. Cohort selection — all mutant + matched wildtype sample
3. Series identification via SQL query on IDC index
4. DICOM image and segmentation download
5. PyRadiomics feature extraction from whole-tumor mask
6. LOOCV-evaluated Logistic Regression and Random Forest classifiers
7. Kaplan-Meier survival analysis with log-rank test
8. Proper CC BY 4.0 data citations

**What ran vs what did not:**

| Section | Status | Reason |
|---|---|---|
| Section 1 — Clinical data load | Ran | CSV retrieval via idc-index |
| Section 2 — Cohort selection | Ran | Pandas operations on clinical table |
| Section 3 — Series identification | Ran | Live SQL query on IDC index |
| Section 4 — DICOM download | Not verified | Requires ~1GB download |
| Section 5 — Feature extraction | Blocked | pyradiomics incompatible with Python 3.12 |
| Section 6 — ML classifier | Blocked | Depends on Section 5 output |
| Section 7 — Survival analysis | Ran | Clinical data only, no imaging required |
| Section 8 — Citation | Ran | idc-index citation function |

**IMPORTANT CLARIFICATION — p=0.002 survival finding:**
The log-rank test result (p=0.002) is real and came from Section 7 only. 
This section uses clinical CSV data — IDH status and survival days — for 
541 patients. No imaging was required and no pyradiomics was involved. 
The survival finding is valid.

The ML classifier predicting IDH status from radiomic features has NOT 
run yet. AUC is unknown. These are completely separate analyses.

**Survival finding (validated):**
IDH-mutant GBM patients show significantly better survival than IDH-wildtype 
patients (log-rank p=0.002, n=541). This is consistent with the well-established 
literature finding that IDH mutation confers better prognosis in glioma.

**Technical blocker identified:**
`pyradiomics` fails to install on Python 3.12 due to a known upstream bug — 
its bundled `versioneer.py` calls a `configparser` API removed in Python 3.12. 
Two documented fixes: (1) create a Python 3.10/3.11 venv, (2) use conda-forge.

---

## Key Gaps Identified In The Existing Skills

Based on both experiments, the following gaps were documented:

**Gap 1 — No cross-commons execution**
The skills can navigate between commons (CTDC → IDC) but cannot execute 
a workflow that spans both in a single pipeline. A researcher gets redirected 
but not helped across the boundary.

**Gap 2 — No analysis execution**
The skills can describe what analysis is needed but cannot run it. The gap 
between "here's what you should do" and "here it is done" is the entire 
scientific workflow.

**Gap 3 — No domain validation**
When the IDC skill generated the notebook, it made radiological decisions 
(whole tumor mask, T1 post-contrast only, LOOCV for small samples) that 
require imaging expertise to evaluate. The skill cannot validate its own 
methodological choices.

**Gap 4 — No iterative refinement**
If the AUC comes back low, the skill cannot look at that result and say 
"try extracting features from the enhancing tumor region separately." 
A human expert would know to do this. The AI does not.
