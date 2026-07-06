Good question, and it's a really common point of confusion, so let's sort out the routing first and then talk cohort size.

## Where your imaging data lives

For melanoma imaging, you're almost certainly going to be pulling from the **NCI Imaging Data Commons (IDC)**. IDC hosts DICOM-formatted radiology and (in some collections) pathology/dermoscopy imaging, harmonized and indexed so you can query it programmatically (via BigQuery or the `idc-index` Python package) and download cohorts via the IDC portal or CLI. If your "imaging" means dermoscopic/skin lesion images specifically, those may also show up in IDC if they've been ingested as a formal collection (some derived from TCGA or other curated dermoscopy sets), but a lot of dermoscopy benchmark data (e.g., ISIC) actually lives outside the NCI Cancer Research Data Commons (CRDC) ecosystem entirely, on the ISIC Archive. So the first branch point is: **is this radiologic imaging (CT/MR/PET) of melanoma patients, or is it skin-surface/dermoscopic imaging?** Those have different homes.

## Where your clinical data lives

This is the part where I want to be upfront that I'm not 100% certain without checking current holdings, but here's how I'd reason about it:

- **CTDC (Clinical and Translational Data Commons)** is the right home for clinical/phenotypic data tied to CRDC-curated clinical trial-style cohorts — things like the Cancer Moonshot Biobank. If your melanoma cohort overlaps with a Moonshot-affiliated trial or biobank effort, the clinical annotations (diagnosis, staging, treatment, demographics) would likely be in CTDC, and you'd want to link those records to imaging via shared case/patient identifiers in IDC.
- **GDC (Genomic Data Commons)** also carries clinical data (demographic, diagnosis, treatment, follow-up) for cohorts that have associated genomic data — for melanoma, the classic example is **TCGA-SKCM** (Skin Cutaneous Melanoma), which has clinical data in GDC and matched imaging in IDC under the same TCGA-SKCM collection name.
- If your cohort is from a specific clinical trial or a single institution's IRB-approved retrospective study rather than a public TCGA/CRDC collection, the clinical data might not be in any of these federal repositories at all — it could be sitting in a local REDCap database, an institutional EHR pull, or a SEER-linked dataset.

So, honestly, **I can't tell you with certainty which one applies without knowing more about your specific cohort.** Could you tell me:

1. Is this a public/TCGA-style cohort (e.g., TCGA-SKCM) or a private/institutional one?
2. Are you trying to link to a specific named trial or biobank (e.g., Cancer Moonshot Biobank), or just "melanoma patients with imaging" broadly?
3. What clinical variables do you actually need — basic demographics/staging, or treatment response/outcomes/genomics?

That will determine whether you're in CTDC, GDC, or somewhere outside the NCI CRDC ecosystem entirely.

## Rough cohort size

I want to flag clearly: **I do not have reliable, current, verified numbers for melanoma case counts in IDC, CTDC, or GDC**, and I don't want to hand you fabricated statistics that you might cite in a grant or paper. What I can tell you directionally, from general familiarity with these resources (not a live lookup):

- **TCGA-SKCM** is the best-known public melanoma cohort with both genomic/clinical data (GDC) and matched imaging (IDC) — historically on the order of a few hundred patients (TCGA-SKCM is commonly cited as having around 470 cases, though I'd treat that as approximate and unverified here), but **not all of those patients have radiology imaging** — TCGA imaging coverage is often sparse and skews toward pathology slides rather than CT/MR.
- CRDC-wide melanoma imaging cohorts outside TCGA do exist but I don't have confident counts to give you.
- Cancer Moonshot Biobank, if relevant, has multiple cancer types and I don't know offhand what fraction is melanoma or what the imaging linkage looks like.

**I'd strongly recommend not relying on my estimate here.** The right move is to query IDC's case/collection metadata directly (filtering on cancer type/primary site = melanoma) and cross-reference patient IDs against whichever clinical source we land on, then count the actual intersection. That intersection — patients with both imaging and the clinical variables you need — is almost always smaller than either source alone, sometimes dramatically so.

## Suggested next steps

1. Confirm which clinical variables and which imaging modality you actually need (this affects routing).
2. Once we know the target collection(s), I can help you write the IDC query (BigQuery or idc-index) to pull melanoma case/patient IDs and modality counts.
3. In parallel, pull the matching clinical table from GDC (if TCGA-SKCM) or CTDC (if Moonshot-affiliated) and compute the actual overlap by patient/case ID.
4. I'd treat any cohort number before that overlap step as a placeholder, not a number to plan a study around.

Let me know which of the scenarios above (public TCGA-style vs. institutional, radiology vs. dermoscopy) matches your situation and I can get much more specific.
