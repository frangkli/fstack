#!/usr/bin/env bash
# Runs the sample workspace with the readiness Rust templates' configs: format, lints, docs,
# dependency policy, tests and the snapshot orphan gate. Run from anywhere in the fstack repo.
set -euo pipefail
repo="$(git rev-parse --show-toplevel)"
templates="$repo/skills/readiness/templates/rust"
root="$(git rev-parse --path-format=absolute --git-common-dir)/scratch"
mkdir -p "$root"
work="$(mktemp -d "$root/rust-templates.XXXXXX")"
trap 'rm -rf "$work"' EXIT

cp -r "$repo/tests/readiness-templates/rust/." "$work/"
rm "$work/check.sh"
cat "$templates/Cargo.toml" "$templates/libraries/insta/Cargo.toml" >> "$work/Cargo.toml"
cp "$templates/clippy.toml" "$templates/deny.toml" "$templates/rustfmt.toml" "$templates/rust-toolchain.toml" "$work/"
mkdir -p "$work/.config" && cp "$templates/.config/nextest.toml" "$work/.config/"
cd "$work"

tools=(mise x cargo-insta@1.49.0 cargo-deny@0.20.2 'github:nextest-rs/nextest[version_prefix=cargo-nextest-]@0.9.148' --)
export CARGO_BUILD_WARNINGS=deny
cargo fmt --all --check
cargo clippy --workspace --all-targets --locked
RUSTDOCFLAGS="-D warnings" cargo doc --workspace --no-deps --locked
if "${tools[@]}" cargo deny --locked fetch >/dev/null 2>&1; then
  "${tools[@]}" cargo deny --locked check
else
  echo "cargo deny: skipped, the advisory database couldn't be fetched (no network?)"
fi
"${tools[@]}" cargo insta test --workspace --test-runner nextest --unreferenced reject --check
echo "rust templates: sample passes"
