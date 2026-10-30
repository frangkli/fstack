# Private, durable records

## Destination

A project workflow's retrospective is owned by and committed in that project's repository. Resolve the repository's docs root and private/public conventions first, then use its `retros/` directory. For example, a private repository may use `docs/retros/`; a repository with an export-excluded docs root uses `retros/` beneath that root. Do not assume a particular docs root or privacy mechanism.

Keep the record private according to those conventions. A directory name alone does not protect content in a public repository. If the repository cannot retain a private record, explain the conflict and ask the owner how to protect it within that project before saving private material. Do not select or create a companion repository, or transfer ownership to a setup repository.

Keep the report with the project even when its proposals target shared skills. The location of a proposed fix does not determine the location of the evidence. For a cross-project run, identify the owning project from the brief or ask the owner; do not infer ownership from the proposed fixes. A user can explicitly direct another destination.

## Canonical bundle

Use one directory per run, under `retros/` in the resolved private docs area:

```text
YYYY-MM-DD-<workflow>-retro/
  index.html       # Same readable report for the owner and synthesis agents
  record.json      # Scope, sources, measurements, findings and proposal states
  evidence/        # Retained supporting excerpts or reports, when needed
```

The date is when the report was first written. Revise that record through Git, rather than creating numbered copies. Optional full patch files supplement inline excerpts. Reuse existing project indexes when present. Add a small index of date, run and report only when several records need one.

`record.json` is a small reproducibility manifest. The HTML report itself contains every substantive finding, measurement definition, limitation and proposal that a synthesis agent needs. Reuse existing JSON/CSV exports; do not build a parallel reporting system. Start with the version 1 shape in [record-example.json](record-example.json). Keep its top-level keys, use null with a reason for missing values, and add source-linked rows as needed. Optional extensions must not change an existing field's meaning. Include:

- Schema version, project/run identity, observation start/end, delivery endpoint, follow-up cutoff, collection time and timezone.
- Code/process/skill commits, session and task membership, parent relationships, exclusions and collection commands.
- Source IDs and retained relative paths, original event/message IDs or line ranges, timestamps, extraction/redaction notes and hashes of retained copies.
- Each displayed measure's value or null, unit, numerator/denominator, sample size, source references, coverage, pricing basis and gaps. Definitions live in [measurements.md](measurements.md); record departures explicitly.
- The coverage audit: each dimension's result or unavailable/not-applicable reason and supporting source IDs.
- Findings and their evidence, with proposals linked to findings. Track report publication separately from proposal decisions, implementation commits and verification results.

Use explicit states such as proposed, approved, rejected, superseded, implemented and verified. A merged report changes only its publication state. It does not mark its proposals approved or implemented.

Version 1 rows use these common fields:

- Sources: `id`, `retained_path`, `sha256`, `original_locator`, `timestamp`, `extraction` and `redactions`.
- Findings: `id`, `candidate_source_ids`, `root_cause_key`, `duplicate_of`, `type`, `severity`, `acceptance`, `verification`, `evidence_source_ids` and `fix_commits`. Keep `root_cause_key` null with an explanation when cause is unestablished. Distinct observations need not be distinct causes.
- Proposals: `id`, `finding_ids`, `destination`, `state`, dated `decision_events`, `implementation_commits` and `verification_source_ids`.

IDs are unique within the record. References resolve to those IDs. Keep acceptance and verification independent. Rows with unresolved classifications carry an explanatory `gap`.

For a narrow single-session retro without calculated figures or cross-run synthesis, an existing private Markdown record can hold the scope, core answers, source references and proposal states directly. Do not create empty HTML/JSON shells. Use the full bundle once reproducible calculations or later synthesis need structured inputs.

## Evidence and privacy

Retain enough primary evidence to reproduce the measurements and assess the findings after worktree cleanup. Prefer small sanitized extracts and normalized data over entire transcripts. Preserve a source document when the report depends on its detailed reasoning. Review secrets and unrelated personal or project information before saving anything, even in a private repository.

Cite retained evidence relatively. Record stable thread/session IDs and event timestamps, but do not rely on a thread URL or local transcript path as the only evidence. Cite repository material at the commit read. A hash proves retained bytes stayed unchanged; it does not prove their interpretation is correct.

Before source-worktree cleanup, verify retained-source hashes, links and measurement inputs. Commit the bundle together, with the private/public separation the repository requires. Keep raw scratch captures only as long as needed. If a source cannot be retained safely, describe the resulting verification limit.

## Corrections and later synthesis

Keep the original observation window and historical findings. Record corrections and later dispositions separately, with their date and evidence. Preserve earlier measurements when a changed method breaks comparability.

A synthesis links the source report and finding. Repeated quotations of one event count as one observation. Recurrence requires distinct runs or events. Carry forward rejected and superseded proposals, and report contradictory evidence rather than silently choosing a favorable source. A synthesis is another private record; its publication also does not apply changes.
