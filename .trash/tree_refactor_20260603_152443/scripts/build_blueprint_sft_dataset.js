const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const BLUEPRINT_DIR = path.join(ROOT, 'data', 'blueprint');
const HANDOFF_BLUEPRINT_DIR = path.join(ROOT, 'madang_learning_core_handoff_20260514_225416', 'data', 'blueprint');

const IN_ALL = path.join(BLUEPRINT_DIR, 'blueprint_image_training_manifest_2026-05-15.jsonl');
const IN_SEED = path.join(BLUEPRINT_DIR, 'blueprint_image_training_seed_2026-05-15.jsonl');

const OUT_FULL = path.join(BLUEPRINT_DIR, 'train_blueprint_full_labeled_sft_2026-05-15.jsonl');
const OUT_SEED = path.join(BLUEPRINT_DIR, 'train_blueprint_seed_sft_2026-05-15.jsonl');
const OUT_TEXT = path.join(BLUEPRINT_DIR, 'train_blueprint_seed_text_2026-05-15.txt');
const OUT_SUMMARY = path.join(BLUEPRINT_DIR, 'train_blueprint_sft_summary_2026-05-15.json');

const HANDOFF_OUT_SEED = path.join(HANDOFF_BLUEPRINT_DIR, 'train_blueprint_seed_sft_2026-05-15.jsonl');
const HANDOFF_OUT_TEXT = path.join(HANDOFF_BLUEPRINT_DIR, 'train_blueprint_seed_text_2026-05-15.txt');

function readJsonl(filePath) {
  const text = fs.readFileSync(filePath, 'utf8').trim();
  if (!text) return [];
  return text.split(/\r?\n/).map((line, index) => {
    try {
      return JSON.parse(line);
    } catch (error) {
      throw new Error(`Invalid JSONL at ${filePath}:${index + 1}: ${error.message}`);
    }
  });
}

function writeJsonl(filePath, rows) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, `${rows.map(row => JSON.stringify(row)).join('\n')}\n`, 'utf8');
}

function compact(value) {
  return String(value || '').replace(/\s+/g, ' ').trim();
}

function requestFor(record) {
  return [
    `Create a blueprint image planning record for ${record.vehicle_label}.`,
    `Part: ${record.part_label}.`,
    `Representative basis: ${record.representative_basis}.`,
    `Use readiness label ${record.training_readiness} and axis quality ${record.axis_quality}.`,
  ].join(' ');
}

function outputFor(record) {
  const isSeed = record.training_readiness === 'train_base_ready';

  return {
    schema: 'blueprint-image-sft-plan-1',
    intent: {
      primary: 'blueprint_image_planning',
      asset_kind: record.asset_kind,
      training_readiness: record.training_readiness,
    },
    vehicle: {
      id: record.vehicle_id,
      label: record.vehicle_label,
      category: record.category,
      representative_basis: record.representative_basis,
      description: record.vehicle_description,
      material: record.vehicle_material,
      process: record.vehicle_process,
      mass: record.vehicle_mass,
      envelope: record.vehicle_envelope,
    },
    part: {
      id: record.part_id,
      index: record.part_index,
      label: record.part_label,
      spec: record.part_spec,
      preset_ref: record.preset_ref,
    },
    image_assets: {
      primary_svg: record.asset_path,
      assembly_part_svg: record.assembly_part_asset_path,
      preset_fallback_svg: record.preset_asset_path,
      axis_svgs: record.axis_assets,
    },
    quality: {
      axis_quality: record.axis_quality,
      part_quality: record.part_quality,
      readiness: record.training_readiness,
      use_for_core_training: isSeed,
      quality_gate: record.output?.quality_gate || '',
    },
    blueprint_requirements: [
      'preserve the locked representative product basis',
      'show the part as a functional engineering component, not a generic icon',
      'use concise labels tied to structure, interfaces, flows, or mounting features',
      'keep the drawing language consistent with dark technical blueprint SVG assets',
      'make the image traceable to the assembly and part identifiers',
    ],
    audit_checks: [
      'asset path exists',
      'axis assets exist',
      'part label matches vehicle part mapping',
      'quality label is kept separate from file coverage',
      'coverage data is not promoted to core training without review',
    ],
    recommendation: record.recommendation,
    next_steps: isSeed
      ? ['include in seed SFT set', 'use as base/adaptor training example', 'review before superquality promotion']
      : ['keep as labeled augmentation data', 'write or verify category spec', 'promote after 3-axis master review'],
  };
}

function textBlock(input, output) {
  return `<|madang:request|>\n${input}\n<|madang:plan|>\n${JSON.stringify(output)}\n<|madang:end|>\n`;
}

function sftRow(record) {
  const input = requestFor(record);
  const output = outputFor(record);
  return {
    input,
    output,
    input_field: 'request',
    output_field: 'plan',
    source_schema: record.schema,
    source_vehicle_id: record.vehicle_id,
    source_part_id: record.part_id,
    training_readiness: record.training_readiness,
    asset_path: record.asset_path,
    text: textBlock(input, output),
  };
}

function summarize(rows, seedRows) {
  const byReadiness = rows.reduce((acc, row) => {
    acc[row.training_readiness] = (acc[row.training_readiness] || 0) + 1;
    return acc;
  }, {});

  const byCategory = rows.reduce((acc, row) => {
    const category = row.output.vehicle.category;
    acc[category] = acc[category] || { records: 0, train_base_ready: 0, train_aug_ready: 0 };
    acc[category].records += 1;
    if (row.training_readiness === 'train_base_ready') acc[category].train_base_ready += 1;
    if (row.training_readiness === 'train_aug_ready') acc[category].train_aug_ready += 1;
    return acc;
  }, {});

  return {
    schema: 'blueprint_sft_summary.v1',
    source_date: '2026-05-15',
    source_files: {
      all_manifest: 'data/blueprint/blueprint_image_training_manifest_2026-05-15.jsonl',
      seed_manifest: 'data/blueprint/blueprint_image_training_seed_2026-05-15.jsonl',
    },
    output_files: {
      full_sft: 'data/blueprint/train_blueprint_full_labeled_sft_2026-05-15.jsonl',
      seed_sft: 'data/blueprint/train_blueprint_seed_sft_2026-05-15.jsonl',
      seed_text: 'data/blueprint/train_blueprint_seed_text_2026-05-15.txt',
      handoff_seed_sft: 'madang_learning_core_handoff_20260514_225416/data/blueprint/train_blueprint_seed_sft_2026-05-15.jsonl',
      handoff_seed_text: 'madang_learning_core_handoff_20260514_225416/data/blueprint/train_blueprint_seed_text_2026-05-15.txt',
    },
    counts: {
      full_sft_records: rows.length,
      seed_sft_records: seedRows.length,
      full_text_blocks: rows.length,
      seed_text_blocks: seedRows.length,
    },
    by_readiness: byReadiness,
    by_category: byCategory,
  };
}

const fullRecords = readJsonl(IN_ALL);
const seedRecords = readJsonl(IN_SEED);
const fullRows = fullRecords.map(sftRow);
const seedRows = seedRecords.map(sftRow);

writeJsonl(OUT_FULL, fullRows);
writeJsonl(OUT_SEED, seedRows);
fs.writeFileSync(OUT_TEXT, seedRows.map(row => row.text).join('\n'), 'utf8');

fs.mkdirSync(HANDOFF_BLUEPRINT_DIR, { recursive: true });
writeJsonl(HANDOFF_OUT_SEED, seedRows);
fs.writeFileSync(HANDOFF_OUT_TEXT, seedRows.map(row => row.text).join('\n'), 'utf8');

const summary = summarize(fullRows, seedRows);
fs.writeFileSync(OUT_SUMMARY, `${JSON.stringify(summary, null, 2)}\n`, 'utf8');

console.log(JSON.stringify({
  full_sft: OUT_FULL,
  seed_sft: OUT_SEED,
  seed_text: OUT_TEXT,
  handoff_seed_sft: HANDOFF_OUT_SEED,
  handoff_seed_text: HANDOFF_OUT_TEXT,
  summary: OUT_SUMMARY,
  counts: summary.counts,
}, null, 2));
