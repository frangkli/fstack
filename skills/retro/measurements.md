# Measurement contract

Collect evidence that answers the retrospective's question. Do not add monitoring, paid calls or production probes just to fill a dashboard. Record missing telemetry and propose the smallest collection needed for a future run.

## Scope before totals

Define start, end and timezone, the delivery endpoint, included tasks, repositories, worktrees and providers. A reopened follow-up has its own interval. If usage includes a closing response after delivery, name that accounting endpoint separately.

Use the core scorecard for every retro. Unknown or not applicable must carry a reason. For a short single-session retro, expand only measures relevant to the question. Multi-agent runs need phase/role breakdowns, concurrency and finding attribution where sources permit them.

## Core scorecard

| Measure | Definition and required context |
| --- | --- |
| Outcome | Completed/accepted work units divided by scoped units; check results on a named head; escaped defects only through an explicit follow-up cutoff. |
| Elapsed time | Delivery endpoint minus run start. Separate the union of active intervals, dependency waits and unclassified time where known. Never call a task's lifetime model compute time. |
| Tokens | Provider-native billable categories, summed once within the accounting scope; show cache separately. Break down by actual model, role and phase, retaining mixed or unknown attribution. |
| Cost | Actual billed spend when available, otherwise a labeled estimate with dated pricing or recorded accounting source. Separate providers, estimates, subscription charges and unpriced usage. A priced subset is not the total run cost. |
| Findings | Raw candidates, accepted concerns and independently verified findings, with type and severity kept separate. Deduplicate confirmed root causes. Show fixed/verified, deferred, refuted and unverifiable separately. Acceptance is not verification. Keep bundled concerns as bundles when atomic counts cannot be established. |
| Review and rework | Review, verification and fixing effort, separately when attributable; new defects introduced by fixes, reopened findings and repeated review rounds. Mark task-level combined review/fix accounts as combined. |
| Evidence coverage | Included/excluded sessions; events with timestamps; classified versus unknown time/tokens; priced usage and follow-up availability. Give the denominator for each coverage claim. |

For a full workflow report, lead with elapsed time, cost, tokens and confirmed findings, then add a compact operational scorecard from the coverage audit below. Useful additions include accepted scope, first-pass acceptance, verified fixes, reopens, check time, blocking waits, tool failures and evidence coverage. Four headline values are an entry point, not a limit. Each value carries its scope and missing-data qualifier. A short session retro can answer the core questions in a compact list.

## Coverage audit

Consider every dimension below before choosing deep dives. Mark each measured, unavailable or not applicable, with a reason and source coverage. A flow-specific dimension can be added. This audit prevents available token totals from crowding out other bottlenecks; it does not require a graph for every row.

Keep the audit in the methods record. Beyond the core overview, publish measurements when they support an observation, explain its scope or qualify its reliability. Broad investigation does not require displaying every available statistic. An ordinary-looking result needs no extra panel merely because it was measured.

| Dimension | Questions and useful measures |
| --- | --- |
| Scope and outcome | Planned/accepted/abandoned units, scope changes, first-pass acceptance and acceptance criteria. Keep units comparable. |
| Requirements and design | Clarification and decision counts, design revisions, rejected approaches, discovery-to-decision intervals and attributable effort. |
| Usage and cost | Provider/model components, phase and role shares, cache, priced/unpriced coverage and cost per accepted comparable unit. |
| Execution and tools | Failed calls by cause, retries, rate limits, context compactions, repeated discovery and abandoned attempts, with attributable time/usage when available. |
| Time and coordination | Elapsed and task time, dependencies, concurrency, queue/approval waits, handoffs and owner interventions. |
| Builds and verification | Compilation/test/check durations and exits, incomplete suites, repeated heads/configurations, cold/warm caches, fuzz or other oracle coverage. |
| Review and rework | Candidate adjudication, severity, independently verified causes, lane overlap, fix rounds, verification coverage, reopens and fix-induced defects. |
| Integration and delivery | Conflicts, integration attempts, CI queue/run time, release/merge gates, accepted-head verification and close-out work. |
| Compute and resources | Run-owned CPU time and peak memory, host/container pressure or limits, lock/network/storage bottlenecks, explicit failure evidence. |
| Evidence and follow-up | Session/usage/exit-result coverage, attribution gaps, preserved inputs and escapes through a stated cutoff. |

Collection stays simple: reuse available session/accounting exports, command logs and CI data. Retain the small query, spreadsheet formula or one-off calculation needed to reproduce a figure. Build a reusable parser or collection service only when separately requested; do not make it a prerequisite for a retro.

## Provider accounting and attribution

- Select sessions by run membership, not project name or working directory alone. Some agents run from the conductor's directory. Record parent/child links and exclude unrelated work in the same window.
- Choose parent totals including children or individually counted child rows. Never sum both. Deduplicate streaming message records by request/message identity and retain final usage. Preserve retries as separate requests.
- Claude input, output, cache creation and cache reads can be separate accounting categories. For Codex, cached input is a subset of input and reasoning output a subset of output. Confirm the source's semantics before adding fields. For cumulative counters use final totals or non-overlapping deltas, never their sum.
- Tool-returned token counters are not automatically full provider usage. Report their name when complete accounting is unavailable. Do not infer dollars from a context counter.
- Role and phase are separate dimensions. An agent's model does not establish its role. A fixer doing verification may span phases. Use tagged events when available; otherwise retain a mixed bucket instead of inventing a split.
- Show token share and dollar share separately. Cheap cache reads can dominate tokens without dominating cost. Keep unpriced categories visible, and use unrounded values for totals.

## Time, concurrency and the critical path

Keep three views distinct:

1. **Elapsed delivery time:** one wall-clock interval.
2. **Task/process time:** task lifetimes, nested commands, CPU time and machine utilization, with units and definitions kept separate.
3. **Critical path:** the dependency chain that determines the delivery endpoint. It can change as work proceeds.

Reconstruct a task dependency graph from launch, report, integration and gate events. Use interval unions for simultaneous activity. A worker waiting on a compiler is not model activity merely because its task is running. Subtracting model-token generation estimates from task lifetimes does not measure idle time.

Report the sum of command wall durations separately from the union of intervals with commands running. Do not count a nested build/test command again inside its enclosing command family when making additive totals. Keep head, configuration and cache state when comparing repeated checks; repetition alone does not establish waste.

For a decomposition that sums to elapsed time, partition the critical path into exclusive intervals such as model/tool work, compilation, tests, approval wait, capacity wait, integration and unknown. State the attribution rule for ties and overlapping intervals. Also show resource activity on parallel lanes when it explains a delay. Build/test durations inside agent spans are drill-downs, not extra slices added to the same whole.

If dependencies or timestamps are insufficient, show overlapping spans and their coverage. Do not manufacture a complete decomposition. A measured critical-path blocker is an upper bound on savings from removing it; rerouting work can expose another bottleneck. Estimate joint changes with the dependency graph instead of adding their isolated savings.

## Conditional deep dives

| Question | Measures and evidence | Useful view |
| --- | --- | --- |
| Where did delivery wait? | Owner decision, permission, queue/capacity, network, provider limit and idle intervals; blocked descendants; intervention count and response latency. | Dependency timeline and exclusive critical-path decomposition. |
| Did builds/tests dominate? | Command start/end, exit, package/head, cold/warm cache, toolchain, queue/lock wait, retries, compilation versus execution. | Duration distribution and timeline; separate CI from local runs. |
| Did review earn its cost? | Unique confirmed findings per lane and severity, overlaps, verifier time, fixed/verified count, regressions from fixes, review rounds and costs. | Lane-overlap matrix and paired cost/yield charts with denominators. |
| Was implementation repeatedly redone? | Superseded work, abandoned attempts, conflict resolution, repeated checks of the same artifact, intervention and rework cost where attributable. | Rework by phase and event timeline. |
| Were resources limiting? | Timestamped CPU/core saturation, run queue, CPU pressure or throttling, memory/RSS pressure, OOM events, I/O wait and build-lock waits, tied to the relevant process or cgroup. | Aligned resource traces over task spans; event annotations. |
| Did quality survive delivery? | Escaped defects per accepted scope and observation window, coverage denominators, fuzz executions/resource failures and verifying oracle, regression-test evidence. | Cohort outcomes with unobserved follow-up marked, not counted as clean. |
| Is a change worth trying? | Observed loss, mechanism, addressable critical-path time or spend, change/run overhead, implementation and maintenance cost, uncertainty and cheapest falsification. | Range or scenario comparison, labeled inferred. |

Also consider a Pareto chart of tool failures, a queue-versus-execution plot, a cumulative accepted-work curve, or a phase-by-role heatmap when the audit points there. Paired token/spend bars reveal differences in cache and pricing; a review-round chart reveals convergence; a candidate-disposition bar reveals adjudication gaps. Use a funnel only when each stage is a true subset of the previous stage.

For findings, “unique to a lane” means no other included independent lane reported that confirmed root cause. State the comparison set. Do not add exclusive lane findings to shared counts twice. Findings per thousand lines or per dollar need the same inspected scope and follow-up conditions; generated code and bundled reports can invalidate that comparison.

Useful conditional ratios include independently verified fixes divided by claimed fixes, reopened findings divided by previously fixed findings, and verified candidates divided by adjudicated candidates. State the adjudication rule and unresolved count. None measures recall: the full defect population is unknown.

Do not use unmatched tickets to claim one model is more capable. A matched trial holds packet, instructions, tools, budget, head and oracle constant and reports repetitions and sample size. A single pair is descriptive. Show sample size with distributions; do not present a small-sample p95 as a stable service-level estimate.

## Resource evidence is not resource causation

A slow command alone does not prove contention. Distinguish process wall time from CPU time and machine-wide utilization from the task's own consumption. Evidence of a bottleneck needs aligned telemetry or an explicit failure, such as an OOM event, then a traced connection to the affected task. A controlled rerun can test the explanation but changes to cache, head, load or runner invalidate a simple before/after claim.

Historical absence of CPU/memory measurements stays unavailable. For future runs, propose bounded collection through existing telemetry or per-command CPU/RSS/exit measurements plus timestamped host/cgroup samples. State sample interval, machine/runner identity, collection overhead, ownership and retention. Use the tools already present, respect shared-machine limits, and stop collectors you started. Do not record secret environment values or monitor unrelated processes.

## Checks before publication

Reconcile scoped totals, phase/role shares and excluded records. Match every number and chart mark to a source. Check that shared IDs, values, limitations and proposal dispositions agree between the HTML and sidecar. Record observed, inferred and unavailable separately. Keep the extraction method and normalized inputs so another reader can recompute the figures after scratch cleanup. Counterfactual savings and recommendations remain proposals, even when their motivating loss was measured.
