---
name: docx
description: Editing and generating Word documents with python-docx — template placeholder filling (including placeholders split across runs), conditional sections spanning multiple paragraphs, tables, headers/footers, and format preservation. Use for any task reading or producing .docx files. Not for PDFs or plain text.
---

# docx

Word templates break naive edits in two specific ways: placeholders split
across XML runs, and conditional blocks spanning multiple paragraphs. Handle
both, then verify by rescanning the saved file.

## Applicability & fallback

- Tool: `python-docx` (`pip install python-docx`; import name is `docx`).
- If a template's structure defeats run-level surgery, a .docx is a zip of
  XML — as a last resort, edit `word/document.xml` textually and re-zip.

## Placeholder replacement (split-run safe)

Word fragments text like `{{NAME}}` into multiple runs unpredictably. Never
search runs; search the paragraph's full text, then rewrite its runs:

```python
import re
PLACEHOLDER = re.compile(r"\{\{([A-Za-z0-9_]+)\}\}")   # allow digits: LINE2, Q3

def all_paragraphs(doc):
    """Every paragraph: body, tables (nested too), headers, footers."""
    def walk(table):
        for row in table.rows:
            for cell in row.cells:
                yield from cell.paragraphs
                for nested in cell.tables:      # tables nest inside cells
                    yield from walk(nested)
    yield from doc.paragraphs
    for t in doc.tables:
        yield from walk(t)
    for s in doc.sections:
        yield from s.header.paragraphs
        yield from s.footer.paragraphs

def fill_paragraph(para, data):
    text = para.text
    new = PLACEHOLDER.sub(lambda m: str(data.get(m.group(1), m.group(0))), text)
    if new != text and para.runs:
        para.runs[0].text = new          # first run keeps its formatting
        for r in para.runs[1:]:
            r.text = ""

for p in all_paragraphs(doc):
    fill_paragraph(p, data)
```

`doc.paragraphs` alone misses most text — placeholders hide in nested tables
and headers/footers. Use the walker above for **every** pass (fill and verify).

## Conditional sections — usually MULTI-paragraph

`{{IF_X}} ... {{END_IF_X}}` markers commonly sit in *different* paragraphs
with whole paragraphs between them. Same-paragraph string surgery cannot
remove such a block. Work at the body level:

```python
def apply_conditional(doc, key, keep):
    start, end = "{{IF_%s}}" % key, "{{END_IF_%s}}" % key
    inside = False
    for para in list(doc.paragraphs):
        has_s, has_e = start in para.text, end in para.text
        if keep:                          # keep content, strip markers only
            if has_s or has_e:
                fill_paragraph_text(para, para.text.replace(start, "").replace(end, ""))
                if not para.text.strip():
                    para._element.getparent().remove(para._element)
        else:                             # drop markers AND everything between
            if has_s: inside = True
            if inside or has_s or has_e:
                para._element.getparent().remove(para._element)
            if has_e: inside = False
```

(`fill_paragraph_text` = write via first run as above.) Handle the
same-paragraph case too: if start and end share a paragraph, string-replace
within it. Decide `keep` from the data (e.g. `"Yes"`/`"No"` flags — compare
case-insensitively and strip whitespace).

## Format & structure preservation

- Modify the template in place; never rebuild the document from scratch —
  styles, numbering, and layout live in parts you won't reproduce.
- Empty leftover paragraphs from removed blocks leave visible blank gaps;
  remove the paragraph element, not just its text.
- Values go in as strings: format numbers/dates the way the letter should
  read (`$15,000`, `March 3, 2026`), not as raw data (`15000.0`).

## Verify before finishing (catches ~every template failure)

Run this after saving — it is part of the task, not optional:

```python
from docx import Document
out = Document(output_path)
leftovers = [p.text for p in all_paragraphs(out)
             if PLACEHOLDER.search(p.text) or "{{IF_" in p.text or "{{END_IF_" in p.text]
assert not leftovers, f"unfinished: {leftovers}"
```

Any `{{...}}` surviving anywhere in the saved file — body, nested tables,
headers, footers — is an unfinished job: fix and re-verify until this passes.
Also confirm conditional content: present when it should be, absent (markers
included) when it shouldn't. Save to the exact output path requested.
