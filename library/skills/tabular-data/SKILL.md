---
name: tabular-data
description: Loading, cleaning, joining, and aggregating tabular data with pandas — dtype pitfalls, missing-value handling, joins that silently multiply rows, and exact-output formatting. Use for CSV/TSV/JSON-records analysis tasks and any computation feeding a numeric answer. Not needed for Excel-specific mechanics (see xlsx) or one-off arithmetic.
---

# tabular-data

Most wrong answers from tabular work are silent: a dtype coerced, a join
duplicated, a NaN dropped. Make each step observable and check invariants.

## Applicability & fallback

- Tool: pandas (usually preinstalled; else `pip install pandas`).
- Small data + no pandas: `csv` module + plain Python is fine — correctness
  rules below still apply, the library doesn't matter.

## Load skeptically

```python
df = pd.read_csv(path)          # then LOOK at it before computing
print(df.shape, df.dtypes, df.head(3), df.isna().sum(), sep="\n")
```

- IDs, codes, and phone/zip columns must stay **strings**: pass
  `dtype={"id": str}` or leading zeros vanish and `1e12` notation appears.
- Numeric columns arriving as `object` contain formatting debris — strip
  `$ , % ( )` then `pd.to_numeric(s, errors="raise")`. Use `errors="raise"`,
  not `"coerce"`, so bad cells surface instead of becoming silent NaN.
- Parse dates explicitly (`pd.to_datetime(s, format=...)`); never rely on
  inference for day/month order.
- Check the delimiter and header row assumption — `sep`, `header`, `skiprows`.

## Joins & aggregation (where answers silently go wrong)

- Before merging, check key uniqueness: `df.key.duplicated().any()`. A
  many-to-many join multiplies rows and inflates every downstream sum.
  Assert expected row counts after each merge:
  `pd.merge(a, b, on=k, validate="one_to_many")` makes the assumption explicit.
- `groupby` drops NaN keys by default (`dropna=True`) — decide deliberately.
- Means of means ≠ overall mean; aggregate from row level unless the task
  says otherwise. For weighted stats, state weights explicitly.
- After filtering, confirm the filter did what you think:
  `len(df_before), len(df_after)` and a peek at excluded rows.

## Missing values

- Distinguish "missing" from zero and from empty string; `fillna(0)` changes
  statistics — only do it when the task's semantics say absent means zero.
- Count and report drops: if you `dropna`, know how many rows went and why.

## Output contract

- Round only at the final step, to the exact precision requested, using the
  requested convention (`round()` is banker's rounding; some tasks expect
  half-up — check the example values).
- Match requested column names, order, index inclusion (`to_csv(index=False)`
  unless an index is asked for), and file path exactly.
- Percentages: confirm whether the contract wants `12.5` or `0.125` or
  `"12.5%"` — all three appear in the wild.

## Verify before finishing

1. Recompute one output value by an independent route (raw-Python loop over
   the source rows, or a hand calculation on a small slice) and compare.
2. Sanity-bound results: totals ≥ parts, rates within [0,1] or [0,100],
   dates within the data's range.
3. Reload the file you wrote and check shape, dtypes, and one value.
