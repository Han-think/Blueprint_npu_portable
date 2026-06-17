# Blueprint Engineering Source Intake Plan

Store legal source documents in:

```text
20_dataset/sources/
  nasa/
  nist/
  additive_guides/
  mit_ocw/
  manufacturer_guides/
  wikipedia_terms/
```

Do not train directly on whole PDFs first. Extract compact criteria into `20_dataset/criteria/*.json`, then cite the source in future `source_refs` fields.

## Priority PDF / Reference Intake

1. NASA Systems Engineering Handbook, NASA/SP-2016-6105 Rev2
   - Put in: `20_dataset/sources/nasa/nasa_systems_engineering_handbook_sp_2016_6105_rev2.pdf`
   - Use for: P0 flow, requirements, interface management, verification/validation, risk, decision analysis.

2. NASA Workmanship / technical standards pages
   - Put in: `20_dataset/sources/nasa/workmanship/`
   - Use for: inspection language, workmanship evidence, design review vocabulary.

3. NIST additive manufacturing reports and benchmark/test artifact documents
   - Put in: `20_dataset/sources/nist/additive_manufacturing/`
   - Use for: additive process evidence, benchmark vocabulary, process traceability.

4. Prusa / Formlabs / Xometry / Protolabs official design guides
   - Put in: `20_dataset/sources/additive_guides/`
   - Use for: wall, clearance, overhang, support, orientation, process limits.

5. MIT OCW machine design / robotics lecture notes
   - Put in: `20_dataset/sources/mit_ocw/`
   - Use for: linkages, joints, bearings, tolerances, load paths, robot mechanisms.

6. Manufacturer public fastener/bearing/tolerance guides
   - Put in: `20_dataset/sources/manufacturer_guides/`
   - Use for: screws, bearings, fits, joints, shaft/axis vocabulary.

7. Wikipedia / SEBoK term snapshots
   - Put in: `20_dataset/sources/wikipedia_terms/`
   - Use only for: vocabulary and high-level taxonomy, not numeric design authority.

## Extraction Rule

For every source, extract only:

```json
{
  "criterion": "short_machine_readable_name",
  "good": "observable good design evidence",
  "bad": "observable bad design evidence",
  "signals": ["words", "fields", "geometry_ops"],
  "loop_feedback": "specific next-generation improvement instruction",
  "source_refs": ["relative/path/or/url"]
}
```

The model should see compact criteria, not entire copyrighted books.
