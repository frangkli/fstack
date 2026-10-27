[00;39m# fstack
[00;39m
[00;39mWhat my agents know. 29 skills, from a one-line fix to a whole product.
[00;39m
[00;39m## Install
[00;39m
[00;39m```bash
[00;39mnpx skills add frangkli/fstack --global
[00;39m```
[00;39m
[00;39mSkills call each other by name, so install them all. The review and fix skills hand work to five Claude Code subagents; copy them too:
[00;39m
[00;39m```bash
[00;39mgit clone https://github.com/frangkli/fstack && cp fstack/agents/*.md ~/.claude/agents/
[00;39m```
[00;39m
[00;39m## Skills
[00;39m
[00;39m**Shape the work**
[00;39m
[00;39m| Skill | What it does |
[00;39m|---|---|
[00;39m| `council` | Five framings answer an open direction, review each other blind, and keep the disagreements. |
[00;39m| `grill` | Interviews you in batched rounds until a plan or idea is settled. |
[00;39m| `research` | A cited research doc on how the code works today, or on outside facts from primary sources. |
[00;39m| `architect` | Competing type-and-signature sketches, judged against a hidden rubric and merged into one design. |
[00;39m| `logic-prototype` | A throwaway prototype that settles a state-model or business-rule question with running code. |
[00;39m| `to-spec` | Turns the conversation into a spec with measurable success criteria. |
[00;39m| `to-tickets` | Breaks a spec into tracer-bullet tickets with blocking edges and one check each. |
[00;39m
[00;39m**Build and ship**
[00;39m
[00;39m| Skill | What it does |
[00;39m|---|---|
[00;39m| `deliver` | A feature end to end: one reviewed plan to approve, then build, review, PR, merge and production check. |
[00;39m| `orchestrate` | Splits implementation into bounded units, each in its own worktree, and re-verifies every one. |
[00;39m| `autopilot` | Drives a spec's tickets to done, unattended, against a countable done-predicate. |
[00;39m| `arena` | Competing builds judged against a rubric written before any of them started. |
[00;39m| `debug` | Builds a failing feedback loop before forming theories. |
[00;39m| `adversarial-review` | Parallel review lanes on a plan or change, with every finding verified before it counts. |
[00;39m| `improve` | Review, verify and fix with a fixed round budget. |
[00;39m| `pr` | Phased commits, a readable PR body, and babysitting until CI and reviews are green. |
[00;39m| `typescript` | Coding and review rules for TypeScript repos. |
[00;39m
[00;39m**Docs and writing**
[00;39m
[00;39m| Skill | What it does |
[00;39m|---|---|
[00;39m| `visual-doc` | Self-contained HTML plans, explainers and reports that help a reader decide. |
[00;39m| `show-me` | Explains the current topic with diagrams and small HTML pages. |
[00;39m| `writing` | Prose for people: messages, docs, specs and announcements, with an AI-tell pass. |
[00;39m| `writing-for-agents` | Skills, AGENTS.md, subagent briefs and prompts. |
[00;39m| `design-rules` | House rules applied alongside impeccable when building or reviewing UI. |
[00;39m| `wait-what` | Makes the agent stop and re-pitch when its last message didn't land. |
[00;39m
[00;39m**Keep the setup improving**
[00;39m
[00;39m| Skill | What it does |
[00;39m|---|---|
[00;39m| `retro` | A retrospective on a session that proposes changes to the agent's setup. |
[00;39m| `prevent-repeats` | Finds mistakes agents keep repeating and adds a check that fails on a real past one. |
[00;39m| `test-audit` | Finds tests that don't earn their place. |
[00;39m| `readiness` | Scores how well agents can work in a repo and fixes the gaps you approve. |
[00;39m| `verify-create` | Generates a project `verify` skill that drives the app the way a user would. |
[00;39m| `verify-maintain` | Keeps that `verify` skill honest as the app changes. |
[00;39m| `tune-up` | Measured improvement runs on a repo or the whole agent setup. |
[00;39m
[00;39m## Requirements
[00;39m
[00;39m- An authenticated [GitHub CLI](https://cli.github.com) and `python3`.
[00;39m- `writing` and `writing-for-agents` read two third-party skills: `npx skills add blader/humanizer danyuchn/asd-ste100-skill --global`.
[00;39m- Optional, used when present: [open-code-review](https://github.com/alibaba/open-code-review) and Codex as extra review lanes, [impeccable](https://github.com/pbakaus/impeccable) for `design-rules`, [AgentsView](https://github.com/kenn-io/agentsview) and [atuin](https://atuin.sh) for `tune-up`, and [T3 Code](https://github.com/pingdotgg/t3code) for delegation and PR watching.
[00;39m- Some skills link to a docs hub, a small server in my [dotfiles](https://github.com/frangkli/dotfiles) that serves every worktree's `docs/` live. Without one, they give the file path instead.
[00;39m
[00;39m## Make them yours
[00;39m
[00;39mPut personal settings, like where private reports go or where notes live, in your `AGENTS.md` or `CLAUDE.md`; the skills read them from there.
[00;39m
[00;39mSeveral skills are adapted from others' work, including [mattpocock/skills](https://github.com/mattpocock/skills), [pstack](https://github.com/cursor/plugins/tree/main/pstack) and [humanlayer/skills](https://github.com/humanlayer/skills). Each skill's `NOTICE` says what it builds on.
[00;39m
[00;39m## License
[00;39m
[00;39m[MIT](LICENSE)
