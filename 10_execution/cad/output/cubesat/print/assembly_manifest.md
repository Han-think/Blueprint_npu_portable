# cubesat — print & assembly guide

**Process:** FDM
**Safety:** EDUCATIONAL DISPLAY MOCKUP — non-functional; do not treat as flight/operational hardware.

## 0. Print the fit coupon first
`fit_test_coupon.stl` — pin Ø6 + holes at [0.2, 0.25, 0.35] mm. Use the loosest hole that still grips.

## 1. Parts
- `new-001_seg1_integrated_rail_frame_spine.stl` × 1 — integrated rail-frame spine (seg1) · bbox [96.0, 96.0, 165.0] mm · clearance 0.0 mm
- `new-001_seg2_integrated_rail_frame_spine.stl` × 1 — integrated rail-frame spine (seg2) · bbox [96.0, 96.0, 165.0] mm · clearance 0.0 mm
- `new-002_removable_service_panels.stl` × 2 — removable service panels · bbox [91.8, 1.6, 150.0] mm · clearance 0.25 mm
- `new-003_seg1_board_shelf_and_standoff_ladder.stl` × 1 — board shelf and standoff ladder (seg1) · bbox [73.7, 17.6, 130.0] mm · clearance 0.35 mm
- `new-003_seg2_board_shelf_and_standoff_ladder.stl` × 1 — board shelf and standoff ladder (seg2) · bbox [73.7, 17.6, 130.0] mm · clearance 0.35 mm
- `new-004_replaceable_antenna_hinge_dummy_pair.stl` × 2 — replaceable antenna hinge dummy pair · bbox [7.8, 7.8, 18.0] mm · clearance 0.2 mm

## 2. Assembly order
1. new-002 → new-001 (slot, 0.25 mm) — service panel slide — cad_brief panel_slide_clearance
2. new-003 → new-001 (slot, 0.35 mm) — board shelf ladder slides inside spine bay — board_dummy_clearance
3. new-004 → new-001 (pin, 0.2 mm) — antenna hinge rotation
4. new-001_seg1 → new-001_seg2 (alignment_key, 0.2 mm) — print-segmentation coupler: 4× 6.0mm corner alignment keys join new-001 segments along axis Z
5. new-003_seg1 → new-003_seg2 (alignment_key, 0.2 mm) — print-segmentation coupler: 4× 6.0mm corner alignment keys join new-003 segments along axis Z

## 3. Hardware
- M2 × 8
- PIN2 × 2
- alignment key 6mm × 8