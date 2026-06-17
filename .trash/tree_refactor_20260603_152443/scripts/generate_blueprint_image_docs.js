const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const MINIMAL = path.join(ROOT, 'Minimal.html');
const OUT = path.join(ROOT, 'docs', 'BLUEPRINT_IMAGE_ASSET_INVENTORY_2026-05-13.md');

const html = fs.readFileSync(MINIMAL, 'utf8');

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

function md(s) {
  return String(s ?? '')
    .replace(/\|/g, '\\|')
    .replace(/\r?\n/g, ' ')
    .trim();
}

function presetRef(preset) {
  return Array.isArray(preset) ? preset.join('/') : '';
}

const PRESET_TREE = extractConst('PRESET_TREE', '// UI에서 카테고리 표시 순서');
const VEHICLE_TEMPLATES = extractConst(
  'VEHICLE_TEMPLATES',
  '// ═══════════════════════════════════════════════════════════════════════════\n// VEHICLE_SCHEMATICS'
);

const assemblyCount = Object.values(VEHICLE_TEMPLATES).reduce((sum, items) => sum + items.length, 0);
const assemblyPartCount = Object.values(VEHICLE_TEMPLATES)
  .flat()
  .reduce((sum, vehicle) => sum + (vehicle.parts || []).length, 0);
const presetCount = Object.values(PRESET_TREE)
  .reduce((sum, cat) => sum + Object.values(cat.types || {})
    .reduce((inner, type) => inner + Object.keys(type.configs || {}).length, 0), 0);

const lines = [];
lines.push('# Blueprint Image Asset Inventory - 2026-05-13');
lines.push('');
lines.push('Generated from `Minimal.html`. Do not hand-edit counts in this file; regenerate it after template or preset changes.');
lines.push('');
lines.push('## Counts');
lines.push('');
lines.push(`- Assembly categories: \`${Object.keys(VEHICLE_TEMPLATES).length}\``);
lines.push(`- Assembly templates: \`${assemblyCount}\``);
lines.push(`- Assembly parts across templates: \`${assemblyPartCount}\``);
lines.push(`- Single-part preset configs: \`${presetCount}\``);
lines.push('- Assembly image axes per vehicle: `exterior`, `internal`, `top/part-zone`');
lines.push('');

lines.push('## Assembly Index');
lines.push('');
for (const [catKey, vehicles] of Object.entries(VEHICLE_TEMPLATES)) {
  lines.push(`### ${catKey}`);
  lines.push('');
  lines.push('| ID | Label | Representative Basis | Parts | Image Files |');
  lines.push('|---|---|---|---:|---|');
  for (const v of vehicles) {
    lines.push(`| \`${md(v.id)}\` | ${md(v.label)} | ${md(v.wikiTitle)} | ${(v.parts || []).length} | \`${v.id}_exterior.svg\`, \`${v.id}_internal.svg\`, \`${v.id}_top.svg\` |`);
  }
  lines.push('');
}

lines.push('## Assembly Part Mapping');
lines.push('');
for (const [catKey, vehicles] of Object.entries(VEHICLE_TEMPLATES)) {
  lines.push(`### ${catKey}`);
  lines.push('');
  for (const v of vehicles) {
    lines.push(`#### ${v.id} - ${md(v.label)}`);
    lines.push('');
    lines.push(`Representative basis: ${md(v.wikiTitle)}`);
    lines.push('');
    lines.push('| Part | Label | Preset Ref | Image Documentation Need |');
    lines.push('|---|---|---|---|');
    for (const p of v.parts || []) {
      lines.push(`| \`${md(p.id)}\` | ${md(p.label)} | \`${md(presetRef(p.preset))}\` | ${md(p.spec)} |`);
    }
    lines.push('');
  }
}

lines.push('## Single-Part Preset Inventory');
lines.push('');
for (const [catKey, cat] of Object.entries(PRESET_TREE)) {
  lines.push(`### ${catKey} - ${md(cat.label || catKey)}`);
  lines.push('');
  for (const [typeKey, type] of Object.entries(cat.types || {})) {
    lines.push(`#### ${typeKey} - ${md(type.label || typeKey)}`);
    lines.push('');
    lines.push('| Config | Label | Material | Process | Image File |');
    lines.push('|---|---|---|---|---|');
    for (const [confKey, conf] of Object.entries(type.configs || {})) {
      lines.push(`| \`${md(confKey)}\` | ${md(conf.label || confKey)} | ${md(conf.material || '')} | ${md(conf.process || '')} | \`vendor/img/presets/${catKey}/${typeKey}/${confKey}.svg\` |`);
    }
    lines.push('');
  }
}

fs.writeFileSync(OUT, `${lines.join('\n')}\n`, 'utf8');
console.log(JSON.stringify({
  out: OUT,
  assembly_categories: Object.keys(VEHICLE_TEMPLATES).length,
  assembly_templates: assemblyCount,
  assembly_parts: assemblyPartCount,
  preset_configs: presetCount,
}, null, 2));
