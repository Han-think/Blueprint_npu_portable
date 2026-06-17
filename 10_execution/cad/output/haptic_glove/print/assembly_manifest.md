# haptic_glove — print & assembly guide

**Process:** FDM
**Safety:** Educational mock assembly for design review; verify all fits with the coupon before committing full prints.

## 0. Print the fit coupon first
`fit_test_coupon.stl` — pin Ø6 + holes at [0.25, 0.3, 0.4] mm. Use the loosest hole that still grips.

## 1. Parts
- `new-001_dorsal_control_module.stl` × 2 — dorsal control module · bbox [86.0, 70.0, 14.0] mm · clearance 0.0 mm
- `new-002_per_finger_exo_linkage_cartridge.stl` × 10 — per-finger exo linkage cartridge · bbox [12.8, 60.0, 5.8] mm · clearance 0.25 mm
- `new-003_flexion_resistance_actuator_module.stl` × 10 — flexion-resistance actuator module · bbox [11.0, 10.7, 8.7] mm · clearance 0.3 mm
- `new-004_adjustable_wrist_band.stl` × 2 — adjustable wrist band · bbox [72.0, 23.6, 23.6] mm · clearance 0.4 mm

## 2. Assembly order
1. new-002 → new-001 (slot, 0.25 mm) — 
2. new-004 → new-001 (snap, 0.4 mm) — wrist band quick-release buckle snaps onto dorsal control module
3. new-003 → new-001 (snap, 0.3 mm) — flexion-resistance actuator snaps into dorsal knuckle-row mount

## 3. Hardware
- M2 screw × 26
- D3 pin × 10