### tracing

The general observability rules are in the root `STYLE.md` (Observability); these are the tracing forms.

1. **Emit `tracing` spans at phase boundaries in library crates:** loading, parsing, each request, each job, each query. Only the binary depends on `tracing-subscriber` (with `env-filter`), writes to stderr and reads `RUST_LOG`; a library that installs a subscriber takes the choice away from its caller.

   ```rust
   tracing_subscriber::fmt().with_env_filter(EnvFilter::from_default_env()).with_writer(std::io::stderr).init();
   ```

2. **Give spans static names and put identifiers in fields.** Use `import` with `source = %name`, never `format!("import {name}")` as the name, so spans group and filter by name.
3. **Record data as structured fields and keep the message a fixed phrase:** `debug!(queue = %name, job_count = n, "batch claimed")`. Fields can be queried; text in a message can't. (mechanical)
4. **Write `#[instrument(skip_all, fields(..))]`, at the default `info` level on phase and request boundaries and at `level = "debug"` for detail inside them.** A bare `#[instrument]` records every argument with `Debug`, which can dump whole request bodies and secrets. The usual production filter, `RUST_LOG=info`, disables `debug` spans, so a `warn!` or `error!` inside a phase whose span is at `debug` prints without that phase's fields. (mechanical)
5. **Use `debug` and `trace` for events in library crates.** A problem the user must see reaches them as data (a returned error, a skipped count, a health report), never only as a log line.
6. **Keep disabled events cheap.** Put no `format!`, `to_string()` or `collect()` in event arguments. A spawned task doesn't inherit the current span: attach it with `.instrument(span)`.
7. **Skip the `log` crate in new code;** tracing-subscriber still collects `log` records from dependencies through `tracing-log`. Skip a metrics crate for counts the user must see: those belong in the program's own output or health data.
