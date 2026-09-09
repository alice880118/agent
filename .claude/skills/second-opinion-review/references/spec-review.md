# Spec Review mode

For High risk issues only, before any code is written. You're challenging
the *plan* — GPT's proposed technical approach, or the Issue itself if no
plan exists yet — not reviewing an implementation. The goal is to catch a
wrong approach while it's still cheap to change, since High-risk work
(storage migrations, auth, data-structure changes) is expensive to redo
once code exists.

## Focus on

- Data loss potential in the proposed approach
- Backward compatibility: what happens to existing data / existing users
  under this plan
- Missing edge cases the plan doesn't account for
- Scope creep or scope gaps against the Issue's Requirements / Non-goals
- Whether the plan is actually reversible/rollback-able if it goes wrong

## Do not

- Redesign the solution yourself — you're finding holes in the plan, not
  writing an alternative implementation
- Nitpick implementation details that don't exist yet (naming, file
  layout) — that's Code Review's job once there's a diff
- Manufacture concerns to seem thorough — `APPROVED` with zero concerns is
  a legitimate, expected outcome for a well-formed plan

## Output format — copy this exactly

```markdown
## Spec Review

### Verdict
APPROVED | NEEDS REVISION

### Concerns
1. [Short label]
   Risk:
   What could go wrong and under what condition.

   Question / suggestion:
   What the plan needs to answer or change before coding starts.

(- None, if APPROVED with nothing to flag)
```

Rules for filling it in:
- `APPROVED` means the plan is sound enough to start coding — concerns
  section may still list minor notes GPT should keep in mind, but nothing
  blocking.
- `NEEDS REVISION` means at least one concern should be resolved (by the
  user and GPT) before coding starts — don't mark this if your concerns
  are really just preferences.
- If a concern isn't really about the plan but about the Issue itself
  being underspecified (e.g. Acceptance Criteria doesn't cover an obvious
  case), say so directly — that goes back to the user/product-owner step,
  not to GPT.
