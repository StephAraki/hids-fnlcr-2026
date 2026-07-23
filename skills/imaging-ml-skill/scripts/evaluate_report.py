#!/usr/bin/env python3
"""Reusable, honest evaluation and reporting for a classification analysis.

Radiomics on small cohorts makes it easy to report a lucky number. These functions turn a
cross-validated model into an honestly-hedged result that any analysis (any dataset, any target)
can use unchanged:

  bootstrap_auc_ci(y, proba)          -> a 95% confidence interval on the AUC
  permutation_auc_pvalue(model,X,y)   -> a permutation p-value (is it above chance at all?)
  clinical_vs_imaging(y, Xi, Xc, cv)  -> does imaging beat a clinical-only baseline (e.g. age)?
  interpret_result(...)               -> a plain-language verdict scaled to the evidence
  full_classification_report(...)     -> runs all of the above and returns one dict

Design note: the permutation test and bootstrap CI wrap any cross-validated estimate, so they
generalize automatically. The metrics themselves are classification-specific (AUC); a regression or
survival analysis would need its own report module with the appropriate metrics. Keeping this file
per-task is deliberate.
"""
from __future__ import annotations
import numpy as np


def bootstrap_auc_ci(y_true, y_proba, n_boot=2000, seed=42, alpha=0.05):
    """95% CI on the AUC by resampling patients (with replacement) from the out-of-fold predictions."""
    from sklearn.metrics import roc_auc_score
    y_true = np.asarray(y_true); y_proba = np.asarray(y_proba)
    rng = np.random.default_rng(seed)
    n = len(y_true)
    aucs = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        if len(np.unique(y_true[idx])) < 2:      # need both classes to compute AUC
            continue
        aucs.append(roc_auc_score(y_true[idx], y_proba[idx]))
    aucs = np.array(aucs)
    return {"auc": float(roc_auc_score(y_true, y_proba)),
            "ci_low": float(np.percentile(aucs, 100 * alpha / 2)),
            "ci_high": float(np.percentile(aucs, 100 * (1 - alpha / 2))),
            "n_boot_used": int(len(aucs))}


def permutation_auc_pvalue(estimator, X, y, cv, n_permutations=100, seed=42, n_jobs=-1):
    """Permutation test: shuffle the labels many times and see where the real AUC falls in the null.

    A small p-value means the model does better than it would on randomly-labelled data, i.e. it is
    picking up real signal rather than fitting noise. This is the single most important check on a
    small cohort.

    Note: pass an estimator whose inner model is single-threaded (n_jobs=1); this function
    parallelizes across permutations, and a parallel inner model would oversubscribe the CPU and
    run much slower.
    """
    from sklearn.model_selection import permutation_test_score
    score, perm_scores, p_value = permutation_test_score(
        estimator, X, y, scoring="roc_auc", cv=cv,
        n_permutations=n_permutations, random_state=seed, n_jobs=n_jobs)
    return {"auc": float(score), "p_value": float(p_value),
            "null_mean": float(np.mean(perm_scores)), "n_permutations": int(n_permutations)}


def _default_pipe(n_features, seed, k=15, n_estimators=300, n_jobs=-1):
    """A standard classification pipeline, used identically for clinical / imaging / combined so the
    comparison is fair. Set n_jobs=1 when the caller parallelizes around it (e.g. the permutation test)."""
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.feature_selection import SelectKBest, f_classif
    from sklearn.ensemble import RandomForestClassifier
    steps = [("scale", StandardScaler())]
    if n_features > k:
        steps.append(("select", SelectKBest(f_classif, k=k)))
    steps.append(("clf", RandomForestClassifier(n_estimators=n_estimators, class_weight="balanced",
                                                 random_state=seed, n_jobs=n_jobs)))
    return Pipeline(steps)


def clinical_vs_imaging(y, imaging_X, clinical_X, cv, seed=42):
    """Compare clinical-only, imaging-only, and combined models by cross-validated AUC.

    Answers the make-or-break question for an imaging biomarker: does the imaging add predictive
    value OVER simple clinical variables (like age), or is it just a proxy for them? Returns the three
    AUCs and whether imaging (alone or combined) beats clinical-only by a meaningful margin.
    """
    import pandas as pd
    from sklearn.model_selection import cross_validate
    imaging_X = pd.DataFrame(imaging_X).reset_index(drop=True)
    clinical_X = pd.DataFrame(clinical_X).reset_index(drop=True)
    y = np.asarray(y)

    def _auc(Xm):
        return cross_validate(_default_pipe(Xm.shape[1], seed), Xm, y, cv=cv,
                              scoring="roc_auc")["test_score"].mean()

    combined = pd.concat([clinical_X.add_prefix("clin_"), imaging_X.add_prefix("img_")], axis=1)
    res = {"clinical_auc": float(_auc(clinical_X)),
           "imaging_auc": float(_auc(imaging_X)),
           "combined_auc": float(_auc(combined))}
    # "Adds value" if imaging-only or combined beats clinical-only by >0.02 AUC.
    res["imaging_adds_value"] = bool(max(res["imaging_auc"], res["combined_auc"])
                                     > res["clinical_auc"] + 0.02)
    return res


def interpret_result(n, auc, ci_low, ci_high, perm_p, imaging_adds_value=None):
    """A plain-language verdict that scales its confidence to the evidence (sample size, CI, p-value).

    Keeps a non-expert from over-reading a lucky number, on any dataset.
    """
    parts = []
    # Above chance at all?
    if perm_p is not None and perm_p >= 0.05:
        parts.append(f"The model is NOT distinguishable from chance (permutation p = {perm_p:.3f}). "
                     f"Treat this as a null / inconclusive result.")
    elif ci_low is not None and ci_low <= 0.5:
        parts.append(f"The AUC's confidence interval reaches down to chance (CI {ci_low:.2f}-{ci_high:.2f}), "
                     f"so above-chance performance is not established.")
    else:
        strength = "modest" if auc < 0.7 else ("moderate" if auc < 0.8 else "strong")
        parts.append(f"The model shows {strength} discrimination (AUC {auc:.2f}, 95% CI "
                     f"{ci_low:.2f}-{ci_high:.2f}, permutation p = {perm_p:.3f}).")
    # Sample-size caveat.
    if n < 50:
        parts.append(f"With only {n} patients the estimate is unstable and the interval is wide; "
                     f"treat this as a proof of concept, not evidence, and validate externally.")
    elif n < 150:
        parts.append(f"At {n} patients this is a small exploratory cohort; external validation is needed "
                     f"before any conclusion.")
    # Beats the clinical baseline?
    if imaging_adds_value is False:
        parts.append("The imaging does NOT clearly beat a clinical-only baseline, so it may not add "
                     "value beyond simple clinical variables here.")
    elif imaging_adds_value is True:
        parts.append("The imaging beats the clinical-only baseline, suggesting it carries independent "
                     "signal (still to be confirmed on larger, external data).")
    return " ".join(parts)


def full_classification_report(model, X, y, oof_proba, cv, clinical_X=None,
                               n_permutations=200, seed=42, verbose=True):
    """Run CI + permutation test + (optional) clinical baseline + interpretation. Returns one dict."""
    import pandas as pd
    n = int(len(y))
    n_feats = pd.DataFrame(X).shape[1]
    ci = bootstrap_auc_ci(y, oof_proba, seed=seed)
    # Permutation test uses a comparable but single-threaded, lighter model so it stays fast
    # (this function parallelizes across permutations).
    perm_model = _default_pipe(n_feats, seed, n_estimators=150, n_jobs=1)
    perm = permutation_auc_pvalue(perm_model, X, y, cv, n_permutations=n_permutations, seed=seed)
    baseline = None
    adds_value = None
    if clinical_X is not None and np.asarray(clinical_X).size:
        baseline = clinical_vs_imaging(y, X, clinical_X, cv, seed=seed)
        adds_value = baseline["imaging_adds_value"]
    verdict = interpret_result(n, ci["auc"], ci["ci_low"], ci["ci_high"], perm["p_value"], adds_value)
    report = {"n_patients": n, "auc": ci["auc"], "auc_ci": [ci["ci_low"], ci["ci_high"]],
              "permutation_p": perm["p_value"], "permutation_null_mean": perm["null_mean"],
              "clinical_baseline": baseline, "interpretation": verdict}
    if verbose:
        print(f"AUC {ci['auc']:.3f}  (95% CI {ci['ci_low']:.3f}-{ci['ci_high']:.3f})")
        print(f"Permutation test: p = {perm['p_value']:.3f}  (null mean AUC {perm['null_mean']:.3f})")
        if baseline:
            print(f"Baseline AUCs -> clinical-only {baseline['clinical_auc']:.3f} | "
                  f"imaging-only {baseline['imaging_auc']:.3f} | combined {baseline['combined_auc']:.3f}")
        print("\nInterpretation:\n  " + verdict)
    return report


if __name__ == "__main__":
    # Self-test on synthetic data with a real-but-weak signal.
    from sklearn.model_selection import StratifiedKFold, cross_val_predict
    rng = np.random.default_rng(0)
    n = 80
    y = rng.integers(0, 2, n)
    X = rng.normal(0, 1, (n, 30)) + y[:, None] * 0.5      # weak signal
    clin = (y * 5 + rng.normal(0, 3, n)).reshape(-1, 1)   # age-like clinical var, correlated with y
    cv = StratifiedKFold(5, shuffle=True, random_state=42)
    model = _default_pipe(30, 42)
    oof = cross_val_predict(model, X, y, cv=cv, method="predict_proba")[:, 1]
    r = full_classification_report(model, X, y, oof, cv, clinical_X=clin, n_permutations=100)
    print("\nreport keys:", list(r.keys()))
