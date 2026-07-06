Before I build your analysis plan, I have a few quick questions to make sure the notebook fits your research question exactly.

You've already told me:

- **Cancer type:** Breast cancer
- **Outcome variable:** Recurrence (prediction)

To generate a scientifically appropriate plan, I still need:

1. **Imaging modality** — What imaging type are you working with (or hoping to use)? CT, MRI (and if so, which sequences — e.g., T1, T2, DCE), mammography, ultrasound, or digital pathology slides? This determines which IDC collections are even candidates and which PyRadiomics feature classes make sense.
2. **Data source intent** — You mentioned you don't have a cohort picked out yet. Do you want me to help you search CTDC and/or IDC for candidate cohorts as the next step, or are you only looking for the shape of the plan right now, with cohort selection deferred to a separate session?
3. **Expertise level** — How comfortable are you with Python and Jupyter notebooks (none / some / comfortable)? This determines how much explanatory scaffolding goes into the eventual notebook.

I don't need all of these to sketch the plan's structure, but I do need at least the imaging modality before I can speak meaningfully to Section 3.2 (feature extraction approach) — feature class selection depends on modality and cancer type, and I won't guess at that.

---

## On "expected sample size"

I want to flag something important up front: **I can't give you an expected sample size yet, and I'm not going to estimate or guess one.** Here's why, and what it would actually take to get a real number.

Sample size in this kind of cross-commons analysis is downstream of three things, none of which are pinned down yet:

- **Which CTDC study (or studies)** would supply breast cancer participants with recurrence outcome data, and how many participants in that study actually have recurrence as a captured, usable field — that requires running a live query against the CTDC GraphQL API, not estimating from memory. I have not run that query in this conversation, so I have no real number to give you.
- **Which IDC collection(s)** would supply the matching imaging data, and how many of those participants have an imaging series of the modality/timepoint you need — that requires a live query against the IDC index (`client.sql_query()`), which I also have not run.
- **The overlap** between the two — i.e., how many participants have *both* usable CTDC clinical/outcome data *and* a matching IDC imaging series — which is typically smaller than either source alone and can only be determined by actually matching participant identifiers after both queries are run.

Any number I gave you right now would be fabricated. The skill I'm following for this workflow explicitly prohibits that: I'm required to say "unverified" rather than invent a count, study name, or collection name. So instead of a number, here's what "Expected sample size" will look like in the Cohort Definition section of your plan once we get there:

> **Expected sample size:** To be determined by live query. Step 1: query CTDC for participants matching breast cancer + recurrence-relevant fields (this needs CTDC's actual GraphQL schema, not improvised syntax — I'll follow the CTDC skill's documented query patterns for this, including its real root resolvers, when we get to that step). Step 2: query IDC for matching imaging series by modality and, where possible, by matching participant/patient identifiers (following the IDC skill's `idc-index` patterns). Step 3: report the actual intersection count, not an estimate.

If you want, the very next thing I can do — once you confirm modality and whether you want cohort discovery now — is actually run those CTDC and IDC queries with you and report the real numbers back. I won't be able to populate "Expected sample size" with anything but a placeholder until that happens.

---

## Skeleton of what the plan will contain (structure only, not filled in)

So you can see where this is going, here is the shape of the analysis plan once the above is answered — none of the bracketed items below are real values, they're placeholders showing what each section will eventually hold:

**3.1 Cohort Definition**
- CTDC study and IDC collection: *pending live query — not yet identified*
- Inclusion/exclusion criteria: *pending — depends on recurrence definition (e.g., time-to-recurrence window, censoring rules) and imaging availability*
- Expected sample size: *pending live query — see above, will not be estimated in advance*
- Imaging/clinical matching strategy: *pending — depends on whether CTDC and IDC share a usable identifier for your target study/collection*

**3.2 Imaging and Feature Extraction Approach**
- Modality and sequence: *pending your answer*
- Tumor ROI/segmentation source: *pending — methodological checkpoint, needs radiologist input regardless of modality*
- PyRadiomics feature classes: *not yet selectable — this skill requires consulting its PyRadiomics reference guide before listing feature classes, and I'll do that once modality is known*
- Preprocessing steps: *depends on modality (resampling, normalization choices differ for MRI vs. CT vs. pathology)*

**3.3 Modeling Strategy**
- Model type: *not yet selectable — this skill requires consulting its model-selection reference guide first, and model choice also depends on the actual sample size and class balance once the cohort is queried*
- Feature selection / class imbalance handling: *depends on the real recurrence/no-recurrence ratio in the matched cohort, which isn't known yet*

**3.4 Evaluation Plan**
- Validation strategy: *likely candidates are k-fold CV or LOOCV given that radiomic cohorts are often small, but the right choice depends on the actual N — to be finalized once sample size is known*
- Primary metric: *AUC-ROC is the typical default for binary recurrence prediction, but this is a methodological choice I'll surface explicitly rather than picking silently once we're at this step*

**3.5 Known Limitations**
- Will include sample size limitations, imaging protocol variability, and lack of external validation, populated with real specifics once the cohort is defined.

---

A couple of other things worth flagging now, before we go further:

- **CTDC access tier:** If the eventual cohort requires participant-level clinical data (e.g., recurrence status, treatment history) from CTDC, that data is governed at three access tiers (open / registered / controlled). Recurrence and outcome data in particular is often part of controlled-tier data requiring dbGaP authorization. If you don't already have dbGaP access for the relevant study, let me know — we can still build the notebook as a skeleton with placeholder data-loading cells, but the actual data pull won't run until access is granted.
- **IDC access:** No authentication is needed for the imaging side — IDC data is public.

Once you answer the three questions above (modality, whether you want cohort discovery now, expertise level), I'll either (a) move straight into a live CTDC/IDC cohort search with you so the plan's sample size section has real numbers, or (b) finalize the rest of the plan structure with explicit placeholders, depending on which you prefer.
