# Operability And Solver Readiness Policy - 2026-06-28

The project direction is not cosmetic CAD. Every seed should move toward
operation-aware engineering structure: parts, interfaces, assembly sequence,
load paths, fluid paths, thermal paths, electrical power paths, signal paths,
inspection points, and solver-ready boundary metadata.

## Required Generation Intent

- `cad_brief.operating_principle`: what the subsystem does in the real machine.
- `cad_brief.failure_modes`: likely structural, thermal, fluid, electrical, or assembly failures.
- `cad_brief.inspection_points`: visible geometry or labels that let a reviewer check the design.
- `verify.multiphysics_paths`: `load_path`, `fluid_path`, `thermal_path`, `electrical_path`, `signal_path`.
- `verify.solver_readiness`: readiness for FEA, CFD/OpenFOAM, thermal, and electrical/signal screening.
- `verify.boundary_conditions`: coordinate-referenced fixtures, thermal zones, and pressure faces.

## High-Risk Boundary

High-risk seeds, including propulsion, flight systems, high voltage, pressure
systems, and medical systems, should be physics-grounded and analysis-oriented.
They may describe topology, subsystem roles, interfaces, inspection logic, and
solver inputs. They must not generate unsafe operational recipes, propellant or
ignition procedures, flight qualification instructions, hazardous setpoints, or
certification claims.

## Practical Evolution Path

1. Generate assembly-aware subsystem CAD JSON.
2. Require multiphysics path metadata and solver readiness fields.
3. Run fast structural/thermal/fluid/electrical proxy checks.
4. Promote only strong candidates to heavier solvers such as OpenFOAM.
5. Feed reviewed solver results back into reference feature cards and seed packs.

This keeps the project aimed at real engineering development while preserving a
reviewable safety and legality boundary.
