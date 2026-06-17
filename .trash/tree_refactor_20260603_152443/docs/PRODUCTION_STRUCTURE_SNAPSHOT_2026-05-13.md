# Blueprint NPU Production Structure Snapshot — 2026-05-13

This note records the current working structure before fine tuning the production UI.

## Verified Working Baseline

- `Minimal.html` is the active design-generation surface.
- The browser can query the local Ollama-compatible endpoint at `http://127.0.0.1:11434`.
- `server/serve.py` serves the static package and exposes:
  - `GET /schema`
  - `POST /validate`
- `schema_v6.json` is the canonical output contract for generated blueprints.
- The generation flow in `Minimal.html` is implemented as:
  1. user brief
  2. Stage 1: generate three brief/part-tree variants
  3. user selects one variant
  4. Stage 2: geometry and CAD brief
  5. Stage 3: verification and risk
  6. Stage 4: print profile and slicer job
  7. final JSON download / inspection
- Assembly mode can generate per-part blueprint packages for selected vehicle templates.

## Current Important Gap

The visual schematic overlay is still manually mapped.

`VehicleSchematic` renders:

```text
vendor/img/<vehicle_id>_top.svg
  + VEHICLE_SCHEMATICS[vehicle_id].zones
```

The top-view SVG image and the zone coordinate system must use the same viewBox. If they do not, labels and highlighted regions drift away from the actual design image.

Example found on 2026-05-13:

- `vendor/img/fighter_f_class_top.svg` uses `viewBox="0 0 700 380"`.
- `VEHICLE_SCHEMATICS.fighter_f_class` was using `vb:'0 0 700 320'`.
- This caused the `BLUEPRINT SCHEMATIC / TOP VIEW` overlay to misalign with the real F-class plan image.

## Next Adjustment Direction

- Treat each vehicle top SVG as the source of truth for schematic coordinates.
- For each vehicle, match `VEHICLE_SCHEMATICS[vehicle_id].vb` to the actual SVG `viewBox`.
- Move each zone to the actual visible component footprint in the SVG, not to a generic aircraft/vehicle layout.
- Keep the existing generation pipeline intact while refining visual fidelity.

## Files To Watch

- `Minimal.html`
- `vendor/img/*_top.svg`
- `vendor/img/*.svg`
- `schema_v6.json`
- `server/serve.py`

## ViewBox Mismatches Found

These schematic entries need the same cleanup pass as `fighter_f_class`:

- `turboprop_transport`: schematic `0 0 680 300`, image `0 0 700 320`
- `civil_airliner`: schematic `0 0 780 320`, image `0 0 820 340`
- `heavy_helicopter`: schematic `0 0 600 400`, image `0 0 620 440`
- `lunar_lander`: schematic `0 0 500 520`, image `0 0 540 540`
- `rov_inspection`: schematic `0 0 600 380`, image `0 0 640 400`
- `underwater_glider`: schematic `0 0 700 240`, image `0 0 740 260`
- `arm_6dof`: schematic `0 0 500 500`, image `0 0 560 540`
- `mars_rover`: schematic `0 0 600 420`, image `0 0 620 440`
- `quadruped_walker`: schematic `0 0 600 440`, image `0 0 620 460`
- `orbital_module`: schematic `0 0 700 400`, image `0 0 800 380`
- `harmonic_drive`: schematic `0 0 500 400`, image `0 0 600 420`
- `suspension_assy`: schematic `0 0 600 400`, image `0 0 700 420`
- `precision_linkage`: schematic `0 0 600 400`, image `0 0 700 440`

## Image Redraw Scope

Assembly vehicle templates:

- Total assembly templates: `40`
- Category split:
  - `drone`: 5
  - `aerospace`: 5
  - `space`: 5
  - `marine`: 5
  - `robotics`: 5
  - `medical`: 5
  - `propulsion`: 5
  - `mechanical`: 5

Assembly schematic coverage:

- `VEHICLE_SCHEMATICS`: 40
- Existing `*_top.svg`: 31
- Missing dedicated top SVG: 9
  - `racing_quad_5in`
  - `cinelifter_x8`
  - `wing_long_range`
  - `cyclocopter_demo`
  - `small_launch_vehicle`
  - `cubesat_3u`
  - `usv_autonomous`
  - `myoelectric_hand`
  - `powered_afo`

Single-part preset configurations:

- Total single-part preset configs: `200`
- Category split:
  - `drone`: 32
  - `aerospace`: 24
  - `space`: 24
  - `marine`: 24
  - `propulsion`: 24
  - `mechanical`: 24
  - `robotics`: 24
  - `medical`: 24

Total redraw target if every assembly and every single-part preset receives a dedicated image: `240`.

## Asset Generation Baseline

Completed as the repeatable baseline:

- Regenerated all assembly top-view schematic SVGs so every assembly has a visible schematic asset.
- Generated all single-part preset schematic SVGs from `PRESET_TREE`.
- Added `scripts/generate_blueprint_assets.js` as the repeatable asset-generation source.
- Wired the selected single-part preset preview into `PresetSelector`.

Generated asset counts:

- Assembly top-view SVGs: `40`
- Single-part preset SVGs: `200`
- Total generated schematic assets: `240`

Verification:

- All generated SVG files parse as XML.
- All assembly SVG `viewBox` values match their `VEHICLE_SCHEMATICS` `vb` values.
- Sample server checks returned `200`:
  - `vendor/img/turboprop_transport_top.svg`
  - `vendor/img/presets/drone/multirotor/quad_x.svg`

Quality correction note:

- A first generated batch over-prioritized coordinate alignment and looked too box-like.
- The generator was revised so assembly assets use recognizable silhouettes inspired by each template's representative reference (`wikiTitle`) such as ATR 72, A320 family, CH-47, Concorde, Perseverance rover, Universal Robots, Spot, and similar class references.
- These are original schematic drawings, not copied production drawings.
- A later pass increased the homage/detail level for key representative classes:
  - F-class fighter: F-15/F-22-like twin-engine, twin-tail, intake, hardpoint, and internal bay cues.
  - Turboprop transport: ATR-style high wing, nacelles, and large prop discs.
  - Small launch vehicle / rocket family: Saturn V-like stage bands, fins, and clustered engine bells.
- A precision pass added professional blueprint detail layers across all 40 assembly images:
  - part-zone wire overlays
  - station/datum lines
  - rivet/bolt reference points
  - callout leaders and labels
  - domain-specific datum notes such as aero, rocket, and kinematic references

## Master-Grade Redraw Track

The generated baseline is useful for coverage, but it is not the final quality target. The user direction on 2026-05-13 is to stop bulk-polishing and upgrade each assembly one by one into a master-grade schematic that can become the reference style for its category.

Current master-grade assembly track:

- `small_launch_vehicle`
  - File: `vendor/img/small_launch_vehicle_top.svg`
  - ViewBox: `0 0 400 680`
  - Direction: Saturn V structural-study basis adapted to the current small-launch-vehicle part tree, original blueprint line art.
  - Uses Saturn V stage logic as the visual foundation: lower S-IC-style tank/thrust section, upper-stage/vacuum-engine section, interstage, IU-like avionics ring, fairing/adapter top, fin can, and clustered engine bay.
  - Includes exterior stack, internal tank/stage bands, station lines, common-bulkhead/aft-dome cues, truss interstage, turbopump/plumbing study, fin/nozzle geometry, callouts, and overlay-ready part zones.
  - Protected from generator overwrite through `MASTER_ASSEMBLY_IDS` in `scripts/generate_blueprint_assets.js`.

Space assembly master pass:

- `small_launch_vehicle`: Saturn V structural-study basis, highest-detail reference for the space category.
- `cubesat_3u`: CubeSat Design Specification-style 3U bus with PC/104 stack, rail structure, deployable solar wings, antennas, ADCS/payload blocks, thrusters, and separation plate.
- `lunar_lander`: Apollo LM / Surveyor-inspired lander structure with central propellant tank, avionics/payload decks, RCS pods, solar wings, high-gain dish, descent engine, and four landing legs.
- `space_telescope`: Hubble-class rolled front view with aperture door, optical tube, primary/secondary mirrors, metering bench, service/equipment section, solar arrays, pointing control, and axial instrument bay.
- `orbital_module`: ISS-module-inspired side view with cylindrical pressure shell, CBM ports, truss attach, radiator, solar array tower, interior rack decks, external payload platform, and ECLSS rack zone.

These five files are protected from generator overwrite through `MASTER_ASSEMBLY_IDS`.

Remaining assembly assets still need master-grade passes. The generated files should be treated as placeholders/reference scaffolds until each one is manually upgraded.

## Three-Axis Assembly Schematic Direction

The assembly schematic should be split into three visual axes so the structure is understandable and useful as learning data:

- Exterior axis: what the product looks like from the outside, focused on recognition and silhouette.
- Internal axis: functional cutaway/section view, focused on tanks, mechanisms, electronics, decks, optical paths, pressure shells, and propulsion flow.
- Part-zone axis: app-facing `p1...pN` overlay map, focused on exact correspondence between generated part data and visible component footprints.

Current implementation:

- `VehicleSchematic` in `Minimal.html` now exposes `외형 / 내부 / 파트존` controls.
- Asset naming convention:
  - `vendor/img/<vehicle_id>_exterior.svg`
  - `vendor/img/<vehicle_id>_internal.svg`
  - `vendor/img/<vehicle_id>_top.svg` for the part-zone map.
- If an exterior/internal asset does not exist yet, the UI falls back to the part-zone map.
- `scripts/generate_blueprint_assets.js` now generates three assembly axes for every vehicle template:
  - `40` exterior-axis SVGs
  - `40` internal-axis SVGs
  - `40` part-zone/top SVGs
- Hand-authored axis assets are protected through `MANUAL_AXIS_ASSET_IDS`.

First completed three-axis reference:

- `small_launch_vehicle`
  - Exterior: `vendor/img/small_launch_vehicle_exterior.svg`
  - Internal: `vendor/img/small_launch_vehicle_internal.svg`
  - Part-zone: `vendor/img/small_launch_vehicle_top.svg`

Whole-assembly coverage status:

- Assembly three-axis coverage is now complete for all `40` vehicle templates.
- This is a structural coverage baseline, not the final master-art quality for every vehicle.
- The next quality pass should upgrade one vehicle at a time by replacing generated exterior/internal/top assets with hand-authored master assets, then adding that vehicle to the relevant protection set.

Space superquality planning:

- The Space category now has a document-first image specification:
  `docs/SPACE_SUPERQUALITY_BLUEPRINT_SPEC_2026-05-13.md`
- This spec should be used before upgrading Space assembly images or Space single-part preset images.

Aerospace superquality planning:

- The Aerospace category now has a document-first image specification:
  `docs/AEROSPACE_SUPERQUALITY_BLUEPRINT_SPEC_2026-05-13.md`
- This spec should be used before upgrading Aerospace assembly images or Aerospace single-part preset images.
- `fighter_f_class` is now fixed to an F-15 Eagle / F-15EX-style twin-engine representative basis rather than an F-16 single-engine basis.
- It records two template-direction issues to preserve image consistency:
  - `civil_airliner` currently uses an A320-family representative basis despite a twin-aisle label.
  - `heavy_helicopter` currently uses a CH-47 tandem-rotor representative basis despite a coaxial label.

Whole-image documentation planning:

- The project now has a documentation-first image workflow:
  `docs/BLUEPRINT_IMAGE_DOCUMENTATION_SYSTEM_2026-05-13.md`
- The project now has an image production tracker:
  `docs/BLUEPRINT_IMAGE_PRODUCTION_TRACKER_2026-05-14.md`
- The project now has a locked representative-basis table:
  `docs/BLUEPRINT_REPRESENTATIVE_BASE_LOCKS_2026-05-13.md`
- The current code-derived image inventory is:
  `docs/BLUEPRINT_IMAGE_ASSET_INVENTORY_2026-05-13.md`
- The inventory is generated from `Minimal.html` by:
  `scripts/generate_blueprint_image_docs.js`
- Current documented scope:
  - `40` assembly templates
  - `120` assembly axis images (`40 exterior`, `40 internal`, `40 top/part-zone`)
  - `359` assembly part mappings
  - `200` single-part preset image configs

Protection update:

- `scripts/generate_blueprint_assets.js` now includes `MANUAL_PRESET_ASSET_IDS`.
- This allows hand-authored superquality single-part preset SVGs to be protected from generator overwrite.

Assembly part-image update:

- The UI now supports assembly-specific part images before falling back to shared preset images.
- Path convention:
  `vendor/img/assembly_parts/<vehicle_id>/<part_id>.svg`
- `small_launch_vehicle` now has `10` assembly-specific part images:
  - `p1` combustion chamber
  - `p2` bell nozzle
  - `p3` turbopump
  - `p4` LOX tank
  - `p5` fuel tank
  - `p6` interstage
  - `p7` stage 2 engine
  - `p8` payload fairing
  - `p9` fin set
  - `p10` avionics bay

CubeSat assembly image update:

- `cubesat_3u` now has hand-authored master three-axis images:
  - `vendor/img/cubesat_3u_exterior.svg`
  - `vendor/img/cubesat_3u_internal.svg`
  - `vendor/img/cubesat_3u_top.svg`
- `cubesat_3u` is protected in both `MASTER_ASSEMBLY_IDS` and `MANUAL_AXIS_ASSET_IDS`.

CubeSat part-image update:

- `cubesat_3u` now has `8` assembly-specific part images:
  - `p1` 3U primary frame
  - `p2` deployable solar panel
  - `p3` antenna deployer
  - `p4` reaction wheel
  - `p5` star tracker mount
  - `p6` payload optics bench
  - `p7` cold gas thruster bracket
  - `p8` separation spring plate

Fighter assembly image update:

- `fighter_f_class` now has F-15-class twin-engine master three-axis images:
  - `vendor/img/fighter_f_class_exterior.svg`
  - `vendor/img/fighter_f_class_internal.svg`
  - `vendor/img/fighter_f_class_top.svg`
- `fighter_f_class` is protected in both `MASTER_ASSEMBLY_IDS` and `MANUAL_AXIS_ASSET_IDS`.

Fighter part-image update:

- `fighter_f_class` now has `10` assembly-specific F-15-class part images:
  - `p1` forward fuselage
  - `p2` center fuselage
  - `p3` aft fuselage
  - `p4` main wing
  - `p5` twin vertical stabilizers
  - `p6` all-moving stabilator
  - `p7` twin engine inlet ducts
  - `p8` twin C-D / TVC nozzles
  - `p9` main landing gear
  - `p10` nose landing gear

Supersonic SST assembly image update:

- `supersonic_sst` now has Concorde-class master three-axis images:
  - `vendor/img/supersonic_sst_exterior.svg`
  - `vendor/img/supersonic_sst_internal.svg`
  - `vendor/img/supersonic_sst_top.svg`
- `supersonic_sst` is protected in both `MASTER_ASSEMBLY_IDS` and `MANUAL_AXIS_ASSET_IDS`.

Supersonic SST part-image update:

- `supersonic_sst` now has `10` assembly-specific Concorde-class part images:
  - `p1` ogive-delta wing
  - `p2` forward fuselage + visor
  - `p3` centre fuselage tanks
  - `p4` aft fuselage + reheat bay
  - `p5` six-section elevon array
  - `p6` paired engine nacelles
  - `p7` variable-geometry intake
  - `p8` fin + rudder
  - `p9` tall main landing gear
  - `p10` droop nose mechanism

Lunar lander assembly image update:

- `lunar_lander` now has hand-authored master three-axis images:
  - `vendor/img/lunar_lander_exterior.svg`
  - `vendor/img/lunar_lander_internal.svg`
  - `vendor/img/lunar_lander_top.svg`
- `lunar_lander` is protected in both `MASTER_ASSEMBLY_IDS` and `MANUAL_AXIS_ASSET_IDS`.

Lunar lander part-image update:

- `lunar_lander` now has `8` assembly-specific part images:
  - `p1` central propellant tank
  - `p2` throttleable main engine
  - `p3` RCS thruster cluster
  - `p4` deployable landing leg
  - `p5` avionics deck
  - `p6` deployable solar wing
  - `p7` high-gain antenna dish
  - `p8` science payload deck

Space telescope assembly image update:

- `space_telescope` now has Hubble-class master three-axis images:
  - `vendor/img/space_telescope_exterior.svg`
  - `vendor/img/space_telescope_internal.svg`
  - `vendor/img/space_telescope_top.svg`
- `space_telescope` is protected in both `MASTER_ASSEMBLY_IDS` and `MANUAL_AXIS_ASSET_IDS`.

Space telescope part-image update:

- `space_telescope` now has `8` assembly-specific part images:
  - `p1` primary mirror cell
  - `p2` secondary mirror assembly
  - `p3` optical metering bench
  - `p4` equipment section bay
  - `p5` solar array wing pair
  - `p6` aperture door
  - `p7` pointing control system
  - `p8` axial instrument bay

Orbital module assembly image update:

- `orbital_module` now has ISS-class master three-axis images:
  - `vendor/img/orbital_module_exterior.svg`
  - `vendor/img/orbital_module_internal.svg`
  - `vendor/img/orbital_module_top.svg`
- `orbital_module` is protected in both `MASTER_ASSEMBLY_IDS` and `MANUAL_AXIS_ASSET_IDS`.

Orbital module part-image update:

- `orbital_module` now has `8` assembly-specific part images:
  - `p1` pressure shell barrel
  - `p2` CBM docking port
  - `p3` integrated truss attach
  - `p4` thermal radiator assembly
  - `p5` solar array tower
  - `p6` habitation interior deck
  - `p7` external payload platform
  - `p8` ECLSS system racks

Civil airliner assembly image update:

- `civil_airliner` now has A320-class master three-axis images:
  - `vendor/img/civil_airliner_exterior.svg`
  - `vendor/img/civil_airliner_internal.svg`
  - `vendor/img/civil_airliner_top.svg`
- `civil_airliner` is protected in both `MASTER_ASSEMBLY_IDS` and `MANUAL_AXIS_ASSET_IDS`.

Civil airliner part-image update:

- `civil_airliner` now has `9` assembly-specific part images:
  - `p1` nose section + radome
  - `p2` fuselage barrel section
  - `p3` CFRP wing box
  - `p4` leading edge + slats
  - `p5` trailing edge + flaps
  - `p6` engine pylon
  - `p7` high-bypass turbofan nacelle
  - `p8` empennage V+H tail
  - `p9` main landing gear bogie

Turboprop transport assembly image update:

- `turboprop_transport` now has ATR72-class master three-axis images:
  - `vendor/img/turboprop_transport_exterior.svg`
  - `vendor/img/turboprop_transport_internal.svg`
  - `vendor/img/turboprop_transport_top.svg`
- `turboprop_transport` is protected in both `MASTER_ASSEMBLY_IDS` and `MANUAL_AXIS_ASSET_IDS`.

Turboprop transport part-image update:

- `turboprop_transport` now has `8` assembly-specific part images:
  - `p1` forward fuselage
  - `p2` main cabin section
  - `p3` tail cone + cargo ramp
  - `p4` high wing two-piece
  - `p5` turboprop engine nacelle
  - `p6` four-blade constant-speed propeller
  - `p7` T-tail empennage
  - `p8` main landing gear sponson

Heavy helicopter assembly image update:

- `heavy_helicopter` now has CH-47-class master three-axis images:
  - `vendor/img/heavy_helicopter_exterior.svg`
  - `vendor/img/heavy_helicopter_internal.svg`
  - `vendor/img/heavy_helicopter_top.svg`
- `heavy_helicopter` is protected in both `MASTER_ASSEMBLY_IDS` and `MANUAL_AXIS_ASSET_IDS`.

Heavy helicopter part-image update:

- `heavy_helicopter` now has `8` assembly-specific part images:
  - `p1` forward rotor hub
  - `p2` aft rotor hub
  - `p3` main gearbox housing
  - `p4` tandem rotor blade set
  - `p5` fuselage cargo cabin
  - `p6` aft pylon + rear ramp
  - `p7` twin turboshaft engine bay
  - `p8` quadricycle landing gear

Turbofan engine assembly image update:

- `turbofan_engine` uses the existing `Minimal.html` LEAP/CFM56-class high-bypass turbofan definition as its current propulsion spec basis.
- `turbofan_engine` now has master three-axis images:
  - `vendor/img/turbofan_engine_exterior.svg`
  - `vendor/img/turbofan_engine_internal.svg`
  - `vendor/img/turbofan_engine_top.svg`
- `turbofan_engine` is protected in both `MASTER_ASSEMBLY_IDS` and `MANUAL_AXIS_ASSET_IDS`.

Turbofan engine part-image update:

- `turbofan_engine` now has `10` assembly-specific part images:
  - `p1` CFRP wide-chord fan blades
  - `p2` fan disk + spinner
  - `p3` low-pressure compressor
  - `p4` high-pressure compressor
  - `p5` annular combustor
  - `p6` high-pressure turbine
  - `p7` low-pressure turbine
  - `p8` exhaust + thrust reverser
  - `p9` nacelle + inlet cowl
  - `p10` accessory gear box
