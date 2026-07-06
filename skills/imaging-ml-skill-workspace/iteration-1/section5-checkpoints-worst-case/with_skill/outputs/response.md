Happy to add the methodological checkpoints section. A couple of things up front, though, since two of the checkpoints depend on decisions you haven't made yet:

- **Mask type**: not yet decided
- **Class balance**: not yet computed

Rather than guess at either of these, I'm going to add the checkpoint cells with those fields left as explicit open items, and I'll point out exactly where you (or whoever generated the notebook with you) need to come back and fill them in once you've made the call / run the numbers. Inventing a placeholder mask type (e.g. "whole tumor") or a placeholder class split would misrepresent your analysis, so I'm not going to do that.

Here is the Methodological Checkpoints content for your notebook. This includes the checkpoint cells (to place inline at the relevant stage of the pipeline) and the checkpoint summary cell (to place near the end of the notebook, before Citations).

---

### CP-01: Tumor Mask Selection

```python
# METHODOLOGICAL CHECKPOINT CP-01: Tumor mask selection
# The segmentation mask determines which voxels are included in feature extraction.
# Choices include: whole tumor, tumor core, enhancing region, peri-tumoral margin.
# This choice significantly affects results and should be validated by a radiologist
# or imaging expert familiar with your cancer type and imaging protocol.
# Current selection: [STATE CURRENT SELECTION]  -- NOT YET DECIDED. You told me you
# haven't chosen a mask type. Pick one (e.g. whole tumor, tumor core, enhancing
# region, peri-tumoral margin) before feature extraction can run, and update this
# line and the corresponding mask-loading code accordingly.
```

### CP-03: Class Imbalance

```python
# METHODOLOGICAL CHECKPOINT CP-03: Class imbalance detected
# Class distribution: [STATE DISTRIBUTION]  -- NOT YET COMPUTED. You told me you
# haven't run the class balance numbers. Once your cohort is finalized, compute the
# actual counts per class (e.g. via value_counts() on your outcome column) and
# replace this placeholder with the real distribution before drawing any conclusions
# about imbalance.
# Imbalanced classes can cause models to overfit to the majority class.
# Consider: oversampling (SMOTE), undersampling, class_weight='balanced', or
# changing evaluation metric from accuracy to AUC-ROC or F1.
# Current approach: [STATE CURRENT APPROACH]  -- Cannot be determined until the
# actual class distribution above is known. Decide an imbalance-handling strategy
# once you have real numbers.
```

I'm leaving CP-02 (MRI sequence selection), CP-04 (data leakage risk), CP-05 (small-sample overfitting risk), and CP-06 (normalization strategy) out of this message because I don't have your notebook content in front of me in this conversation, so I can't confirm which of those actually apply (e.g., whether your modality is MRI with multiple sequences, what your sample size is, what normalization step you're using). If you paste in or point me to the relevant notebook cells, I'll check each one against the catalog and add only the ones that are triggered, with their actual settings — not placeholders.

### Checkpoint Summary Cell

```markdown
## Methodological Checkpoint Summary

The following decisions were made during notebook generation and require expert review
before results are interpreted or reported:

| # | Checkpoint | Location | Current Setting | Reviewed? |
|---|-----------|----------|-----------------|-----------|
| CP-01 | Tumor mask selection | Cell [N — fill in once placed] | NOT YET DECIDED | [ ] |
| CP-03 | Class imbalance | Cell [N — fill in once placed] | NOT YET COMPUTED | [ ] |

**This notebook is not publication-ready without expert review of the items above.**
```

I left the "Location" column as `Cell [N]` because I don't know which cell numbers these will land on in your actual notebook — fill those in once you place the cells. I also did not add rows for CP-02, CP-04, CP-05, or CP-06 above, since I haven't confirmed those apply yet (see above).

Two things I'd ask of you before this section is complete:

1. **Mask type** — once you decide (whole tumor, tumor core, enhancing region, peri-tumoral margin, or something else), let me know and I'll update CP-01's "Current selection" line, and we can also revisit whether that choice has downstream implications for Section 3.2 (feature extraction approach).
2. **Class balance** — once you've run the actual counts per class, send them over and I'll fill in CP-03's "Class distribution" line with the real numbers and help you think through whether an imbalance-handling strategy (SMOTE, class_weight='balanced', metric choice, etc.) is warranted.

Let me know when you have either of those, or if you'd like me to look at the rest of the notebook now to check whether CP-02, CP-04, CP-05, or CP-06 apply.
