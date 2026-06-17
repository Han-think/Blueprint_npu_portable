# Legal Engineering Source Staging

Put only legal/public source material here. Do not add pirated books, scanned textbooks, or shadow-library files.

Suggested layout:

```text
20_dataset/sources/
  nasa/
  nist/
  additive_guides/
  mit_ocw/
  manufacturer_guides/
  wikipedia_terms/
```

After adding a source, extract compact judgment rules into `20_dataset/criteria/*.json`.
The LLM loop should consume criteria summaries first, not raw PDFs.
