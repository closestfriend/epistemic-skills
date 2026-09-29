---
name: pdf
description: Extracting text and tables from PDFs, filling PDF forms, splitting/merging documents, and generating PDFs in Python (pdfplumber, pypdf, reportlab) with OCR fallback for scanned pages. Use for any task that reads, edits, fills, or produces .pdf files. Not needed for HTML-to-PDF rendering or documents that are actually images without a PDF wrapper.
---

# pdf

PDF work is three different jobs wearing one extension. Pick the tool by job;
mixing them is how extractions come back empty and filled forms look blank.

## Applicability & fallback

- Preferred stack: `pdfplumber` (text/tables), `pypdf` (pages/forms/metadata),
  `reportlab` (generation/overlays). Install what's missing via pip.
- CLI fallback when Python libs misbehave: `pdftotext -layout` and `pdfimages`
  from poppler-utils.
- Scanned page (extraction returns ~nothing): rasterize + OCR —
  `pdf2image.convert_from_path()` → `pytesseract.image_to_string()`. Decide
  per page, not per document; hybrids are common.

## First: diagnose the document

```python
import pdfplumber
with pdfplumber.open(path) as pdf:
    page = pdf.pages[0]
    text = page.extract_text() or ""
print(len(text), text[:200])
```
- Real text → digital-born: extract directly.
- Empty/garbage (□□□, CID codes) → scanned or broken encoding: OCR path.
- Check `len(pdf.pages)` before assuming single-page; loop explicitly.

## Extraction quirks (digital-born)

- Reading order follows layout objects, not visual order — multi-column pages
  interleave. `extract_text(layout=True)` or crop by bbox per column when
  order matters.
- Tables: `page.extract_tables()` defaults work on ruled tables; borderless
  tables need `table_settings={"vertical_strategy": "text",
  "horizontal_strategy": "text"}`. Always verify row/column counts against
  the visible table before trusting.
- Numbers extracted from PDFs are strings with formatting glued on — strip
  currency symbols, thousands separators, and parentheses-negatives before
  arithmetic.
- Headers/footers repeat on every page; filter them before joining page text.

## Forms (AcroForm)

```python
from pypdf import PdfReader, PdfWriter
reader = PdfReader(path)
fields = reader.get_fields()          # REAL field names live here
print({k: v.get('/V') for k, v in (fields or {}).items()})

writer = PdfWriter(clone_from=path)   # clone keeps all pages + structure
writer.update_page_form_field_values(writer.pages[0], {"FieldName": "value"},
                                     auto_regenerate=False)
with open(out, "wb") as f: writer.write(f)
```
- Field names are exact internal identifiers (often like `topmostSubform[0].Page1[0].Name[0]`)
  — enumerate them first; never guess from the visible label.
- **Filled values can be invisible in viewers unless the form's
  NeedAppearances flag is set** — with pypdf, pass
  `writer.set_need_appearances_writer(True)` (or keep `auto_regenerate=False`
  and verify values programmatically). Checkboxes take their export value
  (often `/Yes`), not `True`.
- If the PDF has no AcroForm fields (flat scan of a form), fill by overlay:
  draw text at coordinates with reportlab on a transparent canvas, then merge
  onto the original page with pypdf.
- Coordinates are in points (72/inch) with **origin at bottom-left** — y goes
  up, not down.

## Verify before finishing

1. Reopen the output and extract what you wrote: form field values via
   `get_fields()`, or text via pdfplumber — confirm the exact values landed.
2. Page count and page order of the output match the requirement.
3. For extractions feeding calculations: spot-check 2–3 values against the
   source page visually (crop + print the region's text).
4. Output path and filename exactly as specified.
