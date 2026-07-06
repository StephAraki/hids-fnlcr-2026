Before I generate this, a few things I want to flag up front, because they affect how much you should trust what I'm about to hand you.

**I'm going to build this as a clearly-labeled placeholder skeleton, not a notebook backed by real data.** You asked me to make up reasonable placeholder values so you can see the structure, and I will — but I'm not going to present any invented study name, collection name, sample size, or metric value as if it were real or verified. Every made-up value will be marked as a placeholder inline (in `USER ACTION REQUIRED` blocks, `[STATE CURRENT SELECTION]`-style markers, and explicit "not executed / illustrative only" notes), because I have not actually queried CTDC or IDC for this conversation, and I'm not willing to imply that I have.

A few specific limitations worth knowing before you look at the notebook:

1. **No cohort discovery happened.** I did not run a CTDC query to check whether a pancreatic cancer study with matched survival outcomes exists, and I did not run an IDC query to check whether a pancreatic CT (or other modality) collection exists. `CTDC_STUDY_NAME` and `IDC_COLLECTION_ID` in the notebook are literal placeholder strings (`REPLACE_ME_...`) for you to fill in once we've actually looked. If you want, I can run real CTDC and IDC searches next and come back with actual candidate studies/collections instead of placeholders.

2. **Two of this skill's reference guides are currently empty files** — `references/pyradiomics_guide.md` (which is supposed to govern feature-class selection) and `references/model_selection.md` (which is supposed to govern model choice). I'm supposed to read those before picking PyRadiomics feature classes or a survival model, and I can't, because there's nothing in them yet. So the feature classes (first-order, GLCM, GLRLM, GLSZM, shape) and the model (Cox proportional hazards) shown below are generic textbook defaults for radiomics survival modeling, not choices vetted against this skill's own guidance. I've flagged this directly in the notebook rather than quietly picking defaults and presenting them as considered choices.

3. **I skipped the normal intake and plan-approval steps** (cancer subtype detail, modality, outcome definition, data source intent, expertise level, and a reviewed analysis plan) because you explicitly asked for structure over process. That's a reasonable tradeoff for a "show me the shape of this" request, but it means nothing in this notebook reflects an actual approved analysis plan for your specific question — it reflects generic defaults for "pancreatic cancer + imaging + survival."

4. **Sample size, event counts, C-index, and every other number you'd normally see in Section 6/9/10 are not reported as numbers at all.** I don't know them, so the notebook says so explicitly rather than inventing a plausible-looking N or AUC.

With those caveats stated, here is the notebook skeleton: **`notebook.ipynb`**, structured per this skill's 13-section template (Environment Setup → Configuration → Data Loading → Preprocessing → Feature Extraction → Merging → EDA → Feature Selection → Model Training → Evaluation → Visualization → Limitations → Citations), with methodological checkpoints (CP-01 mask selection, CP-03 class imbalance, CP-04 leakage risk, CP-05 small sample, CP-06 normalization) stubbed in as required by the skill, all currently unresolved because there's no real data to resolve them against.

**What would turn this into a real, runnable analysis:**
- Confirm the exact pancreatic cancer subtype/staging you care about, the imaging modality (CT is assumed as a placeholder — most pancreatic radiomics work uses contrast-enhanced CT, but MRI is also used), and how you're defining the survival outcome (overall survival, progression-free survival, a binary cutoff, etc.)
- Let me run real CTDC and IDC searches for a matching cohort and imaging collection
- Tell me your Python/Jupyter comfort level so I calibrate comment density and walkthrough prose appropriately
- Review and sign off on an analysis plan (cohort definition, feature classes, model choice, validation strategy) before I fill in the placeholders with real choices

Want me to go ahead and run real CTDC/IDC searches for a pancreatic cancer cohort with imaging now, or would you rather walk through the intake questions first so the eventual plan is scoped to exactly what you need?
