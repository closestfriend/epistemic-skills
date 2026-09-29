---
name: task-discipline
description: Checklist for producing an exact required deliverable — filling a template, generating a report or document, computing values, converting files, or writing results to a specified path. Read this FIRST for any task that names an output file or format, and again before declaring the task complete. Prevents the commonest failures - unmet requirements, wrong paths, and unverified output.
---

# task-discipline

How to turn a task description into a correct deliverable. Requirements are
exact: most preventable failures are contract misses, not capability misses.

## Applicability & fallback

- Applies to any task with stated deliverables. Costs nothing beyond this page.
- If it conflicts with the task's own instructions, the task wins. Always.

## Read the contract first

1. Before writing code, extract every hard requirement into a short checklist:
   exact output paths, file names, formats, units, rounding, column/field names,
   ordering, encodings. Quote them — do not paraphrase from memory.
2. Distinguish the *goal* (what must be true at the end) from *suggested means*
   (how the text hints you might do it). Satisfy the goal; treat the means as
   optional advice.
3. Note conditionals ("if X, also do Y") — correctness usually hinges on both
   branches, not just the happy path.
4. Inspect provided inputs before processing them: open the file, print the
   schema, check row counts and dtypes. Assumptions about structure are the
   top source of silently wrong outputs.

## Produce to spec, not to taste

- Write outputs to the **exact** path given, including directory and extension.
  `/root/out.json` is not `./out.json` or `/root/output.json`.
- Match formats literally: if the example shows `"2.50"`, decide whether the
  contract is a string, two decimals, or both — and reproduce it.
- Do not add unrequested extras (columns, keys, commentary, headers). Extras
  break strict comparisons as surely as omissions.
- Preserve anything you were told to keep (existing formatting, template
  structure, untouched rows). Edit minimally; never regenerate what you can
  modify in place.

## Verify before declaring done

1. Re-read your requirement checklist and check off each item against the
   actual artifact — reopen the file you wrote, don't trust that you wrote it.
2. Recompute one or two representative values independently (different code
   path or manual arithmetic) and compare.
3. Run the deliverable through its consumer once if cheap: reload the JSON,
   reopen the spreadsheet, re-render the document. A file that won't parse is
   a zero regardless of its contents.
4. If a step failed or was skipped, say so and fix it — never report success
   based on intention. An errored command that "should have worked" did not
   work.

## When stuck

Prefer a simple method that fully satisfies the contract over a sophisticated
one you cannot finish or debug. Partial credit usually follows deliverables,
not ambition.
