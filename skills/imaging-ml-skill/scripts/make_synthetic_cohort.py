#!/usr/bin/env python3
"""Generate a synthetic imaging cohort (3-D volumes + tumor masks + a learnable label).

Purpose: give the pipeline something to run on with NO download and NO internet, for
teaching, CI/smoke-testing the skill, and confirming an environment is set up correctly.
The synthetic survival label depends on tumor SIZE and TEXTURE ROUGHNESS plus noise, so a
correctly-wired radiomics pipeline recovers a clear-but-imperfect signal (AUC ~0.75-0.9).

Writes NIfTI images/masks and a cohort_manifest.csv with columns:
    patient_id, image_path, mask_path, Survival_from_surgery_days, true_tumor_radius, true_texture_roughness

CLI:
    python make_synthetic_cohort.py --n 60 --out ./demo_data
Library:
    from make_synthetic_cohort import make_synthetic_cohort
    df = make_synthetic_cohort(60, "./demo_data", seed=42)
"""
from __future__ import annotations
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import SimpleITK as sitk


def _ellipsoid_mask(shape, center, radii):
    zz, yy, xx = np.ogrid[:shape[0], :shape[1], :shape[2]]
    cz, cy, cx = center
    rz, ry, rx = radii
    return (((zz - cz) / rz) ** 2 + ((yy - cy) / ry) ** 2 + ((xx - cx) / rx) ** 2) <= 1.0


def make_synthetic_cohort(n_patients: int, out_dir: str, seed: int = 0,
                          shape=(32, 48, 48), spacing=(2.0, 1.0, 1.0)) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    out = Path(out_dir)
    img_dir = out / "images"; img_dir.mkdir(parents=True, exist_ok=True)
    msk_dir = out / "masks"; msk_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for i in range(n_patients):
        pid = f"SYN-{i:03d}"
        vol = rng.normal(30, 5, size=shape).astype(np.float32)
        brain = _ellipsoid_mask(shape, (shape[0] / 2, shape[1] / 2, shape[2] / 2),
                                (shape[0] / 2.2, shape[1] / 2.2, shape[2] / 2.2))
        vol[brain] += 40.0

        radius = rng.uniform(3.0, 8.0)
        roughness = rng.uniform(2.0, 14.0)
        brightness = rng.uniform(60.0, 110.0)
        center = (shape[0] / 2 + rng.uniform(-4, 4),
                  shape[1] / 2 + rng.uniform(-8, 8),
                  shape[2] / 2 + rng.uniform(-8, 8))
        radii = (radius * rng.uniform(0.7, 1.1), radius, radius * rng.uniform(0.9, 1.2))
        tum = _ellipsoid_mask(shape, center, radii)
        vol[tum] = brightness + rng.normal(0, roughness, size=tum.sum())

        size_term = (radius - 5.5) / 1.5
        rough_term = (roughness - 8.0) / 3.5
        latent = -1.1 * size_term - 0.7 * rough_term + rng.normal(0, 1.0)
        survival_days = float(np.clip(400 + latent * 180, 30, 1500))

        img = sitk.GetImageFromArray(vol); img.SetSpacing(spacing)
        msk = sitk.GetImageFromArray(tum.astype(np.uint8)); msk.SetSpacing(spacing)
        ip = str(img_dir / f"{pid}.nii.gz"); mp = str(msk_dir / f"{pid}.nii.gz")
        sitk.WriteImage(img, ip); sitk.WriteImage(msk, mp)
        rows.append({"patient_id": pid, "image_path": ip, "mask_path": mp,
                     "Survival_from_surgery_days": round(survival_days),
                     "true_tumor_radius": round(radius, 2),
                     "true_texture_roughness": round(roughness, 2)})
    df = pd.DataFrame(rows)
    df.to_csv(out / "cohort_manifest.csv", index=False)
    return df


def main():
    ap = argparse.ArgumentParser(description="Generate a synthetic imaging cohort for testing.")
    ap.add_argument("--n", type=int, default=60, help="number of synthetic patients")
    ap.add_argument("--out", default="./demo_data", help="output directory")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    df = make_synthetic_cohort(args.n, args.out, seed=args.seed)
    print(f"Wrote {len(df)} synthetic patients -> {args.out}")
    print(df.head())


if __name__ == "__main__":
    main()
