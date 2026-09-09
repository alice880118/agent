# Code Review mode

For Medium/High risk issues, once a PR exists. You are reviewing **the
diff against the issue's Acceptance Criteria** — not the whole repository,
and not your own opinion of how the code should ideally look.

## Focus on

- Bugs the diff introduces
- Regression risk to existing behavior
- Data loss (destructive migrations, overwritten records, dropped fields)
- Backward compatibility (old data / old callers hitting new code paths)
- Edge cases the Acceptance Criteria implies but the diff doesn't handle
- Unrelated or unnecessary changes riding along in the same diff

## Do not

- Suggest stylistic refactors unless they actually affect correctness
  (a rename, a "this could be cleaner" — not your job here)
- Review files the diff doesn't touch
- Pad the findings list to look thorough — an empty severity section is a
  fine, expected outcome

## Severity bar

- **Critical** — will cause data loss, a crash, or a security issue in
  normal use.
- **High** — breaks the Acceptance Criteria, breaks existing behavior for
  a meaningful set of users, or a clear regression.
- **Medium** — *only the meaningful ones*: a real edge case gap or
  backward-compat gap, not a nitpick. If you're unsure whether a Medium is
  "meaningful," leave it out.
- **Low** — never reported by this skill. If all you have is Low-severity
  observations, the section stays "None" — mention them to the user
  conversationally afterward if you think they're worth knowing, but don't
  put them in the handoff document GPT will act on.

## Output format — copy this exactly

This structure is fixed so the user can paste it straight to GPT and say
"fix only High #1 and Medium #1" — don't add sections, rename headers, or
change the numbering scheme.

```markdown
## PR Review

### Critical
- None

### High
1. [Short label]
   File: path/to/file
   Problem:
   One or two sentences on what breaks and how.

   Expected fix:
   One or two sentences on what should happen instead.

### Medium
1. [Short label]
   File: path/to/file
   Problem:
   ...

   Expected fix:
   ...

### Low
- None

## Recommendation
READY | READY AFTER FIX | NOT READY

## Fix Required
- High #1
- Medium #1
```

Rules for filling it in:
- Use `- None` (literally) for any severity section with nothing to
  report — don't delete the section.
- Number findings independently within each severity (`High #1`,
  `High #2`, `Medium #1`, ...) — GPT references them by that pair.
- **Recommendation**:
  - `READY` — no Critical/High/meaningful-Medium findings.
  - `READY AFTER FIX` — findings exist, but the diff would be mergeable
    once they're fixed; nothing here suggests the approach is wrong.
  - `NOT READY` — a Critical finding, or the findings suggest a deeper
    problem than a local fix (rare in Code Review — if you're this
    concerned, say the issue probably needed a Spec Review first).
- **Fix Required** lists only the finding refs GPT should actually act on
  — omit anything you flagged purely for the user's awareness (e.g. an
  observation that doesn't rise to a real finding).
