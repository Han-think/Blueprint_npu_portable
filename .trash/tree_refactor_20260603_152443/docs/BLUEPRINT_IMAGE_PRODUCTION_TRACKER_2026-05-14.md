# Blueprint Image Production Tracker - 2026-05-14

This tracker keeps documentation, image production, validation, and protection status aligned.

The project goal is not to claim exact real-world engineering drawings. The goal is to build a high-purity, representative engineering image base that can support iterative model improvement.

## Core Principle

Every image must stay tied to four things:

1. Representative basis
2. Category/assembly specification
3. Actual UI asset path
4. Validation/protection state

If any one of these is missing, the image is not ready for superquality use.

## Quality States

| State | Meaning | Allowed Use |
|---|---|---|
| `coverage` | File exists and loads in UI | Placeholder / navigation |
| `structured` | Correct major structure and part mapping | Review / refinement |
| `master` | Hand-authored or deeply refined representative blueprint | Category reference |
| `superquality` | Master plus part-level manufacturing detail and verified consistency | Training-base candidate |

## Global Status

| Area | Status | Notes |
|---|---|---|
| Representative base locks | `done` | `BLUEPRINT_REPRESENTATIVE_BASE_LOCKS_2026-05-13.md` |
| Full asset inventory | `done` | Generated from `Minimal.html` |
| Image match evaluation | `done` | `BLUEPRINT_IMAGE_MATCH_EVALUATION_2026-05-15.md` |
| 3D review audit | `in_progress` | `BLUEPRINT_3D_REVIEW_AUDIT_2026-05-15.md`; 11 master seed assemblies have dedicated 3D scaffolds |
| UI manual curation loop | `done` | `Minimal.html` keep/reject/hold queue with JSONL export |
| Generation context packs | `started` | `BLUEPRINT_GENERATION_CONTEXT_PACKS_2026-05-15.md`; category context injected into assembly prompts |
| Design/learning layer boundary | `done` | `BLUEPRINT_LAYER_BOUNDARY_2026-05-15.md` |
| Assembly 3-axis coverage | `done` | 40 exterior, 40 internal, 40 top/part-zone |
| Single-part preset coverage | `done` | 200 preset SVGs |
| Space category spec | `done` | Ready for image master work |
| Aerospace category spec | `done` | F-15 twin-engine fighter basis locked |
| Remaining category specs | `done` | Propulsion, Drone, Robotics, Mechanical, Marine, Medical specs added on 2026-05-15 |
| Superquality image pass | `in_progress` | Space and Aerospace base sets are master references; Propulsion turbofan master pass started |

## Category Queue

| Order | Category | Documentation | Image Status | Next Action |
|---:|---|---|---|---|
| 1 | Space | `done` | `master` | Use as high-confidence training seed |
| 2 | Aerospace | `done` | `master` | Use as high-confidence training seed |
| 3 | Propulsion | `done` | `coverage/master mixed` | Promote non-turbofan 3-axis images |
| 4 | Drone | `done` | `coverage` | Promote category master images one vehicle at a time |
| 5 | Robotics | `done` | `coverage` | Promote category master images one vehicle at a time |
| 6 | Mechanical | `done` | `coverage` | Promote category master images one vehicle at a time |
| 7 | Marine | `done` | `coverage` | Promote category master images one vehicle at a time |
| 8 | Medical | `done` | `coverage` | Promote category master images one vehicle at a time |

## Immediate Image Work Queue

Do not start broad image changes randomly. Use this order:

1. `small_launch_vehicle` single-part images
   - `p1` combustion chamber - `master`
   - `p2` bell nozzle - `master`
   - `p3` turbopump - `master`
   - `p4` LOX tank - `master`
   - `p5` fuel tank - `master`
   - `p6` interstage - `master`
   - `p7` stage 2 engine - `master`
   - `p8` payload fairing - `master`
   - `p9` fin set - `master`
   - `p10` avionics bay - `master`
2. `cubesat_3u` three-axis images - `master`
3. `cubesat_3u` single-part images - `master`
4. `fighter_f_class` three-axis images using F-15 twin-engine basis - `master`
5. `fighter_f_class` single-part images - `master`
6. `supersonic_sst` three-axis images using Concorde-class basis - `master`
7. `supersonic_sst` single-part images - `master`
8. `lunar_lander` three-axis images - `master`
9. `lunar_lander` single-part images - `master`
10. `space_telescope` three-axis images - `master`
11. `space_telescope` single-part images - `master`
12. `orbital_module` three-axis images - `master`
13. `orbital_module` single-part images - `master`
14. `civil_airliner` three-axis images using A320-class basis - `master`
15. `civil_airliner` single-part images - `master`
16. `turboprop_transport` three-axis images using ATR72-class basis - `master`
17. `turboprop_transport` single-part images - `master`
18. `heavy_helicopter` three-axis images using CH-47-class basis - `master`
19. `heavy_helicopter` single-part images - `master`
20. `turbofan_engine` category/spec check using LEAP/CFM56-class code basis - `master`
21. `turbofan_engine` three-axis images - `master`
22. `turbofan_engine` single-part images - `master`

## Assembly Master Checklist

| Category | Vehicle | Parts | 3-Axis | Part Images | Next |
|---|---|---:|---|---|---|
| Space | `small_launch_vehicle` | 10 | `master` | `10/10 master` | done |
| Space | `cubesat_3u` | 8 | `master` | `8/8 master` | done |
| Space | `lunar_lander` | 8 | `master` | `8/8 master` | done |
| Space | `space_telescope` | 8 | `master` | `8/8 master` | done |
| Space | `orbital_module` | 8 | `master` | `8/8 master` | done |
| Aerospace | `fighter_f_class` | 10 | `master` | `10/10 master` | done |
| Aerospace | `supersonic_sst` | 10 | `master` | `10/10 master` | done |
| Aerospace | `civil_airliner` | 9 | `master` | `9/9 master` | done |
| Aerospace | `turboprop_transport` | 8 | `master` | `8/8 master` | done |
| Aerospace | `heavy_helicopter` | 8 | `master` | `8/8 master` | done |
| Propulsion | `turbofan_engine` | 10 | `master` | `10/10 master` | done |
| Propulsion | `solid_rocket_motor` | 8 | `coverage` | `8/8 master` | done |
| Propulsion | `electric_motor_assy` | 8 | `coverage` | `8/8 master` | done |
| Propulsion | `marine_propeller` | 8 | `coverage` | `8/8 master` | done |
| Propulsion | `ion_thruster_assy` | 8 | `coverage` | `8/8 master` | done |
| Drone | `racing_quad_5in` | 13 | `coverage` | `13/13 master` | done |
| Drone | `cinelifter_x8` | 14 | `coverage` | `14/14 master` | done |
| Drone | `wing_long_range` | 13 | `coverage` | `13/13 master` | done |
| Drone | `cyclocopter_demo` | 12 | `coverage` | `12/12 master` | done |
| Drone | `tiltrotor_vtol` | 13 | `coverage` | `13/13 master` | done |
| Robotics | `arm_6dof` | 9 | `coverage` | `9/9 master` | done |
| Robotics | `mars_rover` | 9 | `coverage` | `9/9 master` | done |
| Robotics | `quadruped_walker` | 8 | `coverage` | `8/8 master` | done |
| Robotics | `delta_parallel_robot` | 9 | `coverage` | `9/9 master` | done |
| Robotics | `humanoid_biped` | 9 | `coverage` | `9/9 master` | done |
| Mechanical | `harmonic_drive` | 8 | `coverage` | `8/8 master` | done |
| Mechanical | `suspension_assy` | 8 | `coverage` | `8/8 master` | done |
| Mechanical | `cnc_tool_changer` | 8 | `coverage` | `8/8 master` | done |
| Mechanical | `hydraulic_cylinder` | 8 | `coverage` | `8/8 master` | done |
| Mechanical | `precision_linkage` | 8 | `coverage` | `8/8 master` | done |
| Marine | `rov_inspection` | 9 | `coverage` | `9/9 master` | done |
| Marine | `usv_autonomous` | 8 | `coverage` | `8/8 master` | done |
| Marine | `underwater_glider` | 8 | `coverage` | `8/8 master` | done |
| Marine | `research_submarine` | 8 | `coverage` | `8/8 master` | done |
| Marine | `wave_glider_asv` | 8 | `coverage` | `8/8 master` | done |
| Medical | `myoelectric_hand` | 8 | `coverage` | `8/8 master` | done |
| Medical | `powered_afo` | 8 | `coverage` | `8/8 master` | done |
| Medical | `surgical_robot_arm` | 8 | `coverage` | `8/8 master` | done |
| Medical | `cochlear_implant` | 8 | `coverage` | `8/8 master` | done |
| Medical | `powered_exoskeleton` | 8 | `coverage` | `8/8 master` | done |

Current assembly-specific part image total:

- Completed: `359`
- Total assembly part mappings: `359`
- Remaining: `0`

Recommended next image/data item:

- **All assembly-specific part images complete.** Quality-labeled JSONL export implemented in `scripts/build_blueprint_training_manifest.js`.

## Image Review Checklist

Before marking an image as `master` or `superquality`, check:

- Does the silhouette match the locked representative basis?
- Does the image show the correct engineering hierarchy?
- Does the internal axis explain function, not decoration?
- Does the part-zone axis match visible component footprints?
- Are labels short and functional?
- Are bolts, rails, frames, hinges, ducts, tanks, bearings, or other relevant details present?
- Is the viewBox correct for the UI schematic?
- Does the SVG parse as XML?
- Does the local server return `200`?
- Is the hand-authored asset protected from generator overwrite?

## Protection Rules

Hand-authored assembly top/part-zone images:

```text
scripts/generate_blueprint_assets.js -> MASTER_ASSEMBLY_IDS
```

Hand-authored exterior/internal axis images:

```text
scripts/generate_blueprint_assets.js -> MANUAL_AXIS_ASSET_IDS
```

Single-part image protection still needs to be added before hand-authoring many preset images.

Assembly-specific part images:

```text
vendor/img/assembly_parts/<vehicle_id>/<part_id>.svg
```

These are not produced by the generator and are used before shared preset fallback images in the UI.

## Next Structural Task

Before making many shared preset master images, use the existing protection mechanism for hand-authored preset SVGs.

Recommended name:

```text
MANUAL_PRESET_ASSET_IDS
```

This should prevent high-quality preset images from being overwritten by `scripts/generate_blueprint_assets.js`.

Implemented:

- `MANUAL_PRESET_ASSET_IDS` exists in `scripts/generate_blueprint_assets.js`.
- `small_launch_vehicle` has assembly-specific part images at `vendor/img/assembly_parts/small_launch_vehicle/`.
