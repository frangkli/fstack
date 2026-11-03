## Libraries

The repo's existing choice wins: where it already uses a different crate for a job, use that one and propose a switch in your handoff. The general test for a dependency is in the root `STYLE.md` (Dependencies); these are the Rust forms.

### Choosing a crate

1. **A crate earns its place** when it removes code you would otherwise maintain (derives, retries with backoff, argument parsing), enables what you can't reasonably write (property tests, fuzzing, snapshot review), gives a standard interface other crates already speak (errors, tracing, serialisation, the CLI), or brings a speed-up a profile shows. Better structure, a stricter interface or better fit with the crates around it count too. A crate that is only another way to do what std or a present dependency does doesn't.
2. **Check in this order:** std; a crate already in `Cargo.lock`; then the candidate's maintenance (last release, open "is this maintained?" issues, RustSec advisories), its licence against `deny.toml` (`cargo deny check licenses`), and its cost (`cargo tree` for the crates it adds). A dependency the task didn't call for is the owner's decision: propose it in your handoff with the test it passes.

### Declaring dependencies

1. **Declare each version once, in `[workspace.dependencies]`,** when a crate first uses it, and write `name = { workspace = true }` in the member crates; a single-crate repo declares it in its own `[dependencies]`. One version per dependency keeps the lockfile small; cargo-shear or cargo-machete reject an unused entry.
2. **Turn default features off only when the defaults pull in something unused** (a compression codec, TLS, a clock), and enable extra features in the crate that needs them.
3. **Features unify across one build.** A feature any crate in the build enables is on for every crate, so a missing feature can't keep an API out of library code. Keep it out with Clippy's `disallowed-methods` instead.

### Default picks

| Job | Pick | Section |
|---|---|---|
| Async runtime, shutdown | tokio, tokio-util | tokio |
| Serialisation, JSON, config files | serde, serde_json, toml | serde |
| Errors | thiserror in libraries, anyhow in the binary | thiserror and anyhow |
| Logs and spans | tracing, tracing-subscriber | tracing |
| Command line | clap (derive) | clap |
| HTTP server and middleware | axum, tower, tower-http | axum and tower |
| gRPC and protobuf | tonic, prost | tonic and prost |
| Postgres, SQLite, MySQL | sqlx | sqlx |
| ClickHouse | `clickhouse` | clickhouse |
| Retries | backon | backon |
| Time, UUIDs | chrono, uuid | chrono and uuid |
| OpenAPI from Rust types | utoipa | utoipa |
| `async fn` in `dyn` traits | async-trait | async-trait |
| Insertion-ordered maps | indexmap | indexmap |
| Fast lookup-only maps | rustc-hash | rustc-hash |
| Patterns, many literals | regex, aho-corasick | regex |
| Temporary files | tempfile | tempfile |
| Snapshot tests | insta, cargo-insta | insta |
| Property tests | proptest | proptest |
| Coverage-guided fuzzing | cargo-fuzz, libfuzzer-sys, arbitrary | cargo-fuzz |
| Mutation testing | cargo-mutants | cargo-mutants |
