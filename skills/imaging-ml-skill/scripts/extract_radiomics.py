#!/usr/bin/env python3
"""Batch radiomic feature extraction over a cohort manifest.

This is the reusable, productionised version of the extraction step demonstrated in
notebooks/upenn_gbm_radiomics_poc.ipynb. Use it to scale from a proof-of-concept
subset to a full cohort without re-deriving the logic each time.

INPUT  : a cohort CSV with at least the columns  patient_id, image_path, mask_path
         (image_path / mask_path point to NIfTI or other SimpleITK-readable volumes).
OUTPUT : a features CSV, one row per patient, indexed by patient_id, plus a sidecar
         <output>.failures.csv listing any patients that could not be processed.

CLI:
    python extract_radiomics.py cohort.csv features.csv --params radiomics_params.yaml
As a library:
    from extract_radiomics import extract_cohort
    features_df, failures = extract_cohort(cohort_df, params_path="radiomics_params.yaml")
"""
from __future__ import annotations
import argparse
import logging
import os
from pathlib import Path

import pandas as pd


def get_extractor(params_path: str | None = None, overrides: dict | None = None):
    """Build a PyRadiomics extractor from a params file, or from lean built-in defaults.

    `overrides` updates the extractor settings after loading, e.g. {"normalize": False} for CT
    (absolute Hounsfield units), where MR-style intensity normalization would throw away real signal.
    """
    from radiomics import featureextractor
    logging.getLogger("radiomics").setLevel(logging.ERROR)
    if params_path and Path(params_path).exists():
        ex = featureextractor.RadiomicsFeatureExtractor(str(params_path))
    else:
        # Fallback defaults, matching radiomics_params.yaml, if no file is supplied.
        ex = featureextractor.RadiomicsFeatureExtractor(
            binWidth=25, normalize=True, normalizeScale=100,
            interpolator="sitkBSpline", geometryTolerance=1e-3, label=1)
        ex.disableAllFeatures()
        for fam in ["shape", "firstorder", "glcm", "glrlm", "glszm", "gldm", "ngtdm"]:
            ex.enableFeatureClassByName(fam)
    if overrides:
        ex.settings.update(overrides)   # e.g. normalize=False for CT
    return ex


def extract_cohort(cohort: pd.DataFrame, params_path: str | None = None,
                   image_col: str = "image_path", mask_col: str = "mask_path",
                   id_col: str = "patient_id", verbose: bool = True,
                   overrides: dict | None = None):
    """Extract features for every row of `cohort`. Returns (features_df, failures_df).

    `overrides` is passed to the extractor, e.g. {"normalize": False} for CT.
    """
    required = {id_col, image_col, mask_col}
    missing = required - set(cohort.columns)
    if missing:
        raise ValueError(f"Cohort is missing required columns: {missing}")

    extractor = get_extractor(params_path, overrides=overrides)
    rows, failures = [], []
    n = len(cohort)
    for i, r in cohort.reset_index(drop=True).iterrows():
        pid = r[id_col]
        try:
            result = extractor.execute(str(r[image_col]), str(r[mask_col]))
            feats = {k: float(v) for k, v in result.items() if k.startswith("original_")}
            feats[id_col] = pid
            rows.append(feats)
        except Exception as e:  # keep going; one bad mask should not sink the batch
            failures.append({id_col: pid, "error": str(e)})
        if verbose and ((i + 1) % 10 == 0 or (i + 1) == n):
            print(f"  extracted {i + 1}/{n}")
    features_df = pd.DataFrame(rows).set_index(id_col) if rows else pd.DataFrame()
    return features_df, pd.DataFrame(failures)


def main():
    ap = argparse.ArgumentParser(description="Batch radiomic feature extraction over a cohort.")
    ap.add_argument("cohort_csv", help="CSV with columns patient_id, image_path, mask_path")
    ap.add_argument("output_csv", help="Where to write the features table")
    ap.add_argument("--params", default=str(Path(__file__).with_name("radiomics_params.yaml")),
                    help="PyRadiomics params YAML (default: bundled radiomics_params.yaml)")
    args = ap.parse_args()

    cohort = pd.read_csv(args.cohort_csv)
    features_df, failures = extract_cohort(cohort, params_path=args.params)
    features_df.to_csv(args.output_csv)
    print(f"Wrote {features_df.shape[0]} patients x {features_df.shape[1]} features -> {args.output_csv}")
    if len(failures):
        fp = os.path.splitext(args.output_csv)[0] + ".failures.csv"
        failures.to_csv(fp, index=False)
        print(f"WARNING: {len(failures)} failures -> {fp}")


if __name__ == "__main__":
    main()
