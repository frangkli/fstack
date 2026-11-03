# Template manifest

What a new repo starts with, per unit: each file in [templates/](templates/), where it lands, and what it requires. Setup ([SKILL.md](SKILL.md) step 6, [agent-docs.md](agent-docs.md)) installs the common unit, then each language unit the repo uses, then each library fragment it uses.

"Beside the code" means the language's own folder (`crates/`, `web/`); in a single-language repo the language's style file is appended to the root `STYLE.md` and its configs go at the root. Merge every config into what the repo already has, never overwrite it, and confirm each lint and rule name against the repo's pinned toolchain.

## Common (every repo)

| File | Lands | Requires |
|---|---|---|
| `common/AGENTS.md` | `AGENTS.md`, with `CLAUDE.md` linking or importing it | the commands table filled with measured times; the generated paths, design doc and docs list; the mutation-testing line only in a Rust repo |
| `common/STYLE.md` | `STYLE.md` | its index filled per language; examples rewritten into the repo's languages |
| `common/TESTING.md` | `TESTING.md` | — |
| `common/REVIEW_RULES.md` | `REVIEW_RULES.md` | only the rules that fit; rules 9–12 only where the repo runs services |
| `common/GLOSSARY.md` | `GLOSSARY.md` | the repo's terms |
| `common/.cursor/BUGBOT.md` | `.cursor/BUGBOT.md`, only where the repo uses Bugbot | `REVIEW_RULES.md` |
| `common/prek.toml` | `prek.toml` | prek, betterleaks and typos pinned in mise; the hostname and private-docs placeholders filled, or the publish-guard hook removed in a repo that never goes public |
| `common/.config/mise.toml` | `.config/mise.toml` | mise; current exact versions |
| `common/.gitignore` | merged into `.gitignore` | — |

## Rust

| File | Lands | Requires |
|---|---|---|
| `rust/STYLE.md` | the Rust style file, beside the code; first in the concatenation | — |
| `rust/libraries/README.md` | appended after `rust/STYLE.md` | — |
| `rust/Cargo.toml` | `[workspace.lints]` merged into the root `Cargo.toml`; each member adds `[lints] workspace = true` | the pinned toolchain |
| `rust/clippy.toml` | beside the root `Cargo.toml` | the repo's product names in `doc-valid-idents` |
| `rust/deny.toml` | beside the root `Cargo.toml` | cargo-deny pinned in mise; network for the advisory database |
| `rust/rustfmt.toml` | beside the root `Cargo.toml` | — |
| `rust/rust-toolchain.toml` | repo root | rustup; the current stable pinned |
| `rust/justfile` | recipes merged into the repo's `justfile` | just, jq, `flock` (util-linux), cargo-nextest, cargo-insta, cargo-deny and cargo-mutants pinned in mise; `services-up` filled in where tests need services |
| `rust/.config/nextest.toml` | `.config/nextest.toml` | cargo-nextest; CI uploads `target/nextest/ci/junit.xml` with `if: always()` |
| `rust/.gitignore` | merged into `.gitignore` | — |

### Rust library fragments

Each `rust/libraries/<name>/STYLE.md` is appended after the README for a library the repo uses. Config fragments:

| Fragment | Lands | Requires |
|---|---|---|
| `insta/Cargo.toml` | the root `Cargo.toml`'s dev profiles | insta, cargo-insta |
| `proptest/Cargo.toml`, `chrono-uuid/Cargo.toml` | `[workspace.dependencies]`; `clock` only in the crate that reads the time | — |
| `tokio/Cargo.toml`, `tonic-prost/Cargo.toml` | the using crate's `[dependencies]` | — |
| `cargo-fuzz/justfile` | the `fuzz` recipe, and two lint lines in the check recipe | cargo-fuzz pinned in mise; a `fuzz/` crate outside the workspace |
| `cargo-fuzz/fuzz.yml` | `.github/workflows/fuzz.yml`, with its path filter and targets filled in | mise-action, just |

Fragments: async-trait, axum-tower, backon, cargo-fuzz, cargo-mutants, chrono-uuid, clap, clickhouse, indexmap, insta, proptest, regex, rustc-hash, serde, sqlx, tempfile, thiserror-anyhow, tokio, tonic-prost, tracing, utoipa.

## TypeScript

| File | Lands | Requires |
|---|---|---|
| `typescript/STYLE.md` | the TypeScript style file, beside the code; first in the concatenation | — |
| `typescript/libraries/README.md` | appended after `typescript/STYLE.md` | — |
| `typescript/tsconfig.base.json` | `tsconfig.base.json`, which each package extends, setting its own `include` | TypeScript 5.8 or later |
| `typescript/oxlintrc.json` | `.oxlintrc.json`, or the `lint` block of `vite.config.ts` in a Vite+ repo, which reads the same keys; Vite+'s own preset turns most of these rules off, so the fragment is needed there too | oxlint, and oxlint-tsgolint for the type-aware rules |
| `typescript/pnpm-workspace.yaml` | merged into `pnpm-workspace.yaml` | pnpm 11 or later |

The TypeScript check runs the tests under a pinned locale (`LC_ALL=en_US.UTF-8`) when they assert formatted text.

### TypeScript library fragments

Each `typescript/libraries/<name>/STYLE.md` is appended after the README for a library the repo uses. Config fragments:

| Fragment | Lands | Requires |
|---|---|---|
| `react/oxlintrc.json` | an override merged into the Oxlint config, with `settings` at the top level | Oxlint's react and jsx-a11y plugins |
| `shadcn/oxlintrc.json` | merged into the Oxlint config, only when `components.json` exists | `@shadcn/lint`, Oxlint 1.80 or later |
| `effect/oxlintrc.json`, `effect/tsconfig.json` | merged into the Oxlint config and the Effect package's tsconfig, `<effect-package>` filled in | effect, `@effect/tsgo` or `@effect/language-service`, `effect-tsgo patch` in `prepare` |
| `knip/knip.json` | the package root, entries adjusted; knip runs in the check command | knip |

Fragments: effect, faker, happy-dom, knip, msw, orval, react, shadcn, tanstack-query, tanstack-router, tanstack-start, testing-library, vitest, zod.
