### clap

1. **Derive the CLI** (`#[derive(Parser)]`), model fixed choices as `ValueEnum`, and paths as `PathBuf`. Declare exclusive flags with `#[group(multiple = false)]` or `conflicts_with`, not runtime checks, so `--help` and the parse error state the rule. Read an environment override through the argument (`#[arg(long, env = "APP_CONFIG")]`, which needs clap's `env` feature), so it is parsed and validated with the rest of the command line, in the binary. Keep one test that calls `Cli::command().debug_assert()`; it catches conflicting or misnamed arguments that otherwise fail only when the command runs.

   ```rust
   #[derive(Parser)]
   struct Cli {
       /// Config file to load instead of the default location.
       #[arg(long, env = "APP_CONFIG")]
       config: Option<PathBuf>,
       #[arg(long, value_enum, default_value_t = Format::Table)]
       format: Format,
   }
   ```
