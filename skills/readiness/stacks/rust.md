# Rust stack

The recommended lint setup for a Rust repo: the default to offer for VAL-1 and VAL-2 when the repo has no config, and the settings to merge into an existing config. It also holds the never list that readiness copies into the repo's Rust `STYLE.md`. It matches the `rust` skill, which leaves every lint below to the tools. Confirm each lint name against the repo's pinned toolchain, and keep a repo's own lint set when it already does the job.

## Never

Mistakes that are costly once shipped and that the lints below don't catch. readiness copies this list into the `STYLE.md` beside the repo's Rust code (DOC-9), so implementers see it before the review does; the `rust` skill gives the reasons.

- Never panic on input (files, network payloads, config, requests, CLI arguments, env vars): return an error. `.expect("why this cannot fail")` is for a real invariant only.
- Never pass input inward unparsed: parse it once, where it enters, into types that can't hold invalid values.
- Never format a value into SQL text: bind every value.
- Never key an `FxHashMap` with values an attacker chooses: it has no protection against hash flooding, so use std's `HashMap` there.
- Never create an unbounded channel or queue: bound it, and decide whether a full one waits or drops and counts.
- Never run blocking or CPU-heavy work on the async runtime: do file and network I/O through the runtime's async APIs, and move CPU-heavy work to `spawn_blocking`.
- Never spawn a long-running task that can't be stopped: each one listens to a `CancellationToken`.
- Never retry an operation that isn't idempotent. To make a retried write idempotent, give it a dedup key derived from its content.
- Never accept unknown keys in a config or spec type: put `#[serde(deny_unknown_fields)]` on each, never together with `flatten`. Leave it off types that read upstream data (events, logs, third-party payloads).
- Never write a bare `#[instrument]`: it records every argument with `Debug`, secrets included. Write `skip_all` and name the fields.

## Cargo lints

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

## clippy.toml

Beside the root `Cargo.toml`:

```toml
allow-unwrap-in-tests = true
doc-valid-idents = ["GraphQL", "PostgreSQL", ".."]   # ".." keeps Clippy's defaults

# Library code takes the time and random values as parameters (the rust skill's Data rules).
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
