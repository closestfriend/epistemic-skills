---
name: optimization-modeling
description: Formulating and solving optimization problems — LP/MILP, assignment and scheduling, routing, constrained selection — with scipy, OR-Tools, or cvxpy, including feasibility debugging and solution verification. Use when a task asks to minimize/maximize something under constraints or find a valid schedule/assignment/plan. Not for unconstrained curve fitting (use scipy directly).
---

# optimization-modeling

Write the model on paper before writing code, and always hold a feasible
fallback: a working greedy solution beats a solver you cannot debug.

## Applicability & fallback (read this one first)

- Solvers repay their setup cost on hard combinatorial structure. For small
  instances (≲ a few thousand combinations) or nearly-greedy structure,
  **direct enumeration or a greedy pass is the better engineering choice** —
  simpler, debuggable, and often exactly what the task expects.
- If a solver returns infeasible/unbounded or you cannot make it converge
  within a few attempts, STOP: build the greedy/heuristic solution that
  satisfies all hard constraints, then improve it locally (swaps, 2-opt).
  Deliver valid-and-good over optimal-and-broken.

## Formulate first (5 lines of text, before any code)

1. Decision variables — what is chosen, discrete or continuous, bounds.
2. Objective — one expression; check its units and its direction (min/max).
3. Hard constraints — enumerate ALL from the task, including the implicit
   ones (non-negativity, one-assignment-per-item, capacity).
4. Soft preferences — only if the task scores them; otherwise ignore.
5. Instance size — decides the tool (see below).

## Tool by problem class (use what's installed; check first)

- **LP / MILP**: `scipy.optimize.milp` (scipy ≥1.9, almost always present):
  ```python
  from scipy.optimize import milp, LinearConstraint, Bounds
  import numpy as np
  res = milp(c=cost,                       # minimizes c @ x
             constraints=LinearConstraint(A, lb, ub),
             integrality=np.ones_like(cost),   # 1=integer, 0=continuous
             bounds=Bounds(0, 1))
  assert res.status == 0, res.message       # 0 = optimal
  ```
- **Scheduling / assignment with logical constraints**: OR-Tools CP-SAT
  (`from ortools.sat.python import cp_model`) — model with `NewIntVar`/
  `NewBoolVar`, `AddAllDifferent`, `OnlyEnforceIf`; check
  `status in (cp_model.OPTIMAL, cp_model.FEASIBLE)` before reading values.
- **Convex continuous** (portfolios, dispatch): cvxpy; prefer CLARABEL as
  solver when OSQP/ECOS fail on ill-conditioned problems.
- **Classical planning**: if the task provides PDDL, use the provided
  planner; validate plans step-by-step against preconditions, don't trust
  the planner's own claim.

## Feasibility debugging

- Infeasible model: remove constraint groups one at a time (or widen bounds)
  to find the smallest conflicting set — then reread the task; the conflict
  usually means you mistranslated a constraint, not that no solution exists.
- Check constraint sense (`<=` vs `>=`) and units (per-hour vs total) —
  the two most common formulation bugs.
- Integer variables silently relaxed to continuous produce fractional
  assignments — confirm integrality actually reached the solver.

## Verify before finishing

1. Re-check the returned solution against EVERY hard constraint with plain
   Python (independent of the solver's own status flag).
2. Recompute the objective from the solution directly; it must match the
   solver's reported value.
3. Sanity-bound: is the objective plausible vs a trivial baseline (empty
   solution, greedy)? An optimum *worse* than greedy means the model is
   wrong.
4. Output exactly the requested format — IDs, ordering, units, file path.
