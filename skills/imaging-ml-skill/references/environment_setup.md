# Environment Setup Reference

This guide documents the supported Python environment for imaging-ml-skill, how to create
it reproducibly with `uv`, and the troubleshooting for the version pitfalls the pins resolve.

## Supported setup: uv + lockfile

Python **3.11** (`pyproject.toml` pins `>=3.11,<3.12`). Dependencies are declared in
`pyproject.toml` and locked in `uv.lock`, so `uv sync --locked` reproduces the exact,
verified environment. This is the supported path; the pip and conda recipes further down are
fallbacks.

```bash
cd skills/imaging-ml-skill
uv venv --python 3.11
source .venv/bin/activate
uv sync --locked                 # base stack → demo mode
python -m ipykernel install --user --name imaging-ml --display-name "Python (imaging-ml)"
```

Real-data (IDC download) path — add the extra and register a second kernel:

```bash
uv sync --locked --extra real
python -m ipykernel install --user --name imaging-ml-real --display-name "Python (imaging-ml-real)"
```

JupyterLab is run *outside* this environment (see "Why JupyterLab is not in the environment"):

```bash
uv tool run --from jupyterlab jupyter-lab
```

`uv sync --locked` installs exactly what is in `uv.lock` and errors if the lock has drifted
from `pyproject.toml`. `uv` builds pyradiomics with the older setuptools and NumPy 1.x it
needs automatically, via `[tool.uv.extra-build-dependencies]` in `pyproject.toml` — that
replaces the manual `--no-build-isolation` step the pip fallback still requires. The full run
walkthrough (demo vs real, the `DEMO_MODE` toggle) is in `notebooks/HOW_TO_RUN_v1.md`.

## Verified configuration (pins)

Confirmed importing **and running a real feature extraction** together (numpy 1.26.4, not an
import-only check):

- Python: 3.11
- pyradiomics: 3.0.1
- numpy: 1.26.4   — NumPy 1.x REQUIRED (see "NumPy 2.x failure")
- pandas: 2.2.3   — 2.2.x so idc-index, which needs `pandas<=2.2.4`, can coexist
- scipy: 1.13.1
- scikit-learn: 1.6.1
- SimpleITK: 2.5.3
- matplotlib: 3.9.4 · seaborn: 0.13.2 · PyYAML: 6.0.3 · openpyxl: 3.1.5 · joblib: 1.5.1 · lifelines: 0.30.0 · ipykernel: 6.31.0
- real extra: idc-index 0.12.4 · pydicom 2.4.4 · pydicom-seg 0.4.1

`uv.lock` is the authoritative record of the full resolved set. Do not substitute pyradiomics
3.1.0 or Python 3.12+ (both are confirmed failures below).

## Fallback: pip

If `uv` is unavailable, reproduce the same pins with pip. pyradiomics 3.0.1 must be built with
NumPy 1.x and an older setuptools present first:

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install "setuptools<65" wheel versioneer "numpy==1.26.4"
pip install --no-build-isolation -r requirements.txt        # base (demo)
pip install --no-build-isolation -r requirements-real.txt   # adds idc-index, pydicom, pydicom-seg
```

## Fallback: conda

```bash
conda env create -f environment.yml
conda activate imaging-ml-env
python -c "import radiomics; print(radiomics.__version__)"   # expect 3.0.1
```

## Known failure: pyradiomics 3.1.0 on Python 3.10+ / 3.12

pyradiomics 3.1.0 fails to install on Python 3.10+ and to import on 3.9. Reproduced on Python
3.12: install fails during metadata generation with `AttributeError: module 'configparser'
has no attribute 'SafeConfigParser'` — removed in 3.12 and called by pyradiomics 3.1.0's own
`versioneer.py`. This is a real package incompatibility, not a user misconfiguration. Fix:
pyradiomics 3.0.1 on Python 3.11 with NumPy 1.x (the pinned/locked configuration), not a
different 3.10+ patch version.

## NumPy 2.x failure (why numpy is pinned to 1.26.4)

pyradiomics 3.0.1 ships a compiled C extension (`_cmatrices`) built against the NumPy 1.x C
ABI. Under NumPy 2.x it fails at `import radiomics` with `ImportError: numpy.core.multiarray
failed to import`. A forced source rebuild against numpy 2.0.2 did **not** fix it — the
extension still resolves the NumPy-1.x `numpy.core.multiarray` path that NumPy 2 removed.
numpy 1.26.4 was verified end to end (a real extraction returning ~107 features, not just an
import). An earlier numpy 2.0.2 note came from an Apple-Silicon Mac where only `import
radiomics` was checked, never an extraction — which is exactly where the ABI mismatch bites.
Treat NumPy 1.x as required until someone verifies a full extraction under NumPy 2 on their
platform.

## idc-index coexistence and the resolution-too-deep pitfall

idc-index installs alongside pyradiomics once pandas is pinned to 2.2.3 (idc-index needs
`pandas<=2.2.4`; the earlier conflict was pandas 2.3.3). idc-index is pinned to `==0.12.4`,
not a loose bound: a loose bound pulls duckdb/pyarrow and sends pip's resolver into a
"resolution-too-deep" failure. If you hit that with the pip fallback, install idc-index on its
own line after the rest, or add `duckdb==1.1.3`. `uv` plus the lockfile avoids this entirely.

## Why JupyterLab is not in the environment

pydicom-seg 0.4.1 requires `jsonschema<4`, while modern JupyterLab needs `jsonschema>=4.18`.
Installing both in one environment conflicts. So this environment is used only as a notebook
*kernel*, and JupyterLab is launched separately with `uv tool run --from jupyterlab
jupyter-lab` (or from your base/conda install). Register the kernel with `python -m ipykernel
install --user --name imaging-ml ...` and select it in JupyterLab.

## Version check cell

Notebooks generated by this skill should use a version-check cell that asserts the locked
configuration:

```python
import sys
import importlib.metadata

REQUIRED = {
    "pyradiomics": "3.0.1",
    "SimpleITK": "2.5.3",
    "scikit-learn": "1.6.1",
    "pandas": "2.2.3",     # 2.2.x so idc-index can coexist
    "numpy": "1.26.4",     # NumPy 1.x REQUIRED — see "NumPy 2.x failure"
}

print(f"Python: {sys.version}")
for pkg, exact_ver in REQUIRED.items():
    try:
        installed = importlib.metadata.version(pkg)
        status = "OK" if installed == exact_ver else f"WARNING: {installed} != {exact_ver} (locked version)"
        print(f"{pkg}: {installed} [{status}]")
    except importlib.metadata.PackageNotFoundError:
        print(f"{pkg}: NOT INSTALLED — run: uv sync --locked")
```

An exact-match check is deliberate: pyradiomics 3.1.0 is a confirmed failure, so a `>=` check
would pass a researcher on a broken version. If a newer configuration is verified in future,
update this cell, the pins in `pyproject.toml`, and `uv.lock` together.

## IDC data version

Separately from the Python environment, IDC data is versioned. Any notebook that queries IDC
should call and record `client.get_idc_version()` immediately after data access; results are
not guaranteed to reproduce across IDC data versions.
