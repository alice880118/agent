# Risk classification

Used in Step 0 of `SKILL.md` to decide whether a review is warranted at
all, and which mode(s) apply. When the user hasn't already tagged the
issue, propose a tier using this table and ask them to confirm — don't
silently decide on their behalf, since getting this wrong either wastes a
review or skips one that mattered.

## Low risk — no Claude review

Copy/text changes, spacing, icon/color tweaks, small responsive fixes,
small pure-UI adjustments that don't touch data or app logic.

Examples: "Show only two tags on inspiration cards", fixing a mobile
overflow bug, adjusting button spacing.

→ Tell the user this goes straight through GPT + automated checks (lint /
typecheck / test / build) + their own UI/QA. Decline to review unless
explicitly overridden.

## Medium risk — Code Review only

New components, new interactive features, new fields added with a safe
fallback (e.g. a new `localStorage` field that degrades gracefully for
existing records), card/data ordering, custom styling backed by new state.

Examples: "Add custom colors for tags", "Add manual card ordering",
"Add description field to inspiration details".

→ No Spec Review needed — GPT's plan can be short and doesn't need to be
challenged up front. Do a Code Review once the PR exists.

## High risk — Spec Review + Code Review

Anything touching the data model or storage format, migrations, auth,
large refactors, or anything with a plausible path to data loss or to
breaking a large surface of existing functionality.

Examples: "Preserve local data across app updates" (storage migration),
authentication changes, database migrations, large refactors.

→ Spec Review before code is written (challenge the plan itself), then
Code Review once the PR exists (verify the implementation actually held
to what the reviewed spec promised).

## When it's ambiguous

If an issue sits between tiers — e.g. it touches persisted data but with
an obvious, low-risk fallback — say which two tiers you're weighing and
why, and let the user make the final call rather than picking silently.
