---
name: visual-doc
description: HTML documents (plans, explainers, research reports, designs, audits, experiment results, tradeoffs and specs) that help a reader understand and decide. Use when writing or revising any of these as a page someone will read, when a delivery skill reaches its plan step, or when a diagram, metric or comparison would explain faster than prose.
---

# Visual doc

Write one HTML page that explains a design, result or tradeoff so the reader can decide. Announce use of the skill briefly.

## Write it

Load the `writing` skill and follow its technical mode, including its AI-tell pass. The reader is the owner or a teammate: they know the project, its tools and the vocabulary in its README, AGENTS.md and glossary, but not the details of this work. On top of the technical mode:

- The first screen holds the recommendation or result, why it matters, and what the evidence supports. Open with the lead block (`.callout.recommend`): a few short paragraphs, each opening with its point.
- One `h1` (the title). One `h2` per section, phrased as the claim or question it answers. Number the `h2`s when this page or another doc refers to sections by number, and keep those numbers when revising. `h3` only inside a long section. Lectern builds its contents list from the `h2`s and `h3`s outside components.
- Paragraphs and list items of at most three sentences and 50 words, one idea each. A list item that needs more is a finding, a tab or a section.
- Define a term this work or its sources coin (a stage, a ticket code, a rule ID, a measure) at its first use, in a few words. When four or more of them recur through the page, define them instead in a `dl.terms` list after the lead block: at most 8 entries of one line each. A term the reader knows from the project's own docs, or a tool every engineer on the project uses, needs no definition. A page that teaches the reader a new field defines that field's terms too: the list holds the ones that recur, and the rest are defined in place. Name what each part does and who owns it, never a vague box such as "processing layer".
- For a system's design, walk one concrete request through the parts, with real values (path, ID, payload), in a `<details>` under the structure figure. Show a failure or retry only when it explains the design.
- For options, state what would change the recommendation.
- Put each claim's label from the technical mode (measured, inferred, proposed, illustrative) in the figure itself: the tile's source, the tab name or the caption. A measured number carries its sample size, denominator and date, and a paired comparison states that its conditions match.
- Give the as-of date and whether each change is planned, tested or deployed. An explanation is not approval to implement or deploy.
- Method, sources and implementation notes go in closed `<details>`. A limitation that changes the recommendation stays in the main text. A risk that changes the decision goes in `.callout.risk`.
- Keep the current design apart from history. When revising, rewrite the conclusion instead of appending a status paragraph. A page about a past state (an audit, a spec that later decisions replaced in part) keeps its findings as they were, says so at the top, and marks each part that has changed where it appears: a `.tag` ("fixed 2026-10-20", "replaced 2026-10-20") and one line naming what replaced it. The current state goes in a section after the findings.
- Show a UI change as a small HTML mockup or a screenshot.

| Kind | Sections, in order |
|---|---|
| Plan | Recommendation, then data flow (backend), a mockup (UI) or before and after (refactor), options, order of work, risks, decisions |
| Explainer | Overview, key terms, how it works, where things live, gotchas |
| Tradeoff | Recommendation, each option drawn at one scale, what would change the call, decisions |
| Research (audits and status reports too) | Finding, evidence with claim labels, what it doesn't cover, decisions if any, method in `<details>` |
| Experiment | Result, metrics and results table, conditions and sample size, what it doesn't cover |
| Spec | Testable behaviour, where the code lives, out of scope, done when |

## Visuals

Plan the figures before the prose. For each section, name the question it answers and pick the figure in the table below that answers it. Prose carries the reasoning (why, what it means, what would change the call), so a section with more than about 100 words of prose has a figure. Before you write a sentence, find its place in a figure: a node or edge label, a cell, a bar, a tile or a caption.

Vary the figures. A page reads best with several shapes, each used where it fits: use any one component at most twice in the visible page, and `.phases` once. Past that, the content has been forced into the wrong shape. A table is the last choice: keep one only for many exact values, or for two or three options compared on the same properties. A reference table the reader looks up rather than reads goes in closed `<details>`. When a table stays, give it a read direction: one row per thing the reader compares or acts on, the first column naming the row, rows sorted by what the reader decides on, and at most five columns. When the columns are the options being compared, mark the recommended one with `<col class="chosen">` and `<th class="chosen">`.

Keep the visible text (what a reader sees without opening a `<details>` or a later tab, figures included) under about 1,500 words; `page-stats.py` flags it past 1,650. Meet it by cutting words, never by moving a section's main figure into `<details>`. If the page still runs over, split it; a page that can't be split runs over rather than drop a fact the reader needs.

| Content shape | Visual | Rule |
|---|---|---|
| Parts and owners | `.arch` card grid of `.box`es | Cards hold the parts of a system. `.box.new` and `.tag.new` for new parts, `.box.warn` or `.box.bad` for a part at risk, `.owner` for who runs it |
| Findings, gaps, risks, gotchas | `.findings`, each `<li>` marked `bad`, `warn`, `info` or `good` | Most severe first, each a title and at most one sentence, with severity, location, effort or the fix in `.meta` when the source gives them. Past about 6 items, list the rest in a `.findings.compact` list (title and meta only), with their detail in a closed `<details>` after it. Items with no severity are marked by state (`bad` blocked, `warn` open, `good` done), and gotchas are `info` |
| Calls, edges, states | Mermaid flowchart, sequence or state diagram | See diagram rules |
| One request | `.flow` or a sequence diagram | 3 to 6 steps |
| Order of work | `.phases` | Each phase is its `h3`, one sentence, at most three attributes (effort, risk, coverage) in a `.meta` line, then its check. The kit numbers the phases, so their `h3`s carry no number; `li.good` marks a phase done and `li.info` the one in progress. Steps the reader follows are a plain `<ol>` |
| Dated events (an incident, an audit's history, how a decision was reached) | `.timeline`, one `<li>` per event: its `<time>`, then one line | `li.bad`, `li.warn` or `li.good` marks a change of state; the rest stay grey |
| Options | Table with `tr.chosen` (and `tr.risk` for a risky one), in `.scroll` | Followed by a "what would change this" line |
| Status of items against checks | Table whose cells are marked `good`, `warn` or `bad` | A word in every cell, so colour isn't the only cue |
| 1 to 3 numbers | The sentence, with the key number bold | |
| 2 to 4 headline measurements | `.metrics` | Each tile has a `.source` |
| Change over time | `.spark` sparkline in a tile, or Mermaid `xychart` | 3 or more ordered points. The tile's value is the last point |
| Two to four systems or options measured on the same metrics (a benchmark, spike or experiment) | Grouped `.bars`: a `.group` row per metric, one `.bar.s1` to `.s4` per system, keyed by a `.stack-key` with the same classes | One scale per group. When a group spans more than 10×, chart the ratio ("40× faster") and put the raw values in the labels |
| Magnitudes, or where time goes | `.bars`, with `--start` for a waterfall | 4 or more values, units on every bar. Mark each bar `good`, `warn`, `bad` or `info` by what it means for the reader; grey only when no bar means more than its size |
| Part of a whole | `.stack`; a pie only when one share is the point | Its key names every part with its value. Parts that are states (done, running, blocked) take `good`, `info` and `bad`, not the categorical palette. Several wholes split the same way are one `.stack-row` each on one scale; when the reader needs the exact values, the key is a table with a `.swatch` in each row and `.num` columns |
| Before and after | The same figure twice at one scale, in `.arch.two` | Mark only what changes: `<ins>` for an addition, `<del>` for a removal. A side that is new as a whole is a `.box.new` with no marks. A list item that is only an `<ins>` or `<del>` becomes a tinted row |
| Items in order along one quality (cheap to strong, light to heavy) | `.scale`, its two ends named | The order is the point, so no arrows between items |
| Cases (failure modes, environments), or a comparison whose cells need sentences | Tabs, one panel per case, each named in 1 to 3 words | Never a table of sentences |
| Files and calls | File tree with `# role` comments, or a call tree, in `<pre>` | A diff of the tree when the point is the change. A tour of changed files is one closed `<details>` per file, in reading order: its summary names the file, then a `.tag` for new files and a `.meta` with the line counts (`+24 −61`) |
| Dated work | Mermaid gantt | Without dates, use `.phases` |
| Decisions the reader owns | `<ol class="decisions">`, one `<li>` per decision: the action in plain words, then `<span class="default">Default: …</span>`, then any codes or tickets it settles in a `.meta` | At the end. Lectern collects these on its decisions page, so decisions already taken go in a plain table (a list when each needs a sentence) under a heading that starts "Decided" and may state the takeaway ("Decided: code facts come first"). With none left open, end on "Nothing needs you." Decisions that share one action and one default may form one item, which names each of them |

Each figure makes one claim, and its caption opens with that claim. Each keeps a text or table equivalent beside it or in the caption, and stays readable at 390 px wide. Every number comes from a source you can point to. Never invent a value or a position, a quadrant point included. A chart without real data says "illustrative" in its caption.

Diagrams:

- Past about 12 nodes, draw a Mermaid overview of 5 to 8 nodes and put the detail in cards or a second figure. Hand-draw SVG (`.diagram` with `d-*` classes) only when the layout itself carries meaning.
- Keep node labels to a few words and put the detail and the verb on the edges.
- Draw left to right (`flowchart LR`; kit-js draws state diagrams that way unless they set a `direction`), so the diagram uses the page width and keeps the doc short. Use `TD` only for a hierarchy. A diagram gets at most 6 nodes in a row, or 4 when its edges carry labels, and one node fans out to at most 3: merge steps or split it into two figures. Phones switch to top to bottom on their own.
- Colour a node only with `class <node> good`, `warn` or `bad`. Quote labels that contain punctuation, keep colons out of gantt task names, break lines with `<br/>` (written `&lt;br/&gt;` inside an HTML page's `<pre class="mermaid">`, where the browser would otherwise read it as a tag), and keep the classes `.node`, `.label`, `.cluster`, `.edgeLabel` and `.note` off page elements, since Mermaid styles them.

Charts:

- Two measures per item are a quadrant. Never chart small counts such as 3 of 5.
- Start bars at zero, share one scale across small multiples, and sort by value unless the order means something.
- Use one y-axis, label values directly, add gridlines only when the reader must read values, and annotate only the point the caption names.
- When one series or option is the point, colour it and grey the rest.
- Pie, gantt, timeline, quadrant and sankey charts are fine when they are the clearest form.

Tabs switch real scenarios or evidence, and the conclusion stays visible while they change. Add no decorative controls.

## The kit

Copy [assets/template.html](assets/template.html) to the target path, then replace all of its sample content. Point its `<link id="kit">` and `<script id="kit-js">` at [assets/kit.css](assets/kit.css) and [assets/kit.js](assets/kit.js) in this skill's folder, as absolute `file://` URLs (`file:///home/you/.agents/skills/visual-doc/assets/kit.css`). Lectern replaces both with its own kit. Put page-specific CSS in a second `<style>`, for layout only: colours come from the kit's classes and tokens (`var(--good)`, `var(--cat-2)`, `var(--neutral)`) and shapes from its radii, so every page's figures share one look. Set `<meta name="doc-kind">` to `plan`, `explainer`, `tradeoff`, `research` (audits too), `experiment` or `spec`. See [assets/components.html](assets/components.html) for every component; copy only what the content needs.

Formatting serves clarity and consistency. Break a rule when the figure reads better without it:

- Green means recommended, chosen, new or good. Ochre means a decision for the reader or a draft. Red means a risk or regression. Everything else starts neutral. A chart that must tell categories apart uses the kit's categorical palette, which kit-js also gives Mermaid's pie, timeline, sankey and `xychart`. Pair each colour with a word, and refer to a part of a figure by its name, never by its colour ("the Alloy row", not "the green row").
- Bold marks one key number or term in a paragraph.
- Use the kit's type scale, whose steps and their jobs are listed at the top of `kit.css`. Page CSS sets no font size: a component that needs a size takes the step for its job. Write − for minus, "to" for ranges (5 to 12), × for multipliers, and a no-break space between a number and its unit.
- No external fonts, scripts, CDNs or frameworks, with two exceptions: kit-js loads pinned builds of Mermaid and highlight.js from jsDelivr, with integrity hashes, when the page has a diagram or a code block that names its language. Write code as `<pre><code class="language-ts">`, so it is highlighted; a file tree or plain output needs no class. `data-title="src/a.ts"` on the `<pre>` names its file, and `data-lines="2,4-5"` highlights lines, in Lectern. Kit-js also adds the light, dark and system theme control, so add no other.

Use semantic HTML, labelled and keyboard-operable controls, and visible focus. Keep the content readable without JavaScript and at phone width.

## Save

Write HTML with this skill for every document the owner reads that has structure (sections, figures, comparisons or decisions): plans, explainers, tradeoffs, research, designs, specs, experiment results and audits. Write Markdown for a short note with no figures, for agents' working files (run state, tickets, briefs), and for anything an external tool reads, such as a spec framework or an issue tracker.

A Markdown document uses only what Lectern and GitHub both render:

- Front matter declares its kind (`kind: experiment`).
- Alerts carry the callouts: `> [!TIP]` for the recommendation, `> [!WARNING]` for a risk that changes the decision, `> [!NOTE]` for a caveat or coverage gap.
- The decisions are a `> [!IMPORTANT]` alert that holds only a numbered list, each item ending on its own `Default: …` line. Lectern draws it as the decisions list and collects it on its decisions page.
- Code fences name their language. Add `title="path/to/file.ts"` to name the file, and `{2-4}` to highlight lines.
- `<details>` with a plain-text `<summary>` collapses a section. Lectern shows every other HTML tag as text, so write no other HTML.
- ```` ```mermaid ```` fences become diagrams.

1. Save in the worktree you're working in, named `YYYY-MM-DD-<slug>` by the day it was first written:
   - plans, explainers and tradeoffs in `docs/plans/`;
   - research reports and experiment results in `docs/research/`;
   - specs where `to-spec` puts them.

   If the repo documents its own layout for these folders (AGENTS.md, a README inside them), follow that. If its AGENTS.md says "Docs stay local: write them to `docs/local/` in the main checkout.", save them flat in the main checkout's `docs/local/` and never commit them. A doc about no repo goes where AGENTS.md says, never in a GitHub repo. In both flat folders the kind comes from `doc-kind` or `kind:`.
2. Commit the page with the work it explains, or on its own when the page is the deliverable. It merges to main with the work. When revising, overwrite the same file and let git keep the history: no `-v2` or dated duplicates. Lectern then shows each reader what changed since their last read. The only copy never lives in `.context/`, `/tmp` or an environment-provided visualization directory. Evidence captures that no page links to stay in `.context/`.
3. A page with images, evidence files or sibling pages becomes a directory with `index.html`. Link them relatively, never by `file://` or preview URLs; the two kit links are the only `file://` URLs on a page.

## Check before you finish

1. **Fact-check the page.** List every claim a reader could check (paths, names, behaviour, commands, APIs, numbers, dates, git history) and check each against its source: the code, `git show`, a command you run now, or the cited document. Check a requirement against the spec or contract that governs it, and a status (done, merged, in progress) against the remote's main after a `git fetch`. Mark each verified, corrected, unsupported or unverifiable. Fix an error in place, figures included, so the page states the right fact; what you corrected appears only in the closing note. Remove an unsupported claim or label it inferred or proposed. Every source link must resolve for the reader: cite code as the technical mode says, or link it at a commit the remote already has. Name the commit you read in the page header (or say the tree has none), so a reader can find a cited line after the code moves. Done when every claim has a mark; give the counts in a closing `<details>` note, with what you corrected.
2. **Measure it.** Run `python3 <this skill's folder>/scripts/page-stats.py <page>`. It counts the visible words and each figure, and flags a long paragraph or item, a component used past its limit, and a section of prose with no figure. Done when it exits 0, or each remaining flag is one the page needs and you say why in your reply.
3. **Look at it.** Open the page's Lectern link with the browser tool; Lectern serves every worktree's `docs/` and `internal/docs/` live, so the saved file is already there. AGENTS.md names Lectern and its link form. Without it, open `file://<absolute path>`. Don't start a server. Check at 1280 px and 390 px wide in light and dark, use every control, and look for clipping, unreadable labels, misleading scales and broken sources. Every Mermaid diagram must render: kit-js shows a failed one as its source under a red "This diagram didn't render" note, and the page must contain no "Syntax error" and no `aria-roledescription="error"`. Done when both widths and both themes render cleanly and every control works; if no browser tool is available, say that only source checks ran.
4. **Inspect the file** for leftover sample content, placeholders, external dependencies and private data. List every name on the page the reader can't find in the project's README, AGENTS.md or glossary: stages, ticket and rule codes, coined terms, and specialist tools or methods outside the project's own stack. Done when each is defined in place at its first use, or in the `dl.terms` list right after the lead block.
5. **Run the reader test** from the `writing` skill's technical mode on any page longer than about two screens. Done when the test reader states the conclusion and each decision as you meant them, with no open question.

## Deliver

Return the finding or recommendation, the repo path of the page, and its Lectern link if there is one. End with the decisions the reader needs to make, each with a recommended default, or say that nothing needs them.
