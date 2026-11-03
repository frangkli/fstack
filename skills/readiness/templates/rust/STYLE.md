# Rust style

Rules for what rustfmt, Clippy and the compiler can't check, beyond the shared rules in the root `STYLE.md`. `Cargo.toml` (`[workspace.lints]`), `clippy.toml`, `deny.toml` and `rustfmt.toml` hold the rules a tool enforces. Where a rule here names "(common <Section> <n>)", the root file states the general rule and this file its Rust form.

Write Rust shapes: closed sets as enums, domain strings as newtypes, and data stored once and referred to by index. Habits from other languages (string tags, structs of optional fields, classes with setters, object graphs) compile in Rust but give up what the type system checks.

A rule marked **(mechanical)** names a pattern a tool could find from syntax alone; those are candidates for a future lint.

## Never

Mistakes that are costly once shipped and that the lints don't catch.

- **Never panic on input** (files, network payloads, config, requests, CLI arguments, environment variables): return an error. `.expect("why this cannot fail")` is for a real invariant only; Clippy rejects `unwrap()` outside tests.
- **Never pass input inward unparsed:** parse it once, where it enters, into types that can't hold invalid values (common Boundaries 1).
- **Never format a value into SQL text:** bind every value.
- **Never key an `FxHashMap` with values an attacker chooses:** it has no protection against hash flooding, so use std's `HashMap` there.
- **Never create an unbounded channel or queue:** bound it, and decide whether a full one waits or drops and counts.
- **Never run blocking or CPU-heavy work on the async runtime:** do file and network I/O through the runtime's async APIs, use `spawn_blocking` only for short, bounded blocking calls, limit CPU-heavy parallelism with a `Semaphore` or rayon, and give a worker that runs the whole time its own thread.
- **Never spawn a long-running task that can't be stopped:** each one listens to a `CancellationToken`.
- **Never retry an operation that isn't idempotent.** To make a retried write idempotent, give it a dedup key derived from its content.
- **Never accept unknown keys in a config or spec type:** put `#[serde(deny_unknown_fields)]` on each, never together with `flatten`. Leave it off types that read upstream data (events, logs, third-party payloads).
- **Never write a bare `#[instrument]`:** it records every argument with `Debug`, secrets included. Write `skip_all` and name the fields.

## Types

1. **Model a closed set of cases as an enum whose variants carry their own data** (common Types 1). A `kind: String`, a struct of `Option` fields that encode a state, and a `match s.as_str()` with literal arms are enums written as data. (mechanical)

   ```rust
   struct Payment { kind: String, card: Option<CardToken>, iban: Option<Iban> } // before
   enum Payment { Card(CardToken), BankTransfer(Iban) }                        // after
   ```

2. **Replace a `bool` or `Option` argument that callers pass as a literal with an enum, or split the function.** `export(&orders, true, None)` tells the reader nothing. (mechanical)
3. **Return a named struct when a result has more than one non-trivial part.** A `(Vec<String>, Vec<Vec<String>>)` or a tuple type alias is a struct without field names. (mechanical)
4. **Give each domain identifier a newtype** (`UserId`, `OrderId`, `Sku`), host names and file paths included, even with no rule to check, so the compiler stops one kind of id from passing as another. When the value has rules, keep the field private behind a fallible constructor. When a string operation on a newtype appears twice, make it a method on the newtype.
5. **Parse input once, where it enters, into types that can't hold invalid values.** Pass only the parsed types inward. A `validate()` that returns `bool` or `Result<()>` is a parser that throws away its result.
6. **Put a precondition in the parameter type and move the check to the caller.** Take `&Order`, not `Option<&Order>` with `let Some(order) = order else { return }` as the first line. A doc comment that says a parameter MUST hold some property ("every line MUST belong to `invoice`") names a missing type: move the rule into a type that only a checked constructor builds.
7. **Return proof instead of a `bool`.** Prefer `Option<&T>`, a parsed value or a slice pattern (`match hits.as_slice() { [] => …, [one] => …, _ => … }`) over `is_empty()` followed by indexing.
8. **Implement std traits instead of ad hoc methods.** `FromStr` to parse, `Display` for user-facing text, `TryFrom` or `From` to convert, and `Default` only when a real default exists, in place of a zero-argument `new`. Give each `FromStr` and each conversion of outside input a named error type; `()` fits only a `TryFrom` that narrows an internal enum. Put an enum's string mapping in its own `impl`, never at the call site.
9. **Match your own enums exhaustively.** A `_ =>` arm hides the next variant someone adds. Keep wildcards for foreign types and integers.
10. **Make an out-of-order call a compile error.** Give each state of a multi-step process its own type, and make each transition take `self` and return the next state. When the states share most fields and methods, use one type with a marker parameter (Patterns 2).

    ```rust
    // Before: fn migrate(db: &mut Db, target: SchemaVersion, dry_run: bool)
    #[must_use = "a plan does nothing until `apply` runs it"]
    struct MigrationPlan { steps: Box<[Step]> }
    impl MigrationPlan {
        fn describe(&self) -> impl Iterator<Item = &Step> { self.steps.iter() } // the dry run
        fn apply(self, db: &mut Db) -> Result<SchemaVersion, ApplyError> { /* … */ }
    }
    ```

11. **Match and destructure instead of probing.** Use `match`, `if let`, `let`-`else`, slice patterns and `matches!` instead of `is_some()` followed by `unwrap`, or a chain of `==` checks. Where every field must be handled, destructure your own struct in full (`let Refund { order, amount } = refund;`), so a new field fails to compile at that site.
12. **Mark a type `#[must_use]` when dropping it unused loses work:** a plan whose later `apply` does the writing, a staged result, or a guard. Put the attribute on the type, not on the functions that return it, so every constructor is covered.
13. **Brand ids of one family with a marker parameter when they share every behaviour.** When several kinds of id have one representation and the same methods, and values of different kinds travel in one struct or signature, write one `Id<K>`, so a swapped id fails to compile. Keep an erased default kind for columns that may point at several kinds, with a `From` that erases. Use separate newtypes when the kinds differ in validation or behaviour. Hand-write the trait impls, because `#[derive]` adds a bound on `K`.

    ```rust
    mod sealed { pub trait Sealed {} }
    pub trait IdKind: sealed::Sealed {}
    pub struct Id<K = AnyKind> { raw: u64, kind: PhantomData<fn() -> K> } // Send, Sync, covariant; owns no K
    pub enum AnyKind {} // not an IdKind, so the From below doesn't overlap From<T> for T
    impl sealed::Sealed for User {}
    impl IdKind for User {}
    pub type UserId = Id<User>;
    impl<K: IdKind> From<Id<K>> for Id<AnyKind> { fn from(id: Id<K>) -> Self { Self { raw: id.raw, kind: PhantomData } } }
    impl<K> Clone for Id<K> { fn clone(&self) -> Self { *self } } // and Copy, PartialEq, Eq, Hash, Debug by hand
    ```

14. **Leave `#[non_exhaustive]` off types used only inside the workspace.** Inside it, a new variant should break every `match` (Types 9) and a new field every struct literal. Add it only to a type published for outside crates: on an enum outside code reads, so it can grow, and on a struct outside code reads but never builds, with a constructor.

## Ownership and allocation

1. **Borrow what a function only reads. Take ownership of what it stores.** Take `&str`, `&[T]`, `&Path` and `Option<&T>` for reading. Never clone a borrowed parameter inside the callee: take the owned value and let the caller decide.
2. **Return borrowed views from getters** (`&str`, `&[T]`, `Option<&T>`). Return owned values from constructors and builders.
3. **Use concrete types in internal APIs.** Keep `impl AsRef<Path>` and `impl Into<String>` for the few functions with many external callers.
4. **Take a slice in a helper that only iterates, and return `impl Iterator` from a helper whose callers only iterate.** Take `impl IntoIterator` only when callers would otherwise collect a `Vec` just to make the call. Use `[T; N]` for a fixed count, and `Vec::with_capacity` when the length is known before the loop.
5. **Justify a `.clone()` inside a loop with a comment, or restructure.** Cloning a whole map once per item makes the loop quadratic.
6. **Move values out with `std::mem::take`, `Option::take` or `mem::replace`,** not clone-then-clear.
7. **Store immutable strings and lists as `Box<str>` and `Box<[T]>`.** They drop the unused capacity and say the value won't grow. Reach for `Cow` only on a measured path (Patterns 8).
8. **Shorten a borrow, split a struct or use `mem::take` to satisfy the borrow checker.** A clone, `Rc` or `RefCell` added only to silence it hides a design problem.
9. **Own the data in a struct that outlives one call.** Give a struct a lifetime parameter only for a short-lived view, such as a cursor over a buffer or a parser over a borrowed line. Copy what you keep into owned values before the buffer drops.
10. **Give each smart pointer a reason.** `Box` for a recursive type, a large and rare enum variant or a `dyn` value; `Arc` to share immutable data between threads, as `Arc<str>` or `Arc<[T]>`. Use no `Rc` or `RefCell`: `Rc` isn't `Send` and `RefCell` isn't `Sync`, so tasks on a multi-threaded runtime can't share them, and indexed storage (Data 1) replaces the graphs they build.
11. **Derive `Copy` on small plain values and pass them by value.** Index ids, fieldless enums and spans are `Copy`, so take `OrderIdx`, not `&OrderIdx`. Derive `Clone` on a large type only when a caller needs a second copy.
12. **Write formatted text straight into its destination.** Use `write!` into a `String` or writer, or a `Display` impl, instead of `push_str(&format!(..))` or a temporary `String` printed once. (mechanical)
13. **Undo a temporary change in `Drop`.** For a file, a lock or other state outside the value, return a guard, as `MutexGuard` does, so early returns and panics restore it. For a field of `&mut self`, write a method that takes a closure and swaps the field with `mem::replace` around it, named for the state the closure runs in (`while_paused`), since `with_*` names a constructor (Naming 1).

    ```rust
    #[must_use = "the lock is released when the guard drops"]
    pub struct LockGuard { path: PathBuf }
    impl Drop for LockGuard {
        fn drop(&mut self) {
            // Drop can't return the error, so record it for whoever reads the logs.
            if let Err(error) = fs::remove_file(&self.path) {
                tracing::debug!(path = %self.path.display(), %error, "lock file not removed");
            }
        }
    }
    ```

## Errors

The kinds of failure and how each travels are in common Errors; these are the Rust forms.

1. **Derive every error type a caller may match with `thiserror`.** `anyhow` fits only code whose errors are reported, never matched: a binary's `main` and command handlers, build scripts, tests. Pick one boundary per repo and keep to it; the common one is `anyhow` only in the binary crate.
2. **Carry a typed cause, never a string.** Write no `Result<_, String>` and no `map_err(|e| e.to_string())`. Keep the source error in a `#[source]` field. (mechanical)
3. **Put locations and identifiers in error fields, never only in the message.** A message that starts with `"{path}: "` with no `path` field loses the path as data.
4. **Give each operation its own error enum.** Operations that fail in the same ways can share one. One crate-wide enum makes callers match failures that can't happen.
5. **Use `#[from]` only when every error of that type, at every `?` site, means the same thing.** Otherwise use `#[source]` plus the context that identifies the operand.

   ```rust
   #[error("io error")] Io(#[from] std::io::Error),                                              // before
   #[error("cannot read config {path}")] Read { path: PathBuf, #[source] source: std::io::Error }, // after
   ```

6. **Make an error's message describe only its own layer.** Expose the cause through `source()`. Never also format the cause into the message, because chain printers would show it twice.
7. **Write error messages as lowercase fragments with no final period** that name the action and its operand: `cannot read config app.toml`. Chain printers join them with `: `, so a capital or a period lands mid-sentence. (mechanical)
8. **Recover at the smallest unit that can still give a correct result** (one record, one file, one request): keep the raw input, count it as skipped where the user will see it (a report, a health counter), and go on. Propagate everything else.
9. **Log an error where you handle it, or return it. Never do both.**
10. **Derive `Debug` on value, error and report types, and `PartialEq`, `Eq`, `Hash` and `Ord` on value types that need comparing or deduplicating.** Comparing `format!("{x:?}")` strings is an equality check by accident.

## Functions

1. **Push `if`s up and `for`s down.** Decide once outside a loop. Give hot operations a batch signature, such as `price_all(&orders)`, so setup runs once instead of once per `price(order)` call.
2. **Group shared state into a struct.** When three or more functions thread the same `&mut Vec<Warning>` or other accumulator, make it a struct with methods. Use one error channel per function: either return the results or push them, never both.
3. **Return what a function produces instead of filling a `&mut` parameter.** Take `&mut` to change caller-owned data or reuse a buffer. A recursive walk may fill one accumulator, passed first, behind a function that returns it.
4. **Put a function on the type it builds or reads.** Construct a type from its own crate with an associated function (`File::open`), and make a function that mostly reads one of your own types a method. Free functions suit foreign types and operations that take a context first, as in `fn check(ctx: &Context, expr: &Expr)`. (mechanical)
5. **Prefer no accessors.** A field with no rule to protect is `pub`, at the visibility Traits 2 allows: a getter and setter around it add code and protect nothing. A field with a rule is private, read through a getter named after the field (`len()`, never `get_len()`), with `_mut` last for mutable access only where a borrow can't break the rule (`buffer_mut()` on a field whose type keeps its own invariant), and changed only through the checked constructor or a method named for the domain action (`advance_to(position)`, not `set_position(position)`). `set_x` is only for a plain field that must stay private for another reason. (Rust API Guidelines C-GETTER)
6. **Spell out every field when you build a domain struct.** Keep `..Default::default()` for option and config structs.
7. **Compute a derived value inside the value it describes.** When a function takes several arguments that are all parts of one value (a plan, a batch), or a struct stores a count or hash of an input it also receives, take the value and compute the count, hash or key in its own methods, so the parts can't drift apart.
8. **Write plain code before a macro.** Write a `macro_rules!` only when one block repeats five or more times, with one level of repetition and no recursive or token-munching macros. Write a procedural macro only in a library whose users would otherwise hand-write the same impl for many types: it costs a crate and compile time, and its errors are hard to read.
9. **Put each `unsafe` block under `#[expect(unsafe_code, reason = "...")]`, with a `// SAFETY:` comment** that names the invariant making it sound. Keep the unsafe part to the one call that needs it.

## Traits, modules and crates

1. **Define a trait only for an open set with two or more real implementations.** Use an enum for a closed set and a concrete type for one case. Use generics inside a crate, and `dyn` when the set is open at run time. At a crate boundary, take `&dyn`, or write a thin generic function that calls a non-generic one, as `std::fs::read` does. Put trait bounds on `impl` blocks and functions, not on struct definitions. For one step that varies per call, take a closure (`impl Fn(&Order) -> bool`) instead of a one-method trait.
2. **Keep the public surface minimal.** Make an item `pub` only when another crate uses it now, and `pub(crate)` otherwise. Each `pub use` in `lib.rs` is a contract other crates may lean on: add one only for an item they need.
3. **Give each public item one path.** Keep modules private, re-export items one by one, and never use a glob re-export. (mechanical)
4. **Put modules in `foo.rs` next to `foo/`, never `mod.rs`.** Clippy's `mod_module_files` enforces it.
5. **Put shared code in the lowest crate that needs it.** A helper used in two crates moves to the lowest crate both depend on. A shared test double goes there too, behind a `test-util` feature.
6. **Keep the crate graph layered.** Decide which crates are core and which are leaves (plugins, adapters, one per backend), and make leaves depend only on core crates, never on each other, so one leaf builds and tests alone. Choose which crate owns heavy dependencies such as database drivers: when only that crate and the binary use it, no other crate compiles the driver.
7. **Seal a public trait that other crates use but must not implement:** a marker or capability trait whose implementations the crate owns. The crate can then add methods without a breaking change. Never seal a seam other crates exist to implement (a plugin or backend trait).

   ```rust
   mod sealed { pub trait Sealed {} }
   /// A table this crate knows how to write.
   pub trait Table: sealed::Sealed { const NAME: &'static str; }
   impl sealed::Sealed for OrderRow {}
   impl Table for OrderRow { const NAME: &'static str = "orders"; }
   ```

8. **Write an extension trait only for a foreign type that needs the same domain methods in two or more crates.** Name it `<Type>Ext` and put it in the lowest crate both use. When the value lives in your own structs, write a newtype instead, which can also keep an invariant.
9. **Use an associated type when each implementation picks exactly one type** (`Iterator::Item`), **and a generic parameter when one type implements the trait for several** (`From<T>`). A trait used as `dyn` takes neither, unless every object names the same type (`Box<dyn Parser<Output = Order>>`); for a closed set of outputs, return an enum.
10. **Name a type for the data it owns, not its role.** Write `Pool`, not `ConnectionManager`, and name no type `Manager`, `Service` or `Factory`; traits are exempt. Implement `Deref` only from a newtype to the view it wraps, as `String` does to `str`: `Deref` used for inheritance makes method lookup surprising. (mechanical)

## Data, state and determinism

1. **Store each entity once, in a `Vec` or map owned by one struct, and refer to it by a typed index.** Never build `Rc<RefCell<_>>` graphs or back-pointers.
2. **Keep mutable state on the value that owns it.** Use no `static` or `thread_local!` mutable state; a callback that needs state captures it in its closure. A `LazyLock` for an immutable value, such as a compiled pattern, is fine. (mechanical)
3. **Choose maps by what reaches output.** `BTreeMap` or `BTreeSet` when sorted order is the output order, `IndexMap` when insertion order is, and `FxHashMap` (on keys an attacker doesn't choose) for lookup only. Remove from an `IndexMap` with `shift_remove`, which keeps the order.
4. **Sort by a content-derived total key before results reach output or a snapshot.** Task timing and query plans vary between runs.
5. **Give every SQL query whose rows reach output an `ORDER BY` on a unique key.** Databases return rows in no defined order without one.
6. **Keep the clock, randomness and environment at the edge.** Only the binary reads environment variables, the clock and the random number generator; library code takes the time, a seed or the configuration as parameters, so tests and reruns control them. `clippy.toml`'s `disallowed-methods` enforces it. Derive an identifier from content (a hash of the fields that make a record unique) when a rerun must produce the same id: retried imports, dedup keys, snapshot output. Generate a random or time-based id only when each creation must be distinct, at the edge, and pass it in.

## Concurrency and async

The general rules are in common Concurrency and Retries; these are the tokio forms.

1. **Keep blocking work off the async runtime, and pick the tool by how long the work runs.** File and network I/O use the runtime's async APIs. A short, bounded blocking call, such as hashing one file, runs in `spawn_blocking`. Its pool grows to 512 threads and then queues without limit, and `tokio::fs` calls wait in that same queue, so limit CPU-heavy parallelism: take a `Semaphore` permit before each `spawn_blocking`, or give data-parallel work, such as parsing every file of a batch import, to rayon. A worker that runs for the whole life of the program gets its own thread from `std::thread::spawn`. A started `spawn_blocking` task can't be aborted and runtime shutdown waits for it, so a long CPU loop checks the `CancellationToken` between chunks.
2. **Bound every channel and queue, and decide what happens when it is full:** wait (backpressure) or drop and count. An unbounded channel turns a slow consumer into memory growth.
3. **Hold no `std::sync::Mutex` guard across an `.await`.** Share read-only inputs as `Arc<T>`; give mutable state one owning task that others message.
4. **Make every task cancellable.** Long loops check a `CancellationToken` or sit in `select!` with it, and a cancelled task leaves its saved progress (a cursor, an offset) at the last acknowledged write, so a restart neither loses nor repeats work.
5. **An `async fn` in a trait can't be called through `dyn`.** Which form to use is in the async-trait library section.

## Expensive work

1. **Do each costly setup once per run, not per row, per request or per item.** Costly setup includes opening a connection or repository, creating a temporary directory, compiling a pattern and reading a file. A repeat needs a comment that says why.
2. **Write in batches.** A column-store insert carries thousands of rows, never one row per call; row-store writes that belong together share one transaction.
3. **Compile patterns once, at load time.** For many patterns, prefilter with one aho-corasick automaton over their literal keywords and run only the patterns it hits. Ask for only what you need: `is_match` costs less than `find`, and `find` less than `captures`.

## Naming

The shared naming rules are in the root `STYLE.md`. These are the Rust-specific ones.

1. **Name associated functions by the Rust API Guidelines.** `new` and `with_*` construct, `from_*` converts, `as_*` borrows cheaply, `to_*` computes a new value, and `into_*` consumes `self`. A reader decides from the prefix whether a call allocates or consumes. (mechanical)
2. **Follow std's word order for a family:** `ParseIntError` and `ParseFloatError`, never `IntParseError` beside them (common Naming 12).

## std

1. Collect fallible iterators into `Result<Vec<_>, _>`.
2. Use `Option` and `Result` combinators (`map`, `and_then`, `ok_or_else`, `unwrap_or_default`, `is_some_and`) when one expression covers both cases, and `match` or `let`-`else` when a case has its own logic.
3. Group with `entry(key).or_default()`.
4. Filter and sort in place with `retain`, `extract_if`, `sort_by_cached_key` and `chunk_by`.
5. Handle paths with `Path` and `OsStr` methods, never string operations: a path need not be UTF-8, and separators differ by platform.
6. Return `ExitCode` from `main` instead of calling `process::exit`, which skips destructors.

## Tests

The general testing guide is the root `TESTING.md`; these are the Rust forms.

1. **Place tests by kind.** Unit tests inline under `#[cfg(test)]`, integration tests in the crate's `tests/`, fixtures in `tests/fixtures/` and synthetic only.
2. **Mark a test that needs an outside service (a database, a container) `#[ignore = "needs <service>"]`,** and run those in their own command (`just test-int <crate>`), so `cargo test` stays fast and passes with nothing running.
3. **Define each test helper once,** in a `#[cfg(test)]` module or a `test-util` feature, not once per test file.
4. **Compare values or snapshots, never `Debug` text** in expected values.
5. **Build fixtures with typed builders or literal files,** not `.replace()` on YAML or JSON strings, which breaks silently when the text shifts.
6. **Give every hand-written parser of outside input a proptest that it never panics:** arbitrary bytes or strings in, a value or a typed error out. Parsers derived with serde or clap are exempt; a hand-written tokenizer, a line splitter, a redaction pass or a per-record mapper of outside data is not.
7. **Use each testing tool for its job:** proptest for properties of hand-written parsers, insta for large or structured output with the orphan check in CI (`cargo insta test --unreferenced reject --check`), cargo-fuzz on a schedule for parsers of untrusted input, and cargo-mutants on the change's diff before the final review. Each has its own library section.

## Exceptions

The shared rules for exceptions are in the root `STYLE.md`; this is the Rust syntax.

1. **Write `#[expect(clippy::<lint>, reason = "<why>")]` on the smallest item** (a function, a statement, a block), never `#[allow]`. `#[expect]` warns once the lint stops firing, so a stale exception goes with the code that needed it. Never a crate-wide `#![expect]` or `#![allow]` for one site. List every exception in your handoff.

   ```rust
   #[expect(clippy::print_stdout, reason = "the command's output")]
   fn print_report(report: &Report) { println!("{report}"); }
   ```

2. **Account for every escape hatch in a diff:** each new `#[expect]`, `unsafe` block, `.expect()` or `.clone()` in a loop carries its reason (the `reason =`, a `// SAFETY:` comment, the `.expect` message, a comment).

## Design review

Review the types and signatures before implementation, and review a finished change the same way. Answer each question with file and line evidence.

- **Data model:** does each concept have exactly one type, and can any value hold an invalid state? (Types 1, 4, 5, 10)
- **Ownership and moves:** who owns each value, where does it move, does any function clone what it could borrow or take, and are small values `Copy`? (Ownership 1, 5, 6, 11)
- **Lifetimes and smart pointers:** does a struct with a lifetime outlive one call, and does each `Box` and `Arc` have its reason? (Ownership 9, 10)
- **Mutability:** is every `mut` binding limited to the code that builds the value? (common Structure 4)
- **API shape:** does each constructor and reader live on its type, is each type named for its data, and does each plan and guard carry `#[must_use]`? (Functions 4, Traits 10, Types 12)
- **Public surface:** is each `pub` item used by another crate, are ids of one family branded, and is each derived value computed by the type it describes? (Traits 2, Types 13, Functions 7)
- **Dispatch and generics:** is each trait an open set, does each crate boundary take `&dyn` or a thin generic wrapper, and are bounds on `impl` blocks? (Traits 1)
- **Pattern matching:** are own enums matched exhaustively, and are values destructured instead of probed? (Types 9, 11)
- **Errors:** does each `?` keep the context the caller needs, is each error type per operation, and is no error both logged and returned? (Errors)
- **Iterators and closures:** are transforms chains and side effects loops, with no `Vec` collected only to be iterated, and does a varying step take a closure? (common Structure 3, Ownership 4, Traits 1)
- **Collections:** do parameters take slices, are frozen lists `Box<[T]>`, and does each map's order match its output? (Ownership 4, 7, Data 3)
- **Determinism:** does output get sorted by a content key, and does library code read no clock, randomness or environment? (Data 4, 6)
- **Cost:** is each setup done once, with no allocation or clone in a hot loop, and does each abstraction compile away, with generics or enums instead of `dyn` on hot paths inside a crate? (Expensive work, Ownership 5, Traits 1)
- **Concurrency:** is shared data `Send` and `Sync` without locks, is every channel bounded and every task cancellable? (Concurrency)
- **Later patterns:** would a pattern below remove code, a runtime check or a measured cost?

## Patterns

Each pattern costs more than plain code, so it goes in only where it removes code, a runtime check or a measured cost, or turns a likely mistake into a compile error (common Structure 7). A pattern that needs a new crate also passes the library test in the Libraries section.

| # | Pattern | Use it when | Skip it when |
|---|---|---|---|
| 1 | Typestate, one type per state | a multi-step process must not run out of order, and the states hold different data (Types 10) | one runtime check in one place covers it |
| 2 | Typestate with a marker parameter | the states share most fields and methods, and a wrong order must not compile | the states hold different data: one type per state |
| 3 | Branded id family (`Id<K>`) | several id kinds share one representation and every method, and travel together (Types 13) | the kinds differ in validation or behaviour: separate newtypes |
| 4 | Sealed trait | other crates use a trait but must not implement it (Traits 7) | the trait is a seam other crates exist to implement |
| 5 | Extension trait (`<Type>Ext`) | a foreign type needs the same domain methods in two or more crates (Traits 8) | one crate needs them (a free function), or the value lives in your own structs (a newtype) |
| 6 | Associated type | each implementation picks exactly one type (Traits 9) | one type implements the trait for several types: a generic parameter |
| 7 | `#[must_use]` plan or guard | dropping the value unused loses work or ends a guarded state early (Types 12, Ownership 13) | reading the result is optional |
| 8 | `Cow<'a, str>` | most inputs pass through unchanged, on a measured path | no profile shows the allocation: return `String`, since `Cow` spreads a lifetime through every caller |
| 9 | `SmallVec<[T; N]>` | lists are usually short, and their allocation shows in a profile | no profile: `Vec`. Pick `N` from measured lengths; an inline buffer makes the value larger to move |
| 10 | Zero-copy deserialisation | large inputs parse on a hot path (the field form is in the serde section) | the parsed value outlives the input buffer; convert to owned types before it drops |
| 11 | Lending iterator (GATs) | an iterator yields borrows of its own buffer, and generic code consumes several such types | one type: an inherent `next_*` method. `for` loops and adapters don't work on it; callers write `while let` |
| 12 | Channels between stages | producers and consumers run at different rates (the stage shape is in the tokio section) | the stages run at one rate: call the next stage directly |
| 13 | Arena allocation (`bumpalo`, `typed-arena`) | many small nodes live and die together | nodes are freed one by one. Nodes borrow the arena, so it must outlive every reference to them |
| 14 | Typed index vectors | a `Vec` is indexed by a domain id | the `Vec` is only iterated. An index from another table of the same type can still panic: give each table its own index type |
| 15 | String interning (`lasso`) | the same keys are hashed and compared many times | keys are compared once or twice: the interner's map costs more than it saves |
| 16 | Bit sets (`fixedbitset`) | sets of small dense ids are unioned or intersected in a loop | ids are sparse or the sets are small and rare: a `BTreeSet` or hash set |
| 17 | Worklist to a fixpoint | results depend on each other through cycles | the dependencies are acyclic: process in topological order |
| 18 | Incremental queries (salsa) | an edit must re-derive only what depends on it, in a long-lived process | each run computes everything once. It's a framework: adopt it for a whole subsystem or not at all |
| 19 | Enum dispatch | a closed set needs one interface, and `dyn` shows in a profile | the set is open at run time: keep `dyn` |

Marker-parameter typestate (2): shared methods on `impl<State>`, each state's methods on its own block, and a transition that destructures `self`, so a new field must be moved on by hand.

```rust
enum Draft {}
enum Issued {}
struct Invoice<State> { lines: Vec<Line>, customer: CustomerId, state: PhantomData<State> }
impl<State> Invoice<State> { fn total(&self) -> Money { /* … */ } }
impl Invoice<Draft> {
    fn add_line(&mut self, line: Line) { self.lines.push(line); }
    fn issue(self) -> Invoice<Issued> { let Invoice { lines, customer, state: _ } = self; Invoice { lines, customer, state: PhantomData } }
}
impl Invoice<Issued> { fn record_payment(&self, payment: &Payment) -> Result<Receipt, PaymentError> { /* … */ } }
```

Lending iterator (11): the generic associated type's declaration form.

```rust
trait LendingIterator {
    type Item<'a> where Self: 'a;
    fn next(&mut self) -> Option<Self::Item<'_>>;
}
impl<R: BufRead> LendingIterator for LineReader<R> {
    type Item<'a> = io::Result<&'a str> where Self: 'a;
    fn next(&mut self) -> Option<Self::Item<'_>> { /* clear the buffer, read_line, yield a borrow of it */ }
}
```

Typed index (14): the index is made only by `push`, so an index from this table is always in bounds.

```rust
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
struct CustomerIdx(u32);
impl Customers {
    fn push(&mut self, customer: Customer) -> CustomerIdx {
        let idx = u32::try_from(self.rows.len()).expect("a run holds fewer than 2^32 customers");
        self.rows.push(customer);
        CustomerIdx(idx)
    }
    fn get(&self, idx: CustomerIdx) -> &Customer { &self.rows[idx.0 as usize] }
}
```

Worklist (17): the facts must only grow (a lattice), so the loop ends.

```rust
let mut pending: VecDeque<NodeIdx> = graph.nodes().collect();
while let Some(node) = pending.pop_front() {
    let updated = transfer(&facts, node);
    if updated != facts[node] {
        facts[node] = updated;
        pending.extend(graph.successors(node));
    }
}
```
