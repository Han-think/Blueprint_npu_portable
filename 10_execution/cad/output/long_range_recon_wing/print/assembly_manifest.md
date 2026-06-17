# long_range_recon_wing — print & assembly guide

**Process:** FDM
**Safety:** Educational mock assembly for design review; verify all fits with the coupon before committing full prints.

## 0. Print the fit coupon first
`fit_test_coupon.stl` — pin Ø6 + holes at [0.2, 0.25, 0.3] mm. Use the loosest hole that still grips.

## 1. Parts
- `new-001_seg1_integrated_center_spine_and_spar_socket_.stl` × 1 — integrated center spine and spar socket core (seg1) · bbox [128.0, 57.9, 34.6] mm · clearance 0.0 mm
- `new-001_seg2_integrated_center_spine_and_spar_socket_.stl` × 1 — integrated center spine and spar socket core (seg2) · bbox [128.0, 57.9, 34.6] mm · clearance 0.0 mm
- `new-002_removable_sensor_nose_and_pitot_boom_mod.stl` × 1 — removable sensor nose and pitot boom module · bbox [77.8, 37.8, 34.0] mm · clearance 0.25 mm
- `new-003_slide_in_mission_payload_and_battery_cg_.stl` × 1 — slide-in mission payload and battery CG rail module · bbox [72.0, 31.7, 17.7] mm · clearance 0.3 mm
- `new-004_serviceable_propulsion_display_and_rear_.stl` × 1 — serviceable propulsion-display and rear cable module · bbox [48.0, 25.8, 21.8] mm · clearance 0.2 mm
- `new-005_seg1_replaceable_wing__elevon__and_skid_servi.stl` × 1 — replaceable wing, elevon, and skid service modules (seg1) · bbox [129.9, 33.8, 20.0] mm · clearance 0.2 mm
- `new-005_seg2_replaceable_wing__elevon__and_skid_servi.stl` × 1 — replaceable wing, elevon, and skid service modules (seg2) · bbox [129.9, 33.8, 20.0] mm · clearance 0.2 mm

## 2. Assembly order
1. new-005 → new-001 (press, 0.2 mm) — wing-root spar key ↔ center spine
2. new-002 → new-001 (slot, 0.25 mm) — sensor nose module
3. new-003 → new-001 (slot, 0.3 mm) — mission payload / battery CG rail slide
4. new-005 → new-001 (pin, 0.2 mm) — elevon hinge rotation
5. new-004 → new-001 (face, 0.2 mm) — propulsion-display and rear cable module mounts to center spine rear pylon
6. new-001_seg1 → new-001_seg2 (alignment_key, 0.2 mm) — print-segmentation coupler: 4× 6.0mm corner alignment keys join new-001 segments along axis X
7. new-005_seg1 → new-005_seg2 (alignment_key, 0.2 mm) — print-segmentation coupler: 4× 6.0mm corner alignment keys join new-005 segments along axis X

## 3. Hardware
- M3 × 6
- PIN2 × 2
- alignment key 6mm × 8