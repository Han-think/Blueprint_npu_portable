# Blueprint Visual Audit Notes

Date: 2026-05-16

## Purpose

First visual audit pass for blueprint SVG assets that may be hard to understand at a glance. This is not a final rejection list. It is a repair-priority list for assets that look too icon-like, too sparse, or weakly differentiated across the top / internal / exterior views.

Contact sheets:

- `docs/BLUEPRINT_VISUAL_AUDIT_CONTACT_SHEET_2026-05-16.html`
- `docs/BLUEPRINT_VISUAL_AUDIT_CONTACT_SHEET_2026-05-16_PAGE2.html`

## Assembly 3-Axis Findings

### Priority A: redraw or strongly refine

- `civil_airliner`: silhouette is recognizable, but all three axes are too small and sparse. It does not yet communicate fuselage, wing, engine, landing gear, internal cabin/cargo/fuel structure clearly enough.
- `heavy_helicopter`: top/internal/exterior read as simplified blocks. Rotor system, tail boom, transmission, landing gear, and load path are under-expressed.
- `turboprop_transport`: better than the weakest set, but still icon-like in exterior/internal views. Needs clearer nacelles, high wing, cabin, tail, and landing gear mapping.
- `turbofan_engine`: current axes read as a simple capsule/engine block. Needs visible fan, compressor, combustor, turbine, shaft/core/bypass separation.
- `orbital_module`: shape is readable but generic. Needs clearer docking ports, pressure module, service module, solar/thermal interfaces, internal equipment zones.
- `space_telescope`: too box-like. Needs optical tube/mirror path, aperture, service bay, sunshield/panel relationship, instrument module separation.

### Priority B: usable but should be upgraded before superquality

- `fighter_f_class`: F-15-like twin-engine fighter intent is visible, but internal/exterior views are still too simplified for master-grade learning data. Needs better twin-intake/twin-engine layout, wing/tail planform, cockpit, gear bays, and weapons/hardpoint hints.
- `supersonic_sst`: recognizable long slender transport shape, but the view scale is small and internal logic is weak. Needs cabin/fuel/landing gear/engine placement details.
- `lunar_lander`: visually coherent, but still mostly symbolic. Needs stronger descent stage, tank, engine, landing-leg, avionics, payload mapping.
- `research_submarine`, `usv_autonomous`, `wave_glider_asv`, `underwater_glider`: recognizable marine silhouettes, but internal/exterior detail is light.
- `powered_exoskeleton`, `humanoid_biped`, `powered_afo`: readable as wearable/medical structures, but mechanical joints, actuation, straps, and load paths should be clearer.

### Priority C: currently acceptable as navigation/reference assets

- `small_launch_vehicle`: one of the stronger sets. Still can be refined, but it communicates rocket architecture and subsystem regions better than most.
- `cubesat_3u`: clear enough for current review use, though internal detail can be improved.
- `racing_quad_5in`, `cinelifter_x8`: readable drone layouts; exterior views remain simple but not confusing.
- `electric_motor_assy`, `harmonic_drive`, `cnc_tool_changer`: simple but structurally understandable for the category.
- `marine_propeller`, `hydraulic_cylinder`, `cochlear_implant`: readable basic forms, though not yet superquality.

## Assembly Part Image Findings

Low-complexity part SVG clusters were detected by SVG size, text count, and primitive count. These should be checked visually before they are marked as master or superquality.

Most suspicious clusters:

- `vendor/img/assembly_parts/orbital_module/*.svg`
- `vendor/img/assembly_parts/civil_airliner/*.svg`
- `vendor/img/assembly_parts/turboprop_transport/*.svg`
- `vendor/img/assembly_parts/turbofan_engine/*.svg`
- `vendor/img/assembly_parts/space_telescope/*.svg`
- `vendor/img/assembly_parts/heavy_helicopter/*.svg`
- selected `vendor/img/assembly_parts/lunar_lander/*.svg`
- selected `vendor/img/assembly_parts/supersonic_sst/*.svg`

Representative lowest-complexity files:

- `vendor/img/assembly_parts/orbital_module/p1.svg`
- `vendor/img/assembly_parts/turboprop_transport/p2.svg`
- `vendor/img/assembly_parts/turbofan_engine/p3.svg`
- `vendor/img/assembly_parts/space_telescope/p3.svg`
- `vendor/img/assembly_parts/turbofan_engine/p4.svg`
- `vendor/img/assembly_parts/turbofan_engine/p9.svg`
- `vendor/img/assembly_parts/orbital_module/p4.svg`
- `vendor/img/assembly_parts/civil_airliner/p2.svg`
- `vendor/img/assembly_parts/orbital_module/p5.svg`
- `vendor/img/assembly_parts/turbofan_engine/p6.svg`

## Recommended Repair Order

1. `turbofan_engine`: high value for propulsion reasoning and geometry generation; current image is too generic.
2. `civil_airliner`: common aerospace basis; weak image could teach poor assembly decomposition.
3. `heavy_helicopter`: current simplified shape does not support rotor/transmission/load-path reasoning.
4. `space_telescope`: important space assembly, but current visual logic is too box-like.
5. `orbital_module`: useful space structure, but current asset needs clearer module/interface semantics.
6. `fighter_f_class`: already recognizable, but should be elevated because it is the locked fighter representative.

## Repair Standard

For a repair pass, each 3-axis assembly set should include:

- clear silhouette matching the representative family
- distinct top / internal / exterior views, not three near-duplicates
- 6-10 readable subsystem labels
- visible interface logic between major subsystems
- internal path hints for load, flow, thermal, electrical/data, or motion where relevant
- no generic rectangle/capsule-only construction unless the real object is box-like

Part images should include:

- a part-specific shape, not a reused generic block
- at least 3 visible functional features
- at least 2 interface/service details
- concise labels that match the assembly BOM and generation prompt language
