# How to run the UPenn-GBM notebook

`upenn_gbm_idh_radiomics_survival.ipynb` — step-by-step, written so you can follow it even if you
have not used Jupyter much. It has two modes: **demo mode** (the default, runs offline on synthetic
data in about a minute) and **real mode** (downloads real UPenn-GBM data from the Imaging Data
Commons). Start with demo mode to confirm everything works.

---

## 1. What you need before you start

- **Python 3.9, 3.10, or 3.11 — NOT 3.12 or newer.** PyRadiomics 3.0.1 does not build on Python
  3.12+, and the pinned scientific packages (SciPy, etc.) have no prebuilt wheels there, so pip will
  try to compile them from source and fail. Note that recent macOS / Homebrew default to Python 3.13,
  so check *inside your environment* with `python --version` before installing. If it says 3.12 or
  higher, create the environment with a 3.11 interpreter instead (macOS: `brew install python@3.11`,
  then `python3.11 -m venv ...`; or `conda create -n imaging-ml python=3.11`).
- **NumPy 1.x is required.** PyRadiomics will not import under NumPy 2.x. This is the single most
  common setup problem — see Troubleshooting.
- The notebook must be able to find the `scripts/` folder that ships with the skill. The simplest
  guarantee: keep the notebook where it is, inside the skill folder, so `scripts/` sits one level up
  (`../scripts/`). The notebook looks in a few nearby locations automatically.

## 2. Set up the environment (one time)

You have two options. If you are not sure, use Option A — it is the most reliable.

### Option A — a fresh environment from the pinned file (recommended)

From the skill folder (the one containing `requirements.txt`):

```bash
python3 -m venv venv                 # use a Python 3.9-3.11 interpreter
source venv/bin/activate             # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install "setuptools<65" wheel versioneer "numpy==1.26.4"
pip install --no-build-isolation -r requirements.txt
```

The two-step install matters: NumPy 1.x and an older setuptools must be present **before** PyRadiomics
builds. The `--no-build-isolation` flag is what lets PyRadiomics compile against them.

(If you use conda instead: `conda env create -f environment.yml && conda activate imaging-ml-env`.)

### Option B — reuse an existing Python environment

If you already have a Python 3.9–3.11 environment with PyRadiomics installed, you can reuse it —
just verify it and add the packages this notebook needs:

```bash
source your_env/bin/activate          # activate your existing environment (Windows: your_env\Scripts\activate)
# 1) Confirm NumPy is 1.x and PyRadiomics imports:
python -c "import numpy, radiomics; print('numpy', numpy.__version__, '| pyradiomics', radiomics.__version__)"
# 2) Add packages this notebook needs that a basic radiomics environment may not include:
pip install lifelines                       # survival analysis (needed even in demo mode)
pip install "idc-index==0.12.4" "pydicom>=2.3,<3" pydicom-seg "pandas==2.2.3"   # only needed for REAL mode
```

If step 1 prints a numpy version starting with `2.`, or errors with
`numpy.core.multiarray failed to import`, fix it before going on:
`pip install "numpy==1.26.4"` and, if needed, reinstall PyRadiomics (see Troubleshooting).

## 3. Register the environment with Jupyter (one time)

So Jupyter can use the environment you just built:

```bash
python -m ipykernel install --user --name imaging-ml --display-name "Python (imaging-ml)"
```

## 4. Open the notebook

From the skill folder:

```bash
jupyter lab            # or: jupyter notebook
```

Your browser opens. Navigate into `notebooks/` and open
`upenn_gbm_idh_radiomics_survival.ipynb`. In the top-right kernel picker, choose
**Python (imaging-ml)** if it is not already selected.

## 5. Run it (demo mode — the default)

You do not need to change anything for a first run. A notebook is a stack of **cells** (grey boxes
of code, with text boxes explaining them). Run them top to bottom:

- Click the first cell, then press **Shift + Enter** to run it and move to the next. Repeat down the
  notebook, **or** use the menu **Run → Run All Cells** to run everything at once.
- Always run in order, top to bottom. If things get confused, use **Kernel → Restart Kernel and Run
  All** to start clean.

**What you should see (demo mode):**

- It finishes in roughly a minute on a normal laptop.
- Section 0 prints your package versions and confirms NumPy 1.x.
- Section 2 makes 80 synthetic patients; Section 3 shows one brain slice with a red tumor outline.
- Section 8 prints a cross-validated **ROC-AUC around 0.82 ± 0.09** (it is meant to be good but not
  perfect — that is the honest range for this task).
- Section 9 shows an ROC curve and confusion matrix; Section 10 shows the top features and a
  **Kaplan-Meier survival plot** (IDH-mutant vs wildtype) with a log-rank p-value.
- Section 11 prints a methodological checkpoint summary and saves outputs.

**Where the outputs go:** a new `output/` folder next to the notebook, containing `metrics.json`,
`evaluation.png`, `feature_importance.png`, `km_survival.png`, and `trained_model.joblib`. Synthetic
images and the cohort manifest land in `data/` and `work/`.

## 6. Switching to real UPenn-GBM data (real mode)

Only do this after demo mode works. In **Section 1 (Configuration)**, change one line:

```python
DEMO_MODE = False
```

Real mode additionally needs:

- `idc-index`, `pydicom-seg`, and `pandas==2.2.3` installed (see Option B above).
- An internet connection and several GB of free disk. The first run downloads and converts data, so
  it takes a while (minutes, not seconds). Start small — `N_CASES` is set to 40.
- Nothing else changes: the collection is already `upenn_gbm`, the sequence is T2-FLAIR, and the IDH1
  label and survival are pulled from IDC's own clinical table. Every section after data loading is
  identical to demo mode.

To predict something other than IDH1, or use a different sequence or cohort, edit the clearly-marked
values in Section 1 — nothing below it needs to change.

## 7. Troubleshooting

- **`Cannot import 'mesonpy'`, or pip starts "Preparing metadata" / building SciPy, NumPy, or
  PyRadiomics from source** — your Python is 3.12 or newer (often 3.13, the current macOS/Homebrew
  default). The pinned packages have no wheels there, so pip falls back to source builds that need
  extra tooling and then fail. Fix: recreate the environment with **Python 3.11** (`python --version`
  inside the env should say 3.11.x), then reinstall. Do not just `pip install meson` — PyRadiomics
  3.0.1 will still fail to build on 3.12+.
- **`numpy.core.multiarray failed to import`** (or PyRadiomics won't import) — NumPy 2.x is
  installed. Run `pip install "numpy==1.26.4"`, then
  `pip install --no-build-isolation --force-reinstall pyradiomics==3.0.1`.
- **`resolution-too-deep` / pip backtracks through many `duckdb` versions** — caused by installing
  `idc-index` with a loose version bound. Install in two stages: the core stack first
  (`pyradiomics==3.0.1 SimpleITK==2.5.3 pandas==2.2.3 scipy==1.13.1 scikit-learn matplotlib seaborn
  joblib pydicom lifelines`), then `pip install "idc-index==0.12.4" pydicom-seg` on its own. Demo
  mode needs only the core, so you can defer idc-index entirely until you want real data.
- **`ModuleNotFoundError: No module named 'lifelines'`** — run `pip install lifelines`. (Needed for
  the survival plot even in demo mode.)
- **`ModuleNotFoundError: extract_radiomics`** — the notebook could not find the `scripts/` folder.
  Launch Jupyter from the skill folder (so `scripts/` is one level above the notebook), or move the
  notebook so `scripts/` sits alongside or one level up.
- **`ModuleNotFoundError: idc_index` / `pydicom_seg`** (real mode only) — run
  `pip install "idc-index==0.12.4" "pydicom>=2.3,<3" pydicom-seg "pandas==2.2.3"`.
- **`No module named 'pydicom._storage_sopclass_uids'`** (real mode, reading the segmentation) —
  pydicom 3.x is installed but `pydicom-seg` 0.4.1 needs pydicom 2.x (pydicom 3.0 removed that private
  module). Run `pip install "pydicom==2.4.4"`, then restart the kernel and re-run. Nothing else depends
  on pydicom 3, so this is safe.
- **Wrong kernel** — if imports fail even though you installed everything, the notebook is probably
  using a different Python. Use **Kernel → Change Kernel → Python (imaging-ml)**.
- **A cell shows a red error partway through** — fix that cell first, then **Kernel → Restart Kernel
  and Run All**. Later cells depend on earlier ones, so re-running from the top is the reliable fix.

---
*This notebook is a proof of concept for research and teaching, not a clinical tool.*
