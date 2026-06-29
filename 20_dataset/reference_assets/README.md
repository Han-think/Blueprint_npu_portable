# Reference Assets

This folder stores lawful CAD, drawing, and image references used to guide
Blueprint engineering generation. It is separate from `20_dataset/sources`
because PDFs/books explain engineering rules, while this folder teaches shape,
layout, stations, interfaces, and assembly detail.

The goal is not to copy a real vehicle. The goal is to derive reusable design
grammar:

- silhouette and station layout
- rib/spar/frame/bay decomposition
- service access and inspection features
- interface and datum placement
- plausible internal/external drawing density

## Layout

```text
20_dataset/reference_assets/
  sources.json
  _index.jsonl
  _incoming/
  _quarantine/
  _cache/

  long_range_recon_wing/
    images/
    cad/
    metadata.json
    feature_labels.json
```

## Accepted Inputs

- CAD: `.step`, `.stp`, `.iges`, `.igs`, `.stl`, `.obj`, `.3mf`, `.fcstd`, `.scad`, `.vsp3`
- Drawings/images: `.svg`, `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.pdf`
- Metadata: `.json`, `.jsonl`, `.csv`, `.txt`, `.md`

## Source Rules

Use only sources with a clear lawful basis:

- official public-domain/open-government repositories
- open-source project repositories with an explicit license
- research datasets with published download terms
- user-owned/manual files placed into `_incoming`

Avoid automated scraping of login-only CAD libraries or sites whose terms forbid
bulk download or model training reuse. Put uncertain files in `_quarantine` until
their license is reviewed.

## Workflow

Dry-run source discovery:

```powershell
python tools/crawl_reference_assets.py --dry-run
```

Download from the allowlisted manifest:

```powershell
python tools/crawl_reference_assets.py --download --limit 20
```

Ingest local files already downloaded by the user:

```powershell
python tools/crawl_reference_assets.py --ingest-local "C:\path\to\cad-folder" --seed long_range_recon_wing
```

Rebuild and validate the asset index:

```powershell
python tools/reference_asset_inventory.py
```

The generated `_index.jsonl` is the file future generation/scorecard code should
read first. Do not point model prompts directly at random downloaded files.
