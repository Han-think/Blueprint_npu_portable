# Engineering Expansion Seeds - 2026-06-27

This expansion adds broad engineering-design seed coverage for headless
`generate_batch.py` and RunPod/vLLM production. The goal is not to train on raw
CAD directly, but to teach reusable engineering grammar through BOMs,
PASS-0 skeleton packs, subsystem micro-packs, and prompt-safe reference feature
cards.

## Added Seeds

| Seed | Main Grammar |
| --- | --- |
| `inline_6_engine_gasoline` | block, cranktrain, head/valvetrain, manifolds, lubrication/cooling, fuel/ignition harness, accessory mounts |
| `inline_6_engine_diesel` | reinforced block/head, diesel cranktrain, common rail reference structure, turbo air/exhaust reference structure, oil/cooling, gear timing, mounts |
| `centrifugal_pump` | volute, impeller, shaft, bearing frame, mechanical seal, pipe flanges, baseplate |
| `hydraulic_manifold` | P/T/A/B ports, cross-drilled galleries, cartridge valves, relief/check sections, sensor/test ports |
| `battery_pack_module` | cell carrier, busbar cover, BMS bay, cooling interface, enclosure, disconnect, isolation plates |
| `liquid_cold_plate` | serpentine channels, manifold cap, gasket track, power-module pads, leak test/drain ports |
| `cnc_axis_carriage` | carriage plate, linear rails, ball screw, servo mount, home/limit sensors, way covers, lubrication |
| `gearbox_reducer` | split housing, input/intermediate/output shafts, gear mesh, bearings/seals, lubrication, mounts |
| `underwater_sealed_sensor_housing` | pressure shell, O-ring caps, cable gland, electronics tray, marine cradle, leak test labels |
| `liquid_rocket_engine_academic` | academic liquid propulsion system grammar: chamber/nozzle, injector taxonomy, regenerative cooling, feed architecture, turbomachinery, instrumentation, controls, thrust-frame load path |

## Safety / Boundary Notes

- Engine seeds are conceptual engineering assemblies. They do not claim
  certified working engine performance, emissions compliance, fatigue life, or
  manufacturable production readiness.
- `battery_pack_module` is a no-live-energy training/reference structure seed. It should not
  generate live pack assembly instructions or safety certification claims.
- `liquid_rocket_engine_academic` is an academic, non-buildable propulsion
  study seed. Do not generate buildable engine dimensions, propellant handling
  or ignition procedures, chamber pressure/thrust sizing, injector hole sizing,
  turbopump performance, test-stand operating steps, or flight-use instructions.
- All new reference cards start as `needs_reference_crawl` or
  `blocked_until_license_review` until real source/license review is complete.

## Production Path

Start with generation-only smoke batches:

```bash
BP_LM_URL=http://127.0.0.1:8000/v1 \
BP_LM_MODEL=Qwen/Qwen2.5-14B-Instruct \
BP_BATCH_PARALLEL=13 \
BP_WORKERS=1 \
BP_SKIP_AUDIT=1 \
python generate_batch.py --seeds inline_6_engine_gasoline,centrifugal_pump,battery_pack_module --per-seed 2
```

Then audit a small reviewed subset through CAD/FoS separately. Do not run the
CAD audit at 13-way parallel until output-folder isolation and CPU/I/O limits
are confirmed.

## Files

- `20_dataset/seed_vehicles.json`: new vehicle BOMs
- `20_dataset/packs/<seed>/skeleton.json`: PASS-0 subsystem coverage
- `20_dataset/packs/<seed>/<subsystem>.json`: PASS-1 micro-packs
- `20_dataset/reference_assets/seed_reference_targets.json`: source candidates
- `20_dataset/reference_assets/reference_feature_cards.jsonl`: prompt-safe cards
- `tools/bootstrap_engineering_expansion.py`: reproducible bootstrap script
