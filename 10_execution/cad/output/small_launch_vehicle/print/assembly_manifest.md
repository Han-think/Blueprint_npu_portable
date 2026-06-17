# small_launch_vehicle — print & assembly guide

**Process:** FDM
**Safety:** EDUCATIONAL DISPLAY MOCKUP — non-functional; do not treat as flight/operational hardware.

## 0. Print the fit coupon first
`fit_test_coupon.stl` — pin Ø6 + holes at [0.2, 0.25, 0.3] mm. Use the loosest hole that still grips.

## 1. Parts
- `new-001_seg1_split_cutaway_core_with_alignment_keys.stl` × 1 — split cutaway core with alignment keys (seg1) · bbox [82.0, 82.0, 210.0] mm · clearance 0.0 mm
- `new-001_seg2_split_cutaway_core_with_alignment_keys.stl` × 1 — split cutaway core with alignment keys (seg2) · bbox [82.0, 82.0, 210.0] mm · clearance 0.0 mm
- `new-002_slide_in_tank_and_flow_path_module_pair.stl` × 1 — slide-in tank and flow-path module pair · bbox [59.8, 59.8, 210.0] mm · clearance 0.3 mm
- `new-003_removable_engine_display_cartridge.stl` × 1 — removable engine display cartridge · bbox [36.8, 32.8, 42.7] mm · clearance 0.3 mm
- `new-004_indexed_interstage_and_avionics_service_.stl` × 1 — indexed interstage and avionics service ring · bbox [81.8, 82.0, 13.8] mm · clearance 0.2 mm
- `new-005_replaceable_fairing_and_fin_module_set.stl` × 1 — replaceable fairing and fin module set · bbox [75.8, 75.5, 67.8] mm · clearance 0.25 mm

## 2. Assembly order
1. new-002 → new-001 (slot, 0.3 mm) — tank/flow-path slide module
2. new-003 → new-001 (slot, 0.3 mm) — removable engine display cartridge (boss guide)
3. new-005 → new-001 (press, 0.25 mm) — fairing / fin replaceable
4. new-004 → new-001 (face, 0.2 mm) — indexed interstage/avionics ring keys onto cutaway core alignment features
5. new-001_seg1 → new-001_seg2 (alignment_key, 0.2 mm) — print-segmentation coupler: 4× 6.0mm corner alignment keys join new-001 segments along axis Z

## 3. Hardware
- M3 × 12
- alignment key 6mm × 4