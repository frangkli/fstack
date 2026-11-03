### cargo-fuzz

The general rules for fuzzing are in the root `TESTING.md`; these are cargo-fuzz's forms.

1. **Fuzz parsers of untrusted input with cargo-fuzz, `libfuzzer-sys` and `arbitrary` in a `fuzz/` crate outside the workspace,** with its own `Cargo.lock`. Run it on a schedule or in a CI job filtered to the fuzzed code's paths, not on every pull request (the `fuzz.yml` fragment).
2. **Lint the fuzz crate in the check command:** it is its own workspace, so its targets break unseen otherwise (the `justfile` fragment).
3. **Fuzz the versions the workspace ships:** the CI job copies the workspace's `Cargo.lock` into `fuzz/` before building, since dependency updates touch only the workspace's lockfile.
4. **Build and run with `-s none` (`--sanitizer none`):** only a sanitizer or careful mode adds nightly-only flags, so `cargo fuzz run <target> -s none` builds on stable. A memory sanitizer run still needs nightly.
5. **Fail the job on a crash artifact (`fuzz/artifacts/<target>/crash-*`),** not only on the exit code: libFuzzer's fork mode exits with the last job's code and exits 0 after dropping a seed that crashes. Upload the artifacts when the job fails.
