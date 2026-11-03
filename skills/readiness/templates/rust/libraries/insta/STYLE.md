### insta

The general rules for snapshot tests are in the root `TESTING.md`; these are insta's forms.

1. **Snapshot output that is large or structured** (rendered text, JSON, a report) with insta's `json`, `redactions`, `glob` and `filters` features, and accept changes with `cargo insta review`, reviewing each as a behaviour change. Snapshot a fixture set with `glob!` or named snapshots: unnamed snapshots in a loop are numbered, and the numbers shift when a case is added. Normalise unstable output with `filters` or `redactions`. Skip insta for a small exact value, where `assert_eq!` reads more plainly.
2. **Fail CI on orphaned or unwritten snapshots with `cargo insta test --unreferenced reject --check`.** `--check` fails instead of writing new snapshots.
3. **Keep insta out of tests CI skips (ignored tests):** under `--unreferenced reject` their snapshots look orphaned, so ignored integration tests compare values.
4. **Compile insta and similar optimised in dev builds,** as insta recommends (the `Cargo.toml` fragment).
