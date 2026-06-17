# Medical Superquality Blueprint Spec - 2026-05-15

Medical and assistive device images must explain human interface, safety, adjustability, cleaning, cable/actuator routing, and controlled motion.

This project does not produce clinical instructions. The images are representative engineering training artifacts.

## Category Rules

- Show soft-contact surfaces, rounded edges, adjustment slots, strain relief, safety stops, and serviceable modules.
- Human-worn parts must show straps/cuffs, hinge alignment, sensors, and load transfer.
- Surgical/implant-adjacent parts must show sterile interfaces, compact routing, and controlled motion axes.
- Avoid generic organic shapes or cosmetic shells with no engineering interface.

## Assemblies

| Vehicle | Locked Basis | Must-Show Features | Reject If |
|---|---|---|---|
| `myoelectric_hand` | multi-articulating prosthetic hand | palm shell, finger links, tendon/cable routing, motors, socket electronics, EMG interface, tactile pads | hand silhouette only |
| `powered_afo` | powered ankle-foot orthosis | shin cuff, ankle actuator, footplate, linkage, sensors, straps, safety stop, battery/control pod | brace shape with no hinge/actuator logic |
| `surgical_robot_arm` | Da Vinci-class MIS arm | RCM linkage, sterile drape interface, instrument shaft, wrist, cable drive, trocar alignment, tool changer | no RCM/sterile interface |
| `cochlear_implant` | receiver/electrode system | receiver coil, magnet, stimulator package, lead strain relief, electrode curl, connector transition | simple coil/lead drawing |
| `powered_exoskeleton` | ReWalk/Ekso lower-body exoskeleton | hip/knee/ankle actuators, braces, backpack controller, batteries, foot sensors, straps | humanoid outline only |

## Geometry Requirements

- Include contact/comfort features: pads, cuffs, straps, rounded reliefs, or soft liners.
- Include safety/control features: stops, sensors, cable routing, covers, service access.
- Include at least one human-alignment datum: joint axis, socket plane, foot centerline, trocar/RCM point, or electrode array direction.

## Promotion Criteria

- 2D view must reveal human-device interface.
- 3D view must not be only an outer shell.
- Generated output must label safety, contact, and actuation features.

