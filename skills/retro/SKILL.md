---
name: retro
description: Evidence-led retrospective of a coding session or workflow, with private records, measured outcomes and proposed environment changes.
disable-model-invocation: true
---

Review the session or workflow the user names. Explain its outcomes, reconstruct where resources went, and propose changes supported by the evidence. Publishing a retrospective does not approve or apply its proposals.

## Steps

1. **Scope and record home.** Name the project, run, question, observation window and delivery endpoint. Resolve its private destination with [records.md](records.md). Pin the code, process and skill revisions actually in force. If a historical revision is unavailable, record the gap. Done when unrelated sessions and later follow-ups have explicit inclusion rules.
2. **Collect.** Read primary sources with [session-logs.md](session-logs.md). Read every user turn and failed tool call in the included sessions, then successful work needed to test the explanation. Include child sessions and external reviews. Keep a manifest of included and excluded sources. Done when sources are accounted for, or each missing source is named.
3. **Measure.** Apply [measurements.md](measurements.md). Audit each coverage dimension, then produce the scorecard and relevant breakdowns. Use existing exports and small calculations. Scale investigation to the run: a single session can stay brief, while a parallel workflow needs dependency and overlap analysis. Unknown is a result, not zero. Done when totals reconcile, each dimension has a result or explained gap, and displayed values have definitions and sources.
4. **Investigate.** Test explanations in the categories below. Quantify the observed impact, distinguish correlation from cause, and check counterexamples and successful cases. Trace repeated failures beyond their last symptom. Done when each finding has evidence, an impact or a named measurement gap, and what would disprove it.
5. **Propose.** For each candidate, name its finding, destination, smallest change, expected benefit, cost, trade-off and validation test. Use `writing-for-agents` for instruction text. Use the placement principles in [rules-home.md](../prevent-repeats/rules-home.md), adapted to the repository conventions below. Include a small inline diff when wording matters. Separate measured outcomes from estimated savings. Done when a reader can assess each proposal without reconstructing the session.
6. **Write and preserve.** Use `visual-doc` and the `writing` skill's technical mode, following [report.md](report.md). Write one document for the owner to skim and agents to synthesize. Save it and its supporting inputs per [records.md](records.md), outside scratch storage. Done when source links, retained hashes, arithmetic, chart denominators and the reader test pass, or each limit is stated.
7. **Deliver.** Commit the private record on the task's branch, respecting repo commit boundaries. Push or merge only when authorized. Return its link, publication state, main findings and open decisions. Proposals stay unapplied unless the user separately authorizes them. A newly approved check must fail on the recorded mistake before it counts as implemented.

## Categories

- **Navigation**: how easily did the agent find the right files? Are there hidden dependencies between files? Would a **navigation pointer** help? _Use when_ finding a piece of information took long, or the agent read the same file three or more times.
- **Automated checks**: could a check have caught the agent's mistake: a lint rule, a type, a test, a filesystem check? Read the repo's own check commands first (`GATES.md`, its task scripts, its CI workflow), so a check that exists but sits unwired or silently broken is the finding, not a reinvention. A repo with no **guardrail** (no hook and no CI job running its checks) is itself a finding. _Use when_ the agent made a mistake a check could have caught, or the repo has no guardrail.
- **Review rules**: should reviewers get a new rule, or should one be removed or clarified? Classify the mistake first. A **mechanical** one (a fixed pattern, a banned API, an import shape, a file-location rule) gets a deterministic check: a lint rule, hook or CI job, whichever the repo's tooling makes cheapest. A **judgement call** (cross-file consistency, fit with the surrounding design) gets a rule with a concrete failing case in the repo's review guidance. A pattern reviewers keep flagging that is intended gets a known non-issue entry there. _Use when_ review failed to catch a mistake, or flagged the same non-issue twice.
- **Agent instruction size**: should steering instructions move into a check, or into review guidance where reviewers apply them? _Use when_ the repo's or the user's global agent instructions are large.
- **No-ops**: instructions in steering files that don't change the agent's behaviour. _Use when_ the steering files are large.
- **Tool economy**: expensive tool calls that could be streamlined, or custom tooling (CLIs, MCP servers) that spends many tokens. _Use when_ the agent made an expensive tool call.
- **Workarounds**: the agent routed around a broken script, a flaky check or a missing permission. The finding is fixing it at the source. _Use when_ the agent improvised past a failure.
- **Information access**: give the agent more to see: dev server logs teed to a file, read-only access to third-party services, the repo's observability. _Use when_ a crucial piece of information wasn't available.

## Reference

### Implementation and review

Work goes through implementation and review. The implementing agent carries the most **context pressure**: exploring, writing code, debugging. The reviewer receives a diff and carries the least. So reviewers impose the judgement rules, and checks impose the mechanical ones; the implementer's always-loaded context holds only what it needs to navigate and run checks.

### Repository conventions

Inspect the repository's existing instruction, review-rule and check locations before choosing a proposal's destination. The filenames below are examples; use existing equivalents first. Conducting a retro does not require creating these files or migrating or deleting native bot-rule files. Any convention migration is a separate proposal that needs the owner's approval, including migrations described in the shared placement reference.

### Example files

- `AGENTS.md` (and `CLAUDE.md` where a harness needs it): harness-loaded instructions. Use them sparingly for **navigation pointers**, including a pointer to the repo's review guidance.
- `REVIEW_RULES.md`: review rules and known non-issues. Check which guidance the repo's agents and review bots actually read.
- `GATES.md`: the check commands, what each covers and how long it takes.
- Docs: reference files reached by pointers. Look for an existing doc before writing a new one.
- Skills: for docs whose description should sit in the agent's context, or for commands the user types. Follow `writing-for-agents`.
