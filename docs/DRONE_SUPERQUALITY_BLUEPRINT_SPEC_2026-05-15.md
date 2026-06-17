# Drone Superquality Blueprint Spec - 2026-05-15

Drone images and generated outputs must explain layout, mass distribution, wiring, vibration isolation, and propulsion clearance.

## Category Rules

- Show motor/prop clearance, battery retention, avionics stack, cable routing, antenna/GPS placement, and payload interfaces.
- Multirotors must show arm/hub load paths and motor bolt patterns.
- Fixed-wing and VTOL vehicles must show wing spar, control surfaces, servo pockets, battery CG range, and motor thrust line.
- Experimental rotors must show pitch/drive mechanisms, not just decorative rotors.

## Assemblies

| Vehicle | Locked Basis | Must-Show Features | Reject If |
|---|---|---|---|
| `racing_quad_5in` | 5-inch FPV racing quad | X-frame plates, arms, motor bolt patterns, FC/ESC stack, camera tilt, VTX/GPS, battery strap | looks like generic X with no stack/wiring |
| `cinelifter_x8` | DJI Inspire / X8 cinelifter class | coax arms, dual motor mounts, central hub, gimbal damper, landing gear, dual battery tray | misses coaxial/film payload logic |
| `wing_long_range` | long-range flying wing UAV | center pod, spar, ribs, elevons, pusher mount, pitot/GPS boom, camera bay, battery CG slide | no wing structural hierarchy |
| `cyclocopter_demo` | cyclogyro demonstrator | cyclorotor cylinders, blade pitch links, eccentricity servo, pylon supports, skid clearance | rotors drawn as simple propellers |
| `tiltrotor_vtol` | tiltrotor VTOL UAV | tilting nacelles, wing spar, tilt servo/linkage, V-tail, battery bay, payload nose, landing gear | tilt mechanism missing |

## Geometry Requirements

- Use `8-16` operations for part generation.
- Include at least one mounting pattern or datum interface.
- Include cable/airflow/service clearance features where relevant.
- For electronics parts, include connector windows, cooling vents, screw posts, and cable strain relief.

## Promotion Criteria

- Part thumbnails must clearly map to the assembly location.
- 3-axis images must show propulsion geometry and mass layout.
- Generated output must include wiring/mounting cues, not only structural shells.

