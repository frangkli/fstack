#!/usr/bin/env bash
# Runs the TypeScript sample package under the readiness template configs: tsconfig.base.json and
# oxlintrc.json are copied in from the templates, so a template change that breaks a plain package
# fails here. Runs in a scratch copy under the git common dir, never /tmp.
set -euo pipefail

repo="$(git rev-parse --show-toplevel)"
sample="$repo/tests/readiness-templates/typescript"
templates="$repo/skills/readiness/templates/typescript"
root="$(git rev-parse --path-format=absolute --git-common-dir)/scratch"
mkdir -p "$root"
scratch="$(mktemp -d "$root/readiness-ts.XXXXXX")"
trap 'rm -rf "$scratch"' EXIT

cp -R "$sample/src" "$sample/package.json" "$sample/pnpm-lock.yaml" "$sample/tsconfig.json" "$scratch/"
cp "$templates/tsconfig.base.json" "$templates/oxlintrc.json" "$scratch/"
cd "$scratch"

pnpm install --frozen-lockfile --silent
pnpm exec tsc --noEmit -p tsconfig.json
pnpm exec oxlint -c oxlintrc.json --type-aware src
LC_ALL=en_US.UTF-8 pnpm exec vitest run
echo "not run here: the react, shadcn and effect fragments need their frameworks and plugins installed"
