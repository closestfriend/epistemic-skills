---
name: pptx
description: Creating and editing PowerPoint decks with python-pptx — placeholders and layouts, tables built from data, and text/run formatting. Use for any task reading or producing .pptx files. Not for Word documents or PDF slides.
---

# pptx

python-pptx edits decks reliably but has a strict object model: slides own
shapes, shapes own text frames, text frames own paragraphs, paragraphs own
runs. Formatting lives on runs and fonts, not on "the slide".

## Applicability & fallback

- Tool: `python-pptx` (`pip install python-pptx`; import name `pptx`).
- No native "copy slide" API — build new slides from layouts instead.

## Geometry & units

Positions/sizes are EMUs — always construct with helpers, never raw ints:

```python
from pptx.util import Inches, Pt, Emu
shape = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(4), Inches(1))
```

Font sizes use `Pt`. Colors: `from pptx.dml.color import RGBColor;
run.font.color.rgb = RGBColor(0x1F, 0x2A, 0x44)`.

## Templates, layouts, placeholders

```python
from pptx import Presentation
prs = Presentation(template_path)            # opening a template keeps its design
slide = prs.slides.add_slide(prs.slide_layouts[1])   # inspect layouts by name first
slide.shapes.title.text = "Q3 Review"
for ph in slide.placeholders:                # idx values vary by layout
    print(ph.placeholder_format.idx, ph.name)
body = slide.placeholders[1]
```

- Enumerate layouts (`[l.name for l in prs.slide_layouts]`) and placeholder
  idx values before assuming — they differ per template.
- Editing an existing deck: iterate `prs.slides`, guard every shape with
  `shape.has_text_frame` before touching text; recurse into
  `shape.shapes` when `shape.shape_type == MSO_SHAPE_TYPE.GROUP`.

## Tables from data (the spreadsheet-to-slide pattern)

```python
rows, cols = len(data) + 1, len(headers)
tbl = slide.shapes.add_table(rows, cols, Inches(0.5), Inches(1.5),
                             Inches(9), Inches(0.3 * rows)).table
for c, h in enumerate(headers):
    tbl.cell(0, c).text = str(h)
for r, row in enumerate(data, start=1):
    for c, val in enumerate(row):
        tbl.cell(r, c).text = fmt(val)       # you format; pptx won't
```

- Table cells hold **text only** — there are no number formats. Render values
  exactly as the task requires (`"1,234.50"`, `"12.5%"`) before insertion,
  matching the source's displayed formatting when copying from a spreadsheet.
- Setting `cell.text` replaces the cell's paragraphs and resets formatting —
  set text first, then re-apply font properties via
  `cell.text_frame.paragraphs[0].runs[0].font`.
- Column widths: assign `tbl.columns[i].width = Inches(...)` explicitly;
  defaults are uniform and usually wrong.

## Text formatting model

- A paragraph's formatting (`alignment`, `level`) is separate from its runs'
  (`font.size`, `bold`, `name`). Bullet indent = `paragraph.level` (0-based).
- To restyle existing text without losing it, edit `run.font` attributes;
  don't rebuild paragraphs unless replacing content.
- Overflow is silent: nothing errors when text exceeds its box. Estimate
  need as `chars × 0.5 × font_pt` points of width (≈ average glyph = half
  the em). To make text fit on one line, adjust whichever dimension the task
  leaves free — **if the font size is specified, resize the box, not the
  font** (and vice versa). Never hard-break a line with `\n`.

```python
from pptx.util import Pt
need_w = int(len(text) * 0.5 * font_pt * 12700)        # EMU
shape.width  = max(shape.width, need_w)
shape.left   = (prs.slide_width - shape.width) // 2    # center horizontally
shape.top    = prs.slide_height - shape.height - Pt(20)  # e.g. bottom of slide
```

## Bullets & numbering (no API — requires paragraph XML)

python-pptx has no property for bullet style; set it on the paragraph's XML:

```python
from pptx.oxml.ns import qn

def set_bullet(para, style):
    """style: 'number' | 'bullet' | 'none'"""
    pPr = para._p.get_or_add_pPr()
    for tag in ("a:buChar", "a:buAutoNum", "a:buNone"):
        for el in pPr.findall(qn(tag)):
            pPr.remove(el)
    if style == "number":     # renders 1. 2. 3. automatically
        pPr.append(pPr.makeelement(qn("a:buAutoNum"), {"type": "arabicPeriod"}))
    elif style == "bullet":
        pPr.append(pPr.makeelement(qn("a:buChar"), {"char": "•"}))
    else:
        pPr.append(pPr.makeelement(qn("a:buNone"), {}))
```

Do NOT type literal "1." text to fake numbered lists — ordered-list checks
look for `buAutoNum`, and manual numbers break on reordering. Other
`buAutoNum` types: `arabicParenR` (1)), `romanUcPeriod` (I.), `alphaLcParenR` (a)).

## Reference / agenda slides (listing the deck's own contents)

When a slide must list titles you detected or edited elsewhere in the deck,
its entries are exactly that working set: complete title strings, deduplicated,
one per bullet. Never re-scrape the deck for other text — short names and
summary sentences from slide bodies are not titles — and never add
descriptions of your own.

## Verify before finishing

1. Reopen the saved file with `Presentation(out)`; confirm slide count and
   that required text/tables exist where specified (walk shapes and assert).
2. Titles, per slide, as one atomic check: no `\n` in the text, estimated
   width (`chars × 0.5 × font_pt`) fits the box width, and
   `paragraph.alignment == PP_ALIGN.CENTER` when titles are centered —
   verify all three together; fixing one while regressing another is the
   common failure.
3. For tables: assert row/col counts and spot-check 2–3 cell strings match
   the required formatting exactly.
4. For reference/agenda slides: every entry equals one processed title
   verbatim, and entry count equals the deduplicated title count — no short
   names, no summary text, no extras.
5. Output path and extension exactly as the task states.
