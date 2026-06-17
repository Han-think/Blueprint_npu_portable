const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const OUT_DIR = path.join(ROOT, 'data', 'blueprint', 'curation_evaluated');

function usage() {
  console.error('Usage: node scripts/evaluate_blueprint_curation.js <curation.jsonl>');
  process.exit(1);
}

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
  fs.writeFileSync(filePath, `${rows.map(row => JSON.stringify(row)).join('\n')}\n`, 'utf8');
}

function arr(value) {
  return Array.isArray(value) ? value : [];
}

function scorePartBlueprint(bp) {
  const reasons = [];
  let score = 0;

  if (!bp || typeof bp !== 'object') {
    return { score: 0, reasons: ['missing blueprint object'], decision: 'reject' };
  }

  const partTree = arr(bp.part_tree);
  const geometryOps = arr(bp.geometry_ops);
  const verify = arr(bp.verify);
  const risks = arr(bp.risk);
  const hasBrief = !!bp.brief && typeof bp.brief === 'object';
  const hasCadBrief = !!bp.cad_brief && typeof bp.cad_brief === 'object';
  const hasPrintProfile = !!bp.print_profile && typeof bp.print_profile === 'object';
  const hasSlicerJob = !!bp.slicer_job && typeof bp.slicer_job === 'object';

  if (hasBrief) score += 12; else reasons.push('missing brief');
  if (partTree.length >= 3) score += 14; else reasons.push('part_tree has fewer than 3 nodes');
  if (geometryOps.length >= 3) score += 18; else reasons.push('geometry_ops has fewer than 3 operations');
  if (hasCadBrief) score += 10; else reasons.push('missing cad_brief');
  if (hasPrintProfile) score += 10; else reasons.push('missing print_profile');
  if (hasSlicerJob) score += 6; else reasons.push('missing slicer_job');

  const passCount = verify.filter(v => String(v.result || '').toLowerCase() === 'pass').length;
  const failCount = verify.filter(v => String(v.result || '').toLowerCase() === 'fail').length;
  if (verify.length >= 2) score += 10; else reasons.push('verify has fewer than 2 checks');
  if (passCount >= 1) score += 8; else reasons.push('no passing verify checks');
  if (failCount === 0) score += 8; else reasons.push(`${failCount} failed verify checks`);

  const severeRisk = risks.some(r => /fail|fatal|unsafe|invalid|overstress|collision/i.test(JSON.stringify(r)));
  if (!severeRisk) score += 4; else reasons.push('severe risk keyword found');

  let decision = 'review';
  if (score >= 78 && failCount === 0 && geometryOps.length >= 3) decision = 'accept';
  if (score < 55 || failCount > 0 || geometryOps.length < 2) decision = 'reject';

  return { score, reasons, decision };
}

function scoreAssembly(payload) {
  const reasons = [];
  let score = 0;

  if (!payload || typeof payload !== 'object') {
    return { score: 0, reasons: ['missing assembly payload'], decision: 'reject' };
  }

  const parts = arr(payload.parts);
  const done = parts.filter(p => p.status === 'done' && p.blueprint);
  const valid = done.filter(p => p.valid === true);
  const errored = parts.filter(p => p.status === 'error');
  const total = parts.length || 1;
  const doneRatio = done.length / total;
  const validRatio = done.length ? valid.length / done.length : 0;

  if (payload.vehicle?.id) score += 10; else reasons.push('missing vehicle id');
  if (parts.length >= 3) score += 10; else reasons.push('assembly has fewer than 3 parts');
  if (doneRatio >= 0.9) score += 30; else reasons.push(`low done ratio ${done.length}/${total}`);
  if (validRatio >= 0.75) score += 20; else reasons.push(`low valid ratio ${valid.length}/${done.length || 0}`);
  if (errored.length === 0) score += 15; else reasons.push(`${errored.length} errored parts`);

  const partScores = done.map(p => scorePartBlueprint(p.blueprint));
  const avgPartScore = partScores.length
    ? partScores.reduce((sum, r) => sum + r.score, 0) / partScores.length
    : 0;
  if (avgPartScore >= 70) score += 15; else reasons.push(`low average part score ${avgPartScore.toFixed(1)}`);

  let decision = 'review';
  if (score >= 82 && doneRatio >= 0.9 && errored.length === 0) decision = 'accept';
  if (score < 60 || doneRatio < 0.7 || errored.length > 0) decision = 'reject';

  return { score: Math.round(score), reasons, decision, part_score_average: Math.round(avgPartScore) };
}

function evaluateRecord(record) {
  const manualDecision = record.decision || 'candidate';
  const payload = record.payload;
  const result = record.kind === 'assembly'
    ? scoreAssembly(payload)
    : scorePartBlueprint(payload);

  let finalDecision = result.decision;
  if (manualDecision === 'reject') finalDecision = 'reject';
  if (manualDecision === 'keep' && result.decision === 'review') finalDecision = 'accept';
  if (manualDecision === 'keep' && result.decision === 'reject') finalDecision = 'review';

  return {
    ...record,
    auto_eval: {
      schema: 'blueprint_curation_auto_eval.v1',
      score: result.score,
      decision: result.decision,
      final_decision: finalDecision,
      reasons: result.reasons,
      part_score_average: result.part_score_average,
      evaluated_at: new Date().toISOString(),
    },
  };
}

const input = process.argv[2];
if (!input) usage();

const inputPath = path.resolve(process.cwd(), input);
const rows = readJsonl(inputPath).map(evaluateRecord);
const accepted = rows.filter(r => r.auto_eval.final_decision === 'accept');
const review = rows.filter(r => r.auto_eval.final_decision === 'review');
const rejected = rows.filter(r => r.auto_eval.final_decision === 'reject');

fs.mkdirSync(OUT_DIR, { recursive: true });
const stem = path.basename(inputPath).replace(/\.jsonl$/i, '');
const outAccepted = path.join(OUT_DIR, `${stem}.accepted.jsonl`);
const outReview = path.join(OUT_DIR, `${stem}.review.jsonl`);
const outRejected = path.join(OUT_DIR, `${stem}.rejected.jsonl`);
const outSummary = path.join(OUT_DIR, `${stem}.summary.json`);

writeJsonl(outAccepted, accepted);
writeJsonl(outReview, review);
writeJsonl(outRejected, rejected);

const summary = {
  schema: 'blueprint_curation_eval_summary.v1',
  input: inputPath,
  outputs: {
    accepted: outAccepted,
    review: outReview,
    rejected: outRejected,
  },
  counts: {
    total: rows.length,
    accepted: accepted.length,
    review: review.length,
    rejected: rejected.length,
  },
  score: {
    average: rows.length ? Math.round(rows.reduce((sum, r) => sum + r.auto_eval.score, 0) / rows.length) : 0,
    accepted_average: accepted.length ? Math.round(accepted.reduce((sum, r) => sum + r.auto_eval.score, 0) / accepted.length) : 0,
  },
};

fs.writeFileSync(outSummary, `${JSON.stringify(summary, null, 2)}\n`, 'utf8');
console.log(JSON.stringify(summary, null, 2));
