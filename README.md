# hids-fnlcr-2026

**Summer 2026 HIDS Capstone — AI-assisted cancer imaging analysis on the NCI Cancer Research Data Commons**

**Student:** Stephanie Araki · Health Informatics and Data Science, Georgetown University
**Mentor:** Dr. Mark Jensen, Frederick National Laboratory for Cancer Research (FNLCR)
**Faculty Mentor:** Dr. Yuriy Gusev, Georgetown University

---

## Overview

This project builds and validates a **Claude skill for cancer imaging machine learning** — an
AI-assisted workflow that takes a researcher from a plain-language question to a documented,
reproducible **radiomics** analysis, with methodological checkpoints surfaced for expert review.

The main deliverable is the **[`imaging-ml-skill`](skills/imaging-ml-skill/)**: it extracts
quantitative features from a segmented tumor with PyRadiomics, trains and honestly validates a
scikit-learn model, and reports the result with a confidence interval, a permutation test, and a
clinical baseline. It builds on the [IDC imaging-data-commons skill](https://github.com/ImagingDataCommons/idc-claude-skill)
for data access and demonstrates the full pipeline on the UPenn-GBM brain-tumor cohort.

**Project scope note.** This work began by exploring the Clinical and Translational Data Commons
(CTDC) and moved to the Imaging Data Commons (IDC), where the imaging data needed for a radiomics
pipeline is available. The current focus is IDC. Early CTDC exploration is preserved for history in
`notebooks/01_ctdc_skill_exploration.ipynb` and `docs/`.

## Research question

Can an AI assistant, guided by a purpose-built skill, help a researcher go from a biological question
to a scientifically sound, reproducible imaging-ML analysis — documented well enough that someone
without strong coding skills can follow it?

## Repository structure

```
.
├── skills/
│   ├── imaging-ml-skill/     # ← the main deliverable (see its own README)
│   └── imaging-ml-skill-workspace/   # skill-creator evaluation runs (benchmark evidence)
├── notebooks/
│   └── 01_ctdc_skill_exploration.ipynb   # early CTDC exploration (history)
│       (the UPenn-GBM proof-of-concept notebook lives inside the skill)
├── docs/                     # observations and notes
└── LICENSE
```

The proof-of-concept notebook is intentionally kept **inside the skill**
(`skills/imaging-ml-skill/notebooks/`) so the skill is self-contained.

## Getting started

Everything needed to run the skill and its notebook is in the skill folder:

1. Read **[`skills/imaging-ml-skill/README.md`](skills/imaging-ml-skill/README.md)** for what the
   skill is and how to use it.
2. Follow **[`skills/imaging-ml-skill/notebooks/HOW_TO_RUN_v1.md`](skills/imaging-ml-skill/notebooks/HOW_TO_RUN_v1.md)**
   to set up the environment (Python 3.11 via uv) and run the proof-of-concept notebook (demo mode runs offline in ~1 minute).

## Status

Working draft (skill v0.3.1). The environment setup, the PyRadiomics extraction and evaluation
components, and the proof-of-concept notebook are verified end to end (demo mode offline, and run on
real UPenn-GBM data from IDC). The conversational workflow sections and the real-data path are
written and partially validated. See the Status section in the skill's `SKILL.md` for detail.

## Key resources

- [NCI Imaging Data Commons (IDC) Portal](https://portal.imaging.datacommons.cancer.gov/)
- [IDC imaging-data-commons skill](https://github.com/ImagingDataCommons/idc-claude-skill)
- [TCIA UPenn-GBM dataset](https://www.cancerimagingarchive.net/collection/upenn-gbm/)
- [PyRadiomics documentation](https://pyradiomics.readthedocs.io/)

*Not a medical device. All outputs are for research and education only and must not be used for
clinical decisions.*
