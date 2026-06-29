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

## Local Ingest

If a browser download is easier, download files manually and ingest the folder:

```powershell
python tools/crawl_reference_assets.py --ingest-local "C:\Downloads\cad_refs" --seed robot_arm
```

## Verify

```powershell
python tools/reference_asset_inventory.py
```
