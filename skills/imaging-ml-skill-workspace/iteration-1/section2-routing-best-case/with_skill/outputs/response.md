Thanks for laying out the question so clearly — this is a cross-commons workflow (CTDC + IDC), which is the most involved path this skill supports, so let me walk through the routing and then ask a few quick questions before I draft an analysis plan.

## Data source routing

Your request needs **both CTDC and IDC**:

- **CTDC** for the clinical/molecular cohort definition — EGFR-mutant status and lung adenocarcinoma diagnosis live in clinical/molecular data, not imaging metadata.
- **IDC** for the NSCLC CT imaging itself.

This is the "Imaging + clinical variables together" case, which is the full cross-commons pathway:

1. Use CTDC to define and export the clinical cohort (participant IDs + EGFR mutation status + treatment/response variables).
2. Use IDC to find CT imaging series for those same participants (matched on patient/submitter ID).
3. Download the matched DICOM series from IDC.
4. Extract radiomic features from the CT images with PyRadiomics.
5. Merge radiomic features with the CTDC clinical variables by participant ID.
6. Train and evaluate a model predicting TKI treatment response from the merged feature set.

Before I go further, I want to flag two real uncertainties rather than assume them away:

### 1. I can't yet confirm CTDC has a queryable EGFR-mutation field

CTDC's current verified, populated filter facets are `ctep_disease_term` (8 buckets), `sex`, `race`, and `ethnicity`. The full set of filter arguments the API exposes also includes `targeted_therapy_string`, which *may* be where EGFR-targeted TKI treatment (e.g., osimertinib, erlotinib) shows up — but I have not confirmed that EGFR mutation status itself is a populated, filterable field, and I'm not going to guess at its exact value strings. We'll need to run a discovery query against the live CTDC GraphQL endpoint to see what `targeted_therapy_string` and related fields actually contain before I write the cohort-definition query for the analysis plan. I am not stating any participant count, study name, or field-population claim beyond what's listed above — those are the only facets the CTDC skill's reference files confirm as verified against the live schema (verified May 19, 2026 per that skill's docs).

Also worth knowing: CTDC's currently documented inaugural dataset is the Cancer Moonshot Biobank (CMB). I don't know whether CMB — or any other CTDC study — actually contains a cohort of EGFR-mutant lung adenocarcinoma patients with CT imaging cross-references large enough to be useful for this analysis. That's a discovery question we need to answer with a real query, not something I can state as fact right now.

### 2. I can't yet confirm a specific IDC NSCLC CT collection match

IDC hosts multiple lung-cancer-related collections, but I don't have verified, current details on which collection(s) would best match a CTDC EGFR-mutant cohort (e.g., overlap in patient identifiers, whether CT series exist for the relevant patients, collection size). Per the IDC skill's own guidance, this has to be answered by querying the live `idc-index` locally (`client.sql_query()` against `collections_index` and `index`) — not from memory or web search, since collection contents and sizes change between IDC data versions. I won't name a specific collection or sample size until we've run that query.

### 3. Patient-ID matching between CTDC and IDC is not guaranteed to be trivial

Cross-commons matching in step 2 above depends on CTDC participant IDs and IDC `PatientID` values being linkable (directly, or via a crosswalk/submitter ID). I haven't verified that such a crosswalk exists or is documented for any specific CTDC study against any specific IDC collection. This is a real risk to flag, not something to assume works cleanly.

### Access note

If you don't yet have dbGaP/eRA Commons authorization for CTDC, participant-level clinical data (including treatment/mutation fields) may be Tier 2 (Registered) or Tier 3 (Controlled) rather than open. I can still build a skeleton notebook with placeholder data-loading cells that will run once you have access, but real query results and cohort counts won't be available until then. Let me know your access status so I calibrate the plan correctly.

## What I need from you before I draft the analysis plan

I have most of the required intake information already from your message:

- **Cancer type**: EGFR-mutant lung adenocarcinoma (NSCLC) — confirmed
- **Imaging modality**: CT — confirmed
- **Outcome variable**: treatment response to TKI therapy — confirmed
- **Data source intent**: cross-commons, CTDC + IDC — confirmed

I'm missing two things:

1. **Do you have a specific CTDC study or IDC collection already in mind**, or do you need help discovering them? (This determines whether we start with a live CTDC discovery query or you already know the study name.)
2. **How comfortable are you with Python and Jupyter notebooks** — none, some, or comfortable? This calibrates how much explanatory scaffolding goes into the generated notebook.

3. Also — **do you currently have dbGaP/eRA Commons authorization for CTDC controlled-access data**, or should I build around the open-tier assumption for now?

Once I have those answers, the next concrete step is to actually run discovery queries against the live CTDC GraphQL endpoint and the live IDC index (rather than have me guess at field values or collection names), so the analysis plan I hand you is grounded in real, current query results rather than assumptions. I'll bring those results back to you before writing any notebook code.
