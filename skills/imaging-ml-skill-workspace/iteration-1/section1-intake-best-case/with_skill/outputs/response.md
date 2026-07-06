Before I build your analysis plan, I have a few quick questions to make sure the notebook fits your research question exactly — though it looks like you've already answered most of them.

Here's what I've got from your message:

1. **Cancer type**: Glioblastoma (GBM)
2. **Imaging modality**: MRI — T1-contrast-enhanced and FLAIR sequences
3. **Outcome variable**: Overall survival
4. **Data source intent**: IDC side is set (TCGA-GBM collection); CTDC side is open — you want help finding a study with GBM survival data
5. **Expertise level**: Comfortable with Python/Jupyter — I'll keep comments focused on domain-specific choices and skip beginner walkthroughs

That's all five required intake fields, so I don't need to ask you anything further to proceed — except to flag one real gap on the CTDC side before I can finish routing.

## On finding a CTDC study with GBM survival data

I want to be upfront rather than guess here. CTDC's currently documented dataset is the **Cancer Moonshot Biobank (CMB)** — that's the only study in my CTDC reference material. Two things I can't verify for you without an actual query against the live CTDC GraphQL endpoint:

- **Whether GBM/brain cancer is represented in CMB at all.** The disease-type filter field (`ctep_disease_term`) is documented as having 8 distinct populated values in the current CMB release, but I do not have the list of which 8 disease terms those are. I am not going to guess whether "Glioblastoma" or a brain-cancer term is one of them.
- **Whether CMB has usable survival data even if GBM is present.** The CTDC data model documents a `vital_status` field (alive/deceased) and `cause_of_death`, but I see no documented time-to-event field (e.g., days-to-death or days-to-last-follow-up) in the CTDC reference material. `vital_status` alone is not sufficient for standard overall-survival modeling (Kaplan-Meier, Cox regression) — you need a time component. `stage_of_disease` and `tumor_grade` are also documented as null for every participant in the current CMB public release, in case staging was part of your inclusion criteria.
- **There may be CTDC studies beyond CMB that I'm not aware of.** The CTDC skill's own documentation notes that additional studies are released over time and directs me to check the live Studies page rather than assume CMB is the only one.

I'm not going to state a sample size or confirm GBM availability without running a real query — that would be a fabricated number. Here's the query, following CTDC's actual (non-standard) GraphQL schema, that will tell us definitively whether GBM has CMB participants and roughly how many:

```graphql
query SearchAggregates {
  searchParticipants {
    numberOfParticipants
    participantCountByCtepDiseaseTerm { group subjects }
  }
}
```

```bash
curl -s -X POST "$CTDC_GRAPHQL_URL" \
  -H 'Content-Type: application/json' \
  -d '{"query":"query SearchAggregates { searchParticipants { numberOfParticipants participantCountByCtepDiseaseTerm { group subjects } } }","variables":{}}'
```

(`$CTDC_GRAPHQL_URL` changes between releases — pull the current value from the CTDC portal's network requests before running this; don't hardcode an old endpoint.)

That `participantCountByCtepDiseaseTerm` facet will show every disease bucket and its participant count in one shot, so we can see immediately whether a glioblastoma/brain-cancer term appears and roughly how many participants are in it. If you can run that (or paste me the output), I can tell you definitively whether CMB is viable for your GBM cohort. If GBM isn't represented in CMB, the honest next step is checking the live CTDC Studies page (https://clinical.datacommons.cancer.gov/) for newer studies, since I only have documentation for CMB.

A second option, if CTDC doesn't pan out for GBM survival data: **TCGA-GBM itself has companion clinical data** (including survival) historically distributed via GDC rather than CTDC. That would be a different commons (Genomic Data Commons) than the clinical-data routing this skill handles — flagging it now so you know it's an alternative path, not something I can build for you under this skill, but worth knowing about if CTDC comes up empty for GBM.

## One access note regardless of which CTDC study we land on

CTDC participant-level data has three access tiers (open / registered / controlled-via-dbGaP). If whatever study we land on requires controlled access and you don't already have dbGaP authorization for it, I'll need to know that before I generate any data-loading cells — the notebook would need to be built as a skeleton with placeholder cells marked as blocked on credentialed access, rather than a cell that assumes the data is already reachable. Let me know your authorization status once we've identified the right study.

## What I need from you to move forward

1. Can you run the `searchParticipants` query above (or let me know if you'd rather I just proceed assuming we may need to fall back to a non-CTDC source for survival variables)?
2. If CMB does have a usable GBM bucket — do you already have CTDC access (open-tier is enough for aggregate counts; registered/controlled may be needed for full participant-level export), or do we need to plan around access being pending?

One more thing worth flagging now, separate from the CTDC question: this skill's own internal reference guides for PyRadiomics feature-class selection (`references/pyradiomics_guide.md`) and model selection (`references/model_selection.md`) are currently empty placeholder files in my setup — they haven't been populated yet. I'm required to consult those before recommending specific PyRadiomics feature classes or a specific ML model type in your analysis plan, and I won't fabricate that content. So once we've nailed down the CTDC side, I'll let you know explicitly if I hit that wall when we get to Section 3 (Analysis Planning) — we may need to either wait for those guides to be filled in, or have you confirm you want me to proceed with general PyRadiomics/modeling knowledge while flagging it as unverified against this skill's intended reference material.

To summarize where we stand: intake is complete, but I can't responsibly route you to a specific CTDC study or write the analysis plan's cohort-definition section until we know whether GBM is represented in CMB with usable survival data. Let me know how you'd like to proceed on the query above, and we'll move to the full analysis plan once that's resolved.
