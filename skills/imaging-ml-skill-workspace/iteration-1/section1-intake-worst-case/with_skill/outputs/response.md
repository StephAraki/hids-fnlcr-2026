Before I build your analysis plan, I have a few quick questions to make sure the notebook fits your research question exactly.

You've told me the cancer type — lung cancer — and that you want to relate imaging data to outcomes. I still need a bit more detail before I can route this to the right data sources and put together an analysis plan. Could you answer the following:

1. **Imaging modality** — What imaging type are you working with: CT, MRI, PET, or pathology slides? (Lung cancer imaging cohorts in the Imaging Data Commons are predominantly CT, sometimes PET/CT, so this will narrow things down a lot.)
2. **Outcome variable** — What specifically do you want to predict or stratify by? For example: overall survival, progression-free survival, treatment response, recurrence, or a molecular subtype. "Outcomes" can mean several different things methodologically (survival modeling vs. classification vs. regression), so I need the specific variable.
3. **Data source intent** — Do you already have a specific CTDC study or IDC collection in mind, or do you need help finding/selecting one?
4. **Clinical data needs** — Do you need clinical/outcome variables linked to the imaging (which would mean pulling from CTDC and matching to IDC imaging), or do you already have outcome labels in hand and just need the imaging side (IDC only)?
5. **Your Python/Jupyter comfort level** — none, some, or comfortable? This determines how much explanatory detail and walkthrough text I put in the generated notebook.

A few things up front, so expectations are set correctly before we go further:

- **I have not yet queried CTDC or IDC for lung cancer data**, so I can't tell you right now what specific studies, collections, sample sizes, or patient counts are actually available — I won't guess at those. Once I know your modality and outcome variable, the right next step is to actually query CTDC (clinical/outcome data) and/or IDC (imaging collections) live, rather than me naming studies from memory.
- **If your outcome variable requires participant-level clinical data from CTDC** (e.g., survival times, treatment response, demographics), note that CTDC participant-level data requires dbGaP authorization. If you don't already have that authorization, I can still build the notebook as a skeleton with placeholder data-loading cells that will work once access is granted — just let me know your authorization status when you answer above.
- Once I have your answers, I'll determine whether this routes to IDC only, CTDC only, or a combined CTDC+IDC cross-commons workflow, and I'll walk you through that pathway before writing any analysis plan or code.

No notebook or code yet — that comes after we've nailed down the above and I've put together a written analysis plan for you to review.
