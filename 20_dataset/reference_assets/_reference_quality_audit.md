# Reference Quality Audit

Generated: 2026-06-27T07:22:39Z
Audited CAD assets: 288

## Seed Summary

| seed | status | assets | avg design | avg readiness | key recommendation |
|---|---|---:|---:|---:|---|
| battery_pack_module | watch | 8 | 58.5 | 57.6 | Review manually. |
| cnc_axis_carriage | watch | 29 | 59.5 | 58.1 | Review manually. |
| cubesat | watch | 32 | 44.3 | 43.7 | Good structural/print base: STEP plus prepped STL. Add avionics/solar/EPS reference later for subsystem breadth. |
| gearbox_reducer | watch | 7 | 63.7 | 54.0 | Review manually. |
| haptic_glove | watch | 72 | 55.3 | 56.6 | Strong mesh corpus for fingers/palm/links. Needs licensing pass and possibly assembly docs/URDF mapping before training promotion. |
| hydraulic_manifold | watch | 9 | 61.9 | 52.7 | Review manually. |
| long_range_recon_wing | watch | 12 | 60.3 | 51.8 | Useful OpenVSP geometry grammar for wings/props/aircraft. Needs specific UAV/flying-wing references and 2D/cutaway drawings. |
| robot_arm | watch | 64 | 53.8 | 47.2 | Strong link/joint STL family for industrial arms. License is unresolved; add URDF/joint metadata and one permissively licensed CAD source. |
| small_launch_vehicle | watch | 31 | 53.4 | 53.9 | Good educational rocket/SCAD print reference. Keep non-functional display boundary; do not treat as flight/propulsion design. |
| tiltrotor | watch | 12 | 58.7 | 50.6 | Useful aircraft/rotor VSP grammar but not truly tiltrotor-specific yet. Add nacelle tilt mechanism or VTOL repo references. |
| underwater_sealed_sensor_housing | watch | 12 | 64.4 | 62.0 | Review manually. |

## Per-Seed Detail

### battery_pack_module

- status: watch
- assets: 8
- extensions: {'.scad': 8}
- verdicts: {'reference_only': 8}
- top terms: {'battery': 8, 'pack': 8, 'scad': 8, 'pcb': 1}
- recommendation: Review manually.
- issues:
  - needs more STEP/B-rep source geometry
  - missing expected assembly terms: bms, busbar, cell, connector, cooling

### cnc_axis_carriage

- status: watch
- assets: 29
- extensions: {'.scad': 29}
- verdicts: {'reference_only': 28, 'license_review_then_promote': 1}
- top terms: {'carriage': 29, 'scad': 29, 'bearing': 4, 'gear': 2, 'rail': 2, 'pcb': 1, 'block': 1}
- recommendation: Review manually.
- issues:
  - needs more STEP/B-rep source geometry
  - missing expected assembly terms: ballscrew, sensor

### cubesat

- status: watch
- assets: 32
- extensions: {'.step': 4, '.stl': 5, '.pdf': 10, '.md': 1, '.png': 8, '.jpg': 3, '.csv': 1}
- verdicts: {'reference_only': 9, 'quarantine_or_review': 23}
- top terms: {'hardware': 31, 'eps': 18, 'solar': 11, 'prototype': 11, '3d': 10, 'print': 9, 'prepped': 5, 'stl': 5, 'bottom': 3, 'mid': 3, 'top': 3, 'arch': 3, 'battery': 3, 'pack': 3, 'pdu': 3, 'wall': 3}
- recommendation: Good structural/print base: STEP plus prepped STL. Add avionics/solar/EPS reference later for subsystem breadth.
- issues:
  - missing expected assembly terms: skeleton
  - license unresolved for at least one source; keep as reference-only until reviewed

### gearbox_reducer

- status: watch
- assets: 7
- extensions: {'.scad': 7}
- verdicts: {'reference_only': 7}
- top terms: {'gearbox': 7, 'scad': 7, 'bearing': 2}
- recommendation: Review manually.
- issues:
  - needs more STEP/B-rep source geometry
  - missing expected assembly terms: gear, housing, seal, shaft
  - license unresolved for at least one source; keep as reference-only until reviewed

### haptic_glove

- status: watch
- assets: 72
- extensions: {'.stl': 58, '.obj': 14}
- verdicts: {'reference_only': 69, 'quarantine_or_review': 3}
- top terms: {'stl': 58, 'hand': 50, 'link': 29, 'bend': 15, 'thumb': 8, 'base': 5, 'split': 5, 'ring': 4, 'forearm': 3, 'palm': 2, 'plate': 1, 'wrist': 1}
- recommendation: Strong mesh corpus for fingers/palm/links. Needs licensing pass and possibly assembly docs/URDF mapping before training promotion.
- issues:
  - missing expected assembly terms: finger

### hydraulic_manifold

- status: watch
- assets: 9
- extensions: {'.scad': 9}
- verdicts: {'reference_only': 9}
- top terms: {'hydraulic': 9, 'manifold': 9, 'scad': 9, 'hardware': 1}
- recommendation: Review manually.
- issues:
  - needs more STEP/B-rep source geometry
  - missing expected assembly terms: gallery, plug, port, valve
  - license unresolved for at least one source; keep as reference-only until reviewed

### long_range_recon_wing

- status: watch
- assets: 12
- extensions: {'.vsp3': 11, '.stl': 1}
- verdicts: {'reference_only': 12}
- top terms: {'wing': 12, 'prop': 3, 'rotor': 2, 'hershey': 1, 'rectangle': 1, 'stl': 1}
- recommendation: Useful OpenVSP geometry grammar for wings/props/aircraft. Needs specific UAV/flying-wing references and 2D/cutaway drawings.
- issues:
  - missing expected assembly terms: b777
  - license unresolved for at least one source; keep as reference-only until reviewed

### robot_arm

- status: watch
- assets: 64
- extensions: {'.stl': 64}
- verdicts: {'reference_only': 56, 'quarantine_or_review': 8}
- top terms: {'stl': 64, 'wrist': 24, 'forearm': 12, 'upperarm': 12, 'base': 8, 'shoulder': 8}
- recommendation: Strong link/joint STL family for industrial arms. License is unresolved; add URDF/joint metadata and one permissively licensed CAD source.
- issues:
  - license unresolved for at least one source; keep as reference-only until reviewed

### small_launch_vehicle

- status: watch
- assets: 31
- extensions: {'.scad': 16, '.stl': 15}
- verdicts: {'reference_only': 31}
- top terms: {'scad': 16, 'stl': 15, 'assembly': 4, 'fins': 4, 'body': 4, 'mainbody': 4, 'controller': 2, 'dimensions': 2, 'ring': 2}
- recommendation: Good educational rocket/SCAD print reference. Keep non-functional display boundary; do not treat as flight/propulsion design.
- issues:
  - missing expected assembly terms: engine, fin, nose

### tiltrotor

- status: watch
- assets: 12
- extensions: {'.vsp3': 11, '.stl': 1}
- verdicts: {'reference_only': 12}
- top terms: {'wing': 5, 'prop': 3, 'rotor': 2, 'hershey': 1, 'rectangle': 1, 'stl': 1}
- recommendation: Useful aircraft/rotor VSP grammar but not truly tiltrotor-specific yet. Add nacelle tilt mechanism or VTOL repo references.
- issues:
  - license unresolved for at least one source; keep as reference-only until reviewed

### underwater_sealed_sensor_housing

- status: watch
- assets: 12
- extensions: {'.scad': 12}
- verdicts: {'reference_only': 11, 'license_review_then_promote': 1}
- top terms: {'housing': 12, 'scad': 12, 'sensor': 12, 'assembly': 1, 'ring': 1}
- recommendation: Review manually.
- issues:
  - needs more STEP/B-rep source geometry
  - missing expected assembly terms: cap, cradle, gland, o-ring

## Global Findings

- Watch seed reference sets need targeted补강: battery_pack_module, cnc_axis_carriage, cubesat, gearbox_reducer, haptic_glove, hydraulic_manifold, long_range_recon_wing, robot_arm, small_launch_vehicle, tiltrotor, underwater_sealed_sensor_housing.
- All assets remain license-gated until manual review changes training_use/license_status.
- Reference assets are useful for shape grammar, assembly vocabulary, and scoring; they are not yet wired into generation prompts.
- Next hardening step: generate reference_feature_cards.jsonl with seed-specific part labels, station cues, and forbidden-copy boundary.

## Strongest Assets

| seed | readiness | design | path |
|---|---:|---:|---|
| underwater_sealed_sensor_housing | 66 | 70 | 20_dataset/reference_assets/underwater_sealed_sensor_housing/cad/printed__box_assembly.scad |
| cnc_axis_carriage | 66 | 70 | 20_dataset/reference_assets/cnc_axis_carriage/cad/vitamins__bearing_block.scad |
| underwater_sealed_sensor_housing | 64 | 67 | 20_dataset/reference_assets/underwater_sealed_sensor_housing/cad/printed__box.scad |
| underwater_sealed_sensor_housing | 64 | 67 | 20_dataset/reference_assets/underwater_sealed_sensor_housing/cad/printed__butt_box.scad |
| underwater_sealed_sensor_housing | 64 | 67 | 20_dataset/reference_assets/underwater_sealed_sensor_housing/cad/printed__cable_grommets.scad |
| underwater_sealed_sensor_housing | 64 | 67 | 20_dataset/reference_assets/underwater_sealed_sensor_housing/cad/printed__camera_housing.scad |
| underwater_sealed_sensor_housing | 64 | 67 | 20_dataset/reference_assets/underwater_sealed_sensor_housing/cad/printed__printed_box.scad |
| underwater_sealed_sensor_housing | 64 | 67 | 20_dataset/reference_assets/underwater_sealed_sensor_housing/cad/printed__socket_box.scad |
| underwater_sealed_sensor_housing | 64 | 67 | 20_dataset/reference_assets/underwater_sealed_sensor_housing/cad/utils__tube.scad |
| cnc_axis_carriage | 64 | 67 | 20_dataset/reference_assets/cnc_axis_carriage/cad/vitamins__gear_motor.scad |
| cnc_axis_carriage | 64 | 67 | 20_dataset/reference_assets/cnc_axis_carriage/cad/vitamins__rail.scad |
| haptic_glove | 64 | 65 | 20_dataset/reference_assets/haptic_glove/cad/hand_meshes__inspire_hand__meshes__base_link.STL |
| haptic_glove | 64 | 65 | 20_dataset/reference_assets/haptic_glove/cad/hand_meshes__inspire_hand__meshes__hand_base_link.STL |
| haptic_glove | 64 | 65 | 20_dataset/reference_assets/haptic_glove/cad/hand_meshes__wonik_allegro__assets__base_link_left.stl |
| cnc_axis_carriage | 63 | 66 | 20_dataset/reference_assets/cnc_axis_carriage/cad/printed__pcb_mount.scad |
| cnc_axis_carriage | 62 | 65 | 20_dataset/reference_assets/cnc_axis_carriage/cad/vitamins__sbr_rail.scad |
| cnc_axis_carriage | 61 | 64 | 20_dataset/reference_assets/cnc_axis_carriage/cad/printed__carriers.scad |
| cnc_axis_carriage | 61 | 64 | 20_dataset/reference_assets/cnc_axis_carriage/cad/printed__drag_chain.scad |
| cnc_axis_carriage | 61 | 64 | 20_dataset/reference_assets/cnc_axis_carriage/cad/printed__printed_pulleys.scad |
| cnc_axis_carriage | 61 | 64 | 20_dataset/reference_assets/cnc_axis_carriage/cad/printed__screw_knob.scad |

## Weakest Assets

| seed | readiness | design | path | note |
|---|---:|---:|---|---|
| cubesat | 34 | 36 | 20_dataset/reference_assets/cubesat/images/docs__Orbit_Average_Power_Simulations__image.png | quarantine_or_review |
| cubesat | 35 | 37 | 20_dataset/reference_assets/cubesat/images/docs__MPPT_Prototype__SPV1040_prototype.jpg | quarantine_or_review |
| cubesat | 36 | 38 | 20_dataset/reference_assets/cubesat/images/docs__Solar_Wing_Prototype__wing.PNG | quarantine_or_review |
| cubesat | 36 | 39 | 20_dataset/reference_assets/cubesat/images/docs__Battery_Pack__Battery_Pack_3D.png | quarantine_or_review |
| cubesat | 36 | 39 | 20_dataset/reference_assets/cubesat/images/docs__Battery_Pack__battery_pack_PCB.PNG | quarantine_or_review |
| cubesat | 36 | 39 | 20_dataset/reference_assets/cubesat/images/docs__MPPT_Prototype__SPV1040.pdf | quarantine_or_review |
| cubesat | 36 | 39 | 20_dataset/reference_assets/cubesat/images/docs__PDU__PDUv1_prototype.jpg | quarantine_or_review |
| cubesat | 36 | 39 | 20_dataset/reference_assets/cubesat/metadata/docs__PDU__PDUv1-BOM.csv | quarantine_or_review |
| cubesat | 36 | 39 | 20_dataset/reference_assets/cubesat/images/docs__Solar_Wall_Prototype__solar_wall.PNG | quarantine_or_review |
| cubesat | 38 | 31 | 20_dataset/reference_assets/cubesat/images/hardware__spx__images__arch_spx.png | quarantine_or_review |
| cubesat | 38 | 31 | 20_dataset/reference_assets/cubesat/images/hardware__spy__images__arch_spy.png | quarantine_or_review |
| cubesat | 38 | 31 | 20_dataset/reference_assets/cubesat/images/hardware__spz__images__arch_spz.png | quarantine_or_review |
| cubesat | 38 | 41 | 20_dataset/reference_assets/cubesat/images/docs__Battery_Pack__Battery_Pack.pdf | quarantine_or_review |
| cubesat | 38 | 41 | 20_dataset/reference_assets/cubesat/images/docs__PDU__PDUv1.pdf | quarantine_or_review |
| cubesat | 38 | 41 | 20_dataset/reference_assets/cubesat/images/docs__Solar_Wall_Prototype__Wall.pdf | quarantine_or_review |
| cubesat | 39 | 42 | 20_dataset/reference_assets/cubesat/images/docs__EPS_Prototype_1_cell_level_protection___EPS_prototype_1.jpg | quarantine_or_review |
| cubesat | 39 | 43 | 20_dataset/reference_assets/cubesat/images/docs__Solar_Wing_Prototype__Solar-Wing.pdf | quarantine_or_review |
| cubesat | 40 | 44 | 20_dataset/reference_assets/cubesat/images/docs__LORIS-POW-TEC-01_Power_Subsystem_Document_.pdf | quarantine_or_review |
| cubesat | 41 | 36 | 20_dataset/reference_assets/cubesat/images/doc_project_business_model.pdf | quarantine_or_review |
| cubesat | 41 | 36 | 20_dataset/reference_assets/cubesat/metadata/hardware__README.md | quarantine_or_review |
