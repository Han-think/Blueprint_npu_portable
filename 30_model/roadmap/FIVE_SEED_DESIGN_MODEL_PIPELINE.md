# Five-Seed Design Model Pipeline

This document fixes the current Blueprint design-model direction around five seed targets only.

The goal is not to keep adding many objects. The goal is to use five different engineering structures as stable data axes, accumulate high-quality design-thinking examples, and then use those examples to train or tune a small model that can produce its own structured design judgment.

## Fixed Seed Set

Use only these five seeds for the first design-model cycle:

| Seed | Target asset | Main reasoning axis | Current examples |
|---|---|---|---|
| CubeSat Redesign V1 | `cubesat_3u` | static frame, panels, interfaces, maintenance access | 25 |
| Tiltrotor Drone Redesign V1 | `tiltrotor_vtol` | moving nacelles, tilt axis, battery, wiring, service pods | 25 |
| Robot Arm Redesign V1 | `arm_6dof` | J1-J6 axes, joint cartridges, cable spine, tool flange | 25 |
| Small Launch Vehicle Redesign V1 | `small_launch_vehicle` | staged cutaway, tank/engine display modules, flow readability | 25 |
| Long-Range Recon Wing Redesign V1 | `wing_long_range` | sensor bay, mission payload, CG rail, spar datum, elevons | 25 |

Together these provide 125 first-pass examples. They are intentionally small and focused.

## What The Model Should Learn

The model should learn design judgment, not just shape generation.

The repeated output pattern is:

```text
existing structure
-> problem
-> constraint
-> engineering reasoning
-> integrate / keep separate / reject / risk classification
-> redesign proposal
-> reduced steps
-> retained service access
-> verification checklist
```

The first useful model is a design-judgment assistant. It should classify and propose, not generate final STL files.

Expected reasoning skills:

- decide whether a part can be integrated
- reject integration that blocks service or inspection
- preserve datum, alignment, CG, cable, flow, or axis readability
- identify over-integration risk
- produce verification checks tied to the design package
- keep unsafe or out-of-scope domains at educational mockup level

## Data Accumulation Rule

Do not add new target vehicles during the first cycle.

Grow only these data files:

```text
data/blueprint/cubesat_design_thinking_v1.jsonl
data/blueprint/tiltrotor_design_thinking_v1.jsonl
data/blueprint/robot_arm_design_thinking_v1.jsonl
data/blueprint/small_launch_vehicle_design_thinking_v1.jsonl
data/blueprint/long_range_recon_wing_design_thinking_v1.jsonl
```

Add examples in balanced batches:

- success: integration with guardrail
- failure: over-integration or blocked service access
- risk: datum, CG, flow, cable, hinge, printability, or readability loss
- safety-boundary rejection where the domain could drift into unsafe real-world use

Keep each row compact and structured. The model should see the same judgment pattern repeatedly.

## Training Structure

Use a staged path:

1. Validate every seed package and JSONL file.
2. Combine the five JSONL files into a small training candidate.
3. Split examples into train/eval sets without mixing line formats.
4. Train or tune the model to output design judgment first.
5. Evaluate model output against held-out examples.
6. Only after judgment output is stable, connect the model output back to `schema_v6` design packages.

The first training target should be:

```text
input: existing_structure + problem + constraint
output: reasoning.classification + reasoning.rule + proposal + verification
```

The later training target can include:

```text
input: existing BOM + redesign goal
output: partial design package sections
```

Do not start with full end-to-end STL or CAD generation.

## Model Output Review

After a model is trained or tuned, evaluate its output as design data.

Required checks:

- classification is one of the known judgment classes
- proposal preserves required service access
- verification checks match the constraint
- unsafe or out-of-scope requests are rejected or reframed as educational mockups
- no seed drifts into real flight, weapon, propulsion, industrial payload, or certification guidance
- output can be mapped back into `schema_v6_blueprint` fields

The model is considered useful only when it improves the design-package authoring loop:

```text
human seed package
-> generated judgment examples
-> validation
-> model learning
-> model design judgment output
-> human review
-> stronger package/data examples
```

## Stop Rule

Do not expand to new seeds until:

- the five current seed datasets are larger and balanced
- validation scripts pass
- a small model can classify success/failure/risk cases consistently
- model output can be reviewed against the five design packages
- the next seed would add a genuinely new engineering reasoning axis

For now, five focused seeds are better than many shallow seeds.
