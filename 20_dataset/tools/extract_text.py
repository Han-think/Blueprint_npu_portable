"""Extract targeted page ranges from source PDFs into plain text.

Usage:
  python extract_text.py <pdf_path> <start_page> <end_page> <label>

Pages are 1-based inclusive. Output goes to
20_dataset/sources/_extracted/<pdf_stem>/<label>.txt

Whole-book extraction is intentionally not supported: criteria are built
from targeted chapters, and reference-class books must stay local-only.
"""
import sys
from pathlib import Path

from pypdf import PdfReader

MAX_PAGES = 80  # guard against accidental whole-book dumps


def main() -> None:
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    pdf_path = Path(sys.argv[1])
    start, end = int(sys.argv[2]), int(sys.argv[3])
    label = sys.argv[4]

    if end - start + 1 > MAX_PAGES:
        sys.exit(f"Refusing to extract more than {MAX_PAGES} pages at once.")

    reader = PdfReader(pdf_path)
    if not (1 <= start <= end <= len(reader.pages)):
        sys.exit(f"Page range out of bounds (document has {len(reader.pages)} pages).")

    out_dir = Path(__file__).resolve().parent.parent / "sources" / "_extracted" / pdf_path.stem
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{label}.txt"

    chunks = []
    for i in range(start - 1, end):
        chunks.append(f"--- page {i + 1} ---\n{reader.pages[i].extract_text() or ''}")
    out_file.write_text("\n\n".join(chunks), encoding="utf-8")
    print(f"Wrote {out_file} ({end - start + 1} pages)")


if __name__ == "__main__":
    main()
