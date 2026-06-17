# tiltrotor — print & assembly guide

**Process:** FDM
**Safety:** Educational mock assembly for design review; verify all fits with the coupon before committing full prints.

## 0. Print the fit coupon first
`fit_test_coupon.stl` — pin Ø6 + holes at [0.2, 0.25, 0.3] mm. Use the loosest hole that still grips.

## 1. Parts
- `new-001_integrated_fuselage_spine_and_spar_socke.stl` × 1 — integrated fuselage spine and spar socket core · bbox [210.0, 41.8, 33.8] mm · clearance 0.2 mm
- `new-002_removable_nacelle_service_pods.stl` × 2 — removable nacelle service pods · bbox [46.0, 33.8, 31.8] mm · clearance 0.25 mm
- `new-003_separate_tilt_linkage_cartridges.stl` × 2 — separate tilt linkage cartridges · bbox [33.8, 13.8, 42.0] mm · clearance 0.2 mm
- `new-004_slide_in_battery_and_payload_service_mod.stl` × 1 — slide-in battery and payload service module · bbox [102.5, 41.4, 29.7] mm · clearance 0.3 mm
- `new-005_replaceable_v_tail_and_landing_gear_modu.stl` × 1 — replaceable V-tail and landing gear modules · bbox [48.0, 9.8, 17.8] mm · clearance 0.2 mm

## 2. Assembly order
1. new-001 → new-005 (press, 0.2 mm) — wing-root spar key (boss f-spar-key)
2. new-002 → new-001 (face, 0.25 mm) — nacelle service pod ↔ fuselage spine
3. new-004 → new-001 (slot, 0.3 mm) — battery/payload slide module
4. new-005 → new-001 (pin, 0.2 mm) — V-tail / landing gear replaceable
5. new-003 → new-002 (pin, 0.2 mm) — tilt linkage cartridge pin into nacelle service pod

## 3. Hardware
- M3 × 8
- PIN3 × 2