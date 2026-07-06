Great project — this is a classic "link clinical/molecular cohort to imaging cohort" problem, and the tricky part is almost never the modeling, it's the **cohort matching and identity linkage** between CTDC and IDC. Here's how I'd approach it end to end.

## 1. Clarify the linkage strategy first (this determines everything else)

CTDC (Clinical and Translational Data Commons) and IDC (Imaging Data Commons) are separate repositories under the NCI Cancer Research Data Commons (CRDC) umbrella, and they are **not guaranteed to share patient identifiers out of the box**. Before writing any code, I'd want to know:

- Is your EGFR-mutant cohort coming from a specific CTDC-hosted study (e.g., a trial or biobank collection) that *also* has a companion imaging collection in IDC? Some CRDC programs (e.g., NLST, TCGA, CPTAC-derived efforts) have matched clinical+imaging arms, but most CTDC studies do **not** automatically have a paired IDC collection — you have to check case by case.
- If there's no pre-linked study, you're likely doing a **cross-commons cohort match** based on shared metadata (cancer type, histology, demographics, treatment) rather than a true patient-level join. That's an important distinction to be upfront about — it affects whether you can claim "matched" patients (same individual) versus "matched" cohorts (similar population characteristics).

**My first question back to you:** Do you know whether your CTDC cohort and a target IDC collection share a common study/program (so there's a real submitter ID or case ID crosswalk), or are you trying to match two independently-collected NSCLC cohorts on phenotype alone? The downstream workflow is quite different depending on the answer, and I don't want to assume which one you're in.

## 2. Pull and characterize your CTDC cohort

- Query CTDC (via its GraphQL API or the web portal's cohort builder) for your EGFR-mutant lung adenocarcinoma patients, pulling: case/patient IDs, diagnosis (histology, stage), molecular results (EGFR mutation status/variant), demographics, treatment history (specifically TKI regimen — erlotinib, gefitinib, osimertinib, etc.), and response/outcome data (RECIST response, PFS/OS if available).
- Export this as a flat table (patient ID + relevant fields) — this becomes your "ground truth" labeled cohort for the response-prediction task.
- Pay attention to what identifiers are present. CTDC cases typically carry a study-specific submitter ID; you'll need to know if that ID (or something derivable from it, like an originating biobank/protocol number) appears anywhere in IDC's case metadata.

## 3. Identify candidate IDC collections

- Search IDC's collection catalog for NSCLC / lung adenocarcinoma CT collections. You're looking for collections with chest CT (ideally pre-treatment baseline, since you want to predict response *before* therapy) and enough clinical annotation to potentially cross-reference.
- For each candidate collection, check whether it documents EGFR mutation status or links back to a CTDC/GDC/other CRDC study with molecular data. If a collection's clinical supplement already contains EGFR status, you may not need CTDC at all for that subset — worth checking for overlap/redundancy.
- I don't have current, verified collection names or patient counts in front of me for this — IDC's catalog changes as collections are added/deprecated, so I'd want to pull the live list (via the IDC portal or `idc-index`/BigQuery) rather than rely on collection names from memory, since I can't guarantee any specific number I gave you would be accurate as of today.

## 4. Establish the actual patient-level link

This is the step most people underestimate. Realistic options, roughly in order of rigor:

1. **Shared case/submitter ID crosswalk** — if both repositories descend from the same parent study/program, there's often a crosswalk table (sometimes published, sometimes you derive it by matching submitter IDs that appear in both systems' metadata). This is the only way to get true patient-level (not just cohort-level) matching.
2. **Biospecimen/aliquot ID linkage** — if CTDC has biospecimen barcodes that also appear in IDC's clinical supplement files (common in some TCGA/CPTAC-style collections), that's a usable join key.
3. **Phenotype-matched cohort (no true linkage)** — if there's genuinely no shared ID, you'd instead build two separate cohorts (EGFR+ from CTDC, EGFR+ from an IDC-linked source or matched by close phenotype) and treat this as a cohort-level association study, not a per-patient multimodal study. Be explicit in any resulting paper/notebook about which of these you actually have, since reviewers will ask.

I'd strongly recommend not proceeding past this step until the linkage type is confirmed — it changes your unit of analysis.

## 5. Download and prepare the imaging data

- Once you have the IDC case/series IDs for your matched patients, use IDC's tooling (the `idc-index` Python package or BigQuery access to the IDC metadata tables) to pull series-level metadata, then download DICOM via `s5cmd`/the IDC download tools rather than the web UI, for reproducibility.
- Filter to baseline (pre-TKI) CT series. Watch for: contrast vs. non-contrast, slice thickness consistency, reconstruction kernel — these affect radiomics feature stability and may need to be harmonized or used as stratification/covariates.
- If segmentations (tumor masks) aren't already provided in the collection, you'll need a segmentation step — either manual/semi-automated (e.g., 3D Slicer) or an automated nodule/tumor segmentation model, before feature extraction.

## 6. Feature extraction and modeling

- **Radiomics route:** extract handcrafted features (PyRadiomics is the standard) from the segmented tumor volume — shape, intensity, texture (GLCM, GLRLM, etc.). This is the more defensible starting point for a clinical-translational audience and works with smaller sample sizes.
- **Deep learning route:** 3D CNN or a foundation-model embedding (e.g., a pretrained CT foundation model) on the tumor ROI or whole-lung volume, if your matched cohort is large enough to support it — for TKI response prediction this is often n in the low hundreds at best across public collections, which tends to favor radiomics + classical ML (e.g., regularized logistic regression, random forest, or elastic-net Cox models) over deep learning from scratch.
- **Outcome definition:** decide explicitly what "response" means — RECIST best response, PFS at some landmark, or binary responder/non-responder — and confirm this is consistently defined in your CTDC outcome fields.
- **Multimodal fusion:** if you also want to combine imaging features with the EGFR mutation subtype (exon 19 del vs. L858R vs. others have different TKI sensitivity profiles) and clinical covariates, a late-fusion model (separate imaging and clinical/molecular branches combined at a final layer, or simple feature concatenation into one classical model) is the most robust choice for small-to-moderate cohorts.

## 7. Validation

- Given likely small matched-cohort size, use nested cross-validation or repeated stratified k-fold rather than a single train/test split, and report confidence intervals.
- If at all possible, hold out or seek an external validation cohort (e.g., a different IDC NSCLC collection or a CTDC study not used in training) — single-cohort radiogenomics studies are notoriously prone to overfitting and poor generalization, and reviewers will flag this.
- Check for batch effects between CTDC-sourced and IDC-sourced data if they come from different institutions/scanners — this is a common confound in radiogenomics work.

## What I'd need from you to get more concrete

1. The specific CTDC study/cohort name (e.g., is this Cancer Moonshot Biobank, a specific trial, etc.) — so I can speak to what fields and identifiers it actually exposes.
2. Whether you already know of a specific IDC collection you're targeting, or want help searching for candidates.
3. Roughly how many EGFR-mutant patients are in your CTDC pull — this matters a lot for whether deep learning is even viable versus radiomics + classical ML.
4. How "treatment response" is defined in your data (RECIST, PFS, something else).

Happy to help build out the actual data-pulling code (CTDC query, IDC search/download) once I know which of these linkage scenarios you're in — I'd rather not write a notebook that assumes a patient-level join exists if it turns out you only have two independently-collected cohorts.
