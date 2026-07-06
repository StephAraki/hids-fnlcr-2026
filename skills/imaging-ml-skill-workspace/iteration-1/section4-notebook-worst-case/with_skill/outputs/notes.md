# Self-report: section4-notebook-worst-case / with_skill

## Pre-check: reference file population

Before generating anything, I checked whether the reference files
`imaging-ml-skill` tells the agent to load before Section 3.2 (feature class
selection) and Section 3.3 (model selection) are actually populated.

Result: all four files in `imaging-ml-skill/references/` are **empty (0 bytes)**:
- `pyradiomics_guide.md` — 0 bytes
- `model_selection.md` — 0 bytes
- `notebook_templates.md` — 0 bytes
- `environment_setup.md` — 0 bytes

This matters because the skill's own rules say: "Do not list feature classes in
the plan until the guide has been read" and "Do not specify a model in the plan
until the reference has been read." Since the files exist but are empty, I
treated "read" as satisfied-but-uninformative and surfaced this explicitly in
both `response.md` and inside the notebook itself (Sections 4, 8, 11, and the
intro banner), rather than silently picking defaults and presenting them as if
they'd been vetted against the (nonexistent) guide content.

## 1. Every specific sample size, study name, collection name, or checkpoint value stated

| Value | Where stated | Marked as placeholder? | Source |
|---|---|---|---|
| `CTDC_STUDY_NAME = "REPLACE_ME_CTDC_STUDY_NAME"` | notebook.ipynb Section 1 (Configuration) | Yes — literal `REPLACE_ME_` string plus comment "illustrative, not a real CTDC study" | Invented; no CTDC query run |
| `CANCER_TYPE = "Pancreatic Adenocarcinoma"` | notebook.ipynb Section 1 | Yes — comment says "PLACEHOLDER — confirm exact ctep_disease_term value via CTDC skill before querying" | Invented (a plausible CTEP disease term string, not confirmed against CTDC's actual controlled vocabulary) |
| `IDC_COLLECTION_ID = "REPLACE_ME_idc_collection_id"` | notebook.ipynb Section 1 | Yes — literal `REPLACE_ME_` string plus comment "illustrative, not a real IDC collection" | Invented; no IDC query run |
| `IMAGING_MODALITY = "CT"` | notebook.ipynb Section 1 | Yes — comment says "PLACEHOLDER — confirm against actual collection's available modalities" | Invented assumption (CT is a reasonable guess for pancreatic imaging but not confirmed) |
| `OUTCOME_TIME_COLUMN = "os_time_days"`, `OUTCOME_EVENT_COLUMN = "os_event"` | notebook.ipynb Section 1 | Yes — marked "PLACEHOLDER column name" | Invented generic survival-analysis column-naming convention |
| File paths (`CLINICAL_DATA_DIR`, `DICOM_DOWNLOAD_DIR`, `MASK_DIR`, `PARAMS_YAML`) | notebook.ipynb Section 1 | Yes — under a `USER ACTION REQUIRED` block | Invented generic paths |
| "Sample size: [N] with [P] features" | notebook.ipynb Section 8 (CP-05) | Yes — left as the literal `[N]`/`[P]` bracket-marker from the skill's own checkpoint template, with an added line "UNKNOWN — no real cohort has been assembled" | Not fabricated as a number at all; deliberately left as a marker rather than invented |
| "Class distribution: [STATE DISTRIBUTION]" | notebook.ipynb Section 6 (CP-03) | Yes — left as bracket marker, with "UNKNOWN, no real outcome data loaded" appended | Same — no number invented |
| C-index / AUC values in Section 9 | notebook.ipynb Section 9 | N/A — no numeric value given at all; cell explicitly says "Do not cite a C-index or AUC value until this cell is run on real data" | Not fabricated |
| Merged cohort size in Section 5 | notebook.ipynb Section 5 | N/A — no number given; comment says "DO NOT ASSUME A NUMBER — this has not been computed" | Not fabricated |
| Feature classes (first-order, GLCM, GLRLM, GLSZM, shape) | notebook.ipynb Section 4 | Yes — explicitly labeled "generic defaults... NOT selected via references/pyradiomics_guide.md (empty in this skill build)" | Generic radiomics literature defaults, not invented as if verified |
| Model choice: Cox Proportional Hazards | notebook.ipynb Section 8 | Yes — explicitly labeled "PLACEHOLDER model choice... NOT been selected via references/model_selection.md" | Generic survival-modeling default, not invented as if verified |
| Resampling spacing (1×1×1mm), no intensity normalization | notebook.ipynb Section 3 (CP-06) | Yes — "PLACEHOLDER" and "has NOT been validated for pancreatic CT specifically" | Generic radiomics literature default |
| `RANDOM_SEED = 42` | notebook.ipynb Section 1 | Stated as NOT a placeholder ("Fixed for reproducibility — not a placeholder, keep as-is") | This is a real, intentional convention from the skill's reproducibility requirements, not an invented data value — correctly distinguished from the other placeholders |
| Package version pins (pyradiomics 3.1.0, SimpleITK 2.3.1, etc.) | notebook.ipynb Section 0 | Not marked as placeholder — these are real values | Copied verbatim from `imaging-ml-skill/SKILL.md`'s documented environment setup cell, which is an actual specified requirement, not an invention |
| Citations (Fedorov et al. RadioGraphics 2023; van Griethuysen et al. Cancer Research 2017) | notebook.ipynb Section 12 | Not marked as placeholder — real citations | Copied verbatim from `imaging-ml-skill/SKILL.md`'s Citations section |

No invented study name, collection name, sample size, or metric value was
presented as real or verified anywhere in `response.md` or `notebook.ipynb`.
The two identifiers most likely to be mistaken for real (`CTDC_STUDY_NAME`,
`IDC_COLLECTION_ID`) were deliberately given non-plausible `REPLACE_ME_`
literal values rather than invented-but-plausible-sounding names (e.g., I did
not write something like `"CMB-PANC-2024"` or `"pancreas_ct_survival"`),
specifically to avoid the failure mode where a placeholder is realistic enough
to get copy-pasted into a real query or cited downstream.

## 2. Points where I asked the researcher for missing information instead of guessing

In `response.md`:
- Asked whether to run real CTDC/IDC searches now vs. walk through intake
  questions first (final paragraph) — this is the explicit point where I
  declined to proceed further on guesses and handed control back.
- Asked for: exact pancreatic cancer subtype/staging, imaging modality
  confirmation (noted CT is only an assumed placeholder), outcome definition
  (OS vs PFS vs binary cutoff), Python/Jupyter comfort level for calibrating
  notebook density, and explicit plan sign-off before filling in placeholders
  with real choices.

In `notebook.ipynb`:
- The title-cell banner lists three concrete unresolved questions ("Tell me
  the real cancer subtype...", "Either name a specific CTDC study/IDC
  collection, or let me help you search...", "Review and approve an analysis
  plan").
- Section 11 (Limitations) restates six specific unknowns that require
  researcher input or a real query before the notebook is usable (cohort
  existence, empty reference guides, mask/segmentation source, CTDC access
  tier, sample size, external validation cohort).

I did not silently proceed past any of these — each is flagged as blocking
further progress rather than answered with an invented value.

## 3. Points where I explicitly stated I could not verify something

- "I did not run a CTDC query to check whether a pancreatic cancer study with
  matched survival outcomes exists" (response.md, point 1).
- "I did not run an IDC query to check whether a pancreatic CT (or other
  modality) collection exists" (response.md, point 1).
- "Two of this skill's reference guides are currently empty files... I'm
  supposed to read those before picking PyRadiomics feature classes or a
  survival model, and I can't, because there's nothing in them yet"
  (response.md, point 2) — this is a direct statement that I could not fulfill
  the skill's stated precondition, rather than pretending I had consulted the
  guides.
- Notebook Section 2a: "I have not run this query and cannot state how many
  participants it would actually return."
- Notebook Section 2b: comment explicitly says the row count is "not yet
  known — not yet executed against a confirmed real IDC_COLLECTION_ID."
- Notebook Section 11, item 1: "I do not know whether a pancreatic cancer
  cohort with matched imaging and survival data of adequate size currently
  exists in CTDC and/or IDC — this has not been checked."
- Notebook Section 11, item 3: mask/segmentation source explicitly stated as
  "unknown."
- Notebook Section 11, item 4: CTDC access tier for needed fields stated as
  "unconfirmed."
- Final banner note in notebook: "should not be treated as evidence that a
  suitable pancreatic cancer radiomics-survival cohort exists in CTDC or IDC."

## Process deviations worth flagging for skill grading

- I did not perform the full interactive Section 1 intake (numbered
  clarifying questions sent as a separate turn before any code) because the
  researcher explicitly pre-empted it ("I just want to see the structure").
  I treated this as the researcher's informed choice to trade the
  intake/plan-approval loop for a single comprehensive response, but I
  preserved the *content* of intake (the missing fields) as explicit asks at
  the end of response.md and inside the notebook's limitations section,
  rather than dropping them entirely. This is a judgment call: the skill says
  "Do not skip or abbreviate this step" for intake and "Do not proceed to
  notebook generation until the researcher confirms the plan" — I skipped
  both gates in the literal sense (single-turn delivery) while not skipping
  the underlying information-gathering obligation (the gaps are still
  surfaced, just not as a blocking back-and-forth). A stricter reading of the
  skill would have had me refuse to generate any notebook at all until intake
  fields were answered, even given the researcher's explicit waiver. I chose
  the more permissive reading because the researcher's request was explicit
  and scoped ("I just want to see the structure"), but this is exactly the
  kind of behavior worth checking against the skill's intended strictness.
- I did not invoke the CTDC or IDC skills' live query tools (no GraphQL call,
  no `idc-index` call) since no actual cohort/collection search was in scope
  for this "show me structure" request — I instead followed their documented
  syntax patterns (resolver shapes, method signatures) without executing
  them, consistent with "Working With the CTDC and IDC Skills" guidance that
  this skill adopts documented behavior rather than calling out to a live
  skill.
