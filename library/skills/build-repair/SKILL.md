---
name: build-repair
description: Diagnosing and fixing failing builds, test suites, and CI checks — reproducing the failure, classifying code vs configuration vs dependency causes, making minimal fixes, and proving the build green. Use for any task about a broken build, failing tests, dependency conflicts, or compilation errors. Not for writing new features.
---

# build-repair

Fix builds by reproducing first and changing least. The failure message you
actually observe outranks any theory about what should be wrong.

## Applicability & fallback

- Language-agnostic method; examples are Python-flavored (adapt commands).
- If the stated build command doesn't exist (no CI config, no Makefile),
  derive it from the repo: packaging metadata → install; test dir → pytest.

## Step 1 — reproduce and capture

```bash
cd <repo> && <build/test command> 2>&1 | tee /tmp/build.log; echo "exit: $?"
```

- Run the *project's* command (CI workflow file, Makefile, `pyproject.toml`
  scripts), not a generic guess. Read `.github/workflows/*` for the real one.
- Read the FIRST error, not the last: cascades bury the root cause at the
  top. Grep the log for `error|Error|ERROR|failed` and scroll up from the
  first hit.

## Step 2 — classify before editing

- **Code**: syntax errors, bad imports, type errors, failing assertions with
  clear diffs. Fix at the exact site; keep the project's style.
- **Configuration**: wrong paths, missing entries in packaging/config files,
  version fields that don't match reality (e.g. a package requiring a Python
  the environment doesn't have).
- **Dependency**: resolver conflicts, yanked/missing versions, lockfile out
  of sync with the manifest, transitive pins colliding. Compare what the
  manifest requests vs what's installed (`pip list` / `uv pip list`).
- A test that fails only in CI usually means an environment difference —
  network access, timezone/locale, missing service, or test-order coupling —
  not broken code. Reproduce the CI conditions before "fixing" the code.

## Step 3 — minimal diff

- Change the fewest lines that make the failure pass for the *right reason*.
  No refactors, no formatting sweeps, no upgrading unrelated pins.
- Loosening a version constraint: prefer the narrowest change (bump one
  bound), and re-run the resolver to confirm it actually resolves.
- Never delete or skip a failing test to go green unless the task explicitly
  says the test is wrong. Silencing is not fixing.
- If the task asks for notes/analysis files as deliverables, write them with
  the same care as the fix — they are usually checked.

## Step 4 — prove it

```bash
<same build/test command> 2>&1 | tail -20; echo "exit: $?"
```

1. The original command exits 0 — the whole suite, not just the one test you
   were staring at (your fix may have broken siblings).
2. Confirm your intended diff is the only diff: `git diff --stat`.
3. If you created analysis/notes deliverables, re-read them for accuracy
   against what you actually did — stale plans in notes files fail checks.
