# fstack

What my agents know. 30 skills, from a one-line fix to a whole product.

## Install

```bash
npx skills add frangkli/fstack --global
```

Skills call each other by name, so install them all. The review and fix skills hand work to five Claude Code subagents; copy them too:

```bash
git clone https://github.com/frangkli/fstack && cp fstack/agents/*.md ~/.claude/agents/
```

## Skills

**Shape the work**

| Skill | What it does |
|---|---|
| `council` | Five framings answer an open direction, review each other blind, and keep the disagreements. |
| `grill` | Interviews you in batched rounds until a plan or idea is settled. |
| `research` | A cited research doc on how the code works today, or on outside facts from primary sources. |
| `architect` | Competing type-and-signature sketches, judged against a hidden rubric and merged into one design. |
| `logic-prototype` | A throwaway prototype that settles a state-model or business-rule question with running code. |
| `to-spec` | Turns the conversation into a spec with measurable success criteria. |
| `to-tickets` | Breaks a spec into tracer-bullet tickets with blocking edges and one check each. |

**Build and ship**

| Skill | What it does |
|---|---|
| `deliver` | A feature end to end: one reviewed plan to approve, then build, review, PR, merge and production check. |
| `orchestrate` | Splits implementation into bounded units, each in its own worktree, and re-verifies every one. |
| `autopilot` | Drives a spec's tickets to done, unattended, against a countable done-predicate. |
| `arena` | Competing builds judged against a rubric written before any of them started. |
| `debug` | Builds a failing feedback loop before forming theories. |
| `adversarial-review` | Parallel review lanes on a plan or change, with every finding verified before it counts. |
| `improve` | Review, verify and fix with a fixed round budget. |
| `pr` | Phased commits, a readable PR body, and babysitting until CI and reviews are green. |
| `typescript` | Review rules for TypeScript code. |
| `rust` | Review rules for Rust code. |

**Docs and writing**

| Skill | What it does |
|---|---|
| `visual-doc` | HTML plans, explainers, research and reports that help a reader decide, styled by a shared kit. |
| `show-me` | Explains the current topic with diagrams and small HTML pages. |
| `writing` | Prose for people: messages, docs, specs and announcements, with an AI-tell pass. |
| `writing-for-agents` | Skills, AGENTS.md, subagent briefs and prompts. |
| `design-rules` | House rules applied alongside impeccable when building or reviewing UI. |
| `wait-what` | Makes the agent stop and re-pitch when its last message didn't land. |

**Keep the setup improving**

| Skill | What it does |
|---|---|
| `retro` | A retrospective on a session that proposes changes to the agent's setup. |
| `prevent-repeats` | Finds mistakes agents keep repeating and adds a check that fails on a real past one. |
| `test-audit` | Finds tests that don't earn their place. |
| `readiness` | Scores how well agents can work in a repo and fixes the gaps you approve. |
| `verify-create` | Generates a project `verify` skill that drives the app the way a user would. |
| `verify-maintain` | Keeps that `verify` skill honest as the app changes. |
| `tune-up` | Measured improvement runs on a repo or the whole agent setup. |

## Requirements

- An authenticated [GitHub CLI](https://cli.github.com) and `python3`.
- `writing` and `writing-for-agents` read two third-party skills: `npx skills add blader/humanizer danyuchn/asd-ste100-skill --global`.
- Optional, used when present: [open-code-review](https://github.com/alibaba/open-code-review) and Codex as extra review lanes, [impeccable](https://github.com/pbakaus/impeccable) for `design-rules`, [AgentsView](https://github.com/kenn-io/agentsview) and [atuin](https://atuin.sh) for `tune-up`, and [T3 Code](https://github.com/pingdotgg/t3code) for delegation and PR watching.
- Some skills link to [Lectern](https://github.com/frangkli/lectern), which serves every worktree's `docs/` live. Without it, they give the file path instead.

## Make them yours

Put personal settings, like where private reports go or where notes live, in your `AGENTS.md` or `CLAUDE.md`; the skills read them from there.

Several skills are adapted from others' work, including [mattpocock/skills](https://github.com/mattpocock/skills), [pstack](https://github.com/cursor/plugins/tree/main/pstack) and [humanlayer/skills](https://github.com/humanlayer/skills). Each skill's `NOTICE` says what it builds on.

## License

[MIT](LICENSE)
