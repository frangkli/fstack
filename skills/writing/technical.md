# Technical: explanations, plans, reports and specs

The reader must understand a system or make a decision, often later and without your context. They judge the text by whether they can trust each claim and act on it.

## Evidence

Mark how you know each claim whenever the sentence doesn't already make it clear:

- **Measured:** you ran it. Give the number, its unit, and the command or conditions (commit, input size, number of runs): "p95 latency 45 ms over 200 requests at `abc1234`".
- **Inferred:** you reasoned from code, docs or another result, estimates included. An estimate with no basis, or a fact recalled from memory and not checked, is a `[confirm: …]`, not a claim. Cite where (`file:line`, a doc link) and say what would confirm it: "Likely the cause: `retry.ts:40` retries without backoff. A run with backoff would confirm it."
- **Proposed:** your recommendation or design. Say what it costs and what it gives up.

Write an inferred claim in an inferred voice, never in a measured one. Hedge once, with the basis and what would settle it ("likely, from `retry.ts:40`; a run with backoff would confirm it"), never with stacked qualifiers. These three labels, plus illustrative for made-up examples, are the whole legend: write each label as its word, and invent no codes such as [V] or [3P]. Replace adjectives like fast, slow, large, significant and most with the figure, its unit and its baseline: "from 340 ms to 45 ms", "3 of 120 tests". Every number carries a unit, and each unit stays the same across the document. Check that a figure's basis matches the scope you use it for: a count of rules that need code facts doesn't support a plan that builds only some of those facts. Before you write a claim down, run the cheap check that settles it: open the file, run the command. A correction that changes a number gives the value the reader acts on; the old value is history.

## Sentences

- Headings state the takeaway ("Retries cause the duplicate charges"), not the topic ("Retries").
- One name per thing: the real symbol, file, command or person, spelled the same in every section. An ID such as N3 or T25 always carries its name beside it.
- Start a sentence with what the reader already knows and end it with what is new. Keep the verb close to its subject.
- Say it literally: name the mechanism, not a metaphor for it.
- Table cells hold values and short phrases. Content that needs a sentence per cell goes in prose, cards or a list.
- Cite code as inline code, `path:line` or `path:start-end`, from the repo root. For code in another repo, or from a doc outside any repo, put the repo's folder name first, in every citation: `lectern:src/lib/document.ts:42`. Lectern links each citation to the file on the repo's main branch. A document about a past state (an audit, a retrospective) links each citation to the commit it read instead, as a link to that commit on the remote.
- In a spec, MUST, SHOULD and MAY (RFC 2119) mark requirement levels. Elsewhere, write plain verbs.

## By kind

- **Explanation:** start from what the reader already knows and name the mechanism. Give one concrete case (a real call path, an input and its output) before the general rule. Define each term on first use. When more than two components interact, add a diagram through `show-me` (in chat) or `visual-doc` (in a document).
- **Plan:** goals, non-goals, acceptance criteria a command or observation can check, what gets reused or removed, rollout, risks, and the options you rejected with the reason for each. Batch the decisions at the end, each with a recommended default. A calling skill's template takes precedence.
- **Spec:** every requirement can be tested, and the spec ends with a measurable done-predicate. It goes where the repo keeps specs: OpenSpec or Spec Kit if the repo uses one, repo markdown by default, Linear only if the project tracks work there.
- **Report:** follow the contract below.

## Report contract

Skills with their own report format (`adversarial-review`, `improve`) follow it; this is the default for every other report.

1. **Verified before returning.** Run, trace or reproduce every claim you can check. "Next, verify X" is never a closing line: do it, or say what blocked you.
2. **Verdict first.** One or two sentences that answer the question the report was for.
3. **Each finding stands alone:** what and where (`file:line`), why it matters (a concrete failing case or its impact), the evidence (command and output, or the trace), the recommended fix and its cost, and your confidence.
4. **End with only what needs the reader:** decisions, each with its options, a recommended default and the consequence of each choice, in the decisions format of the `visual-doc` skill. If nothing needs them, write "Nothing needs you."
5. **Reader test for long documents** (more than about two screens): give the document to a fresh subagent on the cheapest model your harness offers, such as Haiku or a Luna model, with only what the real reader already knows (for a project's owner or team, the project's README, AGENTS.md and glossary when it has them) and one line saying who that reader is. Ask it to state the conclusion, each decision with its default, and the questions it still has. Where its answers differ from what you meant, or a question remains, fix the document and test again.

## In a subagent brief

A subagent that writes one of these documents gets this block in its brief, verbatim:

> Write for a person who must understand or decide:
> - Open with the conclusion. Name each thing by its exact technical term, define a term the reader may not know where it first appears, and use the term after that, never a paraphrase. Keep the sentences plain and the reasoning between facts in full sentences. Headings state takeaways.
> - Mark how you know each claim: measured (number, unit, command), inferred (cite `path:line`, say what would confirm it) or proposed (what it costs and gives up). Use only these words as labels.
> - Figures, not adjectives ("340 ms to 45 ms", "3 of 120 tests"); one name per thing, the real symbol, file or command; an ID always carries its name; a fact you lack is a visible `[confirm: …]`, never a guess.
> - End with the open decisions, each with a recommended default, or "Nothing needs you".

## Where it goes

A saved document the owner reads is HTML when it has structure (sections, figures, comparisons or decisions): write the content with this file, then hand it to `visual-doc`, which owns the HTML, the file location and the Lectern link. A short note, agents' working files and anything an external tool reads stay Markdown, written with the Markdown rules in `visual-doc`; tickets go where the spec bullet above says. An answer in chat stays in chat.

Done when every number has a unit and a source, every measured claim names its command or conditions, the text ends with decisions or "Nothing needs you", and the AI-tell pass is done.
