# Run Reference Crawl

Always start with dry-run. Downloads are blocked unless `--download` is present.

## Seed Commands

CubeSat:

```powershell
python tools/crawl_reference_assets.py --dry-run --seed cubesat --url "https://projecthub.arduino.cc/petros_mpla/helioscube-eleni-a-cost-effective-open-source-1u-cubesat-for-microgravity-research-9d78f4" --limit 30
```

Long-range recon wing:

```powershell
python tools/crawl_reference_assets.py --dry-run --seed long_range_recon_wing --url "https://airshow.openvsp.org/" --limit 30
```

Tiltrotor:

```powershell
python tools/crawl_reference_assets.py --dry-run --seed tiltrotor --url "https://airshow.openvsp.org/" --limit 30
```

Robot arm:

```powershell
python tools/crawl_reference_assets.py --dry-run --seed robot_arm --url "https://sites.google.com/view/im2-humanoid-arm" --limit 30
```

Haptic glove:

```powershell
python tools/crawl_reference_assets.py --dry-run --seed haptic_glove --url "https://do-glove.github.io/" --limit 30
```

GitHub repo mode is better when a project page hides CAD behind repository links:

```powershell
python tools/crawl_reference_assets.py --dry-run --seed haptic_glove --github-repo TEA-Lab/DOGlove --cad-only --limit 80
python tools/crawl_reference_assets.py --dry-run --seed robot_arm --github-repo iMSquared/armada --cad-only --limit 80
```

Small launch vehicle:

```powershell
python tools/crawl_reference_assets.py --dry-run --seed small_launch_vehicle --url "https://science.nasa.gov/3d-resources/" --limit 30
```

## Download

After dry-run looks clean, add `--download`.

```powershell
python tools/crawl_reference_assets.py --download --seed haptic_glove --url "https://do-glove.github.io/" --limit 30
python tools/crawl_reference_assets.py --download --seed haptic_glove --github-repo TEA-Lab/DOGlove --cad-only --limit 80
```

Downloaded assets are marked `blocked_until_license_review` by default. Only use
`--allow-training-use` after license review.

## Engineering Expansion Seeds

The following sources were used as conservative reference-only CAD grammar for
new engineering seeds. Keep these assets blocked until license review.

Gearbox reducer / rotating machinery:

```powershell
python tools/crawl_reference_assets.py --dry-run --seed gearbox_reducer --github-repo openscad/MCAD --include-regex "(?i)(bearing|gear|involute|linear_bearing|motors|screw|stepper).*\.scad$" --exclude-regex "(?i)(bitmap|lego|test|example)" --limit 20
python tools/crawl_reference_assets.py --download --seed gearbox_reducer --github-repo openscad/MCAD --include-regex "(?i)(bearing|gear|involute|linear_bearing|motors|screw|stepper).*\.scad$" --exclude-regex "(?i)(bitmap|lego|test|example)" --limit 20
```

Hydraulic manifold block/ports/fasteners:

```powershell
python tools/crawl_reference_assets.py --dry-run --seed hydraulic_manifold --github-repo openscad/MCAD --include-regex "(?i)(boxes|polyholes|nuts_and_bolts|metric_fastners|regular_shapes|shapes|hardware).*\.scad$" --exclude-regex "(?i)(bitmap|lego|test|example)" --limit 20
python tools/crawl_reference_assets.py --download --seed hydraulic_manifold --github-repo openscad/MCAD --include-regex "(?i)(boxes|polyholes|nuts_and_bolts|metric_fastners|regular_shapes|shapes|hardware).*\.scad$" --exclude-regex "(?i)(bitmap|lego|test|example)" --limit 20
```

Battery pack module:

```powershell
python tools/crawl_reference_assets.py --dry-run --seed battery_pack_module --github-repo nophead/NopSCADlib --include-regex "(?i)(battery|batteries|cell|holder|box|pcb_mount|cable|connector|printed_box|fuseholder).*\.scad$" --exclude-regex "(?i)(examples|stls|test|all\.scad)" --limit 30
python tools/crawl_reference_assets.py --download --seed battery_pack_module --github-repo nophead/NopSCADlib --include-regex "(?i)(battery|batteries|cell|holder|box|pcb_mount|cable|connector|printed_box|fuseholder).*\.scad$" --exclude-regex "(?i)(examples|stls|test|all\.scad)" --limit 30
```

CNC axis carriage:

```powershell
python tools/crawl_reference_assets.py --dry-run --seed cnc_axis_carriage --github-repo nophead/NopSCADlib --include-regex "(?i)(linear|rail|bearing|screw|stepper|motor|pulley|drag_chain|carriers|pcb_mount).*\.scad$" --exclude-regex "(?i)(examples|stls|test|all\.scad)" --limit 40
python tools/crawl_reference_assets.py --download --seed cnc_axis_carriage --github-repo nophead/NopSCADlib --include-regex "(?i)(linear|rail|bearing|screw|stepper|motor|pulley|drag_chain|carriers|pcb_mount).*\.scad$" --exclude-regex "(?i)(examples|stls|test|all\.scad)" --limit 40
```

Underwater sealed sensor housing:

```powershell
python tools/crawl_reference_assets.py --dry-run --seed underwater_sealed_sensor_housing --github-repo nophead/NopSCADlib --include-regex "(?i)(o_ring|cable_grommets|box|camera_housing|gasket|seal|tube|printed_box).*\.scad$" --exclude-regex "(?i)(examples|stls|test|all\.scad)" --limit 25
python tools/crawl_reference_assets.py --download --seed underwater_sealed_sensor_housing --github-repo nophead/NopSCADlib --include-regex "(?i)(o_ring|cable_grommets|box|camera_housing|gasket|seal|tube|printed_box).*\.scad$" --exclude-regex "(?i)(examples|stls|test|all\.scad)" --limit 25
```

## Empty Seeds — Need CAD References

These 5 seeds have metadata.json but no CAD files yet. Sources are in sources.json.

Inline 6 Engine (Gasoline + Diesel):

```powershell
# FreeCAD community library — engine/piston/valve related
python tools/crawl_reference_assets.py --dry-run --seed inline_6_engine_gasoline --github-repo FreeCAD/FreeCAD-library --include-regex "(?i)(engine|piston|valve|bearing|shaft|flange|gasket).*\.(step|stp|fcstd|stl)$" --exclude-regex "(?i)(logo|icon|test|thumbnail)" --limit 30
python tools/crawl_reference_assets.py --dry-run --seed inline_6_engine_diesel --github-repo FreeCAD/FreeCAD-library --include-regex "(?i)(engine|diesel|turbo|piston|valve|bearing|pump).*\.(step|stp|fcstd|stl)$" --exclude-regex "(?i)(logo|icon|test|thumbnail)" --limit 30
# MCAD for parametric parts
python tools/crawl_reference_assets.py --dry-run --seed inline_6_engine_gasoline --github-repo openscad/MCAD --include-regex "(?i)(bearing|motor|shaft|screw).*\.scad$" --exclude-regex "(?i)(bitmap|lego|test)" --limit 15
```

Centrifugal Pump:

```powershell
# OpenFOAM tutorial geometries — pump/impeller/mixer
python tools/crawl_reference_assets.py --dry-run --seed centrifugal_pump --github-repo OpenFOAM/OpenFOAM-dev --include-regex "(?i)(pump|impeller|mixer|rotor).*\.(stl|obj|step)$" --exclude-regex "(?i)(test|doc|logo)" --limit 20
# FreeCAD library
python tools/crawl_reference_assets.py --dry-run --seed centrifugal_pump --github-repo FreeCAD/FreeCAD-library --include-regex "(?i)(pump|impeller|volute|flange).*\.(step|stp|fcstd|stl)$" --limit 20
```

Liquid Cold Plate:

```powershell
# OpenFOAM conjugate heat transfer tutorials
python tools/crawl_reference_assets.py --dry-run --seed liquid_cold_plate --github-repo OpenFOAM/OpenFOAM-dev --include-regex "(?i)(heat|channel|plate|conjugate|cold).*\.(stl|obj|step)$" --limit 20
# Elmer FEM thermal examples
python tools/crawl_reference_assets.py --dry-run --seed liquid_cold_plate --github-repo ElmerCSC/elmerfem --include-regex "(?i)(heat|thermal|convection|plate).*\.(stl|step|stp|geo)$" --limit 15
```

Liquid Rocket Engine (Academic):

```powershell
# OpenRocket motor/component data
python tools/crawl_reference_assets.py --dry-run --seed liquid_rocket_engine_academic --github-repo openrocket/openrocket --include-regex "(?i)(motor|engine|nozzle|thrust|chamber|component).*\.(csv|json|xml|stl|step)$" --exclude-regex "(?i)(test|doc|gradle|maven|logo)" --limit 25
# NASA 3D Resources — rocket models
python tools/crawl_reference_assets.py --dry-run --seed liquid_rocket_engine_academic --url "https://science.nasa.gov/3d-resources/" --limit 20
```

## Manual Download Targets (GrabCAD/NTRS)

For seeds where automated crawl returns too few results, download manually:

| Seed | Search Query | Source |
|------|-------------|--------|
| inline_6_engine_gasoline | "inline 6 engine cutaway STEP" | GrabCAD |
| inline_6_engine_diesel | "inline 6 diesel engine turbo cutaway STEP" | GrabCAD |
| centrifugal_pump | "centrifugal pump cutaway impeller STEP" | GrabCAD |
| liquid_cold_plate | "cold plate liquid cooling heat sink STEP" | GrabCAD |
| liquid_rocket_engine_academic | "rocket engine nozzle cutaway academic" | GrabCAD + NTRS |

Then ingest:

```powershell
python tools/crawl_reference_assets.py --ingest-local "C:\Downloads\engine_refs" --seed inline_6_engine_gasoline
python tools/crawl_reference_assets.py --ingest-local "C:\Downloads\pump_refs" --seed centrifugal_pump
```

## Existing Seed Enrichment

Existing seeds that need more diversity beyond current SCAD/STL:

```powershell
# cubesat — add solar panel, ADCS, PCB stack references
python tools/crawl_reference_assets.py --dry-run --seed cubesat --github-repo polaris-labs/PROVES-PCB --cad-only --limit 20
# tiltrotor — add nacelle tilt mechanism
python tools/crawl_reference_assets.py --dry-run --seed tiltrotor --github-repo PX4/PX4-Autopilot --include-regex "(?i)(tilt|nacelle|vtol|frame).*\.(stl|step|obj)$" --limit 15
# long_range_recon_wing — add airframe structure
python tools/crawl_reference_assets.py --dry-run --seed long_range_recon_wing --github-repo ArduPilot/ardupilot --include-regex "(?i)(frame|wing|fuselage|airframe).*\.(stl|step|obj)$" --limit 15
```

## Local Ingest

If a browser download is easier, download files manually and ingest the folder:

```powershell
python tools/crawl_reference_assets.py --ingest-local "C:\Downloads\cad_refs" --seed robot_arm
```

## Verify

```powershell
python tools/reference_asset_inventory.py
```
