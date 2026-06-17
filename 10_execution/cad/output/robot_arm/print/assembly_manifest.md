# robot_arm — print & assembly guide

**Process:** FDM
**Safety:** Educational mock assembly for design review; verify all fits with the coupon before committing full prints.

## 0. Print the fit coupon first
`fit_test_coupon.stl` — pin Ø6 + holes at [0.15, 0.3] mm. Use the loosest hole that still grips.

## 1. Parts
- `new-001_serviceable_base_and_shoulder_cartridge_.stl` × 1 — serviceable base and shoulder cartridge set · bbox [110.0, 97.7, 62.0] mm · clearance 0.0 mm
- `new-002_hollow_upper_and_forearm_link_pair_with_.stl` × 1 — hollow upper and forearm link pair with open cable channel · bbox [41.9, 26.7, 152.0] mm · clearance 0.15 mm
- `new-003_removable_elbow_and_wrist_joint_module_s.stl` × 1 — removable elbow and wrist joint module set · bbox [43.9, 44.0, 29.8] mm · clearance 0.15 mm
- `new-004_tool_flange_service_module.stl` × 1 — tool flange service module · bbox [42.0, 41.9, 7.8] mm · clearance 0.15 mm
- `new-005_external_replaceable_cable_spine.stl` × 1 — external replaceable cable spine · bbox [34.0, 17.7, 230.0] mm · clearance 0.3 mm

## 2. Assembly order
1. new-002 → new-001 (face, 0.15 mm) — upper/forearm hollow link ↔ base/shoulder
2. new-003 → new-002 (face, 0.15 mm) — elbow/wrist joint cartridge ↔ link
3. new-005 → new-002 (snap, 0.3 mm) — external replaceable cable spine clip
4. new-004 → new-003 (face, 0.15 mm) — tool flange service module bolts onto wrist joint module

## 3. Hardware
- M4 × 4
- M3 × 10