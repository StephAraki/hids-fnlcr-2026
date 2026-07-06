Before I build your analysis plan, I have a few quick questions to make sure the notebook fits your research question exactly. But first, here's the routing answer you asked for, plus what I could actually verify about cohort size — I ran live queries rather than guessing, so I want to be precise about what's confirmed versus what still needs your input.

## Routing: you'll likely need both CTDC and IDC

For melanoma, "imaging + other clinical info" almost always means a **cross-commons workflow**:

- **CTDC (Clinical and Translational Data Commons)** is where the non-imaging clinical variables live — demographics, diagnosis details, treatment/targeted therapy records, specimen metadata.
- **IDC (Imaging Data Commons)** is where the imaging series themselves live, plus basic imaging-adjacent metadata (modality, body part, etc.).

There is currently **one study in CTDC**: the **Cancer Moonshot Biobank (CMB)**, a longitudinal clinical/biospecimen dataset collected from late-stage cancer patients during standard-of-care treatment (ClinicalTrials.gov NCT04314401). I'm not asserting there's a melanoma-specific CTDC study beyond this — CTDC's current inaugural dataset is CMB, and additional studies are released over time, so it's worth checking the CTDC portal's Studies page yourself before we lock anything in, in case something new has been added since I checked.

On the imaging side, I queried IDC directly and found an IDC collection called **`cmb_mel`** whose patient IDs use the same `MSB-#####` ID format as CTDC's CMB participants — this is the Cancer Moonshot Biobank's melanoma imaging arm, and it's listed as linked to "Clinical" supporting data in IDC's collection metadata (meaning the imaging is intended to pair with the CTDC clinical record, not duplicate it). There are also other melanoma-related IDC collections (e.g., `tcga_skcm`, `tcga_uvm`, `cptac_cm`) that are **not** linked to CTDC — those are standalone imaging+genomics cohorts, not clinical+imaging via CTDC. If your "other clinical info" need is broader than what CTDC harmonizes (e.g., genomic subtype, specific lab values), one of those other collections — or a GDC/PDC pairing instead of CTDC — might actually be the better fit. I don't yet know enough about which specific clinical variables you need to tell you definitively, which is part of why I want to ask the intake questions below.

## Rough cohort size — verified just now, not estimated

I ran live, anonymous-access queries against the CTDC production GraphQL endpoint and the IDC index (`idc-index` v0.12.3, IDC data version v24) to get real numbers rather than guess. As of this query:

| Source | Filter | Count |
|---|---|---|
| CTDC (CMB study) | `ctep_disease_term: ["Melanoma"]` | **45 participants** (out of 248 total CMB participants currently in CTDC) |
| IDC | `collection_id = 'cmb_mel'` | **54 patients**, 777 imaging series |
| Overlap | Same participant ID present in both | **42 participants** |

So a rough working cohort — melanoma patients with *both* CTDC clinical data and matched IDC imaging via the linked `cmb_mel` collection — is in the neighborhood of **~42 participants** right now. That's a small cohort for most ML approaches, and it's a snapshot: CTDC's filter is on `ctep_disease_term`, and I want to flag that this is the only disease-classification field that's actually populated for melanoma right now — `stage_of_disease` and `tumor_grade` are both empty in the current CMB release in CTDC, so if "other clinical info" includes disease stage, that variable is not currently available from CTDC for this cohort, full stop. You'd need a different source for it if it's essential.

A few more caveats on those numbers, stated plainly so you can decide how much to lean on them:

- These were anonymous (no dbGaP/eRA login) queries. CTDC's open tier can silently undercount if any matching participants are controlled-access — the count could be a floor, not an exact total, until run with credentials.
- The `cmb_mel` IDC collection breaks down by modality as: SM (slide microscopy) 49 patients/116 series, CT 32 patients/617 series, PT (PET) 5 patients/38 series, US 5 patients/5 series, MR 1 patient/1 series — so depending on which modality you need, your *usable* cohort could be much smaller than 42–54. For example, if you specifically need CT, you're looking at 32 IDC patients before even checking how many of those also have the clinical variable you care about in CTDC.
- I have not checked whether CTDC participant-level access for this cohort requires dbGaP authorization for the specific fields you'd want — see the access note below.

## Access note

CTDC participant-level data has three access tiers (open / registered / controlled). I don't yet know which fields you need, so I can't tell you which tier applies to your specific pull. If your analysis needs anything beyond open-tier aggregate/summary data, you may need dbGaP authorization before the notebook's CTDC cells can actually run. If you don't already have that authorization, let me know and I'll build the notebook with that step clearly flagged as blocked until access is granted, rather than assuming you have it.

IDC imaging itself is fully public — no authentication needed for the `cmb_mel` series.

## What I still need from you before I can build an analysis plan

1. **Imaging modality** — Given the breakdown above (SM, CT, PT, US, MR), which one(s) do you actually want? This drives both your real cohort size and the feature-extraction approach.
2. **Outcome variable** — What are you trying to predict or stratify (survival, treatment response, a molecular subtype, something else)? This affects both modeling choices and whether CTDC's currently-populated fields (`ctep_disease_term`, `sex`, `race`, `ethnicity`) are sufficient, or whether you need fields that aren't populated yet (like stage).
3. **The "other clinical info"** — Can you say more specifically what clinical variables you need? If it's demographics/treatment/targeted-therapy data, CTDC's CMB likely has it. If it's something like molecular subtype or detailed staging, we may need to route partly or fully outside CTDC.
4. **Do you have dbGaP/eRA Commons authorization for CTDC controlled-access data**, or should I plan for an open-tier-only pull for now?
5. **Your comfort level with Python/Jupyter** (none / some / comfortable) — so I calibrate how much explanation goes into the notebook once we get there.

Once I have these, I'll put together a full written analysis plan (cohort definition, imaging/feature-extraction approach, modeling strategy, evaluation plan, and known limitations) for you to review before I generate any notebook code.
