# Libraries

Read when adding, choosing or configuring a dependency, or when writing code against a library listed here. The repo's existing choice wins (SKILL.md, Precedence): where it already uses a different crate for a job, use that one and mention a proposed switch in your handoff.

## When a library earns its place

A library earns its place when it does one of these:

- **Removes code you would otherwise maintain** (derives, retries with backoff, argument parsing).
- **Enables something** you can't reasonably write yourself: property tests, fuzzing, snapshot review.
- **Gives a standard interface** that other crates and tools already speak: errors, logging and tracing, serialisation, the CLI.
- **Brings a measured performance benefit** on a path a profile shows.

Better structure, more readable code, a stricter interface or better compatibility with the crates around it count as clear benefits. A library doesn't earn its place when it is only another way to do what std or an existing dependency already does.

Before adding one, check in this order: std; a crate already in `Cargo.lock`; then the candidate's maintenance (last release, open "is this maintained?" issues, RustSec advisories), its license against the repo's allow list (`cargo deny check licenses`), and its cost (`cargo tree` for the crates it adds). A dependency the task didn't call for is the owner's decision: propose it in your handoff with the test it passes.

## Declaring dependencies

- **In a workspace, declare each version once, in `[workspace.dependencies]`,** when a crate first uses it, and write `name = { workspace = true }` in the member crates; a single-crate repo declares it in its own `[dependencies]`. One version per dependency keeps the lockfile small; tools such as cargo-shear or cargo-machete reject an unused entry.
- **Turn default features off only when the defaults pull in something unused** (a compression codec, TLS, a clock), and enable extra features in the crate that needs them.
- **Features unify across one build.** A feature any crate in the build enables is on for every crate, so a missing feature can't keep an API out of library code. Keep it out with Clippy's `disallowed_methods` ([lint.md](lint.md)).

## thiserror and anyhow

- **thiserror:** derive every error type a caller may match (SKILL.md, Errors). It writes the `Display`, `Error::source` and `From` impls you would otherwise maintain by hand. A `Path` or `PathBuf` field formats with `{path}` directly.
- **anyhow:** for code whose errors are only reported, never matched: a binary's command handlers, build scripts, tests. Add context at each `?` with `.with_context(|| format!("cannot load {}", path.display()))`. Keep it out of library crates: a caller can't match an `anyhow::Error` without downcasting.
- **Report at the top of the binary with `{:#}`,** which prints the whole cause chain on one line, and return `ExitCode`:

  ```rust
  #[expect(clippy::print_stderr, reason = "the binary reports its own failure")]
  fn main() -> ExitCode {
      match run() {
          Ok(()) => ExitCode::SUCCESS,
          Err(error) => {
              eprintln!("error: {error:#}");
              ExitCode::FAILURE
          }
      }
  }
  ```

## serde, serde_json and toml

- **serde** is the standard interface for serialisation; derive `Serialize` and `Deserialize` instead of writing parsers for JSON, TOML or YAML.
- **Put `deny_unknown_fields` and `rename_all` on every config and spec type,** so a misspelt key fails loudly. Never combine `deny_unknown_fields` with `flatten`: serde doesn't support the pair. Use `#[serde(default)]` on optional config keys.
- **Parse records you keep raw anyway leniently:** leave `deny_unknown_fields` off types that read upstream data (events, logs, third-party payloads), so a new upstream field doesn't stop ingestion.
- **Choose an enum's tagging by its format and readers.** Externally tagged (serde's default) works in every format. Internally tagged, `#[serde(tag = "kind")]` with the repo's discriminant name, gives the flat JSON objects other languages expect, but needs a self-describing format and allows no tuple variants. Never use `untagged`: its only error is "data did not match any variant of untagged enum".
- **serde_json:** parse into typed structs; reach for `serde_json::Value` only where the shape is open, such as an attributes map. A typed parse skips the fields you don't read and is about twice as fast as building a `Value`. Switch to simd-json or sonic-rs only after measuring on your own data: on typed structs serde_json is often as fast.
- **toml** for config files a person edits.

## clap

- **Derive the CLI** (`#[derive(Parser)]`), model fixed choices as `ValueEnum`, and paths as `PathBuf`.
- **Declare exclusive flags with `#[group(multiple = false)]` or `conflicts_with`,** not runtime checks, so `--help` and the parse error state the rule.
- **Read an environment override through the argument** (`#[arg(long, env = "APP_CONFIG")]`, which needs clap's `env` feature), so it is parsed and validated with the rest of the command line, in the binary.
- **Keep one test that calls `Cli::command().debug_assert()`;** it catches conflicting or misnamed arguments that otherwise fail only when the command runs.

  ```rust
  #[derive(Parser)]
  struct Cli {
      /// Config file to load instead of the default location.
      #[arg(long, env = "APP_CONFIG")]
      config: Option<PathBuf>,
      #[arg(long, value_enum, default_value_t = Format::Table)]
      format: Format,
  }

  #[derive(Clone, Copy, ValueEnum)]
  enum Format { Table, Json }
  ```

## tracing and tracing-subscriber

- **tracing** is the standard interface for logs and spans; libraries emit, the binary decides where events go. How to write spans and events: [review.md](review.md), Tracing.
- **tracing-subscriber** (with `env-filter`) only in the binary, writing to stderr and filtered by `RUST_LOG`:
  ```rust
  tracing_subscriber::fmt().with_env_filter(EnvFilter::from_default_env()).with_writer(std::io::stderr).init();
  ```
- Skip the `log` crate in new code; tracing-subscriber still collects `log` records from dependencies through `tracing-log`. Skip a metrics crate for counts the user must see: those belong in the program's own output or health data.

## tokio and tokio-util

- **tokio** when the program waits on many sockets, files, timers or child processes at once. Each crate enables only the features it uses (`rt-multi-thread`, `macros`, `net`, `fs`, `io-util`, `time`, `sync`, `signal`, `process`). A CLI that does one thing at a time needs no runtime: std's blocking I/O is simpler.
- **tokio-util** for shutdown: a `CancellationToken` that every long task listens to, and a `TaskTracker` to wait for them all.

  ```rust
  let token = CancellationToken::new();
  let tracker = TaskTracker::new();
  let worker = tracker.spawn(run_worker(queue, token.child_token()));
  tokio::signal::ctrl_c().await?;
  token.cancel();
  tracker.close();
  tracker.wait().await;
  worker.await??;
  ```

## Async traits: async-trait against native `async fn`

- **Native `async fn` in a trait** (stable since Rust 1.75) when the trait is never a trait object. In a public trait, the `async_fn_in_trait` lint warns because callers can't require the future to be `Send`: declare the method as `fn run(&self) -> impl Future<Output = Report> + Send` (impls may still write `async fn`).
- **`#[async_trait]`** when the trait is used as `dyn`: an `async fn` in a trait can't be called through `dyn`. It boxes each future, one allocation per call, which is fine when calls happen per job or per connection, not per item. Put the attribute on the trait and on each impl. When leaf crates may depend only on a core crate, re-export the macro from it (`pub use async_trait::async_trait;`).
- Skip writing `Pin<Box<dyn Future<..> + Send + '_>>` by hand: it is the code the macro generates.

## backon

Retry with `backon` instead of a hand-written loop: exponential backoff with jitter, a cap on attempts, and a `when` that retries only errors that can pass.

```rust
let status = (|| fetch_status(&client, &url))
    .retry(ExponentialBuilder::default().with_jitter())
    .when(FetchError::is_transient)
    .await?;
```

- Retry a timeout, a refused connection, HTTP 429 or 503 and their gRPC equivalents; never a 400 or 413, which fail again the same way. Retry only idempotent operations.
- Skip the `backoff` crate: it is unmaintained (RUSTSEC-2025-0012).

## indexmap and rustc-hash

- **indexmap** when insertion order reaches output (SKILL.md, Data). Remove with `shift_remove`, which keeps the order; `swap_remove` is faster and reorders.
- **rustc-hash** (`FxHashMap`, `FxHashSet`) for lookup-only maps on keys an attacker doesn't choose: it hashes much faster than std's SipHash but doesn't resist hash flooding. Keep std's `HashMap` for keys from requests or uploaded files. Neither map's iteration order may reach output.

## aho-corasick and regex

- **regex** for patterns: it runs in linear time, so a crafted input can't make it backtrack. Compile once (a `LazyLock` or at load time). When patterns are ASCII by intent, build them with `RegexBuilder::unicode(false)` over `regex::bytes`: Unicode classes (`\w`, `\d`, `\b`) can make a compiled pattern many times larger.
- **aho-corasick** to find many literal strings in one pass, and as a keyword prefilter in front of many regexes (SKILL.md, Expensive work). For one or two literals, `str::contains` or `memchr::memmem` is enough.
- **`RegexSet`** says which patterns match, not where. It keeps one bounded lazy cache for all its patterns, where N separate `Regex` values keep N caches of up to about 2 MiB each, so it suits a large pattern list when you need only which patterns matched. When you need positions, prefilter with aho-corasick and run the `Regex` of each pattern whose keyword appeared.

## chrono

- Hold instants as `chrono::DateTime<Utc>` and durations as `std::time::Duration`.
- **Pick the time crate your boundaries support.** sqlx, the `clickhouse` crate and utoipa all read and write chrono types, so `DateTime<Utc>` crosses each without adapters. jiff has better-designed types and time-zone handling; choose it when your database and API clients support it or you accept writing the adapters. Never add `time` beside chrono: it does the same job.
- Declare it with `default-features = false, features = ["std", "serde"]`, and add `clock` only in the crate that reads the time.

## tempfile

All temporary files and directories in tests and code go through `tempfile` (`tempdir()`, `NamedTempFile`), which deletes them when the guard drops, even on a panic. How to hold the guard: [review.md](review.md), Tests. Skip hand-built paths under `std::env::temp_dir()`: they collide between parallel tests and leak on failure.

## insta

- Snapshot output that is large or structured (rendered text, JSON, a report), with the `json`, `redactions`, `glob` and `filters` features. Compile it optimised in dev builds, as insta recommends:
  ```toml
  [profile.dev.package.insta]
  opt-level = 3
  [profile.dev.package.similar]
  opt-level = 3
  ```
- Use `cargo-insta`: `cargo insta review` to accept changes, and `cargo insta test --unreferenced reject` in CI to fail on orphaned snapshots.
- Skip it for a small exact value, where `assert_eq!` reads more plainly. Usage rules: [review.md](review.md), Tests.

## proptest

- Enables property tests: a hand-written parser never panics on arbitrary input, `decode(encode(x)) == x`, an invariant holds for any input. Declare it with `default-features = false, features = ["std"]` to roughly halve the crates it pulls.
- Skip quickcheck (weaker shrinking, no regex strategies) and bolero (pays off only with its fuzz engines).
- For coverage-guided fuzzing of parsers of untrusted input, add `cargo-fuzz` with `libfuzzer-sys` and `arbitrary` in a `fuzz/` crate outside the workspace, run on a schedule rather than per pull request.

## cargo-mutants

Enables the check a coverage figure can't make: it changes the code (a function returns a constant, a condition flips) and reports each change no test catches. Run it on the branch's diff before review (`cargo mutants --in-diff <diff file>`), not in CI, since a run takes minutes. It copies the tree into a temporary directory, so point `TMPDIR` at a scratch directory when `/tmp` is small. Pin its version in the repo's tool config.

## Database clients

The reasons below hold for any database client; sqlx (Postgres, SQLite, MySQL) and the `clickhouse` crate are the examples.

- **One crate owns the drivers.** Row structs that derive the driver's traits live there, converted from the domain types with `From`, so domain crates don't compile the driver (SKILL.md, crate graph). The orphan rule also stops that crate from implementing the driver's trait on another crate's types.
- **Bind every value; never format a value into SQL text.** Formatting invites injection and breaks on quoting.
- **Compile-time checked queries or runtime queries.** sqlx's `query!` macros check SQL against a live database or a committed `.sqlx/` cache, at the cost of a database or a JSON file per query, a `cargo sqlx prepare --check` step in CI, and `DATABASE_URL` or `SQLX_OFFLINE` in every build. Choose them when many queries have no test of their own. Choose `sqlx::query_as::<_, T>()` with `#[derive(FromRow)]` when every query runs against a real database in an integration test, which is the check the macros add. sqlx's `macros` feature is still needed for `migrate!` and `#[sqlx::test]`.

  ```rust
  let orders = sqlx::query_as::<_, OrderRow>("SELECT id, total_cents FROM orders WHERE customer_id = $1 ORDER BY id")
      .bind(customer_id)
      .fetch_all(&pool)
      .await?;
  ```

- **ClickHouse parameters:** bind with `Query::param` and `{name:Type}` placeholders. Bind an instant as integer nanoseconds, `fromUnixTimestamp64Nano({start_ns:Int64}, 'UTC')`: ClickHouse rejects chrono's RFC 3339 text for a `DateTime64` parameter. Write a `DateTime64(9)` field with `#[serde(with = "clickhouse::serde::chrono::datetime64::nanos")]`.
- **ClickHouse exactly-once inserts:** when a retried batch must not count twice, write each planned range as one `Insert` with `.with_setting("insert_deduplication_token", ..)` derived from the range. Leave the crate's `inserter` feature off in that case: it ends a batch on a timer, so a retry can cut the range differently and get a different token.
- **ClickHouse schema cache:** the client validates rows against each table's schema and caches it; call `clear_cached_metadata()` after a migration.
- **Compression:** turn a client's default compression off (`clickhouse`'s `lz4`) when the database runs on the same host, where it costs CPU and saves no transfer time; keep it for a remote server.
