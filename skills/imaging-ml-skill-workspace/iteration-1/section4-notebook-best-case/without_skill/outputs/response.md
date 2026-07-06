Got it — since you've already nailed down the design, here's a complete notebook scaffold for the CPTAC-LUAD EGFR mutation prediction task: CTDC for clinical/cohort data, IDC for CT imaging, first-order + GLCM radiomic features, random forest with 5-fold CV.

A few things up front, before you run this, because I'd rather flag them than have you discover them at 2am:

1. **I can't independently verify the "84 patients" figure.** I'm taking that as a number you've already derived (e.g., from your own CTDC query or a prior cohort definition). I have not queried CTDC myself in this conversation, so I don't know the current total enrollment, the number with EGFR mutation calls available, or the number with matched CT imaging in IDC. The notebook below queries CTDC and IDC directly and asserts/reports the actual count it finds — please check that it lands on 84, and if it doesn't, treat my notebook's filtering logic as the thing to debug, not the number 84.

2. **I don't know the exact current CTDC GraphQL schema field names off the top of my head** (e.g., whether the mutation field is `mutation_status`, `egfr_mutation_status`, under a `molecular_characterization` node, etc.), and I haven't called the live API to check. I've written the query with my best-guess field names based on how CTDC's data model is typically structured (case → diagnosis → molecular characterization), but you will very likely need to adjust field names after inspecting the actual schema (introspection query included) or the CTDC data dictionary.

3. **I don't know the exact current IDC collection identifier string, S3/GCS bucket layout, or DICOM series counts for `cptac_luad`** — I'm using `idc-index` (the standard Python client) with collection_id `"cptac_luad"`, which matches IDC's lowercase-underscore naming convention for CPTAC collections, but I have not run this against the live IDC index in this conversation, so I can't confirm the spelling, the current data release version, or how many series/patients actually come back.

4. **Radiomics extraction needs lesion segmentation masks.** CPTAC-LUAD CT in IDC may or may not ship with existing tumor segmentations (SEG/RTSTRUCT objects). I haven't verified this. The notebook includes a step to check for existing segmentation objects and a fallback placeholder for manual/3D Slicer segmentation if none exist — this is the single most likely place your actual N will drop below 84, since radiomics requires an ROI, not just a CT series.

5. **EGFR mutation status as a label**: I'm assuming you mean a binary mutant/wild-type label. If CTDC reports multiple EGFR variant types (exon 19 del, L858R, T790M, etc.) you'll want to decide whether to collapse them or model variant-specific status — I've left a single TODO for that decision rather than guessing.

I did not ask you clarifying questions about any of this because you explicitly asked me to skip intake — but I want to be upfront that "skip the intake" means I'm filling these gaps with reasonable defaults and clearly marked TODOs rather than verified facts, not that I independently confirmed your numbers.

Here's the notebook (`notebook.ipynb`, saved alongside this response). Structure:

1. **Setup & environment** — package installs (`requests`, `idc-index`, `pyradiomics`, `SimpleITK`, `scikit-learn`, `pandas`)
2. **CTDC cohort query** — GraphQL query against the CTDC API for CPTAC-LUAD cases with EGFR mutation status, with an introspection cell to confirm/correct field names
3. **IDC imaging pull** — `idc-index` lookup of `cptac_luad` CT series, joined to the CTDC case IDs by patient/case identifier
4. **Segmentation check** — verify availability of ROI masks; placeholder/TODO if absent
5. **Radiomic feature extraction** — `pyradiomics` configured for first-order + GLCM classes only
6. **Modeling** — `RandomForestClassifier`, stratified 5-fold CV, ROC-AUC / accuracy / F1 reporting, feature importance plot
7. **Caveats cell** at the end re-stating what's unverified

Take a look, swap in the real CTDC field names once you've checked the schema, confirm the IDC collection pull returns what you expect, and let me know if the segmentation step is a blocker — happy to help wire up a 3D Slicer or TotalSegmentator fallback if CPTAC-LUAD doesn't ship masks.
