# Fixing agent docs and gates

For gaps in the agent docs and build-and-checks areas. Read `writing-for-agents` before writing any of these files. The files start from [templates/](templates/); [manifest.md](manifest.md) says where each lands.

## AGENTS.md

Start from [templates/common/AGENTS.md](templates/common/AGENTS.md).

- One root file under ~60 lines, never over 100. Add an app-level `AGENTS.md` only where that app's commands differ, shorter than the root.
- Pointers, not copies: one line each to `STYLE.md`, `TESTING.md`, `REVIEW_RULES.md`, `GLOSSARY.md`, the `verify` skill, the design doc, setup docs, architecture and security docs that exist. Repo-relative paths only.
- The line that tells every agent to read the root `STYLE.md` and the language's style file before implementing and before any style review, and to name both in every brief for a subagent or a review lane (DOC-9).
- Cache only what an agent can't find by looking: unwritten conventions, the reason behind a surprising choice, gotchas. Leave out linter settings, installed skills, slogans and commit attribution.
- Where the repo has a design source-of-truth doc, the line that a changed decision updates it with a dated entry in its decision log.
- Claude reads `AGENTS.md` when `CLAUDE.md` links to it (`ln -s AGENTS.md CLAUDE.md`) or imports it (`@AGENTS.md`); add one only if the repo lacks both. Project skills live in `.agents/skills/`, with `.claude/skills` as a link to it.
- A tool writes into `AGENTS.md` or `CLAUDE.md` only when the owner opts in, and only between its own markers (`<!-- <tool>:start -->` / `<!-- <tool>:end -->`), so it can update or remove its block without touching hand-written text. Flag tool-written text outside a fence.
- Before finishing, run every command in the file and resolve every path.

## The commands table

The commands table lives in `AGENTS.md`, with the columns `Command | Covers | Time`, file-scoped rows first (test one file, lint one file, check one package) and the full check last, followed by the line on running the cheapest covering check while iterating and the full check only at ship points, and the recipe mapping (`setup`, `teardown`, `check`, `fix`, `test <path>`, `dev`). A repo that already keeps these in `GATES.md` passes BLD-3 and DOC-3 as it is; don't move them.

Times come from runs you measured on this machine, rounded. Remove any line that asks for the full check before every hand-off.

## STYLE.md and TESTING.md

Write them at setup from the templates, as [SKILL.md](SKILL.md) step 6 describes:

- The root `STYLE.md` is [templates/common/STYLE.md](templates/common/STYLE.md), with its index filled: one row per language the repo uses, naming its style file and its lint and compiler config files. `TESTING.md` is [templates/common/TESTING.md](templates/common/TESTING.md).
- Each language's style file is the language's `STYLE.md`, then `libraries/README.md`, then the fragment of each library the repo uses, concatenated in that order. It sits beside that language's code (`crates/STYLE.md`, `web/STYLE.md`); in a single-language repo the root `STYLE.md` takes it after its own sections.
- Rewrite each example in the repo's languages and naming case, and point Naming 4 at the file that defines the repo's domain terms (`GLOSSARY.md`, DOC-7).
- When the repo already has a style document, merge the templates into it instead: keep its rules, add the missing ones, and name each conflict in the hand-off for the owner to decide. Move its shared rules to the root `STYLE.md` and its language rules to that language's file.

After setup the project owns its copies: it edits them freely, splits nothing out, and links nothing back to readiness.

## GLOSSARY.md

Start from [templates/common/GLOSSARY.md](templates/common/GLOSSARY.md). One line per domain term, alphabetical. Take the terms from type names, routes, tables and the README, and keep only words whose meaning here differs from everyday use or that a newcomer would have to look up. Grep each term; drop any that appear nowhere in the code or docs.

## REVIEW_RULES.md

Create `REVIEW_RULES.md` at the repo root from [templates/common/REVIEW_RULES.md](templates/common/REVIEW_RULES.md), keeping only the rules that fit the repo, and link it from the root `AGENTS.md`. Rules 9–12 apply to repos that run services. If AGENTS.md has a `## Code Review Rules` section, move its rules into the file and replace the section with the link. Each Known non-issue names the test that pins it, where one exists.

A review bot that reads only its own rules file gets a file that links `REVIEW_RULES.md` and holds no rules of its own, so the bot reviews against the same rules as everyone else and nothing is kept twice. For Bugbot that file is [templates/common/.cursor/BUGBOT.md](templates/common/.cursor/BUGBOT.md): Bugbot always includes the root `.cursor/BUGBOT.md` and counts every `.md` file it links as a rule, and its dashboard holds only rules written there, with no setting that reads a repo file ([Cursor's Bugbot docs](https://cursor.com/docs/bugbot), checked 2026-11-02). Move any rules already in a bot's file into `REVIEW_RULES.md`, leaving the link.
