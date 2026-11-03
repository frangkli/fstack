### cargo-mutants

The general rules for mutation testing are in the root `TESTING.md`; these are cargo-mutants' forms.

1. **Run cargo-mutants on the change's diff** (`cargo mutants --in-diff <diff file>`, the `mutants` recipe), once per change, before the final review round, and only when the change touches Rust; not in CI, since a run takes minutes. It changes the code (a function returns a constant, a condition flips) and reports each change no test catches.
2. **Point `TMPDIR` at a scratch folder:** cargo-mutants copies the tree into a temporary directory, and `/tmp` is often small. The recipe takes a lock under the git common dir's `scratch/`, so one run happens at a time across worktrees.
3. **Pin its version in the repo's tool config.**
