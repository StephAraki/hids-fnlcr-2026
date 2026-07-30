# imaging-ml-skill

<img width="3600" height="1080" alt="v7_3_bare" src="https://github.com/user-attachments/assets/69418400-2f92-41e9-ad96-89b5415cec3e" />

An AI-assisted workflow skill for **cancer imaging machine learning** on NCI Cancer Research Data
Commons (CRDC) data. It guides a researcher from a plain-language biological question to a
documented, reproducible **radiomics** analysis: extract quantitative features from a segmented
tumor with PyRadiomics, then train and honestly validate a scikit-learn model — with methodological
checkpoints surfaced for expert review at every step.

- **Version:** 0.3.1
- **Author:** Stephanie Araki (Georgetown HIDS Capstone, Frederick National Laboratory)
- **Companion skills:** `imaging-data-commons` (IDC access), `ctdc-skill` (clinical data)

> **Proof of concept for research and education only. Not a medical device.** Outputs must never be
> used for clinical decisions.

---

## What this repository contains

This folder is a **Claude skill**: a set of instructions and bundled resources that Claude reads to
help build imaging-ML analyses. It also ships a fully worked, runnable proof-of-concept notebook.

```
imaging-ml-skill/
├── SKILL.md                     # the skill itself: the workflow Claude follows
├── README.md                    # you are here
├── pyproject.toml               # dependencies (source of truth)
├── uv.lock                      # locked versions for reproducible installs
├── requirements.txt             # pip fallback
├── environment.yml              # conda fallback
├── references/                  # guides Claude loads on demand
│   ├── environment_setup.md     #   installing PyRadiomics reliably (the version pitfalls)
│   ├── pyradiomics_guide.md     #   feature families + extraction settings
│   ├── model_selection.md       #   leak-proof modeling, cross-validation, metrics
│   └── notebook_structure.md    #   the 13-section notebook layout and cell standards
├── scripts/                     # tested, reusable components (called by the notebook)
│   ├── extract_radiomics.py     #   batch PyRadiomics feature extraction
│   ├── evaluate_report.py       #   honest reporting: CI, permutation test, clinical baseline
│   ├── make_synthetic_cohort.py #   offline synthetic data (demo mode / smoke tests)
│   ├── idc_helpers.py           #   inspect a collection + preflight-check a config
│   └── radiomics_params.yaml    #   the feature-extraction settings
└── notebooks/
    ├── upenn_gbm_idh_radiomics_survival.ipynb   # the proof-of-concept notebook
    └── HOW_TO_RUN_v1.md         # step-by-step run guide (read this to run the notebook)
```

---

## Two ways to "run" this skill

### 1. Use the skill with Claude

The skill is a knowledge layer that shapes how Claude helps with imaging-ML tasks. To use it, make
`SKILL.md` and its folder available to Claude — for example by adding this folder to a Claude
project, a Claude Code workspace, or Cowork. Then ask a question in plain language, such as *"I want
to predict IDH1 status from MRI radiomics in a brain-tumor cohort"*, and Claude will follow the
skill's workflow: clarify the question, plan the analysis, generate a documented notebook, and flag
the decisions that need expert review. See `SKILL.md` for the full workflow and behavioral rules.

### 2. Run the proof-of-concept notebook yourself

The notebook `notebooks/upenn_gbm_idh_radiomics_survival.ipynb` demonstrates the whole pipeline on
the UPenn-GBM brain-tumor cohort (predicting IDH1 mutation status from T2-FLAIR tumor radiomics,
plus a Kaplan-Meier survival comparison). It runs in two modes:

- **Demo mode** (default): offline synthetic data, no download, finishes in ~1 minute. Use it to
  confirm your environment works.
- **Real mode**: downloads real UPenn-GBM data from the Imaging Data Commons.

**The complete step-by-step run guide is `notebooks/HOW_TO_RUN_v1.md`** — read that to run the
notebook. The short version (Python 3.11, using [uv](https://docs.astral.sh/uv/)):

```bash
# 1. Create the environment and install the locked dependencies
cd skills/imaging-ml-skill
uv venv --python 3.11
source .venv/bin/activate
uv sync --locked                 # base stack → demo mode

# 2. Register the environment as a Jupyter kernel
python -m ipykernel install --user --name imaging-ml --display-name "Python (imaging-ml)"

# 3. Launch JupyterLab from outside the env, open
#    notebooks/upenn_gbm_idh_radiomics_survival.ipynb, select the "Python (imaging-ml)"
#    kernel, and Run All. It is in demo mode by default.
uv tool run --from jupyterlab jupyter-lab
```

To run on real data instead, install the real extra and set `DEMO_MODE = False` in the
notebook's Configuration cell:

```bash
uv sync --locked --extra real
```

See `notebooks/HOW_TO_RUN_v1.md` for details and troubleshooting. A pip/conda fallback
(`requirements.txt`, `environment.yml`) is documented in `references/environment_setup.md`.

---

## Environment notes (important)

PyRadiomics 3.0.1 is version-sensitive. Two constraints matter, and the `uv.lock` /
`pyproject.toml` pins handle both:

- **Python 3.11.** PyRadiomics 3.0.1 does not build on Python 3.12+; the project pins `>=3.11,<3.12`.
- **NumPy 1.x required.** PyRadiomics 3.0.1's compiled extension will not import under NumPy 2.x.

If an install fails, `references/environment_setup.md` has the recipe and the fixes for the
common errors.

---

## Status

Working draft (v0.3.1). Verified end to end: the environment setup, the PyRadiomics extraction
component, the leak-proof modeling pipeline, and the proof-of-concept notebook (which runs in demo
mode offline and has been run on real UPenn-GBM data from IDC). The conversational workflow sections
(intake, routing, planning) and the real-data path are written and partially validated. Treat
untested sections as a draft. See the Status section in `SKILL.md` for detail.

## License and attribution

Skill code: Apache-2.0. IDC data is public and mostly CC-BY — cite the data sources when you use it
(the notebook's Citations section lists them, and `idc-index` can generate citations for the exact
series used). Key references: NCI Imaging Data Commons (Fedorov et al., 2023), UPenn-GBM (Bakas et
al., 2022), PyRadiomics (van Griethuysen et al., 2017).
