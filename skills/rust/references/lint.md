# Lint

Read when a lint gets in the way, when you want to disable one, or when you set up or change a repo's workspace lints or `clippy.toml`. The repo's config wins (SKILL.md, Precedence); the baseline below is for a repo that has none, or for proposing what it lacks.

## Never loosen to get green

- A failing lint is fixed in the code. Keep every lint and level as it is, and keep each exception to the smallest item that needs it.
- Changing lint settings is a task of its own. Inside an unrelated change, propose the setting and its reason in your handoff instead.
- Where the repo's config lacks a lint the baseline has, write the code as if it were on, and propose it in your handoff.
- Where the repo's config contradicts this skill, the repo wins: write the code its way and name the conflict in your handoff.

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

## Baseline

In a workspace, set the lints once in the root `Cargo.toml` and inherit them in each member with `[lints] workspace = true`; a single crate sets them in its own `[lints]` tables. CI denies every warning (`cargo clippy --workspace --all-targets -- -D warnings`), so `warn` here means "fails CI" while still letting a local build finish mid-edit.

```toml
[workspace.lints.rust]
unsafe_code = "deny"                 # each unsafe block carries #[expect(unsafe_code, reason)] and a // SAFETY: comment
unsafe_op_in_unsafe_fn = "warn"      # an unsafe fn body still marks each unsafe operation
unreachable_pub = "warn"             # pub only for what another crate can reach
missing_docs = "warn"                # every public item states its contract

# Groups first, then the allows that loosen them, then single lints.
[workspace.lints.clippy]
pedantic = { level = "warn", priority = -1 }
nursery = { level = "warn", priority = -1 }
must_use_candidate = "allow"         # fires on nearly every getter; #[must_use] goes on plan and guard types instead
similar_names = "allow"              # flags names one letter apart that a reader tells apart at a glance
missing_errors_doc = "allow"         # the error type's variants document the failures
missing_panics_doc = "allow"         # the .expect message states the invariant
missing_const_for_fn = "allow"       # const is an API promise; add it on purpose, not on every candidate
option_if_let_else = "allow"         # rewrites a readable match into map_or_else
use_self = "allow"                   # naming the type and writing Self read equally well
or_fun_call = "allow"                # flags cheap constructors as if they were costly
cognitive_complexity = "allow"       # an unreliable metric; review checks that functions stay flat
redundant_pub_crate = "allow"        # contradicts rustc's unreachable_pub
allow_attributes = "warn"            # exceptions use #[expect(..., reason = "...")]
allow_attributes_without_reason = "warn"
clone_on_ref_ptr = "warn"            # write Arc::clone(&x), so a cheap clone looks cheap
dbg_macro = "warn"
error_impl_error = "warn"            # a type named `Error` hides which error it is
exit = "warn"                        # process::exit skips destructors; return ExitCode
format_push_string = "warn"          # write! into the String instead
get_unwrap = "warn"
mod_module_files = "warn"            # foo.rs next to foo/, never mod.rs
print_stderr = "warn"                # libraries emit tracing events; the binary opts in where it writes output
print_stdout = "warn"
redundant_clone = "warn"
todo = "warn"
undocumented_unsafe_blocks = "warn"
unimplemented = "warn"
unused_result_ok = "warn"            # `.ok();` throws an error away without a trace
unwrap_used = "warn"                 # write .expect("why this cannot fail") instead
```

And beside it, `clippy.toml`:

```toml
allow-unwrap-in-tests = true
doc-valid-idents = ["GraphQL", "PostgreSQL", ".."]   # ".." keeps Clippy's defaults

# Library code takes the time and random values as parameters (SKILL.md, Data).
# The few binary call sites that need them carry #[expect(clippy::disallowed_methods, reason = "...")].
# allow-invalid: these paths exist only in builds that enable the crate or feature.
disallowed-methods = [
    { path = "std::time::SystemTime::now", reason = "take the time as a parameter", allow-invalid = true },
    { path = "std::time::SystemTime::elapsed", reason = "reads the clock; take the time as a parameter", allow-invalid = true },
    { path = "std::time::Instant::now", reason = "take the time as a parameter", allow-invalid = true },
    { path = "tokio::time::Instant::now", reason = "take the time as a parameter", allow-invalid = true },
    { path = "chrono::Utc::now", reason = "take the time as a parameter", allow-invalid = true },
    { path = "chrono::Local::now", reason = "take the time as a parameter", allow-invalid = true },
    { path = "uuid::Uuid::new_v4", reason = "derive ids from content, or take one as a parameter", allow-invalid = true },
    { path = "uuid::Uuid::now_v7", reason = "reads the clock; derive ids from content, or take one as a parameter", allow-invalid = true },
]
```

- Add to `disallowed-methods` the other ways your dependencies read the clock, randomness or the environment (`rand::random`, `std::env::var`) where library code must not, each with a reason that says what to write instead.
- Add the repo's product and protocol names to `doc-valid-idents`, so `doc_markdown` doesn't ask for backticks around them.
- Code that measures elapsed time (a timeout, a progress bar) belongs in the binary or behind a clock parameter, which is why `Instant::now` is on the list.
