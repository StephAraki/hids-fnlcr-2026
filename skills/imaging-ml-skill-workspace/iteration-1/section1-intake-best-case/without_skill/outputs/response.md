Great project — GBM survival prediction from radiomics is a well-trodden but still very active area, and TCGA-GBM is a natural choice on the imaging side because it has a matched genomics/clinical cohort (TCGA) that's been used in a lot of published radiogenomics work. Let me walk through how I'd approach the clinical/outcome data side, since that's what you're missing.

## On finding a CTDC study with GBM survival data

A few things worth being upfront about:

1. **I don't have live access to query the CTDC (Clinical and Translational Data Commons) catalog from here**, so I can't give you a verified, current list of CTDC study IDs, exact participant counts, or confirm which studies have GBM patients with survival/follow-up data as of today. CTDC is a relatively newer NCI Cancer Research Data Commons (CRDC) node, and its study list has been evolving, so anything I say from memory risks being stale or wrong.

2. **What I'd suggest instead of guessing study names:**
   - Go to the CTDC portal directly (search for "CTDC NCI" — it's part of the CRDC ecosystem alongside GDC, IDC, PDC, etc.) and use the cohort/study search filtered by disease site = "Brain" or diagnosis containing "glioblastoma" / "astrocytoma, IDH-wildtype."
   - Look specifically for studies that are **NCI-sponsored clinical trials or natural history studies with a neuro-oncology arm**, since CTDC's strength tends to be trial-linked clinical/outcome data (vs. TCGA-GBM itself, which has only limited, somewhat outdated clinical fields).
   - The CTDC GraphQL API (if you're comfortable with Python) lets you query programmatically once you've identified candidate study codes — I can help you write that query once you have a study ID, but I don't want to fabricate one.

3. **A more reliable path for TCGA-GBM-matched clinical/survival data specifically:** since your imaging cohort is TCGA-GBM, your clinical/survival variables will match up most cleanly with the **TCGA Pan-Cancer Clinical Data Resource (TCGA-CDR)** or the GDC's clinical endpoints for the TCGA-GBM project, rather than a CTDC study — because CTDC studies are generally *separate trial cohorts*, not necessarily linked by patient ID to TCGA barcodes. If your imaging data is TCGA-GBM (patient IDs like `TCGA-02-0003`), you want clinical data that's keyed to those same TCGA barcodes, which lives in:
   - **GDC (Genomic Data Commons)** — has the official TCGA-GBM clinical supplement (vital status, days to death/last follow-up, age, KPS, treatment).
   - **TCGA-CDR** (Liu et al., *Cell* 2018, "An Integrated TCGA Pan-Cancer Clinical Data Resource") — a commonly used curated outcomes resource that resolved a lot of inconsistencies in raw TCGA clinical files; widely used as the survival ground truth in TCGA radiogenomics papers.
   - **cBioPortal** for TCGA-GBM, which also exposes overall survival as months + status in an easy-to-query format.

   If you specifically need a CTDC-hosted study, that would be additive/comparison data from a different cohort (not patient-matched to your TCGA-GBM scans), useful for external validation but not for joining directly to your TCGA imaging features.

**My honest recommendation:** before I help you build a CTDC query, can you tell me — do you actually need the clinical data to come from CTDC specifically (e.g., institutional requirement, or you want an independent validation cohort), or would TCGA-GBM's own matched clinical/survival data (via GDC or TCGA-CDR) work for your primary analysis? That changes the right next step a lot, and I'd rather ask than send you chasing a CTDC study ID I'm not sure exists.

## What I can help with right now: the imaging/radiomics pipeline

While you sort out the clinical data source, here's a concrete pipeline for the IDC side that doesn't depend on that decision, since T1-CE and FLAIR feature extraction is identical either way:

### 1. Pull the TCGA-GBM series from IDC
Use `idc-index` (the lightweight Python client) to find the series UIDs for T1-post-contrast and FLAIR. In practice, TCGA-GBM's DICOM metadata is inconsistent in `SeriesDescription` (it's an older, retrospectively-curated collection), so you'll likely need to filter using a combination of `SeriesDescription` string matching (e.g., containing "FLAIR", "T1", "+C", "POST") and manual spot-checking rather than trusting a clean modality tag. I'd budget real time for this curation step — it's usually the most annoying part of working with TCGA-GBM imaging.

### 2. Get segmentations, or plan to generate them
Check whether the **TCGA-GBM collection in IDC has companion tumor segmentations** available as DICOM-SEG or RTSTRUCT objects (there are published GBM segmentation sets, e.g., from the BraTS-adjacent or QIN efforts, that have been mapped onto some TCGA cases) — if not, you'll need a segmentation step before radiomics, either:
   - A pretrained deep learning segmenter (e.g., an nnU-Net BraTS-trained model, or HD-GLIO) applied to your downloaded NIfTI/converted volumes, or
   - Manual/semi-automated segmentation if your sample size is small enough.

I don't want to assert that a specific named segmentation set exists for all TCGA-GBM cases in IDC without you confirming it in the portal — that's exactly the kind of detail that changes between IDC data releases.

### 3. Convert DICOM to NIfTI and extract radiomics
Standard stack: `dcm2niix` or `dicom2nifti` for conversion, then **PyRadiomics** for feature extraction (shape, first-order, GLCM/GLRLM/GLSZM/NGTDM texture features) per sequence, per tumor sub-region (enhancing tumor, edema, necrosis if you have multi-label masks).

### 4. Survival modeling
Once you have features + matched survival labels:
   - Start with **Cox proportional hazards** (via `lifelines`) using a handful of clinically-motivated features plus a small radiomics panel — avoid throwing hundreds of PyRadiomics features at a Cox model with a TCGA-GBM-sized cohort (n is typically in the low hundreds at most for this collection), since you'll badly overfit.
   - Consider penalized Cox (`scikit-survival`'s `CoxnetSurvivalAnalysis`) for feature selection under high dimensionality, or a random survival forest as a nonlinear baseline.
   - Report concordance index (C-index) with cross-validation, not just training fit, and consider a held-out or external validation split given how heavily TCGA-GBM radiomics has already been mined in the literature (reviewer pushback on overfitting/leakage is common in this exact subfield).

Want me to sketch the actual `idc-index` query code for pulling the T1-CE/FLAIR series first, or would it be more useful to nail down the clinical/survival data source before writing any code?
