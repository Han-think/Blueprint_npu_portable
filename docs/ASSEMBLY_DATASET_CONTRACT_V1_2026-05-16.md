# Assembly Dataset Contract v1

Date: 2026-05-16

## Purpose

This contract defines the design-data structure for assembly-primary learning data. The goal is not to collect isolated part sketches, but to produce integrated assembly bundles where every subsystem carries function, physics path, interfaces, internal features, manufacturable geometry, and review feedback.

## Core Philosophy

Successful products should be decomposed into engineering thought units, then recomposed into simpler, more integrated additive-manufacturing structures.

Target direction:

```text
successful product basis
→ function and physics-path understanding
→ subsystem role and interface graph
→ internal feature ontology
→ coordinate-bearing geometry
→ manufacturable integrated structure
→ score / review / loop feedback
→ curated learning data
```

## Primary Data Unit

The primary training unit is an assembly bundle.

```text
assembly bundle
  vehicle
  dataset_contract
  fixed BOM subsystems
  subsystem blueprints
  engineering scorecard
  curation decision
  loop lineage
```

Single-part outputs are auxiliary references only. They may help prompt/debug the system, but they are not the default base training unit.

## Required Reasoning Chain

Every assembly datum should preserve this chain:

```text
function
→ physics_path
→ subsystem_role
→ interfaces
→ internal_features
→ geometry_ops
→ manufacturing_strategy
→ verification
→ loop_feedback
```

## Internal Pipeline Stages

The UI may expose this as one assembly generation action, but the learning datum should preserve the staged internal factory flow:

```text
P0 subsystem plan
→ S1 brief and part_tree
→ S2 coordinate-bearing geometry_ops
→ S3 verification and risk
→ S4 print/manufacturing profile
→ engineering scorecard
→ human curation
→ loop regeneration
```

`P0 subsystem plan` is the bridge between product understanding and CAD-like output. It should define subsystem role, physics paths, adjacent interfaces, internal feature targets, integration opportunities, and verification focus before any geometry is emitted.

Coverage rule: every fixed BOM subsystem in every Full Assembly template must carry a P0 plan. If the model fails to produce a usable plan, the application should attach a deterministic local fallback plan so the assembly bundle still preserves the full reasoning chain.

## Assembly Fields

- `assembly_intent`: what the complete product is trying to do
- `coordinate_convention`: X/Y/Z convention and local datum rule
- `physics_paths`: force, flow, thermal, electrical, motion, pressure, or human-interface paths
- `subsystems`: fixed BOM parts inside the assembly
- `interfaces`: how subsystems connect or exchange force/flow/power/data
- `integration_opportunities`: functions that can be merged into printable structures
- `simulation_hooks`: future CFD/FEA/thermal boundary placeholders

## Subsystem Contract

Each subsystem part should target:

- `5-9` internal child features in `part_tree` when meaningful
- `12-24` coordinate-bearing `geometry_ops`
- at least `3` adjacent-module interfaces or mounting datums
- at least `3` negative/service features such as holes, pockets, ducts, channels, ports, vents, drains, or access cuts
- traceability between important `part_tree` child names and `geometry_ops` ids/targets

## Feature Ontology

Common feature types:

- structure: shell, body, spar, rib, frame, stringer, stiffener, gusset
- interface: flange, bolt circle, clamp band, datum pin, mount pad, hardpoint
- flow: inlet, outlet, duct, channel, throat, diffuser, manifold, port
- thermal: liner, insulation, cooling jacket, heat shield, radiator, thermal strap
- motion: joint axis, bearing seat, hinge, actuator clevis, reducer interface, hard stop
- service: access cover, inspection port, drain, vent, removable insert, label
- electrical/data: harness channel, connector panel, cable gland, sensor pocket, grounding boss
- human interface: trim line, padding, strap anchor, soft liner groove, safety stop

## Additive-Manufacturing Aim

Use 3D printing/additive manufacturing to reduce unnecessary assembly complexity:

- merge ducts, brackets, channels, ribs, cable paths, and sensor mounts when feasible
- create internal flow/cooling/drainage routes directly in geometry
- reduce leak points and fastener count
- preserve service covers where inspection, wear, cleaning, or safety requires separability
- optimize for mass, cost, stiffness, thermal safety, flow efficiency, and maintainability

## Future Simulation Hooks

CFD-ready fields:

- flow path
- inlet/outlet
- walls
- obstructions
- pressure/velocity/temperature boundary conditions

FEA-ready fields:

- load path
- fixed datums
- force or pressure loads
- material
- wall thickness
- stress concentration features

Thermal-ready fields:

- heat source
- cooling path
- thermal boundary
- insulation/liner
- radiator or conduction path

## Curation Rule

Only kept assembly bundles should enter the primary training set. Rejects and auxiliary single-part outputs remain useful as evaluation, debugging, and contrastive material, but should not be merged into the base set without explicit labeling.
