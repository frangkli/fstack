# Review and polish

Read when reviewing Rust, or when polishing code that already works (a style pass, a review lane). A review checks SKILL.md's rules first, since those decide correctness; this file adds the idioms a style pass can find and fix, and the design-review checklist. Mechanical rules stay with Clippy (the readiness skill's [stacks/rust.md](../../readiness/stacks/rust.md)).

Precedence is SKILL.md's: the repo's config and conventions win. Change idioms only in code the task touches; mention the rest in the handoff.

## Naming

The repo's own naming rules come first. These are the Rust-specific ones:

- **Name associated functions by the Rust API Guidelines.** `new` and `with_*` construct, `from_*` converts, `as_*` borrows cheaply, `to_*` computes a new value, and `into_*` consumes `self`. A reader decides from the prefix whether a call allocates or consumes.
- **Put the category word last, and keep one word order across a family.** std writes `ParseIntError` and `ParseFloatError`, never `IntParseError` beside them.
- **Name a type for the data it owns, not its role.** Write `Pool`, not `ConnectionManager`, and name no type `Manager`, `Service` or `Factory`; traits are exempt. A role name hides what the type holds.
- **Implement `Deref` only from a newtype to the view it wraps,** as `String` does to `str`. `Deref` used for inheritance makes method lookup surprising.

## Idioms

- **Move values out with `std::mem::take`, `Option::take` or `mem::replace`,** not clone-then-clear.
- **Store immutable strings and lists as `Box<str>` and `Box<[T]>`.** They drop the unused capacity and say the value won't grow. Reach for `Cow` only on a measured path ([patterns.md](patterns.md)).
- **Derive `Copy` on small plain values and pass them by value.** Index ids, fieldless enums and spans are `Copy`, so take `OrderIdx`, not `&OrderIdx`. Derive `Clone` on a large type only when a caller needs a second copy.
- **Write formatted text straight into its destination.** Use `write!` into a `String` or writer, or a `Display` impl, instead of `push_str(&format!(..))` or a temporary `String` that is printed once.
- **Derive `Debug` on value, error and report types, and `PartialEq`, `Eq`, `Hash` and `Ord` on value types that need comparing or deduplicating.** Comparing `format!("{x:?}")` strings is an equality check by accident.
- **Write error messages as lowercase fragments with no final period** that name the action and its operand: `cannot read config app.toml`. Chain printers join them with `: `, so a capital or a period lands mid-sentence.

## std

- Collect fallible iterators into `Result<Vec<_>, _>`.
- Use `Option` and `Result` combinators (`map`, `and_then`, `ok_or_else`, `unwrap_or_default`, `is_some_and`) when one expression covers both cases, and `match` or `let`-`else` when a case has its own logic.
- Group with `entry(key).or_default()`.
- Filter and sort in place with `retain`, `extract_if`, `sort_by_cached_key` and `chunk_by`.
- Handle paths with `Path` and `OsStr` methods, never string operations: a path need not be UTF-8, and separators differ by platform.
- Return `ExitCode` from `main` instead of calling `process::exit`, which skips destructors.

## Tracing

- **Emit `tracing` spans at phase boundaries in library crates:** loading, parsing, each request, each job, each query. Only the binary depends on `tracing-subscriber`, writes to stderr and reads `RUST_LOG`; a library that installs a subscriber takes the choice away from its caller.
- **Give spans static names and put identifiers in fields.** Use `import` with `source = %name`, never `format!("import {name}")` as the name, so spans group and filter by name.
- **Record data as structured fields and keep the message a fixed phrase:** `debug!(queue = %name, job_count = n, "batch claimed")`. Fields can be queried; text in a message can't.
- **Write `#[instrument(level = "debug", skip_all, fields(..))]`.** A bare `#[instrument]` records every argument with `Debug`, which can dump whole request bodies and secrets.
- **Use `debug` and `trace` for events in library crates.** A problem the user must see reaches them as data (a returned error, a skipped count, a health report), never only as a log line.
- **Keep disabled events cheap.** Put no `format!`, `to_string()` or `collect()` in event arguments. A spawned task doesn't inherit the current span: attach it with `.instrument(span)`.

## Tests

- **Place tests by kind.** Unit tests inline under `#[cfg(test)]`, integration tests in the crate's `tests/`, fixtures in `tests/fixtures/` and synthetic only, so the repo never holds real user data.
- **Mark a test that needs an outside service (a database, a container) `#[ignore = "needs <service>"]`,** and run those in their own command, so `cargo test` stays fast and passes with nothing running.
- **Define each test helper once,** in a `#[cfg(test)]` module or a `test-util` feature, not once per test file.
- **Create temporary files only through `tempfile`,** and bind the guard to a named variable for the whole test: `let dir = tempdir()?; let root = dir.path();`. The directory is deleted when the guard drops, so `let _ = tempdir()?;` deletes it at once.
- **Compare values or snapshots, never `Debug` text** in expected values.
- **Build fixtures with typed builders or literal files,** not `.replace()` on YAML or JSON strings, which breaks silently when the text shifts.
- **Snapshot output with insta, and review snapshot changes as behaviour changes** with `cargo insta review`. Snapshot a fixture set with `glob!` or named snapshots: unnamed snapshots in a loop are numbered, and the numbers shift when a case is added. Normalise unstable output with insta `filters` or `redactions`. Where CI rejects unreferenced snapshots, keep insta out of tests CI skips (ignored tests): their snapshots would look orphaned.
- **Give every hand-written parser of outside input a proptest that it never panics:** arbitrary bytes or strings in, a value or a typed error out. Parsers derived with serde or clap are exempt; a hand-written tokenizer, a line splitter or a redaction pass is not.

## Design review

Review the types and signatures before implementation, and review a finished change the same way. Answer each question with file and line evidence. Sections in parentheses are SKILL.md's unless they name this file.

- **Data model:** does each concept have exactly one type, and can any value hold an invalid state? (Model the domain: enums, newtypes, parse once, typestate)
- **Ownership and moves:** who owns each value, where does it move, does any function clone what it could borrow or take, and are small values `Copy`? (Ownership: borrow or own, clone in a loop; Idioms: `mem::take`, `Copy`)
- **Lifetimes and smart pointers:** does a struct with a lifetime outlive one call, and does each `Box` and `Arc` have its reason? (Ownership: own the data, smart pointers)
- **Mutability:** is every `mut` binding limited to the code that builds the value? (Functions: build a value, then stop mutating it)
- **API shape:** does each constructor and reader live on its type, is each type named for its data, and does each plan and guard carry `#[must_use]`? (Functions: put a function on its type; Naming here; Model the domain: out-of-order calls)
- **Public surface:** is each `pub` item used by another crate, are ids of one family branded, and is each derived value computed by the type it describes? (Traits, modules and crates: public surface; Functions: derived values; [patterns.md](patterns.md), branded id family)
- **Dispatch and generics:** is each trait an open set, does each crate boundary take `&dyn` or a thin generic wrapper, and are bounds on `impl` blocks? (Traits, modules and crates: define a trait only for an open set)
- **Pattern matching:** are own enums matched exhaustively, and are values destructured instead of probed? (Model the domain: exhaustive, match and destructure)
- **Errors:** does each `?` keep the context the caller needs, is each error type per operation, and is no error both logged and returned? (Errors; std here)
- **Iterators and closures:** are transforms chains and side effects loops, with no `Vec` collected only to be iterated, and does a varying step take a closure? (Functions: chains and loops; Ownership: slices and iterators; Traits: closures)
- **Collections:** do parameters take slices, are frozen lists `Box<[T]>`, and does each map's order match its output? (Ownership: slices; Idioms: `Box<str>`; Data: maps by output)
- **Determinism:** does output get sorted by a content key, and does library code read no clock, randomness or environment? (Data: sort, the edge)
- **Cost:** is each setup done once, with no allocation or clone in a hot loop, and does each abstraction compile away, with generics or enums instead of `dyn` on hot paths inside a crate? (Expensive work; Ownership: clone in a loop; Traits)
- **Concurrency:** is shared data `Send` and `Sync` without locks, is every channel bounded and every task cancellable? (Concurrency and async)
- **Later patterns:** would a pattern from [patterns.md](patterns.md) remove code, a runtime check or a measured cost?
