# Setup: getting the notebook ready to run

This page walks you through building the software environment the UPenn-GBM notebook needs. You
only do this **once**. After that, you just activate the environment and open the notebook.

You do not need to understand the commands to run them. Copy each block, paste it into a terminal,
and press Enter. Where something might go differently on your machine, this page says so.

There is nothing here that requires editing a configuration file by hand. If you were ever told to
"update `environment.yml`," you can ignore that — the notebook installs what it needs on its own.

---

## What you need first

- A Mac (these instructions were written and tested on an Apple-chip MacBook Air).
- **Miniconda** installed. This is the tool that manages separate Python setups so they do not
  interfere with each other. If you do not have it, install it from
  https://docs.conda.io/en/latest/miniconda.html and then restart your terminal.

To check whether you already have it, open a terminal and type:

```bash
conda --version
```

If that prints a version number, you are set. If it says "command not found," install Miniconda
first.

---

## The one-time build

The notebook needs an **older version of Python (3.9)**. This is not optional — the measurement
library, PyRadiomics, does not work on newer Python. So the first step is to create a dedicated
Python 3.9 environment. We will call it `radiomics_env`.

### Step 1 — Create the environment

```bash
python3.9 -m venv ~/radiomics_env
```

If that gives an error saying `python3.9` is not found, you do not have Python 3.9 available yet.
Install it, then re-run the line above:

```bash
conda create -y -n py39helper python=3.9
conda run -n py39helper python -m venv ~/radiomics_env
```

Either way, you should now have a folder at `~/radiomics_env`. That folder *is* the environment.

### Step 2 — Turn the environment on

```bash
source ~/radiomics_env/bin/activate
```

Your terminal prompt should now start with `(radiomics_env)`. That prefix is how you know the
environment is active. **Every time** you come back to work on this notebook, you run this one line
first.

Confirm you are on the right Python:

```bash
python --version
```

It should say **Python 3.9.something**. If it says 3.11, 3.12, or 3.13, the environment is not
active — go back and run the `source` line again.

### Step 3 — Install the packages

You have two options here, and they end in the same place.

**Option A — let the notebook do it (simplest).** Just open the notebook (Step 4 below) and run its
first cell. That cell installs everything automatically. Choose this if you would rather not think
about it.

**Option B — install now, from the terminal.** Some people prefer to see the install finish before
opening the notebook. If so, run:

```bash
pip install \
  pandas==2.2.3 numpy==1.26.4 SimpleITK==2.5.3 pyradiomics==3.0.1 \
  pydicom==2.4.4 pydicom-seg==0.4.1 scikit-learn==1.6.1 lifelines \
  idc-index jupyterlab ipykernel
pip install "jsonschema>=4.18.0"
```

That last line matters: the package before it quietly installs an old helper that breaks
JupyterLab, and this puts the right version back. Running it every time is harmless.

The exact version numbers are not arbitrary. They are the combination verified to work together;
the reasoning is in `../skills/imaging-ml-skill/references/environment_setup.md` if you are curious.

### Step 4 — Register the environment with Jupyter, then open it

```bash
python -m ipykernel install --user --name radiomics_env
jupyter lab
```

JupyterLab opens in your browser. Open the notebook
`02_upenn_gbm_idh_radiomics_survival.ipynb`, and check the **kernel name in the top-right corner**.
It should say `radiomics_env`. If it says anything else, click it and choose
**Change Kernel → radiomics_env**. Running against the wrong kernel is the single most common way to
waste an hour, so it is worth the two-second glance.

---

## Every time after this

Once the one-time build is done, starting a work session is just two lines:

```bash
source ~/radiomics_env/bin/activate
jupyter lab
```

---

## If something looks wrong

**`python --version` says 3.12 (or anything not 3.9).**
The environment is not active. Run `source ~/radiomics_env/bin/activate` again and check the prompt
starts with `(radiomics_env)`.

**JupyterLab will not start, mentioning `jsonschema`.**
Run `pip install "jsonschema>=4.18.0"` and start it again.

**The notebook's version-check cell shows a `WARNING`.**
It will tell you which package is the wrong version and what it expected. Re-run the notebook's
install cell, or the Option B block above, to correct it.

**A download cell hangs or errors partway.**
It is usually a network hiccup. Re-run the cell; downloads resume where they left off.

**The notebook's data-gathering step says it found zero usable image + outline pairs.**
That is a real finding, not a crash — it means the tumor outlines were drawn on a different scan
than the notebook expected, and the notebook prints which scan they were drawn on. Bring that
message back and the analysis can be pointed at the right scan.
