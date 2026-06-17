# Blueprint 3D Review Audit - 2026-05-15

This audit separates visual file coverage from actual 3D review readiness.

## Status Labels

| Status | Meaning | Training Use |
|---|---|---|
| `master_3d_scaffold` | Dedicated reference 3D scaffold exists for the whole assembly. | Can be used for visual review, but generated `geometry_ops` still need coordinate audit. |
| `part_reference_only` | Dedicated 2D part SVGs exist, but 3D part scaffold is not complete for the full category. | Use for 2D review and weak-label data only. |
| `schematic_extrusion_placeholder` | Full Assembly 3D is still derived from schematic zones and may appear box-like. | Do not use as 3D quality evidence. |

## Current Master 3D Scaffold Coverage

Implemented in `Minimal.html` build `design-pack-v11`.

| Category | Assembly | 3D Status | Notes |
|---|---|---|---|
| Space | `small_launch_vehicle` | `master_3d_scaffold` | Rocket stack scaffold plus 10 part-level fallback scaffolds. |
| Space | `cubesat_3u` | `master_3d_scaffold` | 3U bus, deployable panels, reaction wheel/boom cues. |
| Space | `lunar_lander` | `master_3d_scaffold` | Deck, tanks, descent engine, legs, top panel. |
| Space | `space_telescope` | `master_3d_scaffold` | Optical tube, mirror aperture, panels, instrument bay. |
| Space | `orbital_module` | `master_3d_scaffold` | Pressure module, CBM rings, arrays, radiator/payload cues. |
| Aerospace | `fighter_f_class` | `master_3d_scaffold` | Twin-engine fighter-style fuselage, wing, tail, engines. |
| Aerospace | `supersonic_sst` | `master_3d_scaffold` | Long slender fuselage, swept/delta wing, tail. |
| Aerospace | `civil_airliner` | `master_3d_scaffold` | Tube-and-wing airliner with nacelles. |
| Aerospace | `turboprop_transport` | `master_3d_scaffold` | Regional turboprop fuselage, wing, nacelles, prop disks. |
| Aerospace | `heavy_helicopter` | `master_3d_scaffold` | Tandem-rotor helicopter body and two rotor stations. |
| Propulsion | `turbofan_engine` | `master_3d_scaffold` | Nacelle, fan, compressor, combustor, turbine, exhaust flow hierarchy. |

## Pending 3D Scaffold Promotions

These assemblies still need a category-specific 3D pass before their Full Assembly 3D view should be treated as review evidence:

| Category | Assemblies |
|---|---|
| Propulsion | `solid_rocket_motor`, `electric_motor_assy`, `marine_propeller`, `ion_thruster_assy` |
| Drone | `racing_quad_5in`, `cinelifter_x8`, `wing_long_range`, `cyclocopter_demo`, `tiltrotor_vtol` |
| Robotics | `arm_6dof`, `mars_rover`, `quadruped_walker`, `delta_parallel_robot`, `humanoid_biped` |
| Mechanical | `harmonic_drive`, `suspension_assy`, `cnc_tool_changer`, `hydraulic_cylinder`, `precision_linkage` |
| Marine | `rov_inspection`, `usv_autonomous`, `underwater_glider`, `research_submarine`, `wave_glider_asv` |
| Medical | `myoelectric_hand`, `powered_afo`, `surgical_robot_arm`, `cochlear_implant`, `powered_exoskeleton` |

## Required Review Gates

Before an assembly can be promoted from placeholder to review-ready:

1. Whole Assembly 3D must show the representative product silhouette, not only schematic boxes.
2. Main subsystem positions must be visually distinguishable and labeled.
3. Generated part `geometry_ops` must pass coordinate audit, preferably `explicit at[] >= 80%`.
4. Part-level 3D fallback scaffolds must exist when generated output is coordinate-poor or box-dominated.
5. `keep data` should be used only after both 2D reference and 3D review agree with the intended assembly.

## Generated Output Rule

As of `design-pack-v12`, reference scaffolds are not considered generated design output.

- The primary 2D review panel must be `ACTUAL GENERATED 2D DESIGN`, drawn only from `geometry_ops`.
- As of `design-pack-v13`, the generated 2D panel must show three orthographic projections: TOP `X/Y`, FRONT `X/Z`, and SIDE `Y/Z`.
- The primary part 3D view must show actual generated `geometry_ops`, even when the result is poor or box-like.
- Reference SVGs and reference scaffolds are targets/grounding aids only.
- A record with `_generated_design_audit.status = fail` must not be promoted with `keep data`.
