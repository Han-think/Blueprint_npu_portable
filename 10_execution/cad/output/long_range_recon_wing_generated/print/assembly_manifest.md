# long_range_recon_wing — print & assembly guide

**Process:** FDM
**Safety:** Educational mock assembly for design review; verify all fits with the coupon before committing full prints.

## 0. Print the fit coupon first
`fit_test_coupon.stl` — pin Ø6 + holes at [0.25] mm. Use the loosest hole that still grips.

## 1. Parts
- `new-001_seg1_spine.stl` × 1 — Spine (seg1) · bbox [200.0, 40.0, 30.0] mm · clearance 0.0 mm
- `new-001_seg2_spine.stl` × 1 — Spine (seg2) · bbox [200.0, 40.0, 30.0] mm · clearance 0.0 mm
- `new-002_motor_pod.stl` × 1 — Motor Pod · bbox [39.8, 39.8, 60.0] mm · clearance 0.25 mm

## 2. Assembly order
1. new-002 → new-001 (face, 0.25 mm) — mount: bolt
2. new-001_seg1 → new-001_seg2 (alignment_key, 0.2 mm) — print-segmentation coupler: 4× 6.0mm corner alignment keys join new-001 segments along axis X

## 3. Hardware
- M3 × 4
- alignment key 6mm × 4