# Marine Superquality Blueprint Spec - 2026-05-15

Marine images and generated outputs must explain hydrodynamics, sealing, pressure, buoyancy, corrosion, and service access.

## Category Rules

- Show wet/dry boundaries, seals, pressure housings, cable glands, fairings, buoyancy/ballast, and corrosion protection.
- Underwater parts must show depth-rated closure and penetrator logic.
- Surface vessels must show hull/deck separation, drainage, sensor mast, power bay, and propulsion pod layout.
- Avoid generic boat/submarine silhouettes without systems.

## Assemblies

| Vehicle | Locked Basis | Must-Show Features | Reject If |
|---|---|---|---|
| `rov_inspection` | BlueROV2 / inspection ROV | open frame, pressure tube, thrusters, buoyancy blocks, camera dome, lights, manipulator, tether box | no pressure/seal/thruster logic |
| `usv_autonomous` | solar-electric survey ASV | catamaran hulls, cross deck, solar panels, pod motors, rudders, mast, wet/dry payload bay | just a hull outline |
| `underwater_glider` | Slocum/Seaglider class | pressure hull, wings, buoyancy pump, sliding battery, roll mass, tail antenna, sensor bay, drop weight | no buoyancy/CG system |
| `research_submarine` | DSV Alvin class | pressure hull, viewsphere, ballast, thruster pods, LARS frame, life support, science basket | lacks pressure hull hierarchy |
| `wave_glider_asv` | Wave Glider class | surface float, submerged glider, tether, wave fins, solar deck, sensor bay, comm mast, battery | no tethered two-body architecture |

## Geometry Requirements

- Include at least one seal or pressure boundary feature.
- Include cable/tether/penetrator details when relevant.
- Include hydrodynamic direction or flow/fairing cue.
- Include access hatch, service panel, or lift/recovery point.

## Promotion Criteria

- 2D view distinguishes wet/dry/pressure regions.
- 3D view shows fairing/pressure/housing hierarchy.
- Generated labels identify seals, penetrators, buoyancy, or hull interfaces.

