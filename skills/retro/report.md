# One report for skimming and synthesis

The owner skims this report; later agents read the same document to synthesize changes across retros. Use `visual-doc`'s shared HTML kit for full workflow reports. The [chart menu](assets/report-example/index.html) demonstrates several chart choices with explicitly invented data. Its density and chart count are not the usual report format or a target to match.

[records.md](records.md) owns destination and publication; use `visual-doc` for presentation and checks. Its generic save/publish defaults do not relocate or authorize publication of this record.

Keep the first screen compact and informative. Put important charts and findings in the visible page, with exact-value tables and extraction detail in disclosures. The report may exceed a generic word target when that preserves material evidence or coverage; reduce repeated prose before dropping information. A narrow single-session retro can use private Markdown per [records.md](records.md).

## Reading order

1. **Outcome and scorecard.** Run identity, endpoint and result, then elapsed time, cost, usage and confirmed findings. Add operational measures from the coverage audit in [measurements.md](measurements.md). Show units, denominators and data gaps. The opening must reveal quality and coordination as well as spending.
2. **Effort and delivery.** Show phase/role composition, provider/cache effects and task spans. Establish the critical path only when dependencies support it. Otherwise identify overlaps and missing dependencies. Separate elapsed, accumulated task and command time.
3. **Quality and process.** Show relevant candidate dispositions, review convergence, rework, command durations, tool failures, delivery gates or resource traces. Select charts from the run's evidence, not a predetermined count. Keep applicable coverage gaps visible even when no chart is possible.
4. **Findings and proposals.** Give each finding a stable anchor and name. Connect observation, measured exposure, mechanism and alternatives, focused inline diff, expected value and validation. Include successes worth preserving. Rank by severity and measured impact, with uncertainty separate.
5. **Decisions and synthesis record.** State options, costs, trade-offs and defaults for open choices. Give each proposal its state, destination and linked findings. Keep rejected/superseded proposals and later corrections available. Publishing the report does not approve changes.
6. **Method and evidence.** Include the full coverage audit, definitions, scope/membership, denominators, extraction/calculation commands, exact inputs and source manifest. Link retained evidence relatively. Describe what cannot be concluded.

## Chart selection

Start with an evidence-backed observation, then choose its presentation. A chart earns its place when its pattern, distribution, overlap, relationship or comparison helps the reader assess that observation beyond what the heading and a short sentence convey. If removing the chart loses no useful information, use the sentence. A simple count or percentage rarely needs a graph. There is no minimum chart count, and variety alone is not a reason to include one.

| Question | Useful chart | Constraint |
| --- | --- | --- |
| Who spent effort on what? | Phase-by-role heatmap or grouped bars | Keep role and phase distinct; retain mixed/unmapped work. |
| Do tokens explain spend? | Paired token/spend composition bars | Separate provider semantics and unpriced work. |
| What overlapped or blocked delivery? | Dependency lanes and evidenced blocking intervals | No elapsed-time pie of overlapping task spans. |
| Did remediation converge? | New/fixed/reopened/open findings by round | Reconcile opening balance plus arrivals minus fixes. |
| What did independent review add? | Shared/exclusive finding matrix | Same inspected scope; deduplicate confirmed causes. |
| Where did candidate concerns end up? | Disposition bar | Acceptance is not verification; funnel stages need real subsets. |
| Which checks were slow or repeated? | Command-duration dots grouped by head/configuration | Show sample size and cache state; repetition alone is not waste. |
| What caused execution friction? | Ranked failure bars or cumulative Pareto chart | State denominator, recovery and attributable cost. |
| Did resources coincide with failures? | Aligned CPU/memory/pressure and command traces | Missing samples stay gaps; correlation is not causation. |
| Did delivery or quality change across runs? | Accepted-work, escape or cost trends | Match definitions, workload and follow-up windows. |

Use small multiples for related questions, direct labels and shared scales where comparable. Pair each chart with its supported observation and explain what the marks add. Keep exact values accessible without hover. During the final skim, remove charts and auxiliary statistics that support no observation; preserve necessary scope, denominators and uncertainty. Do not fill missing historical data with estimates presented as observations.

## Synthesis must work from the HTML alone

Use stable named anchors for findings, proposals, figures and source entries. Include exact values, definitions, evidence references, observation windows, baseline revisions, uncertainty and proposal disposition in the document text. Data is present in semantic HTML without executing chart JavaScript. A sidecar supports recomputation; it must not contain the only copy of a finding or qualification.

When revising an existing report, compare its sections with the replacement before continuing. Account for earlier findings, successful practices, qualifications and proposals in the same document; a retained source link alone does not make them discoverable. Use a short synopsis and a historical disclosure when full detail would overwhelm the skim. Label historical proposals and superseded definitions so they cannot become current decisions by accident. Preserve exact source bytes separately when repository formatting hooks normalize browsable copies.

For each finding, include the smallest event sequence or reproducer, measured impact or explicit gap, mechanism and competing explanation, proposed destination/diff, estimated benefit and cost, and cheapest falsification test. Distinguish observed exposure from potential savings. Keep severity meaningful even when dollars are unknown.

Later synthesis links the source run and finding, carries contradictory evidence and rejected proposals, and counts distinct events rather than quotations. No composite efficiency score or model ranking is required. Existing exports and a few reproducible calculations are sufficient; this contract does not require a reporting application.
