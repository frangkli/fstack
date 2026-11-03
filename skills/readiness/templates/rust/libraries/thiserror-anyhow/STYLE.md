### thiserror and anyhow

1. **Derive every error type a caller may match with thiserror.** It writes the `Display`, `Error::source` and `From` impls you would otherwise maintain by hand. A `Path` or `PathBuf` field formats with `{path}` directly.
2. **Use anyhow only for code whose errors are reported, never matched:** a binary's command handlers, build scripts, tests. Add context at each `?` with `.with_context(|| format!("cannot load {}", path.display()))`. Keep it out of library crates: a caller can't match an `anyhow::Error` without downcasting.
3. **Report at the top of the binary with `{:#}`,** which prints the whole cause chain on one line, and return `ExitCode`.

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
