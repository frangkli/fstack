---
name: rust
description: 'Review rules for Rust code: domain types, ownership, errors, traits, concurrency, patterns and libraries. Load when reviewing, auditing or polishing Rust (a PR review, a design review of planned types, a final style pass, a design-and-style review lane), even when the request never says "Rust" but the change has .rs files, and before changing Cargo.toml lints or clippy.toml, e.g. "review this PR" or "make the clippy lints stricter". Not for writing new code or making a fix: an agent asked to "add a retry to the HTTP client" or "fix the off-by-one in the tokenizer" works from the repo''s own conventions and leaves these rules to the review.'
---

# Rust

The rules a review checks Rust code against: domain types, ownership and allocation, errors, functions, traits and modules, data and determinism, concurrency and async, and expensive work. Load this file to review, audit or polish code, and before changing Cargo.toml lints or clippy.toml. Implementation works from the repo's own conventions; these rules apply once the code works.

Where the guidance lives:

- **This skill:** the review catalogue, in the rules below and the references the table under Precedence loads. For a style pass or a review, read [references/review.md](references/review.md) for naming, idioms, std usage, tracing, tests and the design-review checklist. In a polish or style pass, fix what it flags in the changed code; in a review lane, report it. The repo's workflow runs this pass once the code works.
- **The readiness skill's [stacks/rust.md](../readiness/stacks/rust.md):** the Cargo lints and `clippy.toml` that readiness offers and merges into a repo. Once merged into the repo's config, they enforce the mechanical rules: no `unwrap` outside tests, no `#[allow]`, no `mod.rs`, no printing, clock or randomness in library code. [references/lint.md](references/lint.md) says when a lint may be disabled and what to do where the repo's config lacks one.
- **In the repo:** where the repo has them, a root `STYLE.md` for the naming, comment and structure rules every language shares and a Rust `STYLE.md`; and the `Cargo.toml` lints, `clippy.toml` and `rustfmt.toml`.

Write Rust shapes: closed sets as enums, domain strings as newtypes, and data stored once and referred to by index. Habits from other languages (string tags, structs of optional fields, classes with setters, object graphs) compile in Rust but give up what the type system checks.

## Precedence

1. **The repo first.** Its `Cargo.toml` lints, `clippy.toml`, `rustfmt.toml`, `STYLE.md` files and AGENTS.md win over this skill. Match the conventions of the crate and module you're in.
2. **Where the repo has no convention,** use the documented current practice for the edition, toolchain and crate versions it pins (read `rust-toolchain.toml`, `Cargo.toml` and `Cargo.lock`; read a crate's source under `~/.cargo/registry/src/` or its docs at that version).
3. **Where an existing pattern is clearly worse** than a rule here (a `Result<_, String>`, a `bool` argument that switches behaviour, an `unwrap` on input), use the better pattern in the code you're changing and say why in your handoff. Leave untouched code as it is and mention it instead.

Load a reference only when its case applies:

| Case | Read |
|---|---|
| The code has or needs typestate, a marker parameter, a branded id family, a sealed or extension trait, an associated type, a `#[must_use]` plan or guard, or reaching for `Cow`, `SmallVec`, an arena, interning or another pattern to cut a measured cost | [references/patterns.md](references/patterns.md) |
| The change adds, chooses or configures a dependency, or uses serde, clap, tracing, tokio, a retry or database client, or another library it lists | [references/libraries.md](references/libraries.md) |
| A lint gets in the way, you want to disable one, or the repo's config lacks or contradicts a lint | [references/lint.md](references/lint.md) |

## A finished pass

- **Checks pass on the change.** Run the repo's commands (its `GATES.md`; without one, AGENTS.md, the repo's task runner and its CI config) over the changed crates (`cargo clippy -p <crate> --all-targets`, `cargo test -p <crate>`) and the crates that depend on a changed `pub` item. Show the output: zero errors, zero warnings.
- **Every escape hatch in the diff is accounted for.** Each new `#[expect]`, `unsafe` block, `.expect()` or `.clone()` in a loop meets its rule here and carries its reason (the `reason =`, a `// SAFETY:` comment, the `.expect` message, a comment); one without a reason is a finding.
- **No suppression bought green.** An `#[allow]` or a loosened lint level in the diff is a finding: fix the code instead.
- **The style pass ran.** The diff was read against [references/review.md](references/review.md).
- **Every advanced pattern pays for itself.** Each trait, generic, marker parameter, lifetime parameter, macro or smart pointer in the diff removes a runtime check, a clone, a duplicated declaration or a measured cost, or turns a likely mistake into a compile error. One whose payoff nobody can name becomes the plain type.

## Model the domain

- **Model a closed set of cases as an enum whose variants carry their own data.** A `kind: String`, a struct of `Option` fields that encode a state, and a `match s.as_str()` with literal arms are enums written as data:
  ```rust
  struct Payment { kind: String, card: Option<CardToken>, iban: Option<Iban> } // before
  enum Payment { Card(CardToken), BankTransfer(Iban) }                        // after
  ```
- **Replace a `bool` or `Option` argument that callers pass as a literal with an enum, or split the function.** `export(&orders, true, None)` tells the reader nothing.
- **Return a named struct when a result has more than one non-trivial part.** A `(Vec<String>, Vec<Vec<String>>)` or a tuple type alias is a struct without field names.
- **Give each domain identifier a newtype** (`UserId`, `OrderId`, `Sku`), host names and file paths included, even with no rule to check, so the compiler stops one kind of id from passing as another. When the value has rules, keep the field private behind a fallible constructor. When a string operation on a newtype appears twice, make it a method on the newtype.
- **Parse input once, where it enters, into types that can't hold invalid values.** Pass only the parsed types inward. A `validate()` that returns `bool` or `Result<()>` is a parser that throws away its result.
- **Put a precondition in the parameter type and move the check to the caller.** Take `&Order`, not `Option<&Order>` with `let Some(order) = order else { return }` as the first line. A doc comment that says a parameter MUST hold some property ("every line MUST belong to `invoice`") names a missing type: move the rule into a type that only a checked constructor builds.
- **Return proof instead of a `bool`.** Prefer `Option<&T>`, a parsed value or a slice pattern (`match hits.as_slice() { [] => …, [one] => …, _ => … }`) over `is_empty()` followed by indexing.
- **Implement std traits instead of ad hoc methods.** `FromStr` to parse, `Display` for user-facing text, `TryFrom` or `From` to convert, and `Default` only when a real default exists, in place of a zero-argument `new`. Give each `FromStr` and each conversion of outside input a named error type; `()` fits only a `TryFrom` that narrows an internal enum. Put an enum's string mapping in its own `impl`, never at the call site.
- **Match your own enums exhaustively.** A `_ =>` arm hides the next variant someone adds. Keep wildcards for foreign types and integers.
- **Match and destructure instead of probing.** Use `match`, `if let`, `let`-`else`, slice patterns and `matches!` instead of `is_some()` followed by `unwrap`, or a chain of `==` checks. Where every field must be handled, destructure your own struct in full (`let Refund { order, amount } = refund;`), so a new field fails to compile at that site.
- **Make an out-of-order call a compile error.** Give each state of a multi-step process its own type, and make each transition take `self` and return the next state: a `plan()` that returns a `MigrationPlan` whose `describe()` serves a dry run and whose `apply(self)` does the writing, instead of `migrate(.., dry_run: bool)`. Mark such a plan, a staged result or a guard `#[must_use]` on the type. Typestate, marker parameters and branded id families: [references/patterns.md](references/patterns.md).

## Ownership and allocation

- **Borrow what a function only reads; take ownership of what it stores.** Take `&str`, `&[T]`, `&Path` and `Option<&T>` for reading. Never clone a borrowed parameter inside the callee: take the owned value and let the caller decide. Getters return borrowed views; constructors and builders return owned values.
- **Use concrete types in internal APIs.** Keep `impl AsRef<Path>` and `impl Into<String>` for the few functions with many external callers.
- **Take a slice in a helper that only iterates, and return `impl Iterator` from a helper whose callers only iterate.** Take `impl IntoIterator` only when callers would otherwise collect a `Vec` solely to make the call. Use `[T; N]` for a fixed count, and `Vec::with_capacity` when the length is known before the loop.
- **Justify a `.clone()` inside a loop with a comment, or restructure.** Cloning a whole map once per item makes the loop quadratic.
- **Shorten a borrow, split a struct or use `mem::take` to satisfy the borrow checker.** A clone, `Rc` or `RefCell` added only to silence it hides a design problem.
- **Own the data in a struct that outlives one call.** Give a struct a lifetime parameter only for a short-lived view, such as a cursor over a buffer or a parser over a borrowed line. Copy what you keep into owned values before the buffer drops.
- **Give each smart pointer a reason.** `Box` for a recursive type, a large and rare enum variant or a `dyn` value; `Arc` to share immutable data between threads, as `Arc<str>` or `Arc<[T]>`. Use no `Rc` or `RefCell`: `Rc` isn't `Send` and `RefCell` isn't `Sync`, so neither can be shared by tasks on a multi-threaded runtime, and indexed storage (Data, below) replaces the graphs they build.
- **Undo a temporary change in `Drop`.** For a file, a lock or other state outside the value, return a guard, as `MutexGuard` does, so early returns and panics restore it. For a field of `&mut self`, write a method that takes a closure and swaps the field with `mem::replace` around it, named for the state the closure runs in (`while_paused`), since `with_*` names a constructor.

## Errors

- **Derive every error type a caller may match with `thiserror`.** `anyhow` fits only code whose errors are reported, never matched: a binary's `main` and command handlers, build scripts, tests. Pick one boundary per repo and keep to it; the common one is `anyhow` only in the binary crate.
- **Never panic on input:** files, network payloads, config, API requests, CLI arguments, environment variables. For a real invariant, write `.expect("why this cannot fail")`; Clippy rejects `unwrap()` outside tests.
- **Carry a typed cause, never a string.** Write no `Result<_, String>` and no `map_err(|e| e.to_string())`. Keep the source error in a `#[source]` field.
- **Put locations and identifiers in error fields, never only in the message.** A message that starts with `"{path}: "` with no `path` field loses the path as data.
- **Give each operation its own error enum.** Operations that fail in the same ways can share one. One crate-wide enum makes callers match failures that can't happen.
- **Use `#[from]` only when every error of that type, at every `?` site, means the same thing.** Otherwise use `#[source]` plus the context that identifies the operand:
  ```rust
  #[error("io error")] Io(#[from] std::io::Error),                                         // before
  #[error("cannot read config {path}")] Read { path: PathBuf, #[source] source: std::io::Error }, // after
  ```
- **Make an error's message describe only its own layer.** Expose the cause through `source()`. Never also format the cause into the message, because chain printers would show it twice.
- **Recover at the smallest unit that can still give a correct result** (one record, one file, one request): keep the raw input, count it as skipped where the user will see it (a report, a health counter), and go on. Propagate everything else.
- **Log an error where you handle it, or return it. Never do both.**

## Functions

- **Push `if`s up and `for`s down.** Decide once outside a loop. Give hot operations a batch signature, such as `price_all(&orders)`, so setup runs once instead of once per `price(order)` call.
- **Group shared state into a struct.** When three or more functions thread the same `&mut Vec<Warning>` or other accumulator, make it a struct with methods. Use one error channel per function: either return the results or push them, never both.
- **Return what a function produces instead of filling a `&mut` parameter.** Take `&mut` to change caller-owned data or reuse a buffer. A recursive walk may fill one accumulator, passed first, behind a function that returns it.
- **Put a function on the type it builds or reads.** Construct a type from its own crate with an associated function (`File::open`), and make a function that mostly reads one of your own types a method. Free functions suit foreign types and operations that take a context first, as in `fn check(ctx: &Context, expr: &Expr)`.
- **Prefer no accessors.** A field with no rule to protect is `pub` (at the visibility the crate allows): a getter and setter around it add code and protect nothing. A field with a rule is private, read through a getter named after the field (`len()`, never `get_len()`), with `_mut` for mutable access only where a borrow can't break the rule, and changed only through the checked constructor or a method named for the domain action (`advance_to(position)`, not `set_position(position)`). `set_x` is only for a plain field that must stay private for another reason. (Rust API Guidelines C-GETTER)
- **Write pure transforms as iterator chains and side effects as `for` loops.** A chain of `filter`, `map` and `collect` reads as data flow; keep its closures free of side effects, and write the loop when the body pushes, writes, logs or exits early, or when the chain needs nested closures or captured mutable state. `for_each` fits only as the last step of a longer chain whose body is one call.
- **Build a value, then stop mutating it.** Construct it with `collect`, a struct literal or a block expression, so the binding that outlives construction is not `mut`. Mutating a local while it is being built is fine as long as nothing else holds it yet.
- **Spell out every field when you build a domain struct.** Keep `..Default::default()` for option and config structs.
- **Compute a derived value inside the value it describes.** When a function takes several arguments that are all parts of one value (a plan, a batch), or a struct stores a count or hash of an input it also receives, take the value and compute the count, hash or key in its own methods, so the parts can't drift apart.

## Traits, modules and crates

- **Define a trait only for an open set with two or more real implementations.** Use an enum for a closed set and a concrete type for one case. Use generics inside a crate, and `dyn` when the set is open at run time. At a crate boundary, take `&dyn`, or write a thin generic function that calls a non-generic one, as `std::fs::read` does. Put trait bounds on `impl` blocks and functions, not on struct definitions. For one step that varies per call, take a closure (`impl Fn(&Order) -> bool`) instead of a one-method trait. Sealed traits, extension traits, and associated types against generic parameters: [references/patterns.md](references/patterns.md).
- **Keep the public surface minimal.** Make an item `pub` only when another crate uses it now, and `pub(crate)` otherwise. Each `pub use` in `lib.rs` is a contract other crates may lean on.
- **Give each public item one path.** Keep modules private, re-export items one by one, and never use a glob re-export.
- **Add `#[non_exhaustive]` only to types published outside the workspace.** Inside it, a new variant should break every `match` and a new field every struct literal. On a published enum that outside code reads, it lets the enum grow; on a published struct that outside code reads but never builds, add it with a constructor.
- **Put shared code in the lowest crate that needs it.** A helper used in two crates moves to the lowest crate both depend on. A shared test double goes there too, behind a `test-util` feature.
- **Keep the crate graph layered.** Decide which crates are core and which are leaves (plugins, adapters, one per backend), and make leaves depend only on core crates, never on each other, so one leaf builds and tests alone. Choose which crate owns heavy dependencies such as database drivers: when only that crate and the binary use it, no other crate compiles the driver.
- **Write plain code before a macro.** Write a `macro_rules!` only when one block repeats five or more times, with one level of repetition and no recursive or token-munching macros. Write a procedural macro only in a library whose users would otherwise hand-write the same impl for many types: it costs a crate and compile time, and its errors are hard to read.
- **Put each `unsafe` block under `#[expect(unsafe_code, reason = "...")]`, with a `// SAFETY:` comment** that names the invariant making it sound. Keep the unsafe part to the one call that needs it.

## Data, state and determinism

- **Store each entity once, in a `Vec` or map owned by one struct, and refer to it by a typed index.** Never build `Rc<RefCell<_>>` graphs or back-pointers.
- **Keep mutable state on the value that owns it.** Use no `static` or `thread_local!` mutable state; a callback that needs state captures it. A `LazyLock` for an immutable value, such as a compiled pattern, is fine.
- **Choose maps by what reaches output.** `BTreeMap` or `BTreeSet` when sorted order is the output order, `IndexMap` when insertion order is, and a fast hash map (`FxHashMap`, on keys an attacker doesn't choose; [references/libraries.md](references/libraries.md)) for lookup only. Remove from an `IndexMap` with `shift_remove`, which keeps the order.
- **Sort by a content-derived total key before results reach output or a snapshot.** Task timing and query plans vary between runs. Give every SQL query whose rows reach output an `ORDER BY` on a unique key: databases return rows in no defined order without one.
- **Keep the clock, randomness and environment at the edge.** Only the binary reads environment variables, the clock and the random number generator; library code takes the time, a seed or the configuration as parameters, so tests and reruns control them. Derive an identifier from content (a hash of the fields that make a record unique) when a rerun must produce the same id: retried imports, dedup keys, snapshot output. Generate a random or time-based id only when each creation must be distinct, at the edge, and pass it in.

## Concurrency and async

- **Keep blocking work off the async runtime.** Parsing a large file, compressing a batch or other CPU-heavy work runs in `spawn_blocking`; file and network I/O use the runtime's async APIs.
- **Bound every channel and queue, and decide what happens when it is full:** wait (backpressure) or drop and count. An unbounded channel turns a slow consumer into memory growth.
- **Hold no `std::sync::Mutex` guard across an `.await`.** Share read-only inputs as `Arc<T>`; give mutable state one owning task that others message.
- **Make every task cancellable.** Long loops check a `CancellationToken` or sit in `select!` with it, and a cancelled task leaves its saved progress (a cursor, an offset) at the last acknowledged write, so a restart neither loses nor repeats work.
- **An `async fn` in a trait can't be called through `dyn`.** Which form to use: [references/libraries.md](references/libraries.md), async traits.

## Expensive work

- **Do each costly setup once per run, not per row, per request or per item.** Costly setup includes opening a connection or repository, creating a temporary directory, compiling a pattern and reading a file. A repeat needs a comment that says why.
- **Write in batches.** A column-store insert carries thousands of rows, never one row per call; row-store writes that belong together share one transaction.
- **Compile patterns once, at load time.** For many patterns, prefilter with one aho-corasick automaton over their literal keywords and run only the patterns it hits. Ask for only what you need: `is_match` costs less than `find`, and `find` less than `captures`.
