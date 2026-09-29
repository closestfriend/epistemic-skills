---
name: xlsx
description: Reading, editing, and creating Excel workbooks (.xlsx/.xlsm) with openpyxl — preserving formulas and formatting, recalculating values, and writing correctly-typed cells. Use for any task that opens, modifies, analyzes, or produces spreadsheet files. Not needed for plain CSV/TSV work — use pandas directly for those.
---

# xlsx

Spreadsheet work with openpyxl. The library edits files faithfully but **never
computes formulas** — most spreadsheet failures trace to that one fact.

## Applicability & fallback

- openpyxl is the default tool; it is usually preinstalled where .xlsx work is
  expected (`pip install openpyxl` otherwise).
- For formula *evaluation* with no Excel available: `pip install formulas`
  (pure Python). If installs are blocked, compute the needed values yourself in
  Python and write literals where values are required (see Recalculation).

## The two-handle rule (avoids destroying the workbook)

`load_workbook(path)` gives formulas as strings; `data_only=True` gives the
values cached at last save — **and if you save from a `data_only` handle, every
formula in the file is permanently replaced by its cached value or None.**

```python
from openpyxl import load_workbook
wb  = load_workbook(path)                  # edit THIS one; formulas intact
wbv = load_workbook(path, data_only=True)  # read cached values; NEVER save
```

- Edited or newly written formulas have **no cached value** until something
  recalculates the file — reading them back via `data_only` yields None, not 0.
- Preserve what exists: modify cells in place; do not delete and rebuild sheets
  (that discards styles, widths, merges, names). Respect existing templates'
  formats rather than imposing your own.

## Recalculation (choose by what the deliverable needs)

1. **Deliverable wants formulas** (a working model): write the formulas with
   openpyxl and stop — do not try to also inject cached values.
2. **Deliverable wants correct values** and formulas are yours to choose:
   compute in Python (pandas/arithmetic) and write literal values with the
   right types and number formats. Simplest and most reliable.
3. **Both, or you must evaluate an existing workbook's formulas**:
   ```python
   import formulas                      # pip install formulas
   xl = formulas.ExcelModel().loads(path).finish()
   sol = xl.calculate()                 # keys like "'[book.xlsx]Sheet1'!A1"
   ```
   Use it to *read* computed results or produce a value-bearing copy; keep the
   formula-bearing original as the deliverable when formulas are required.
   `formulas` covers common functions; if it rejects a niche function, fall
   back to computing that cell in Python.

## Types and formats (what strict readers check)

- Write numbers as `int`/`float`, never `"123"` strings; write dates as
  `datetime` objects, not date-looking text.
- Percentages are stored as fractions: 12.5% is `0.125` with number format
  `0.0%`. Currency/thousands looks: set `cell.number_format` (e.g. `#,##0.00`)
  — formatting changes display, never the stored value.
- Formula strings start with `=` and use **English function names and comma
  separators** regardless of locale.
- Sheet names, header text, and cell addresses in the task are exact contracts
  — `Sheet1` ≠ `sheet1`. Check `wb.sheetnames` before assuming.
- Merged cells hold their value in the top-left cell only; unmerge or read
  that cell, don't iterate the merged range expecting copies.

## Verify before finishing

1. Reopen the saved file fresh. If formulas were required: confirm they are
   still formulas (`load_workbook(path)`, cell.value starts with `=`).
2. If values were required: confirm the numbers are numbers (not None, not
   text) at the exact cells/sheets named by the task.
3. Recompute one or two result cells independently in Python and compare.
4. Confirm the output path and extension match the task exactly.
