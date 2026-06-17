# cubesat — print & assembly guide

**Process:** FDM
**Safety:** EDUCATIONAL DISPLAY MOCKUP — non-functional; do not treat as flight/operational hardware.

## 0. Print the fit coupon first
`fit_test_coupon.stl` — pin Ø6 + holes at [0.25] mm. Use the loosest hole that still grips.

## 1. Parts
- `new-001_seg1_spine.stl` × 1 — Spine (seg1) · bbox [95.8, 95.8, 150.0] mm · clearance 0.25 mm
- `new-001_seg2_spine.stl` × 1 — Spine (seg2) · bbox [95.8, 95.8, 150.0] mm · clearance 0.25 mm
- `new-002_board.stl` × 1 — Board · bbox [70.0, 18.0, 120.0] mm · clearance 0.0 mm

## 2. Assembly order
1. new-001 → new-002 (slide, 0.25 mm) — slide: shelf
2. new-001_seg1 → new-001_seg2 (alignment_key, 0.2 mm) — print-segmentation coupler: 4× 6.0mm corner alignment keys join new-001 segments along axis Z

## 3. Hardware
- alignment key 6mm × 4