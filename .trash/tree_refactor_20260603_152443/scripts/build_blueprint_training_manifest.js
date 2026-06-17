const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const MINIMAL = path.join(ROOT, 'Minimal.html');
const EVAL_DOC = path.join(ROOT, 'docs', 'BLUEPRINT_IMAGE_MATCH_EVALUATION_2026-05-15.md');
const OUT_DIR = path.join(ROOT, 'data', 'blueprint');
const OUT_ALL = path.join(OUT_DIR, 'blueprint_image_training_manifest_2026-05-15.jsonl');
const OUT_SEED = path.join(OUT_DIR, 'blueprint_image_training_seed_2026-05-15.jsonl');
const OUT_SUMMARY = path.join(OUT_DIR, 'blueprint_image_training_manifest_summary_2026-05-15.json');

const html = fs.readFileSync(MINIMAL, 'utf8');
const evalDoc = fs.readFileSync(EVAL_DOC, 'utf8');

function extractConst(name, endNeedle) {
  const start = html.indexOf(`const ${name}`);
  if (start < 0) throw new Error(`Missing ${name}`);
  const end = html.indexOf(endNeedle, start);
  if (end < 0) throw new Error(`Missing end marker for ${name}`);
  const code = html.slice(start, end);
  return vm.runInNewContext(`${code}\n${name};`, {
    C: {
      lox: '#9fd3ff',
      inter: '#89ffa8',
      risk: '#ff9fb5',
      halo: '#caa9ff',
      lh2: '#ffd39f',
    },
  });
}

function cleanCell(value) {
  return String(value || '')
    .trim()
    .replace(/^`|`$/g, '')
    .replace(/\\\|/g, '|')
    .trim();
}

function parseEvaluationRows(markdown) {
  const rows = new Map();
  const lines = markdown.split(/\r?\n/);

  for (const line of lines) {
    if (!line.startsWith('| ')) continue;
    if (line.includes('---')) continue;
    if (line.includes('| Category | Vehicle |')) continue;

    const cells = line
      .slice(1, -1)
      .split('|')
      .map(cleanCell);

    if (cells.length !== 6) continue;
    const [category, vehicleId, axisQuality, partImages, readiness, recommendation] = cells;
    if (!vehicleId || !readiness) continue;
    if (!['train_base_ready', 'train_aug_ready', 'hold_for_spec', 'superquality_candidate'].includes(readiness)) continue;

    rows.set(vehicleId, {
      category,
      vehicle_id: vehicleId,
      axis_quality: axisQuality,
      part_images: partImages,
      training_readiness: readiness,
      recommendation,
    });
  }

  return rows;
}

function presetRef(preset) {
  return Array.isArray(preset) ? preset.join('/') : '';
}

function rel(...parts) {
  return parts.join('/').replace(/\\/g, '/');
}

function existsRel(relativePath) {
  return fs.existsSync(path.join(ROOT, relativePath));
}

function recordForPart(catKey, vehicle, part, partIndex, evalRow) {
  const assemblyPartPath = rel('vendor', 'img', 'assembly_parts', vehicle.id, `${part.id}.svg`);
  const presetPath = Array.isArray(part.preset)
    ? rel('vendor', 'img', 'presets', part.preset[0], part.preset[1], `${part.preset[2]}.svg`)
    : '';
  const exteriorPath = rel('vendor', 'img', `${vehicle.id}_exterior.svg`);
  const internalPath = rel('vendor', 'img', `${vehicle.id}_internal.svg`);
  const topPath = rel('vendor', 'img', `${vehicle.id}_top.svg`);
  const hasAssemblyPartAsset = existsRel(assemblyPartPath);

  return {
    schema: 'blueprint_image_training_manifest.v1',
    source_date: '2026-05-15',
    category_key: catKey,
    category: evalRow.category,
    vehicle_id: vehicle.id,
    vehicle_label: vehicle.label,
    representative_basis: vehicle.wikiTitle || '',
    vehicle_description: vehicle.desc || '',
    vehicle_material: vehicle.material || '',
    vehicle_process: vehicle.process || '',
    vehicle_mass: vehicle.mass || '',
    vehicle_envelope: vehicle.envelope || '',
    asset_kind: 'assembly_part',
    part_index: partIndex + 1,
    part_id: part.id,
    part_label: part.label,
    part_spec: part.spec || '',
    preset_ref: presetRef(part.preset),
    asset_path: hasAssemblyPartAsset ? assemblyPartPath : presetPath,
    assembly_part_asset_path: assemblyPartPath,
    assembly_part_asset_exists: hasAssemblyPartAsset,
    preset_asset_path: presetPath,
    preset_asset_exists: presetPath ? existsRel(presetPath) : false,
    axis_assets: {
      exterior: exteriorPath,
      internal: internalPath,
      top: topPath,
    },
    axis_assets_exist: {
      exterior: existsRel(exteriorPath),
      internal: existsRel(internalPath),
      top: existsRel(topPath),
    },
    axis_quality: evalRow.axis_quality,
    part_quality: 'master',
    training_readiness: evalRow.training_readiness,
    recommendation: evalRow.recommendation,
    instruction: 'Create or evaluate a representative engineering blueprint image for this assembly part while respecting the vehicle context and quality label.',
    input: {
      vehicle: `${vehicle.label} (${vehicle.id})`,
      representative_basis: vehicle.wikiTitle || '',
      part: `${part.label} (${part.id})`,
      part_spec: part.spec || '',
      preset_ref: presetRef(part.preset),
      axis_quality: evalRow.axis_quality,
      training_readiness: evalRow.training_readiness,
    },
    output: {
      expected_asset_path: hasAssemblyPartAsset ? assemblyPartPath : presetPath,
      desired_style: 'dark technical blueprint SVG with concise functional labels, visible structural hierarchy, and category-consistent engineering detail',
      quality_gate: evalRow.training_readiness === 'train_base_ready'
        ? 'usable for high-confidence base/adaptor seed training'
        : 'use only as augmentation or weak-label data until category spec and 3-axis master review are complete',
    },
  };
}

function sortRecord(a, b) {
  return a.category_key.localeCompare(b.category_key)
    || a.vehicle_id.localeCompare(b.vehicle_id)
    || a.part_index - b.part_index;
}

const VEHICLE_TEMPLATES = extractConst(
  'VEHICLE_TEMPLATES',
  '// ═══════════════════════════════════════════════════════════════════════════\n// VEHICLE_SCHEMATICS'
);
const evalRows = parseEvaluationRows(evalDoc);

const records = [];
const missingEvalRows = [];

for (const [catKey, vehicles] of Object.entries(VEHICLE_TEMPLATES)) {
  for (const vehicle of vehicles) {
    const evalRow = evalRows.get(vehicle.id);
    if (!evalRow) {
      missingEvalRows.push(vehicle.id);
      continue;
    }

    for (const [partIndex, part] of (vehicle.parts || []).entries()) {
      records.push(recordForPart(catKey, vehicle, part, partIndex, evalRow));
    }
  }
}

records.sort(sortRecord);

const seedRecords = records.filter(r => r.training_readiness === 'train_base_ready');
const summary = {
  schema: 'blueprint_image_training_manifest_summary.v1',
  source_date: '2026-05-15',
  source_files: {
    vehicle_templates: 'Minimal.html',
    image_match_evaluation: 'docs/BLUEPRINT_IMAGE_MATCH_EVALUATION_2026-05-15.md',
  },
  output_files: {
    all_manifest: 'data/blueprint/blueprint_image_training_manifest_2026-05-15.jsonl',
    seed_manifest: 'data/blueprint/blueprint_image_training_seed_2026-05-15.jsonl',
    summary: 'data/blueprint/blueprint_image_training_manifest_summary_2026-05-15.json',
  },
  counts: {
    assemblies: Object.values(VEHICLE_TEMPLATES).flat().length,
    all_records: records.length,
    train_base_ready_records: seedRecords.length,
    train_aug_ready_records: records.filter(r => r.training_readiness === 'train_aug_ready').length,
    assembly_part_assets_present: records.filter(r => r.assembly_part_asset_exists).length,
    missing_assembly_part_assets: records.filter(r => !r.assembly_part_asset_exists).length,
    missing_eval_rows: missingEvalRows.length,
  },
  by_readiness: records.reduce((acc, r) => {
    acc[r.training_readiness] = (acc[r.training_readiness] || 0) + 1;
    return acc;
  }, {}),
  by_category: records.reduce((acc, r) => {
    acc[r.category] = acc[r.category] || { records: 0, train_base_ready: 0, train_aug_ready: 0 };
    acc[r.category].records += 1;
    if (r.training_readiness === 'train_base_ready') acc[r.category].train_base_ready += 1;
    if (r.training_readiness === 'train_aug_ready') acc[r.category].train_aug_ready += 1;
    return acc;
  }, {}),
  missing_eval_rows: missingEvalRows,
};

fs.mkdirSync(OUT_DIR, { recursive: true });
fs.writeFileSync(OUT_ALL, `${records.map(r => JSON.stringify(r)).join('\n')}\n`, 'utf8');
fs.writeFileSync(OUT_SEED, `${seedRecords.map(r => JSON.stringify(r)).join('\n')}\n`, 'utf8');
fs.writeFileSync(OUT_SUMMARY, `${JSON.stringify(summary, null, 2)}\n`, 'utf8');

console.log(JSON.stringify({
  all_manifest: OUT_ALL,
  seed_manifest: OUT_SEED,
  summary: OUT_SUMMARY,
  counts: summary.counts,
}, null, 2));
