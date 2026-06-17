# Robotics Superquality Blueprint Spec - 2026-05-15

Robotics images and generated outputs must explain motion, torque paths, cable paths, sensors, and serviceable modules.

## Category Rules

- Show joint axes, bearings, reducers, encoders, cable routing, actuator interfaces, and end stops.
- Links must show hollow sections, mounting flanges, weight relief, and datum faces.
- Mobile robots must show ground contact, suspension/compliance, sensor placement, and power/control bays.
- End effectors must show tool interfaces and utility pass-throughs.

## Assemblies

| Vehicle | Locked Basis | Must-Show Features | Reject If |
|---|---|---|---|
| `arm_6dof` | UR-class cobot | J1-J6 axes, joint housings, link tubes, wrist stack, tool flange, cable spine | no joint axis/encoder/reducer cues |
| `mars_rover` | Perseverance-class rover | rocker-bogie suspension, six wheels, body deck, mast, arm, HGA, science payload | wheels/body only with no suspension logic |
| `quadruped_walker` | Spot/ANYmal class | hip/knee actuators, thigh/shin links, body battery, sensor head, foot pads, compliance | legs lack actuator axis hierarchy |
| `delta_parallel_robot` | industrial delta robot | fixed base, three upper arms, parallelogram rods, moving platform, tool flange, guard frame | no parallel linkage geometry |
| `humanoid_biped` | humanoid research robot | pelvis/torso, head/neck, arms, hands, hip/knee/ankle chains, battery/computer backpack | human silhouette only |

## Geometry Requirements

- Include at least one explicit rotational or translational axis.
- Include bearing/reducer/encoder or actuator features.
- Include cable or utility routing.
- Include mounting datum or calibration marks.

## Promotion Criteria

- 2D preview must reveal kinematic chain.
- 3D view must show separable joint/link components.
- Generated output must identify axes and interfaces in labels.

