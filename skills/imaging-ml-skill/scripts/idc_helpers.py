#!/usr/bin/env python3
"""Discover an IDC collection's real names, and validate a config before downloading.

The most common way this pipeline breaks on a NEW dataset is a config that names a sequence,
segmentation, clinical column, or class value that does not match what the collection actually
uses (e.g. `IDH1_status` when the column is really `idh1`, or `Mutant` when the value is `Mutated`).
These helpers prevent that:

  inspect_collection(id)  -> print the collection's real MR/SEG series descriptions and clinical
                             columns + values, so you fill the config from reality, not a guess.
  preflight_check(...)    -> validate a config against the LIVE collection before any download;
                             raises with the available options on any mismatch (fail fast, fail helpful).
  check_label_coverage(y) -> guard the modeling step: enough classes and enough per class for CV.

idc-index is imported lazily inside the IDC functions, so importing this module (and using
check_label_coverage) works fine in environments without idc-index installed (e.g. demo mode).

CLI:  python idc_helpers.py inspect <collection_id>
"""
from __future__ import annotations


def _client(client=None):
    if client is not None:
        return client
    from idc_index import IDCClient
    return IDCClient()


_LABEL_HINTS = ("idh", "mgmt", "surviv", "vital", "status", "grade", "stage",
                "gender", "sex", "response", "subtype", "death", "censor", "os_", "pfs")


def inspect_collection(collection_id, client=None, max_values=8):
    """Print the sequences, segmentations, and clinical columns/values a collection actually has.

    Run this before filling in SEQUENCE_MATCH, SEGMENTATION_MATCH, OUTCOME_COLUMN, and the
    class-value / survival-column settings for a dataset you have not used before.
    """
    c = _client(client)
    print(f"=== Collection: {collection_id}  (IDC {c.get_idc_version()}) ===\n")

    print("MR series descriptions  (choose SEQUENCE_MATCH from a substring of one of these):")
    mr = c.sql_query(f"""SELECT SeriesDescription, COUNT(*) n FROM index
        WHERE collection_id='{collection_id}' AND Modality='MR'
        GROUP BY SeriesDescription ORDER BY n DESC""")
    print(mr.head(25).to_string(index=False) if len(mr) else "  (no MR series)")

    print("\nSEG series descriptions  (choose SEGMENTATION_MATCH from a substring of one of these):")
    seg = c.sql_query(f"""SELECT SeriesDescription, COUNT(*) n FROM index
        WHERE collection_id='{collection_id}' AND Modality='SEG'
        GROUP BY SeriesDescription ORDER BY n DESC""")
    print(seg.to_string(index=False) if len(seg) else "  (no SEG series)")

    print("\nClinical tables and columns  (choose OUTCOME_COLUMN / survival columns from these):")
    try:
        c.fetch_index("clinical_index")
        tabs = c.sql_query(
            f"SELECT DISTINCT short_table_name FROM clinical_index WHERE collection_id='{collection_id}'")
        if not len(tabs):
            print("  (no clinical tables for this collection)")
        for t in tabs["short_table_name"]:
            df = c.get_clinical_table(t)
            print(f"\n  [{t}]  ({df.shape[0]} rows)")
            print(f"    columns: {list(df.columns)}")
            for col in df.columns:
                if any(k in col.lower() for k in _LABEL_HINTS):
                    vals = list(df[col].dropna().unique()[:max_values])
                    print(f"    {col}: {vals}")
    except Exception as e:  # network / access issues
        print(f"  (could not load clinical tables: {e})")


def preflight_check(collection_id, sequence_match, segmentation_match,
                    outcome_column=None, positive_class=None, negative_class=None,
                    modality="MR", client=None):
    """Validate a config against the live collection BEFORE downloading anything.

    Checks that the imaging series (of the given modality; matched by sequence_match if that modality
    has sequences), segmentation match, outcome column, and class values all resolve against the real
    data. For CT/PT set sequence_match="" (one series per patient, no sequence to match). Raises
    ValueError listing the available options on any mismatch; returns a small summary dict on success.
    """
    c = _client(client)
    problems, summary = [], {}

    seq_filter = f"AND LOWER(SeriesDescription) LIKE '%{sequence_match.lower()}%'" if sequence_match else ""
    img = c.sql_query(f"""SELECT COUNT(*) n FROM index
        WHERE collection_id='{collection_id}' AND Modality='{modality}' {seq_filter}""")
    summary["image_series"] = int(img["n"].iloc[0])
    if summary["image_series"] == 0:
        opts = c.sql_query(f"""SELECT DISTINCT SeriesDescription FROM index
            WHERE collection_id='{collection_id}' AND Modality='{modality}' LIMIT 40""")
        problems.append(f"No {modality} series matched"
                        + (f" SEQUENCE_MATCH '{sequence_match}'" if sequence_match else "")
                        + f". Available {modality} descriptions include: {list(opts['SeriesDescription'])[:20]}")

    seg = c.sql_query(f"""SELECT COUNT(*) n FROM index
        WHERE collection_id='{collection_id}' AND Modality='SEG'
          AND LOWER(SeriesDescription) LIKE '%{segmentation_match.lower()}%'""")
    summary["seg_series"] = int(seg["n"].iloc[0])
    if summary["seg_series"] == 0:
        opts = c.sql_query(f"""SELECT DISTINCT SeriesDescription FROM index
            WHERE collection_id='{collection_id}' AND Modality='SEG'""")
        problems.append(f"SEGMENTATION_MATCH '{segmentation_match}' matched no SEG series. "
                        f"Available SEG descriptions: {list(opts['SeriesDescription'])}")

    if outcome_column:
        c.fetch_index("clinical_index")
        tabs = c.sql_query(
            f"SELECT DISTINCT short_table_name FROM clinical_index WHERE collection_id='{collection_id}'")
        cols_by_table, values = {}, None
        for t in tabs["short_table_name"]:
            df = c.get_clinical_table(t)
            cols_by_table[t] = list(df.columns)
            if outcome_column in df.columns:
                values = list(df[outcome_column].dropna().unique())
                break
        if values is None:
            problems.append(f"OUTCOME_COLUMN '{outcome_column}' not found. Columns by table: {cols_by_table}")
        else:
            summary["outcome_values"] = values
            for cls, label in [(positive_class, "POSITIVE_CLASS"), (negative_class, "NEGATIVE_CLASS")]:
                if cls is not None and cls not in values:
                    problems.append(f"{label} '{cls}' is not a value of '{outcome_column}'. "
                                    f"Actual values: {values}")

    if problems:
        raise ValueError("Preflight check FAILED (fix the config in Section 1):\n  - "
                         + "\n  - ".join(problems))
    print("Preflight check passed:", summary)
    return summary


def check_label_coverage(y, n_splits, min_per_class=None):
    """Guard the modeling step. Raise a clear error if there aren't enough labels for CV.

    Catches the two silent failures: a mis-spelled class value that leaves only one class, and a
    class too small for the requested number of cross-validation folds.
    """
    import pandas as pd
    vc = pd.Series(list(y)).value_counts()
    min_per_class = min_per_class or n_splits
    if len(vc) < 2:
        raise ValueError(
            f"Only one class present after labeling (counts: {vc.to_dict()}). "
            f"This usually means POSITIVE_CLASS/NEGATIVE_CLASS do not match the data's actual values "
            f"-- run inspect_collection() to see them.")
    smallest = int(vc.min())
    if smallest < min_per_class:
        raise ValueError(
            f"Smallest class has only {smallest} patients, but {n_splits}-fold CV needs at least "
            f"{min_per_class} per class. Increase N_CASES, lower CV_FOLDS, or choose a more balanced "
            f"target. Class counts: {vc.to_dict()}")
    return dict(vc)


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3 and sys.argv[1] == "inspect":
        inspect_collection(sys.argv[2])
    else:
        print("Usage: python idc_helpers.py inspect <collection_id>")
