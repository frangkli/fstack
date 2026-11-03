# <Project>

<One or two sentences: what the repo is, who uses it, and how it's deployed or published.>

## Commands

| Command | Covers | Time |
|---|---|---|
| `<test one file>` | <the tests of one file or one test name> | ~1 s |
| `<lint one file>` | <lint and format of one file> | ~1 s |
| `<check one package>` | <one package's lint, types and tests> | ~10 s |
| `<full check>` | everything CI runs: lint, types, all tests, build | ~3 min |

While iterating, run the cheapest command that covers your change; check the packages a unit touched when it's done; run the full check only at ship points: before opening or updating a pull request, and before merge.

| Recipe | Command |
|---|---|
| `setup` / `teardown` | `<runner> setup` / `<runner> teardown` |
| `check` / `fix` | `<runner> check` / `<runner> fix` |
| `test <path>` | `<runner> test <path>` |
| `dev` | `<runner> dev` |

## Code

- Read `STYLE.md` and the style file of each language you work in (`STYLE.md` lists them) before implementing and before any style review. Name both files in every brief you give a subagent or a review lane.
- `TESTING.md` says which kind of test a change needs and what a good one looks like.
- Generated files are never edited: change their source and regenerate. <List the generated paths and the command that regenerates each.>
- Read a library's source or docs at the version the repo pins before using its API; never guess one.
- A general rule fix you find here (a style or testing rule that isn't about this project) also goes back to the readiness templates, by hand, with this project's names and details removed.

## Workflow

- Mutation testing (`<mutants command>`) runs once per change, before the final review round, and only when the change touches Rust.
- `<design doc>` is the source of truth for what the project is and how it's built, with a dated decision log. A changed decision updates the doc and adds a dated entry; decisions never live only in chat.

## Docs

- Review rules and known non-issues: [REVIEW_RULES.md](REVIEW_RULES.md).
- Domain terms: [GLOSSARY.md](GLOSSARY.md).
- Driving the app to see a change work: the `verify` skill in `.agents/skills/verify/`.
- <Setup, architecture and security docs that exist, one line each.>
