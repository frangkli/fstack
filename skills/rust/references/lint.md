# Lint

Read when a lint gets in the way, when you want to disable one, or when the repo's config lacks or contradicts a lint this skill leaves to the tools. The baseline lint set, to set up or change a repo's Cargo lints or `clippy.toml`, is in the readiness skill's [stacks/rust.md](../../readiness/stacks/rust.md).

## Never loosen to get green

- A failing lint is fixed in the code. Keep every lint and level as it is, and keep each exception to the smallest item that needs it.
- Changing lint settings is a task of its own. Inside an unrelated change, propose the setting and its reason in your handoff instead.
- Where the repo's config lacks a lint the baseline has, write the code as if it were on, and propose it in your handoff.
- Where the repo's config contradicts this skill, the repo wins (SKILL.md, Precedence): write the code its way and name the conflict in your handoff.

## Exceptions on one item

Only where the code is right and the lint can't see why: the binary printing its output, the one call site that reads the clock, an `unsafe` block with a proven invariant. Then:

- Write `#[expect(clippy::<lint>, reason = "<why>")]` on the smallest item (a function, a statement, a block), never `#[allow]`. `#[expect]` warns once the lint stops firing, so a stale exception is removed with the code that needed it.
  ```rust
  #[expect(clippy::print_stdout, reason = "the command's output")]
  fn print_report(report: &Report) { println!("{report}"); }
  ```
- Never a crate-wide `#![expect]` or `#![allow]` for one site.
- List every exception in your handoff.

## When a lint may be turned off workspace-wide

Turn a lint off for the whole workspace only when it fires on code that follows this skill, across many sites, and say why in a comment beside it. "Too many warnings to fix now" is not a reason: fix them, or leave the lint on and propose the cleanup.
