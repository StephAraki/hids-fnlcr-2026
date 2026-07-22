## Setup

This project requires Python 3.11. The recommended setup uses `uv`, which can create the virtual environment and install dependencies faster than plain `venv`/`pip`.

Install `uv` first if needed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## For demo mode: 

```bash
cd skills/imaging-ml-skill
uv venv --python 3.11
source .venv/bin/activate
uv sync
python -m ipykernel install --user --name imaging-ml --display-name "Python (imaging-ml)"
```

## Run Jupyter outside the project environment:

`uv tool run --from jupyterlab jupyter-lab`

Open `notebooks/upenn_gbm_idh_radiomics_survival.ipynb` and select the kernel named `Python (imaging-ml)`.

## Real Data Mode

Shutdown the current demo-mode using `ctrl+c` on the terminal. Also close the jupyter notebook running in your browser to cleanly initialize the real mode. 

The default notebook runs in demo mode with synthetic data. To use real UPenn-GBM data, install the real-data extra:
```bash
cd /Users/apple/Documents/FNL/hids-fnlcr-2026/skills/imaging-ml-skill
source .venv/bin/activate
uv sync --extra real
```

After that, register the real kernel:
`python -m ipykernel install --user --name imaging-ml-real --display-name "Python (imaging-ml-real)"`

Relaunch Jupyter:

`uv tool run --from jupyterlab jupyter-lab`

Then set this in the notebook:

`DEMO_MODE = False`

## Why JupyterLab Is Not Installed In This Environment
pydicom-seg==0.4.1 requires jsonschema<4, while modern JupyterLab server requires jsonschema>=4.18. Installing both in the same environment creates a dependency conflict. For that reason, this project environment is used as a notebook kernel, and JupyterLab is launched separately with uv tool run jupyterlab