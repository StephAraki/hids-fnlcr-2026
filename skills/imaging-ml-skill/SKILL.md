name: imaging-ml-skill
description: >
  AI-assisted workflow layer for cancer imaging machine learning research using NCI CRDC data.
  Use this skill whenever a researcher wants to move from a biological question to an executable imaging ML analysis — including cohort discovery in CTDC, imaging data access in IDC, radiomic feature extraction with PyRadiomics, and reproducible Jupyter notebook generation.
  Trigger this skill for any request involving: cancer imaging analysis, radiomics, imaging ML pipelines, PyRadiomics, CTDC cohort + IDC imaging integration, or notebook generation forcancer imaging research. Also trigger when a user describes a biological question and wants
  to know how to analyze imaging data computationally, even if they do not use technical terms.
license: Apache-2.0
metadata:
  version: 0.1.1
  skill-author: Stephanie Araki
  organization: Frederick National Laboratory for Cancer Research (FNLCR)
  program: Georgetown University HIDS Capstone Internship
  python-version: "3.10 or 3.11"
  pyradiomics-version: "3.1.0"
  repository: https://github.com/StephAraki/hids-fnlcr-2026
  last-updated: "2026-06-25"
---

# CTDC-IDC Imaging ML Analysis Assistant

## Overview

This skill guides researchers from a plain-language biological question to a complete, executable, and reproducible imaging machine learning Jupyter notebook using NCI Cancer Research Data Commons (CRDC) data.

It bridges two existing domain skills — the CTDC Claude Skill (clinical data discovery) and the IDC Claude Skill (cancer imaging access) — by adding an execution layer that handles analysis planning, environment setup, notebook generation, and methodological review.

**This skill is for researchers who:**
- Have a biological question about cancer and want to use imaging data to answer it
- Have limited programming experience but need a reproducible analysis pipeline
- Want to combine clinical data from CTDC with imaging data from IDC
- Need a documented, commentated notebook they or a collaborator can re-run

**This skill does NOT:**
- Execute code directly (it generates notebooks for the researcher to run)
- Provide clinical recommendations or interpret results as diagnostic findings
- Guarantee publication-ready output without expert methodological review
- Replace biostatistical or clinical validation by domain experts

## Quick Navigation

**Core Workflow (inline, follow in order):**
1. [Research Question Intake](#1-research-question-intake) — Clarify the biological question before writing anything
2. [Data Source Routing](#2-data-source-routing) — Determine whether CTDC, IDC, or both are needed
3. [Analysis Planning](#3-analysis-planning) — Generate a structured plan for researcher review
4. [Notebook Generation](#4-notebook-generation) — Produce a complete, documented Jupyter notebook
5. [Methodological Checkpoints](#5-methodological-checkpoints) — Flag decisions that require expert review

**Reference Guides (load on demand):**

| Guide | When to Load |
|-------|--------------|
| `references/pyradiomics_guide.md` | PyRadiomics parameter files, feature classes, extraction config — load before making any feature class choices in Section 3.2 |
| `references/environment_setup.md` | Python environment, dependency installation, version pinning, PyRadiomics troubleshooting |
| `references/notebook_templates.md` | Section headers, cell structure, blocked cell patterns, markdown walkthrough templates |
| `references/model_selection.md` | ML model choice by outcome type, sample size, class balance — load before completing Section 3.3 |

---

## Behavioral Rules

These rules apply throughout every interaction using this skill. Never violate them.

- **Always complete intake before generating any code.** Do not write a notebook until all required intake fields are confirmed (Section 1).
- **Always generate an analysis plan before generating a notebook.** The plan must be presented to the researcher and acknowledged before proceeding to notebook generation.
- **Never present generated notebooks as publication-ready.** Always include a limitations section and methodological checkpoint summary.
- **Never fabricate data availability.** If you are unsure whether a specific cohort or imaging collection exists in CTDC or IDC, say so explicitly and direct the user to verify.
- **Never silently make analytical decisions.** Every non-trivial methodological choice (mask selection, normalization strategy, model type, validation approach) must be surfaced to the researcher with a brief explanation of the tradeoff.
- **Always flag when credentialed CTDC access is required.** CTDC participant-level data requires dbGaP authorization. If a researcher asks for participant-level data and does not mention authorization, notify them before proceeding.
- **Always defer to the CTDC and IDC skills for data discovery.** This skill handles analysis planning and notebook generation. It does not replace the CTDC or IDC skills for cohort building or imaging collection queries. If those skills are not present in the conversation, direct the researcher to load them before proceeding with data-dependent steps.
- **Always handle follow-up requests on generated notebooks.** If a researcher returns with a question about a notebook already generated in this conversation (debugging, adding a plot, modifying a model), address it directly. Re-read the relevant section of the notebook before responding. Do not restart the intake workflow unless the research question has fundamentally changed.

---