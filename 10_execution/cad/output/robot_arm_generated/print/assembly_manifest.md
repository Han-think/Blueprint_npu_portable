# robot_arm — print & assembly guide

**Process:** FDM
**Safety:** Educational mock assembly for design review; verify all fits with the coupon before committing full prints.

## 0. Print the fit coupon first
`fit_test_coupon.stl` — pin Ø6 + holes at [0.25] mm. Use the loosest hole that still grips.

## 1. Parts
- `new-001_base.stl` × 1 — Base · bbox [80.0, 79.8, 39.8] mm · clearance 0.25 mm
- `new-002_link.stl` × 1 — Link · bbox [40.0, 40.0, 180.0] mm · clearance 0.0 mm

## 2. Assembly order
1. new-001 → new-002 (face, 0.25 mm) — mount: bolt

## 3. Hardware
- M3 × 4