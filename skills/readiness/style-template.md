# Style

The naming, comment and structure rules no formatter, linter or compiler checks, and each language's never list. Read this file before writing code, and a language's style file before working in that language.

| Language | Style file | Lint config | Reviewed with |
|---|---|---|---|
| <Language> | `<path>/STYLE.md` | `<lint and compiler config files>` | the `<language>` skill |

## Naming

1. Name a value for what it is in the domain, not its container: `invoices`, not `data`; `data`, `item`, `value`, `result` and `tmp` fit only a scope a few lines long.
2. Name the exact concept, not a broader one it belongs to: `dedupe_ranges`, not `process_ranges`.
3. Use one word per concept and one concept per word: once a read position is a `cursor`, no module calls it an `offset`.
4. Check a new domain word against `GLOSSARY.md`, and add a new concept's term there.
5. Make a name promise no more and no less than the code does: `load` and `fetch` do I/O, accessors are cheap and can't fail, and `parse_header` doesn't also store the row.
6. Name a function without side effects with a noun phrase, one with effects with an imperative verb, and an expensive or remote read with a verb: `row_count()`, `flush()`, `fetch_rates()`. Predicates (Naming 9) and the language's conversion and constructor prefixes (`parse`, `to_`, `as_`, `from_`, `new`) keep their forms.
7. Make the return type agree with the name: a plural returns a collection, `is_` and `has_` a boolean, `parse` and `to_` the converted value, and `set_` nothing.
8. Keep a name, its type and its comment saying the same thing, and name a stateful type for every state it reaches: an `is_loading` that stays true after an error belongs in a status with one value per state.
9. Name booleans and predicates as questions, never negated: `is_stale`, `has_rows`, `can_retry`, not `not_ready`.
10. Put the unit in the name when the type doesn't carry it: `timeout_ms`, `size_bytes`.
11. Name bounds with fixed pairs: `start` and `end` are half-open, `first` and `last` inclusive, and the pairs never mix.
12. Put computed-value qualifiers (`max`, `min`, `count`, `total`) last, so a family sorts together: `latency_max`, `retry_count`. Put a category word (`Error`) where the language's standard library puts it, last in most (`ParseIntError`).
13. Don't repeat what the receiver, type or module already says: `session.id`, not `session.session_id`.
14. When the type is weak (a string, an integer), let the parameter name carry the role: `tag(rule_id, line_number)`, not `tag(s, n)`.
15. Let a name's length follow its scope: single letters only for short, conventional roles, such as a one-line callback's parameter.
16. Write whole words, and abbreviate only established terms (`id`, `url`, `ms`), never one the project coined: `threshold`, not `thld`.
17. Use no numeric suffixes and no near-twin names in one scope: `raw_rows` and `deduped_rows`, not `rows2` and `rows_new`.
18. Treat an `and` in a name, or a name you can't make precise, as a design problem: `parse_and_store` becomes `parse` and `store`.
19. Name an error variant for the step that failed, not the system it called: `ReadConfig`, not `Io`.
20. Name a test for the behaviour it protects: `skips_a_range_already_inserted`, not `test_insert_2`.

## Comments

Code documents itself through its names and types, and every non-obvious choice gets a comment, one line by default.

1. Give each public item other modules use a doc comment that says what it is, what it guarantees and when it fails, unless its error type already says so.
2. Write the doc summary in words other than the item's name: not "Returns the path." on `path()`.
3. In a doc comment, state whichever the caller needs: units, inclusive or exclusive bounds, what empty or absent means, ownership and cleanup, thread safety, invariants.
4. Keep how it works out of the doc comment: that goes in line comments in the body, next to the code it explains.
5. Comment the why above the code it explains, in one line unless the reader needs more: an optimisation, a workaround, an invariant, or a choice that would make a reviewer stop.
6. Section a long block with blank lines and a short comment per section that names what it achieves; if the section's first line says the same as the comment, delete the comment.
7. Keep comments true: a change that makes a comment wrong fixes or deletes it in the same commit.
8. Write about the code, never about the review or the agent: no "per review feedback" comment.
9. Write no banner comments, commented-out code or change history: git holds the history.

## Structure

1. Keep functions flat: return early, make decisions in the caller, and put the straight-line work in the helpers it calls.
2. Organise modules by domain, and keep each type next to the code that keeps its invariants: no module named `utils`, `helpers`, `common`, `types` or `models`.
3. Write pure transforms as chains (`map`, `filter`) and side effects as loops, and keep a chain's callbacks free of side effects; use a loop for a pure transform that exits early, builds several outputs or is measured-hot.
4. Build a value, then stop changing it: the binding that outlives construction is immutable.
5. Declare each fact once: when two declarations must agree, derive one from the other.

## Never: <Language>

<The never list from the readiness skill's `stacks/<language>.md`, one section per language.>
