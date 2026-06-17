const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const MINIMAL = path.join(ROOT, 'Minimal.html');
const OUT_IMG = path.join(ROOT, 'vendor', 'img');
const OUT_PRESETS = path.join(OUT_IMG, 'presets');
const MASTER_ASSEMBLY_IDS = new Set([
  'small_launch_vehicle',
  'cubesat_3u',
  'lunar_lander',
  'space_telescope',
  'orbital_module',
  'fighter_f_class',
  'supersonic_sst',
  'civil_airliner',
  'turboprop_transport',
  'heavy_helicopter',
  'turbofan_engine',
]);
const MANUAL_AXIS_ASSET_IDS = new Set([
  'small_launch_vehicle',
  'cubesat_3u',
  'lunar_lander',
  'space_telescope',
  'orbital_module',
  'fighter_f_class',
  'supersonic_sst',
  'civil_airliner',
  'turboprop_transport',
  'heavy_helicopter',
  'turbofan_engine',
]);
const MANUAL_PRESET_ASSET_IDS = new Set([
  // Format: category/type/config
]);

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

const PRESET_TREE = extractConst('PRESET_TREE', '// UI에서 카테고리 표시 순서');
const VEHICLE_SCHEMATICS = extractConst('VEHICLE_SCHEMATICS', '// ═══════════════════════════════════════════════════════════════════════════\n// PresetSelector');

function esc(s) {
  return String(s ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function parseVB(vb) {
  const [x, y, w, h] = String(vb).split(/\s+/).map(Number);
  return { x, y, w, h };
}

function zoneBounds(z) {
  if (z.shape === 'R') return { x: z.x, y: z.y, w: z.w, h: z.h };
  if (z.shape === 'C') return { x: z.cx - z.r, y: z.cy - z.r, w: z.r * 2, h: z.r * 2 };
  const pts = String(z.pts).trim().split(/\s+/).map(p => p.split(',').map(Number));
  const xs = pts.map(p => p[0]);
  const ys = pts.map(p => p[1]);
  const x = Math.min(...xs);
  const y = Math.min(...ys);
  return { x, y, w: Math.max(...xs) - x, h: Math.max(...ys) - y };
}

function centroid(z) {
  const b = zoneBounds(z);
  return { x: b.x + b.w / 2, y: b.y + b.h / 2 };
}

function zoneShape(z, idx) {
  const stroke = idx % 3 === 0 ? 'rgba(159,211,255,.72)' : idx % 3 === 1 ? 'rgba(137,255,168,.58)' : 'rgba(255,211,159,.58)';
  const fill = idx % 3 === 0 ? 'rgba(8,28,48,.66)' : idx % 3 === 1 ? 'rgba(10,38,44,.50)' : 'rgba(42,31,24,.38)';
  if (z.shape === 'R') {
    return `<rect x="${z.x}" y="${z.y}" width="${z.w}" height="${z.h}" rx="3" class="zone" fill="${fill}" stroke="${stroke}"/>`;
  }
  if (z.shape === 'C') {
    return `<circle cx="${z.cx}" cy="${z.cy}" r="${z.r}" class="zone" fill="${fill}" stroke="${stroke}"/>`;
  }
  return `<polygon points="${esc(z.pts)}" class="zone" fill="${fill}" stroke="${stroke}"/>`;
}

function connector(z, vb) {
  const c = centroid(z);
  const side = c.x < vb.w / 2 ? -1 : 1;
  const tx = c.x + side * Math.min(42, Math.max(18, vb.w * 0.045));
  const ty = c.y - Math.min(18, Math.max(8, vb.h * 0.035));
  return `<path d="M${c.x.toFixed(1)} ${c.y.toFixed(1)} L${tx.toFixed(1)} ${ty.toFixed(1)}" class="lead"/>`;
}

function labels(zones, vb) {
  const seen = new Set();
  return zones.map((z, idx) => {
    if (seen.has(z.id)) return '';
    seen.add(z.id);
    const c = centroid(z);
    const b = zoneBounds(z);
    const label = esc(z.label || z.id);
    const font = Math.max(7, Math.min(11, vb.w / 70));
    const y = Math.max(18, Math.min(vb.h - 12, c.y));
    return `<text x="${c.x.toFixed(1)}" y="${y.toFixed(1)}" text-anchor="middle" dominant-baseline="middle" class="label" font-size="${font}">${label}</text>`;
  }).join('\n');
}

function zoneWire(z, idx) {
  const cls = idx % 2 ? 'zonewire alt' : 'zonewire';
  if (z.shape === 'R') {
    return `<rect x="${z.x}" y="${z.y}" width="${z.w}" height="${z.h}" rx="2" class="${cls}"/>`;
  }
  if (z.shape === 'C') {
    return `<circle cx="${z.cx}" cy="${z.cy}" r="${z.r}" class="${cls}"/>`;
  }
  return `<polygon points="${esc(z.pts)}" class="${cls}"/>`;
}

function blueprintDetailLayer(id, spec, vb, zones) {
  const seen = new Set();
  const callouts = [];
  const wires = [];
  const rivets = [];
  zones.forEach((z, idx) => {
    wires.push(zoneWire(z, idx));
    const b = zoneBounds(z);
    const c = centroid(z);
    const samples = [
      [b.x, b.y], [b.x + b.w, b.y], [b.x, b.y + b.h], [b.x + b.w, b.y + b.h],
      [b.x + b.w / 2, b.y], [b.x + b.w / 2, b.y + b.h],
    ];
    samples.forEach(([x, y], j) => {
      if (j % 2 === idx % 2) rivets.push(`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="1.4" class="rivet"/>`);
    });
    if (!seen.has(z.id) && callouts.length < 12) {
      seen.add(z.id);
      const left = c.x < vb.w / 2;
      const lane = callouts.length;
      const tx = left ? 18 : vb.w - 18;
      const ty = 44 + (lane % 6) * Math.max(18, Math.min(26, vb.h / 15));
      const midx = left ? Math.max(38, c.x - 28) : Math.min(vb.w - 38, c.x + 28);
      const anchor = left ? 'start' : 'end';
      callouts.push(`<path d="M${c.x.toFixed(1)} ${c.y.toFixed(1)} L${midx.toFixed(1)} ${ty.toFixed(1)} L${tx.toFixed(1)} ${ty.toFixed(1)}" class="callout-line"/>`);
      callouts.push(`<text x="${tx}" y="${ty - 3}" text-anchor="${anchor}" class="callout">${esc(z.label || z.id)}</text>`);
    }
  });

  const stations = [];
  const vertical = /launch|rocket|motor|lander|telescope|exo|afo|humanoid|cochlear/.test(id);
  const n = vertical ? 8 : 10;
  for (let i = 1; i < n; i++) {
    if (vertical) {
      const y = 34 + i * ((vb.h - 72) / n);
      stations.push(`<line x1="${(vb.w * 0.18).toFixed(1)}" y1="${y.toFixed(1)}" x2="${(vb.w * 0.82).toFixed(1)}" y2="${y.toFixed(1)}" class="station"/>`);
    } else {
      const x = 34 + i * ((vb.w - 68) / n);
      stations.push(`<line x1="${x.toFixed(1)}" y1="${(vb.h * 0.14).toFixed(1)}" x2="${x.toFixed(1)}" y2="${(vb.h * 0.88).toFixed(1)}" class="station"/>`);
    }
  }

  const special = [];
  if (/launch|rocket|motor/.test(id)) {
    special.push(`<text x="${vb.w - 24}" y="${vb.h * 0.18}" text-anchor="end" class="micro">STAGE DATUM · INTERTANK · ENGINE CLUSTER</text>`);
    special.push(`<path d="M${vb.w * 0.34} ${vb.h * 0.82} Q${vb.w * 0.5} ${vb.h * 0.76} ${vb.w * 0.66} ${vb.h * 0.82}" class="thrust-arc"/>`);
  }
  if (/fighter|transport|airliner|helicopter|sst|wing|tiltrotor/.test(id)) {
    special.push(`<text x="${vb.w - 24}" y="${vb.h * 0.14}" text-anchor="end" class="micro">AERO DATUM · SPAR · CONTROL SURFACE MAP</text>`);
  }
  if (/rover|robot|arm|quadruped|linkage|suspension/.test(id)) {
    special.push(`<text x="${vb.w - 24}" y="${vb.h * 0.14}" text-anchor="end" class="micro">KINEMATIC DATUM · JOINT AXES · LOAD PATH</text>`);
  }

  return `<g class="detail-layer">
    ${stations.join('\n')}
    ${wires.join('\n')}
    ${rivets.join('\n')}
    ${callouts.join('\n')}
    ${special.join('\n')}
  </g>`;
}

function fitArtwork(vb, content, baseW = 700, baseH = 420) {
  const sx = vb.w / baseW;
  const sy = vb.h / baseH;
  return `<g transform="scale(${sx.toFixed(5)} ${sy.toFixed(5)})">${content}</g>`;
}

function vehicleArtwork(id, vb) {
  const common = {
    droneQuad: `<circle cx="160" cy="120" r="52" class="rotor"/><circle cx="540" cy="120" r="52" class="rotor"/><circle cx="540" cy="300" r="52" class="rotor"/><circle cx="160" cy="300" r="52" class="rotor"/><path d="M160 120 L350 210 L540 120 M160 300 L350 210 L540 300" class="major"/><rect x="275" y="165" width="150" height="90" rx="8" class="skin"/><rect x="305" y="188" width="90" height="44" rx="3" class="panel"/>`,
    aircraftJet: `<path d="M350 24 C333 48 321 92 315 148 C307 222 310 304 324 350 C332 368 342 378 350 382 C358 378 368 368 376 350 C390 304 393 222 385 148 C379 92 367 48 350 24 Z" class="skin"/><path d="M320 128 C330 96 340 72 350 60 C360 72 370 96 380 128 L374 168 C366 180 358 184 350 184 C342 184 334 180 326 168 Z" class="glass"/><path d="M315 158 C264 166 172 212 66 292 L82 318 C176 284 242 264 318 236 Z" class="skin"/><path d="M385 158 C436 166 528 212 634 292 L618 318 C524 284 458 264 382 236 Z" class="skin"/><path d="M310 178 C284 184 268 202 260 226 L280 238 L312 222 Z" class="panel"/><path d="M390 178 C416 184 432 202 440 226 L420 238 L388 222 Z" class="panel"/><rect x="326" y="222" width="48" height="76" rx="4" class="panel"/><path d="M318 292 L178 338 L184 364 L326 318 Z" class="skin"/><path d="M382 292 L522 338 L516 364 L374 318 Z" class="skin"/><path d="M318 320 L292 256 L324 258 L340 330 Z" class="skin"/><path d="M382 320 L408 256 L376 258 L360 330 Z" class="skin"/><ellipse cx="328" cy="374" rx="22" ry="12" class="nozzle"/><ellipse cx="372" cy="374" rx="22" ry="12" class="nozzle"/><g class="minor"><path d="M318 174 L86 306 M382 174 L614 306 M318 232 L92 316 M382 232 L608 316"/><circle cx="222" cy="242" r="5"/><circle cx="478" cy="242" r="5"/><circle cx="180" cy="266" r="5"/><circle cx="520" cy="266" r="5"/></g>`,
    airliner: `<path d="M350 42 C322 62 306 118 302 208 C298 302 316 358 350 382 C384 358 402 302 398 208 C394 118 378 62 350 42 Z" class="skin"/><path d="M304 166 L74 258 L84 286 L310 230 Z" class="skin"/><path d="M396 166 L626 258 L616 286 L390 230 Z" class="skin"/><ellipse cx="218" cy="238" rx="34" ry="26" class="nozzle"/><ellipse cx="482" cy="238" rx="34" ry="26" class="nozzle"/><path d="M322 326 L218 382 L228 402 L330 350 Z" class="skin"/><path d="M378 326 L482 382 L472 402 L370 350 Z" class="skin"/><path d="M326 82 L374 82 M306 150 L394 150 M302 210 L398 210 M306 286 L394 286" class="minor"/><g class="minor">${Array.from({length:18},(_,i)=>`<line x1="${322+i*3.3}" y1="${112+i*11.4}" x2="${328+i*2.5}" y2="${112+i*11.4}"/>`).join('')}</g>`,
    rover: `<rect x="185" y="145" width="330" height="140" rx="10" class="skin"/><rect x="245" y="95" width="210" height="44" rx="4" class="panel"/><path d="M185 210 L105 260 M515 210 L595 260" class="major"/><circle cx="105" cy="282" r="34" class="rotor"/><circle cx="250" cy="306" r="34" class="rotor"/><circle cx="450" cy="306" r="34" class="rotor"/><circle cx="595" cy="282" r="34" class="rotor"/><path d="M210 145 L120 100 L88 112" class="major"/>`,
    engine: `<ellipse cx="350" cy="210" rx="230" ry="112" class="skin"/><ellipse cx="350" cy="210" rx="170" ry="80" class="panel"/><ellipse cx="350" cy="210" rx="86" ry="42" class="nozzle"/><g class="minor">${Array.from({length:18},(_,i)=>{const a=i*20*Math.PI/180; const x1=350+52*Math.cos(a), y1=210+25*Math.sin(a), x2=350+160*Math.cos(a), y2=210+75*Math.sin(a); return `<line x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}"/>`;}).join('')}</g>`,
    gearbox: `<circle cx="350" cy="210" r="145" class="skin"/><circle cx="350" cy="210" r="94" class="panel"/><circle cx="350" cy="210" r="42" class="nozzle"/><g class="minor">${Array.from({length:12},(_,i)=>{const a=i*30*Math.PI/180; const x=350+118*Math.cos(a), y=210+118*Math.sin(a); return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="8"/>`;}).join('')}</g>`,
  };

  const map = {
    racing_quad_5in: common.droneQuad,
    cinelifter_x8: `<circle cx="150" cy="110" r="58" class="rotor"/><circle cx="550" cy="110" r="58" class="rotor"/><circle cx="550" cy="310" r="58" class="rotor"/><circle cx="150" cy="310" r="58" class="rotor"/><circle cx="150" cy="110" r="34" class="rotor"/><circle cx="550" cy="110" r="34" class="rotor"/><circle cx="550" cy="310" r="34" class="rotor"/><circle cx="150" cy="310" r="34" class="rotor"/><path d="M150 110 L350 210 L550 110 M150 310 L350 210 L550 310" class="major"/><rect x="250" y="150" width="200" height="120" rx="10" class="skin"/><rect x="280" y="276" width="140" height="44" rx="4" class="panel"/>`,
    wing_long_range: `<path d="M70 224 L350 110 L630 224 L480 254 L350 220 L220 254 Z" class="skin"/><rect x="294" y="158" width="112" height="74" rx="8" class="panel"/><circle cx="350" cy="120" r="26" class="nozzle"/><path d="M292 238 L238 286 M408 238 L462 286" class="major"/>`,
    cyclocopter_demo: `<rect x="90" y="120" width="145" height="190" rx="18" class="skin"/><rect x="465" y="120" width="145" height="190" rx="18" class="skin"/><circle cx="162" cy="215" r="58" class="rotor"/><circle cx="538" cy="215" r="58" class="rotor"/><rect x="260" y="165" width="180" height="120" rx="10" class="panel"/><path d="M235 185 L260 185 M440 185 L465 185" class="major"/>`,
    tiltrotor_vtol: `<path d="M330 92 L370 92 L390 300 L310 300 Z" class="skin"/><path d="M90 170 L310 190 L310 230 L90 250 Z" class="skin"/><path d="M610 170 L390 190 L390 230 L610 250 Z" class="skin"/><circle cx="95" cy="210" r="54" class="rotor"/><circle cx="605" cy="210" r="54" class="rotor"/><path d="M390 292 L480 350 L462 370 L382 316 Z M310 292 L220 350 L238 370 L318 316 Z" class="skin"/>`,
    fighter_f_class: common.aircraftJet,
    turboprop_transport: `<path d="M350 48 C318 74 304 132 302 216 C300 300 320 354 350 374 C380 354 400 300 398 216 C396 132 382 74 350 48 Z" class="skin"/><path d="M302 156 L80 210 L80 244 L304 218 Z" class="skin"/><path d="M398 156 L620 210 L620 244 L396 218 Z" class="skin"/><rect x="176" y="174" width="76" height="58" rx="7" class="panel"/><rect x="448" y="174" width="76" height="58" rx="7" class="panel"/><circle cx="214" cy="204" r="48" class="rotor"/><circle cx="486" cy="204" r="48" class="rotor"/><path d="M214 144 L214 264 M154 204 L274 204 M178 168 L250 240 M250 168 L178 240 M486 144 L486 264 M426 204 L546 204 M450 168 L522 240 M522 168 L450 240" class="minor"/><path d="M320 326 L230 376 L238 398 L330 350 Z" class="skin"/><path d="M380 326 L470 376 L462 398 L370 350 Z" class="skin"/><rect x="326" y="344" width="48" height="30" rx="4" class="panel"/><path d="M304 194 L396 194 M304 240 L396 240 M318 96 L382 96" class="minor"/>`,
    civil_airliner: common.airliner,
    heavy_helicopter: `<ellipse cx="320" cy="220" rx="180" ry="82" class="skin"/><path d="M450 210 L650 188 L650 232 L450 230 Z" class="skin"/><circle cx="320" cy="108" r="54" class="rotor"/><path d="M70 108 L570 108 M320 20 L320 196" class="major"/><rect x="245" y="148" width="150" height="64" rx="8" class="panel"/><circle cx="610" cy="210" r="28" class="rotor"/>`,
    small_launch_vehicle: `<path d="M350 26 C328 52 318 84 318 126 L318 348 L382 348 L382 126 C382 84 372 52 350 26 Z" class="skin"/><rect x="318" y="96" width="64" height="42" class="panel"/><rect x="318" y="168" width="64" height="48" class="panel"/><rect x="318" y="258" width="64" height="46" class="panel"/><path d="M318 138 L382 138 M318 216 L382 216 M318 304 L382 304" class="minor"/><path d="M318 332 L252 392 L302 392 L330 348 Z" class="skin"/><path d="M382 332 L448 392 L398 392 L370 348 Z" class="skin"/><ellipse cx="350" cy="374" rx="19" ry="13" class="nozzle"/><ellipse cx="322" cy="370" rx="14" ry="10" class="nozzle"/><ellipse cx="378" cy="370" rx="14" ry="10" class="nozzle"/><ellipse cx="350" cy="348" rx="14" ry="10" class="nozzle"/><g class="minor"><path d="M318 116 L382 116 M318 188 L382 188 M318 282 L382 282"/><rect x="332" y="74" width="36" height="12"/><rect x="330" y="236" width="40" height="12"/></g>`,
    cubesat_3u: `<path d="M250 80 L430 132 L430 338 L250 286 Z" class="skin"/><path d="M250 80 L170 130 L170 336 L250 286 Z" class="panel"/><path d="M170 130 L350 180 L430 132 M170 198 L430 198 M170 266 L430 266" class="minor"/><path d="M150 140 L70 92 M450 154 L610 86 M150 310 L68 370 M450 310 L610 368" class="major"/>`,
    lunar_lander: `<rect x="275" y="120" width="150" height="112" rx="12" class="skin"/><path d="M300 120 L350 54 L400 120" class="skin"/><path d="M290 232 L210 340 L168 340 M410 232 L490 340 L532 340 M290 232 L258 344 M410 232 L442 344" class="major"/><circle cx="350" cy="176" r="34" class="panel"/><path d="M286 252 L414 252 L390 302 L310 302 Z" class="nozzle"/>`,
    space_telescope: `<rect x="280" y="90" width="140" height="230" rx="10" class="skin"/><circle cx="350" cy="130" r="54" class="panel"/><path d="M260 175 L80 140 L80 280 L260 245 Z M440 175 L620 140 L620 280 L440 245 Z" class="skin"/><path d="M304 320 L396 320 L418 372 L282 372 Z" class="nozzle"/>`,
    orbital_module: `<ellipse cx="350" cy="205" rx="180" ry="102" class="skin"/><rect x="260" y="112" width="180" height="186" rx="14" class="panel"/><path d="M170 205 L62 160 M170 205 L62 250 M530 205 L638 160 M530 205 L638 250" class="major"/><circle cx="350" cy="205" r="48" class="nozzle"/>`,
    rov_inspection: `<rect x="120" y="125" width="460" height="170" rx="12" class="skin"/><rect x="225" y="158" width="190" height="90" rx="10" class="panel"/><circle cx="145" cy="210" r="38" class="rotor"/><circle cx="555" cy="210" r="38" class="rotor"/><circle cx="350" cy="112" r="28" class="rotor"/><path d="M120 270 L74 330 M580 270 L626 330" class="major"/>`,
    usv_autonomous: `<path d="M92 210 C138 130 250 96 350 102 C450 96 562 130 608 210 C562 290 450 324 350 318 C250 324 138 290 92 210 Z" class="skin"/><rect x="270" y="150" width="160" height="92" rx="8" class="panel"/><path d="M210 132 L490 132 M220 288 L480 288" class="minor"/>`,
    underwater_glider: `<path d="M70 210 C145 160 250 145 350 150 C450 145 555 160 630 210 C555 260 450 275 350 270 C250 275 145 260 70 210 Z" class="skin"/><path d="M250 170 L90 115 L110 145 L260 208 Z M450 170 L610 115 L590 145 L440 208 Z" class="skin"/><path d="M545 210 L630 174 L630 246 Z" class="panel"/>`,
    research_submarine: `<path d="M72 210 C130 120 260 94 388 112 C520 130 600 168 636 210 C600 252 520 290 388 308 C260 326 130 300 72 210 Z" class="skin"/><circle cx="160" cy="210" r="44" class="panel"/><rect x="370" y="112" width="82" height="58" rx="6" class="panel"/><circle cx="560" cy="172" r="24" class="rotor"/><circle cx="560" cy="248" r="24" class="rotor"/>`,
    wave_glider_asv: `<path d="M116 156 C174 118 278 108 350 124 C422 108 526 118 584 156 L550 262 C468 294 232 294 150 262 Z" class="skin"/><rect x="238" y="150" width="224" height="72" rx="8" class="panel"/><path d="M190 286 L160 360 M510 286 L540 360 M232 332 L468 332" class="major"/>`,
    arm_6dof: common.rover.replace('M185 210 L105 260 M515 210 L595 260','M160 300 L270 248 L350 196 L468 132').replace(/<circle cx="595"[\s\S]*?class="rotor"\/>/,'<circle cx="468" cy="132" r="36" class="rotor"/>'),
    mars_rover: common.rover,
    quadruped_walker: `<rect x="225" y="150" width="250" height="120" rx="16" class="skin"/><circle cx="260" cy="300" r="30" class="rotor"/><circle cx="440" cy="300" r="30" class="rotor"/><path d="M250 252 L170 334 L138 320 M450 252 L530 334 L562 320 M260 150 L176 80 L140 96 M440 150 L524 80 L560 96" class="major"/><rect x="285" y="104" width="130" height="46" rx="6" class="panel"/>`,
    delta_parallel_robot: `<circle cx="350" cy="238" r="62" class="panel"/><circle cx="350" cy="80" r="40" class="rotor"/><circle cx="180" cy="320" r="40" class="rotor"/><circle cx="520" cy="320" r="40" class="rotor"/><path d="M350 120 L350 176 M205 300 L296 260 M495 300 L404 260" class="major"/><path d="M350 120 L296 260 M350 120 L404 260 M205 300 L350 176 M495 300 L350 176" class="minor"/>`,
    humanoid_biped: `<circle cx="350" cy="76" r="44" class="panel"/><rect x="280" y="130" width="140" height="126" rx="14" class="skin"/><path d="M280 160 L190 230 L168 310 M420 160 L510 230 L532 310 M316 256 L286 376 M384 256 L414 376" class="major"/><circle cx="168" cy="310" r="24" class="rotor"/><circle cx="532" cy="310" r="24" class="rotor"/>`,
    surgical_robot_arm: `<circle cx="170" cy="310" r="52" class="rotor"/><path d="M200 280 L310 230 L410 160 L530 108" class="major"/><circle cx="310" cy="230" r="34" class="rotor"/><circle cx="410" cy="160" r="28" class="rotor"/><path d="M530 108 L592 82 M530 108 L590 134" class="minor"/><rect x="122" y="330" width="112" height="38" rx="5" class="skin"/>`,
    cochlear_implant: `<path d="M190 210 C190 116 276 58 372 78 C486 102 518 242 434 304 C364 356 250 328 244 238 C240 178 298 132 358 154 C414 174 420 250 368 272 C330 288 286 264 292 224" class="skin"/><rect x="454" y="150" width="104" height="84" rx="12" class="panel"/><path d="M244 238 L454 192" class="major"/>`,
    powered_exoskeleton: `<rect x="286" y="80" width="128" height="128" rx="14" class="skin"/><path d="M286 130 L210 230 L190 344 M414 130 L490 230 L510 344 M318 208 L286 364 M382 208 L414 364" class="major"/><circle cx="210" cy="230" r="28" class="rotor"/><circle cx="490" cy="230" r="28" class="rotor"/><circle cx="286" cy="364" r="24" class="rotor"/><circle cx="414" cy="364" r="24" class="rotor"/>`,
    myoelectric_hand: `<path d="M290 185 C260 205 238 250 250 306 C266 370 340 376 372 326 C400 282 386 226 352 192 Z" class="skin"/><path d="M294 184 L270 70 M318 180 L326 54 M342 184 L382 66 M360 202 L442 116 M272 226 L190 152" class="major"/><circle cx="326" cy="54" r="15" class="rotor"/>`,
    powered_afo: `<path d="M330 62 C284 120 272 214 298 314 L180 344 L174 384 L388 384 C420 310 414 170 374 70 Z" class="skin"/><path d="M300 310 L414 310 M290 188 L386 188" class="minor"/><circle cx="350" cy="206" r="30" class="rotor"/>`,
    turbofan_engine: common.engine,
    solid_rocket_motor: `<rect x="292" y="58" width="116" height="250" rx="30" class="skin"/><path d="M292 308 L234 380 L466 380 L408 308 Z" class="skin"/><path d="M314 78 L386 78 M292 132 L408 132 M292 206 L408 206 M292 276 L408 276" class="minor"/><path d="M322 102 C370 132 322 162 370 192 C322 222 370 252 322 282" class="panel"/><ellipse cx="350" cy="344" rx="34" ry="18" class="nozzle"/><ellipse cx="310" cy="356" rx="17" ry="11" class="nozzle"/><ellipse cx="390" cy="356" rx="17" ry="11" class="nozzle"/>`,
    electric_motor_assy: common.gearbox,
    marine_propeller: `<circle cx="350" cy="210" r="70" class="panel"/><path d="M350 140 C422 70 506 76 520 116 C456 154 410 176 350 210 Z" class="skin"/><path d="M420 210 C520 238 548 318 516 348 C462 306 426 270 350 210 Z" class="skin"/><path d="M350 280 C278 350 194 344 180 304 C244 266 290 244 350 210 Z" class="skin"/><path d="M280 210 C180 182 152 102 184 72 C238 114 274 150 350 210 Z" class="skin"/>`,
    ion_thruster_assy: common.engine.replace('rx="230" ry="112"', 'rx="150" ry="150"').replace('rx="170" ry="80"', 'rx="104" ry="104"'),
    harmonic_drive: common.gearbox,
    suspension_assy: `<path d="M125 135 L460 180 L452 210 L120 162 Z" class="skin"/><path d="M120 278 L472 232 L482 262 L128 310 Z" class="skin"/><rect x="440" y="150" width="84" height="146" rx="8" class="panel"/><circle cx="506" cy="224" r="48" class="rotor"/><path d="M260 205 L382 170 M260 245 L384 286 M150 160 L94 240" class="major"/>`,
    cnc_tool_changer: `<circle cx="350" cy="210" r="170" class="skin"/><circle cx="350" cy="210" r="76" class="panel"/>${Array.from({length:12},(_,i)=>{const a=i*30*Math.PI/180; const x=350+132*Math.cos(a), y=210+132*Math.sin(a); return `<rect x="${(x-16).toFixed(1)}" y="${(y-12).toFixed(1)}" width="32" height="24" rx="4" class="nozzle"/>`;}).join('')}<rect x="300" y="180" width="100" height="60" rx="6" class="panel"/>`,
    hydraulic_cylinder: `<rect x="120" y="176" width="360" height="68" rx="12" class="skin"/><rect x="480" y="190" width="150" height="40" rx="8" class="panel"/><rect x="70" y="164" width="70" height="92" rx="8" class="panel"/><circle cx="94" cy="210" r="26" class="rotor"/><circle cx="606" cy="210" r="22" class="rotor"/>`,
    precision_linkage: `<rect x="96" y="300" width="508" height="40" rx="6" class="panel"/><circle cx="160" cy="210" r="36" class="rotor"/><circle cx="310" cy="150" r="32" class="rotor"/><circle cx="450" cy="230" r="32" class="rotor"/><circle cx="560" cy="172" r="30" class="rotor"/><path d="M160 210 L310 150 L450 230 L560 172" class="major"/><path d="M160 210 L450 230" class="minor"/>`,
  };

  const art = map[id] || common.gearbox;
  return fitArtwork(vb, art);
}

function assemblySvg(id, spec) {
  const vb = parseVB(spec.vb);
  const zones = spec.zones || [];
  const grid = Math.max(20, Math.round(Math.min(vb.w, vb.h) / 12));
  const label = id.replace(/_/g, ' ').toUpperCase();
  const art = vehicleArtwork(id, vb);
  const details = blueprintDetailLayer(id, spec, vb, zones);
  const dimY = Math.max(24, vb.h - 28);
  const dimX2 = Math.max(40, vb.w - 40);

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${spec.vb}">
  <rect width="${vb.w}" height="${vb.h}" fill="#050d18"/>
  <defs>
    <pattern id="fine" width="${grid / 2}" height="${grid / 2}" patternUnits="userSpaceOnUse">
      <path d="M ${grid / 2} 0 L 0 0 0 ${grid / 2}" fill="none" stroke="rgba(39,74,121,.08)" stroke-width=".4"/>
    </pattern>
    <pattern id="grid" width="${grid}" height="${grid}" patternUnits="userSpaceOnUse">
      <path d="M ${grid} 0 L 0 0 0 ${grid}" fill="none" stroke="rgba(39,74,121,.16)" stroke-width=".55"/>
    </pattern>
    <style>
      .skin{fill:#081c30;stroke:rgba(100,160,240,.76);stroke-width:1.35;vector-effect:non-scaling-stroke}
      .panel{fill:rgba(100,160,240,.035);stroke:rgba(100,160,240,.36);stroke-width:.9;stroke-dasharray:5 4;vector-effect:non-scaling-stroke}
      .glass{fill:rgba(100,160,240,.055);stroke:rgba(100,160,240,.38);stroke-width:.9;vector-effect:non-scaling-stroke}
      .rotor{fill:#061625;stroke:rgba(100,160,240,.58);stroke-width:1.15;vector-effect:non-scaling-stroke}
      .nozzle{fill:#050d18;stroke:rgba(137,255,168,.48);stroke-width:1;vector-effect:non-scaling-stroke}
      .major{fill:none;stroke:rgba(100,160,240,.48);stroke-width:1.15;vector-effect:non-scaling-stroke}
      .minor,.minor *{fill:none;stroke:rgba(100,160,240,.22);stroke-width:.75;vector-effect:non-scaling-stroke}
      .station{fill:none;stroke:rgba(100,160,240,.085);stroke-width:.5;stroke-dasharray:3 8;vector-effect:non-scaling-stroke}
      .zonewire{fill:none;stroke:rgba(159,211,255,.28);stroke-width:.75;stroke-dasharray:6 4;vector-effect:non-scaling-stroke}
      .zonewire.alt{stroke:rgba(137,255,168,.18)}
      .rivet{fill:rgba(100,160,240,.24);stroke:none}
      .callout-line{fill:none;stroke:rgba(159,211,255,.3);stroke-width:.65;stroke-dasharray:4 3;vector-effect:non-scaling-stroke}
      .callout{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:7px;letter-spacing:.1em;fill:rgba(230,236,245,.58)}
      .thrust-arc{fill:none;stroke:rgba(137,255,168,.25);stroke-width:.75;stroke-dasharray:5 4;vector-effect:non-scaling-stroke}
      .title{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:8px;letter-spacing:.28em;fill:rgba(159,211,255,.5)}
      .micro{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:6px;letter-spacing:.16em;fill:rgba(100,160,240,.32)}
      .dim{fill:none;stroke:rgba(100,160,240,.18);stroke-width:.55;vector-effect:non-scaling-stroke}
    </style>
  </defs>
  <rect width="${vb.w}" height="${vb.h}" fill="url(#fine)"/>
  <rect width="${vb.w}" height="${vb.h}" fill="url(#grid)"/>
  <text x="18" y="20" class="title">PLAN VIEW · ${esc(label)}</text>
  <line x1="${vb.w / 2}" y1="26" x2="${vb.w / 2}" y2="${Math.max(30, vb.h - 32)}" class="dim" stroke-dasharray="8 6"/>
  ${art}
  ${details}
  <line x1="40" y1="${dimY}" x2="${dimX2}" y2="${dimY}" class="dim"/>
  <line x1="40" y1="${dimY - 4}" x2="40" y2="${dimY + 4}" class="dim"/>
  <line x1="${dimX2}" y1="${dimY - 4}" x2="${dimX2}" y2="${dimY + 4}" class="dim"/>
  <text x="${vb.w / 2}" y="${Math.min(vb.h - 8, dimY + 13)}" text-anchor="middle" class="micro">OVERLAY-READY · ${esc(spec.view || 'SCHEMATIC')} · ${zones.length} ZONES</text>
</svg>
`;
}

function axisSvg(id, spec, axis) {
  const vb = parseVB(spec.vb);
  const zones = spec.zones || [];
  const grid = Math.max(20, Math.round(Math.min(vb.w, vb.h) / 12));
  const label = id.replace(/_/g, ' ').toUpperCase();
  const art = vehicleArtwork(id, vb);
  const isExterior = axis === 'exterior';

  const internalBlocks = zones.map((z, idx) => {
    const b = zoneBounds(z);
    const c = centroid(z);
    const fill = idx % 2 ? 'rgba(10,38,44,.48)' : 'rgba(8,28,48,.62)';
    const stroke = idx % 2 ? 'rgba(137,255,168,.46)' : 'rgba(159,211,255,.5)';
    const rect = `<rect x="${b.x.toFixed(1)}" y="${b.y.toFixed(1)}" width="${Math.max(8, b.w).toFixed(1)}" height="${Math.max(8, b.h).toFixed(1)}" rx="4" class="system" fill="${fill}" stroke="${stroke}"/>`;
    const text = `<text x="${c.x.toFixed(1)}" y="${c.y.toFixed(1)}" text-anchor="middle" dominant-baseline="middle" class="label">${esc(z.label || z.id)}</text>`;
    return `${rect}\n${connector(z, vb)}\n${text}`;
  }).join('\n');

  const flowLines = zones.slice(0, -1).map((z, idx) => {
    const a = centroid(z);
    const b = centroid(zones[idx + 1]);
    return `<path d="M${a.x.toFixed(1)} ${a.y.toFixed(1)} C${((a.x + b.x) / 2).toFixed(1)} ${a.y.toFixed(1)} ${((a.x + b.x) / 2).toFixed(1)} ${b.y.toFixed(1)} ${b.x.toFixed(1)} ${b.y.toFixed(1)}" class="flow"/>`;
  }).join('\n');

  const exteriorNote = `${esc(spec.view || 'SCHEMATIC')} · FORM / SILHOUETTE / REFERENCE PROPORTION`;
  const internalNote = `${zones.length} FUNCTIONAL SYSTEMS · LOAD PATH / FLOW / SUBSYSTEM RELATION`;

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${spec.vb}">
  <rect width="${vb.w}" height="${vb.h}" fill="#050d18"/>
  <defs>
    <pattern id="fine" width="${grid / 2}" height="${grid / 2}" patternUnits="userSpaceOnUse">
      <path d="M ${grid / 2} 0 L 0 0 0 ${grid / 2}" fill="none" stroke="rgba(39,74,121,.08)" stroke-width=".4"/>
    </pattern>
    <pattern id="grid" width="${grid}" height="${grid}" patternUnits="userSpaceOnUse">
      <path d="M ${grid} 0 L 0 0 0 ${grid}" fill="none" stroke="rgba(39,74,121,.16)" stroke-width=".55"/>
    </pattern>
    <style>
      .skin{fill:#081c30;stroke:rgba(100,160,240,.76);stroke-width:1.35;vector-effect:non-scaling-stroke}
      .panel{fill:rgba(100,160,240,.035);stroke:rgba(100,160,240,.36);stroke-width:.9;stroke-dasharray:5 4;vector-effect:non-scaling-stroke}
      .glass{fill:rgba(100,160,240,.055);stroke:rgba(100,160,240,.38);stroke-width:.9;vector-effect:non-scaling-stroke}
      .rotor{fill:#061625;stroke:rgba(100,160,240,.58);stroke-width:1.15;vector-effect:non-scaling-stroke}
      .nozzle{fill:#050d18;stroke:rgba(137,255,168,.48);stroke-width:1;vector-effect:non-scaling-stroke}
      .major{fill:none;stroke:rgba(100,160,240,.48);stroke-width:1.15;vector-effect:non-scaling-stroke}
      .minor,.minor *{fill:none;stroke:rgba(100,160,240,.22);stroke-width:.75;vector-effect:non-scaling-stroke}
      .ghost{opacity:.18}
      .system{stroke-width:.9;vector-effect:non-scaling-stroke}
      .flow{fill:none;stroke:rgba(137,255,168,.22);stroke-width:.8;stroke-dasharray:5 4;vector-effect:non-scaling-stroke}
      .lead{fill:none;stroke:rgba(159,211,255,.25);stroke-width:.6;stroke-dasharray:4 3;vector-effect:non-scaling-stroke}
      .title{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:8px;letter-spacing:.26em;fill:rgba(159,211,255,.64)}
      .label{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:${Math.max(6, Math.min(9, vb.w / 82)).toFixed(1)}px;letter-spacing:.06em;fill:rgba(230,236,245,.64)}
      .micro{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:6px;letter-spacing:.14em;fill:rgba(100,160,240,.34)}
      .dim{fill:none;stroke:rgba(100,160,240,.18);stroke-width:.55;vector-effect:non-scaling-stroke}
    </style>
  </defs>
  <rect width="${vb.w}" height="${vb.h}" fill="url(#fine)"/>
  <rect width="${vb.w}" height="${vb.h}" fill="url(#grid)"/>
  <text x="18" y="20" class="title">${isExterior ? 'EXTERIOR' : 'INTERNAL'} AXIS · ${esc(label)}</text>
  <text x="18" y="34" class="micro">${isExterior ? exteriorNote : internalNote}</text>
  <line x1="${vb.w / 2}" y1="42" x2="${vb.w / 2}" y2="${Math.max(46, vb.h - 34)}" class="dim" stroke-dasharray="8 6"/>
  ${isExterior ? art : `<g class="ghost">${art}</g>\n${flowLines}\n${internalBlocks}`}
  <text x="${vb.w / 2}" y="${Math.max(20, vb.h - 12)}" text-anchor="middle" class="micro">AXIS ${isExterior ? '1' : '2'} OF 3 · ${isExterior ? 'EXTERIOR RECOGNITION' : 'FUNCTIONAL STRUCTURE'}</text>
</svg>
`;
}

function presetIconGeometry(cat, type, conf) {
  const k = `${cat} ${type} ${conf}`.toLowerCase();
  if (k.includes('multirotor') || k.includes('quad') || k.includes('coax') || k.includes('tri_')) {
    return `
      <circle cx="170" cy="120" r="32" class="round"/><circle cx="430" cy="120" r="32" class="round"/>
      <circle cx="430" cy="300" r="32" class="round"/><circle cx="170" cy="300" r="32" class="round"/>
      <path d="M170 120 L300 210 L430 120 M170 300 L300 210 L430 300" class="line"/>
      <rect x="246" y="172" width="108" height="76" rx="5" class="body"/>`;
  }
  if (k.includes('wing') || k.includes('air') || k.includes('uav') || k.includes('turbofan') || k.includes('supersonic')) {
    return `
      <path d="M300 66 C282 112 274 166 274 262 C274 310 288 338 300 350 C312 338 326 310 326 262 C326 166 318 112 300 66 Z" class="body"/>
      <path d="M276 170 L80 270 L92 296 L278 230 Z" class="body"/>
      <path d="M324 170 L520 270 L508 296 L322 230 Z" class="body"/>
      <path d="M278 282 L172 322 L176 342 L284 304 Z" class="body"/>
      <path d="M322 282 L428 322 L424 342 L316 304 Z" class="body"/>`;
  }
  if (k.includes('rocket') || k.includes('nozzle') || k.includes('chamber') || k.includes('thruster') || k.includes('tank')) {
    return `
      <path d="M300 52 C262 92 252 154 252 230 L252 300 L348 300 L348 230 C348 154 338 92 300 52 Z" class="body"/>
      <path d="M260 300 L216 360 L384 360 L340 300 Z" class="body"/>
      <line x1="252" y1="190" x2="348" y2="190" class="line"/>
      <line x1="252" y1="244" x2="348" y2="244" class="line"/>`;
  }
  if (k.includes('marine') || k.includes('rov') || k.includes('underwater') || k.includes('hull') || k.includes('propeller')) {
    return `
      <path d="M92 210 C126 138 214 104 300 104 C386 104 474 138 508 210 C474 282 386 316 300 316 C214 316 126 282 92 210 Z" class="body"/>
      <rect x="222" y="164" width="156" height="92" rx="8" class="body"/>
      <circle cx="130" cy="210" r="26" class="round"/><circle cx="470" cy="210" r="26" class="round"/>`;
  }
  if (k.includes('robot') || k.includes('arm') || k.includes('joint') || k.includes('gripper')) {
    return `
      <circle cx="160" cy="284" r="48" class="round"/>
      <rect x="194" y="242" width="156" height="42" rx="8" class="body" transform="rotate(-18 272 263)"/>
      <circle cx="350" cy="210" r="36" class="round"/>
      <rect x="374" y="166" width="116" height="34" rx="7" class="body" transform="rotate(-26 432 183)"/>
      <path d="M482 150 L532 124 M490 166 L544 160" class="line"/>`;
  }
  if (k.includes('medical') || k.includes('prosthetic') || k.includes('brace') || k.includes('hand') || k.includes('orthosis')) {
    return `
      <path d="M254 78 C220 128 216 206 236 292 C248 338 276 360 300 362 C324 360 352 338 364 292 C384 206 380 128 346 78 Z" class="body"/>
      <path d="M238 186 L142 242 L158 274 L252 230 Z" class="body"/>
      <path d="M362 186 L458 242 L442 274 L348 230 Z" class="body"/>
      <circle cx="300" cy="136" r="36" class="round"/>`;
  }
  return `
    <rect x="148" y="128" width="304" height="164" rx="8" class="body"/>
    <circle cx="216" cy="210" r="42" class="round"/>
    <circle cx="384" cy="210" r="42" class="round"/>
    <line x1="148" y1="170" x2="452" y2="170" class="line"/>
    <line x1="148" y1="250" x2="452" y2="250" class="line"/>`;
}

function presetSvg(catKey, cat, typeKey, type, confKey, conf) {
  const title = `${cat.label} / ${type.label}`;
  const label = conf.label || confKey;
  const geometry = presetIconGeometry(catKey, typeKey, confKey);
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 420">
  <rect width="600" height="420" fill="#050d18"/>
  <defs>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M40 0 L0 0 0 40" fill="none" stroke="rgba(39,74,121,.14)" stroke-width=".55"/>
    </pattern>
    <style>
      .body{fill:#081c30;stroke:rgba(159,211,255,.76);stroke-width:1.4;vector-effect:non-scaling-stroke}
      .round{fill:#061625;stroke:rgba(137,255,168,.58);stroke-width:1.2;vector-effect:non-scaling-stroke}
      .line{fill:none;stroke:rgba(255,211,159,.5);stroke-width:1;stroke-dasharray:5 4;vector-effect:non-scaling-stroke}
      .title{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:8px;letter-spacing:.22em;fill:rgba(159,211,255,.52)}
      .label{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:18px;letter-spacing:.08em;fill:rgba(230,236,245,.88)}
      .micro{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:8px;letter-spacing:.12em;fill:rgba(100,160,240,.36)}
    </style>
  </defs>
  <rect width="600" height="420" fill="url(#grid)"/>
  <text x="22" y="26" class="title">${esc(title.toUpperCase())}</text>
  ${geometry}
  <rect x="32" y="338" width="536" height="50" rx="3" fill="rgba(5,13,24,.72)" stroke="rgba(39,74,121,.72)"/>
  <text x="300" y="360" text-anchor="middle" class="label">${esc(label)}</text>
  <text x="300" y="380" text-anchor="middle" class="micro">${esc(`${catKey}/${typeKey}/${confKey}`)}</text>
</svg>
`;
}

function writeAssemblyAssets() {
  ensureDir(OUT_IMG);
  let count = 0;
  let axisCount = 0;
  for (const [id, spec] of Object.entries(VEHICLE_SCHEMATICS)) {
    const target = path.join(OUT_IMG, `${id}_top.svg`);
    if (!MASTER_ASSEMBLY_IDS.has(id)) {
      fs.writeFileSync(target, assemblySvg(id, spec), 'utf8');
    }
    for (const axis of ['exterior', 'internal']) {
      const axisTarget = path.join(OUT_IMG, `${id}_${axis}.svg`);
      if (!MANUAL_AXIS_ASSET_IDS.has(id)) {
        fs.writeFileSync(axisTarget, axisSvg(id, spec, axis), 'utf8');
      }
      axisCount++;
    }
    count++;
  }
  return { topCount: count, axisCount };
}

function writePresetAssets() {
  ensureDir(OUT_PRESETS);
  let count = 0;
  for (const [catKey, cat] of Object.entries(PRESET_TREE)) {
    for (const [typeKey, type] of Object.entries(cat.types || {})) {
      const dir = path.join(OUT_PRESETS, catKey, typeKey);
      ensureDir(dir);
      for (const [confKey, conf] of Object.entries(type.configs || {})) {
        const presetId = `${catKey}/${typeKey}/${confKey}`;
        if (!MANUAL_PRESET_ASSET_IDS.has(presetId)) {
          fs.writeFileSync(path.join(dir, `${confKey}.svg`), presetSvg(catKey, cat, typeKey, type, confKey, conf), 'utf8');
        }
        count++;
      }
    }
  }
  return count;
}

const { topCount: assemblyCount, axisCount: assemblyAxisCount } = writeAssemblyAssets();
const presetCount = writePresetAssets();

console.log(JSON.stringify({
  assembly_top_svgs: assemblyCount,
  assembly_axis_svgs: assemblyAxisCount,
  preset_svgs: presetCount,
  total: assemblyCount + assemblyAxisCount + presetCount,
}, null, 2));
