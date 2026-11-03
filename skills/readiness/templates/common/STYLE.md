# Style

The rules every language here shares: naming, comments, structure and the general guidance on types, errors, boundaries, concurrency, retries, observability, security, dependencies, API design and performance. Each language's style file holds the rules and tooling that only that language has. `TESTING.md` holds the testing guide.

Every agent reads this file and the style file of each language it works in before implementing and before any style review. A brief for a subagent or a review lane names both files.

| Language | Style file | Lint config |
|---|---|---|
| <Language> | `<path>/STYLE.md` | `<lint and compiler config files>` |

Each rule gives its reason and an example in each language. A rule marked **(mechanical)** names a pattern that a tool could find from syntax alone; those are candidates for a future lint.

Where existing code follows a clearly worse pattern than a rule here, use the better pattern in the code you change and say why in the handoff. Leave untouched code as it is and mention it instead.

## Naming

A reader sees a name at every use and its definition only once, so the name has to say what the thing is and what it does, in the words the project uses.

1. **Name a value for what it is in the domain, not its container.** `data`, `info`, `item`, `value`, `result`, `tmp`, `handle` and `process` say only that something exists, so they fit a scope a few lines long. Rust: `let invoices = load_invoices(dir)?;`, not `let data = …`. TypeScript: `InvoiceTimeline` and `useQuotaRunway`, not `DataTable2` and `useData`.
2. **Name the exact concept, not a broader one it belongs to.** A broad name sends the reader into the body to learn what the function does. Rust `fn dedupe_ranges(ranges: &mut Vec<Range>)`, which changes its argument, and TypeScript `dedupedRanges(ranges)`, which returns a new array; not `process_ranges` or `processRanges`.
3. **Use one word per concept and one concept per word.** A synonym makes a reader look for a difference that isn't there, and a homonym hides one that is. Once a stored read position is a `cursor`, no module calls it an `offset` or a `checkpoint`, and `cursor` means nothing else. Rust `struct ReadCursor` and `fn cursor_for(stream)`; TypeScript `cursorFor(stream)`.
4. **Check a new domain word against `GLOSSARY.md`, and add a new concept's term there.** Two developers choose the same name for a concept only rarely, so the shared words have to be written down. A paying user is a `Customer` in Rust and `customer` in a TypeScript union, as the glossary defines it, never an `Account` in one module and a `Client` in another.
5. **Make a name promise no more and no less than the code does.** Callers decide from the name whether a call is cheap, safe to repeat and free of I/O. `connect`, `load` and `fetch` do I/O; `as_*` and accessors are cheap and can't fail; a function named for one step does only that step. Rust: `fn parse_header(line: &str) -> Result<Header, ParseHeaderError>` doesn't also write the row. TypeScript: `sortedRows(rows)` doesn't fetch.
6. **Name a function without side effects with a noun phrase, a function with effects with an imperative verb, and an expensive or remote read with a verb.** The form tells the reader whether calling it twice is safe and cheap. Predicates (Naming 9) and the conventional conversion and constructor prefixes (`parse`, `to_*`, `as_*`, `from_*`, `new`) keep their forms. Rust: `fn row_count(&self)`, `fn flush(&mut self)`, `async fn fetch_lag(&self)`. TypeScript: `relativeAge(ms)`, `invalidateLag()`, `computeRunway(usage)`.
7. **Make the return type agree with the name.** A plural returns a collection, `is_` and `has_` a bool, `to_`, `into_` and `parse` the converted value, and `set_` nothing. When they disagree, the reader's guess from the name is wrong. Rust: `fn parse_header(line: &str) -> Result<Header, ParseHeaderError>`, not `-> bool`. TypeScript: `sessions(): Session[]` and `isStale(row): boolean`, not a `sessions()` that returns a count.
8. **Keep a name, its type and its comment saying the same thing, and name a stateful type for every state it reaches.** A contradiction leaves the reader to guess which one is true. Rust: an `is_loading: bool` that stays `true` after an error is a status enum with one variant per state. TypeScript: an `isLoading` that stays `true` after an error is a `status` union.
9. **Name booleans and the functions that return them as questions (`is_`, `has_`, `can_`), and never negated.** `if !is_not_ready` makes the reader undo two negations. Rust `is_stale`, `has_rows`; TypeScript `isStale`, `hasRows`, `canRetry`; not `not_ready` or `noCache`.
10. **Put the unit in the name when the type doesn't carry it.** A bare `timeout` invites a seconds-for-milliseconds bug. Rust `timeout_ms: u64`, or a `Duration`, which carries it; TypeScript `timeoutMs`, `refetchIntervalMs`, `sizeBytes`.
11. **Name bounds with fixed pairs: `start` and `end` are half-open, `first` and `last` are inclusive, and the pairs never mix.** Readers infer from the words whether the end is included. Rust `start..end` and `first..=last`; TypeScript `{ start, end }` with `end` excluded.
12. **Put computed-value qualifiers (`max`, `min`, `count`, `total`, `sum`, `avg`) last, so a family sorts together, and keep one word order across it.** An adjective that says which value it is (`raw_rows`, `pending_ranges`) stays in front. Rust `lag_max`, `lag_min`, `row_count`; TypeScript `lagMax`, `rowCount`. Put a category word (`Error`, `Props`) where the language's standard library and generated code put it: Rust's like std's `ParseIntError` (`ParseHeaderError`, `InvalidSpecError`), TypeScript's like generated clients' `LagQueryError`; keep one order within each language.
13. **Don't repeat what the receiver, type or module already says.** The context is in front of the reader at every use. Rust `Session::id` and `store::Pool`, not `session_id` on `Session` or `store::StorePool`; TypeScript `session.id`, not `session.sessionId`. Review checks this: Clippy's `module_name_repetitions` also fires on names that are right, so the Rust template allows it.
14. **When the type is weak (`&str`, `u64`, `string`, `number`), let the parameter name carry the role.** The type doesn't say which string or which number. Rust `fn tag(rule_id: &str, line_number: u64)`; TypeScript `sessionUrl(sessionId: string)`.
15. **Let a name's length follow its scope, and use single letters only for short, conventional roles.** A closure variable lives for one line; a module item is read everywhere. Rust `rows.iter().map(|r| r.id)` and `pending_ranges` across a function; TypeScript `rows.map((r) => r.id)` and `pendingRanges`.
16. **Write whole words, and abbreviate only established terms** (`id`, `url`, `ms`), never a project-coined one. Whole words are read faster than abbreviations. Rust `normalizer`, not `nrm`; TypeScript `lagThreshold`, not `lagThld`.
17. **Use no numeric suffixes and no near-twin names in one scope.** `rows2` and `rowsNew` don't say how they differ from `rows`. Rust `raw_rows` and `deduped_rows`; TypeScript `rawRows` and `dedupedRows`.
18. **Treat an `and` in a name, or a name you can't make precise, as a design problem.** Split or redesign the function instead of naming it. Rust `parse_and_store` becomes `parse` and `store`; TypeScript `fetchAndRender` becomes a query and a component.
19. **Name an error variant for the step that failed, not the system it called.** The step tells the reader what went wrong and what to fix. Rust `Read { path, source }`, not `Io(io::Error)` (the Rust style file's `#[from]` rule); TypeScript `{ failed: "parse-event" }`, not `{ failed: "zod" }`.
20. **Name a test for the behaviour it protects.** A failing test's name is the first line of its bug report. Rust `fn skips_a_range_already_inserted()`, not `fn test_insert_2()`; TypeScript `it("shows the problem's title when the API returns a 404")`, not `it("works")`.
21. **Name a type for one value in the singular.** A plural type name reads as a collection at every use. Rust `enum Route`, not `enum Routes`, for one route; TypeScript `type Route = "home" | "settings"`, not `Routes`.

## Comments

Code documents itself through its names and types, and every non-obvious choice gets a comment. Comments are concise and precise: one line by default, longer for interface docs and for anything a reader can't follow without it.

1. **Give each public item that other modules use a doc comment** (`///` in Rust, `/** */` in TypeScript) that says what it is, what it guarantees and when it fails, unless its error type already says so. Editors show it on hover, so it is the item's contract. In Rust, `missing_docs` checks that it exists; in TypeScript, write no types in `@param` or `@returns`, since the signature has them.
2. **Write the doc summary in words other than the item's name.** `/// Returns the path.` on `fn path()` and `/** Gets the lag. */` on `getLag` say nothing; say what the path or lag is.
3. **State whichever of these the caller needs: units, inclusive or exclusive bounds, what `None`, `null` or empty means, ownership and cleanup, thread safety, and invariants.** Skip parameters whose meaning is obvious. Rust: `/// Rows in start..end; empty when the range was already inserted.` TypeScript: `/** Milliseconds since the newest row, or null when the stream has none. */`
4. **Keep how it works out of the doc comment.** A doc comment says what the caller needs; how it works goes in `//` comments in the body, next to the code that changes with it. Rust: `/// The rows in start..end.` above the function and `// The ranges are sorted, so binary search.` inside it; TypeScript the same split between `/** */` and `//`.
5. **Comment the why above the code it explains, in one line unless the reader needs more**: an optimisation, a workaround, an invariant, a unit, or a choice that would make a reviewer stop. Apart from the section comments of rule 6, code that reads clearly gets no comment. Rust: `// The database rejects RFC 3339 text for this parameter, so bind nanoseconds.` TypeScript: `// The client doesn't validate error bodies, so a problem's text is shown only once it parses.`
6. **Section a long block, even one of simple lines, with blank lines and a short comment over each section that names what it achieves, in words not already in the code.** Blank lines do more for readability than comments do. Test a section comment by deleting it and reading the section's first line: if that line says the same, the comment goes. In a parser, put one comment over each group of related `match` or `switch` arms, not one per arm. Extract a function to keep control flow flat, not to replace a section comment.

   ```rust
   fn publish(path: &Path) -> Result<Version, PublishError> {
       // Pick the next version nobody has published yet.
       let manifest = Manifest::read(path)?;
       let version = manifest.next_version()?;
       if registry::has(&manifest.name, version)? {
           return Err(PublishError::Exists(version));
       }

       // The registry rejects a partial upload, so a failure here leaves nothing to clean up.
       let archive = Archive::build(&manifest, version)?;
       registry::upload(&archive)?;
       Ok(version)
   }
   ```

   ```ts
   function lagSummary(rows: readonly LagRow[]): LagSummary {
     // A stream with no rows yet is idle, not lagging.
     const live = rows.filter((row) => row.newest !== null);
     const idleCount = rows.length - live.length;

     // The most-lagged stream sets the card's state.
     const worst = live.reduce<LagRow | null>((max, row) => (max === null || row.lagMs > max.lagMs ? row : max), null);
     return { worst, idleCount };
   }
   ```

7. **Keep comments true.** A change that makes a comment or doc wrong fixes or deletes it in the same commit, because a reader trusts a wrong comment over the code. Rust: the commit that makes `retry` try five times instead of three fixes its `/// Tries three times.`; TypeScript: the commit that stops returning `null` deletes the `/** … or null when … */` clause.
8. **Write about the code, never about the review or the agent.** `// per review feedback` and `// added for the agent` tell a later reader nothing about the code.
9. **Write no banner comments, commented-out code or change history**: git holds the history. Rust `// ===== helpers =====` and `// let old = parse_v1(line);`; TypeScript `// changed to fix the 404 loop`. (mechanical)

## Structure

1. **Keep functions flat.** Return early, make decisions in the caller and put the straight-line work in the helpers it calls, so each function reads top to bottom. Rust uses early returns, `let`-`else`, `?` and let chains: `let Some(cursor) = cursors.get(stream) else { return Ok(None); };`. TypeScript returns early and narrows with guards: `if (rows.length === 0) { return null; }` before the main path.
2. **Organise modules by domain, and keep each type next to the code that keeps its invariants.** A grab-bag module collects code nobody owns, so name no module or file `types`, `utils`, `helpers`, `common` or `models`. Rust `mod cursor`; TypeScript `relative-age.ts` and `session-timeline.tsx`. (mechanical)
3. **Write pure transforms as chains and side effects as loops.** A chain reads as data flow; keep its callbacks free of side effects, and write a loop when the body pushes, writes, logs, exits early or fills several outputs, or when the transform is measured-hot. Add a `pipe` helper only where the repo already has one. Rust: `filter`, `map` and `collect` for a transform, and a `for` loop when a chain needs nested closures, captured mutable state or early exits; `for_each` fits only as the last step of a longer chain whose body is one call. TypeScript: `map`, `filter` and `flatMap` for a transform and `for…of` for effects; iterations that must await one after another, such as a paginated read, carry a `no-await-in-loop` disable with the reason, and the rest run concurrently.
4. **Build a value, then stop changing it.** A binding that never changes after construction is one fewer thing to track. Rust: construct it with `collect`, a struct literal or a block expression, so the binding that outlives construction is not `mut`. TypeScript: construct it with a literal, a chain or `Object.fromEntries`, so the binding is a `const` that is never mutated. Mutating a local value while it is being built is fine, as long as nothing else holds it yet.
5. **Declare each fact once.** When two declarations must agree, derive one from the other instead of keeping them in step by hand. Rust: derive a table name from its enum variant rather than asserting that they match; when each copy of a repeated call names the same thing twice, as in `record(&[File], insert(table(File), rows))`, change the signature or add a helper so each call names it once. TypeScript: derive a route's query key from its search schema, and check a lookup table against its union with `satisfies`.
6. **Make each new module, wrapper, layer or option hide more complexity than it adds.** A file that only forwards calls is a cost every reader pays: inline it. Rust: a `mod client` whose functions only call `reqwest` with the same arguments goes. TypeScript: a `api.ts` that re-wraps each generated function one to one goes.
7. **Make every advanced construct pay for itself.** A trait, generic, brand, marker or lifetime parameter, macro, smart pointer, or conditional or mapped type stays only where it removes a runtime check, a cast, a clone, a duplicated declaration or a measured cost, or turns a likely mistake into a compile error; one whose payoff nobody can name becomes the plain form. Rust: a `Store<B: Backend>` with one backend becomes `Store`. TypeScript: a `DeepPartial<Config>` used once becomes the interface it produces.

## Exceptions

1. **Fix the code, not the check.** A failing lint, compiler flag or hook is fixed in the code, with every rule and level kept as it is. A green run bought with a loosened rule hides the next real failure. Rust: restructure the `unwrap` away instead of adding `#[allow(clippy::unwrap_used)]`; TypeScript: narrow the value instead of adding `as`.
2. **Keep each exception to the smallest scope, and name the rule and the reason.** One line or one item, never a file or a crate, so the exception leaves with the code that needed it. Rust: `#[expect(clippy::print_stdout, reason = "the command's output")]` on the one function; TypeScript: `// oxlint-disable-next-line <rule> -- <why>`.
3. **Change lint or compiler settings as a task of its own.** Inside an unrelated change, propose the setting and its reason in the handoff instead, so a reviewer weighs it on its own. Rust: propose a new `[workspace.lints]` entry; TypeScript: propose a new Oxlint rule.
4. **Where the config lacks a rule the templates have, write the code as if it were on, and propose it; where the config contradicts a rule here, the config wins and the handoff names the conflict.** The repo's config is what CI runs. Rust: write no `unwrap` even where `unwrap_used` is off; TypeScript: write no `!` even where `no-non-null-assertion` is off.
5. **Turn a rule off repo-wide only when it fires on code that follows these rules at many sites, with a comment saying why.** "Too many warnings to fix now" is not a reason: fix them, or leave the rule on and propose the cleanup. Rust: `use_self = "allow" # naming the type and writing Self read equally well`; TypeScript: `"no-underscore-dangle": "off" // flags _tag reads`.
6. **Give every escape hatch in a diff its reason where the language puts it.** An escape hatch without a reason is a finding, because the next reader can't tell a proven case from a shortcut. Rust: the `reason =` of an `#[expect]`, a `// SAFETY:` comment, an `.expect("why")` message; TypeScript: the `-- why` of a disable, a comment above an `as`.

## Types

1. **Model a closed set of cases as a tagged union whose variants carry their own data.** A string tag, or a record of optional fields that encode a state, is a union written as data, and the compiler can check neither. Rust: `enum Payment { Card(CardToken), BankTransfer(Iban) }`, not `struct Payment { kind: String, card: Option<CardToken>, iban: Option<Iban> }`. TypeScript: `{ status: "loaded"; user: User } | { status: "failed"; error: Error }`, not `{ loading: boolean; data?: User; error?: Error }`.
2. **Make illegal states unrepresentable.** When a comment would be needed to say which field combinations are valid, the type is too loose; two flags that must agree become one status. Rust: `enum Upload { Pending, Done(Url) }`, not `pending: bool, url: Option<Url>`. TypeScript: `status: "idle" | "saving" | "saved"`, not `isSaving` and `isSaved`.
3. **Match a closed set exhaustively, so a new case fails the build.** A catch-all arm hides the next variant someone adds. Rust: list every variant of your own enum, no `_ =>`. TypeScript: end a `switch` over a union with a `never` arm that throws.
4. **Give each domain identifier or unit that travels beside others of the same representation its own type, built by one validating constructor.** The compiler then stops an order id from passing as a user id. Rust: `struct OrderId(Uuid)` behind `OrderId::parse`. TypeScript: a branded `OrderId` whose only `as` is in `parseOrderId`.
5. **Stop at the simplest total type.** Strengthen a type only where the loose one forces a cast, a check or a can't-happen failure; a stronger type everywhere else costs readers and buys nothing. Rust: keep `Vec<T>` until code indexes `[0]` and needs a non-empty type. TypeScript: keep `T[]` until a `!` on `items[0]` asks for `[T, ...T[]]`.
6. **Make an out-of-order call a compile error with a type per state.** A runtime flag such as `dry_run` lets a caller skip a step. Rust: `plan()` returns a `MigrationPlan` whose `apply(self)` does the writing, instead of `migrate(.., dry_run: bool)`. TypeScript: `issue(invoice: ValidatedInvoice)`, where only `validation()` makes a `ValidatedInvoice`.

## Errors

1. **Split failures by kind.** Bugs and broken invariants fail loudly; expected outcomes the caller branches on (not found, conflict, validation failed) are part of the return type, named for the domain, each variant carrying the data the caller needs to respond. A caller can't branch on a message string. Rust: `enum ReserveError { SoldOut, OverLimit { limit: u32 } }`. TypeScript: `{ outcome: "over-limit"; limit: number }`.
2. **Never swallow an error.** Catch only to recover, to translate at a boundary or to clean up; a success-shaped default on required data hides the failure from everyone downstream. Rust: no `.unwrap_or_default()` on a row that must exist, no `let _ =` on a `Result`. TypeScript: no `catch { return [] }`, and no `?? []` on data the caller requires.
3. **Log an error where you handle it, or return it, never both.** Doing both reports one failure twice, at two layers. Rust: return the `Err` and let the caller decide. TypeScript: rethrow with `cause`, or handle and log, not both.
4. **Recover at the smallest unit that still gives a correct result.** Keep the raw input, count what was skipped where the user sees it (a report, a health counter), and go on; propagate everything else. Rust: skip one bad record, increment `skipped_count`, keep its raw line. TypeScript: render the card that failed as an error state and the rest of the page as usual.
5. **Carry the cause as a typed value, never a string, with identifiers in fields.** Each message describes only its own layer, as a lowercase fragment with no final period naming the action and the operand, so chain printers join them cleanly. Rust: `#[error("cannot read config {path}")] Read { path: PathBuf, #[source] source: io::Error }`. TypeScript: `new Error("cannot parse event 42", { cause: error })`.
6. **Never crash on input.** Files, network payloads, config, requests, arguments and environment variables can hold anything; a crash on them is a denial of service. Rust: return an error instead of `unwrap` or indexing; TypeScript: parse instead of asserting a shape.
7. **Surface each error where the user is looking.** A problem the user must see reaches them as data (a returned error, a skipped count, a status branch), never only as a log line. Rust: the import report lists the skipped files. TypeScript: a failed query renders its own error state in the panel that asked for it.

## Boundaries

1. **Treat data from outside as untrusted until parsed, once, where it enters, into types that can't hold invalid values.** Inside, trust the type and don't re-check it, because a second check drifts from the first. Rust: `let config: Config = toml::from_str(&text)?;` at load, then pass `&Config`. TypeScript: `const event = LiveEvent.parse(JSON.parse(text))` at the socket, then pass `event`.
2. **Return the parsed value from a validator.** A validator that returns a boolean is a parser that throws its result away, and its caller re-reads the raw input. Rust: `fn parse_port(s: &str) -> Result<Port, ParsePortError>`, not `fn is_valid_port(s: &str) -> bool`. TypeScript: `parsePort(s): Port`, not `isValidPort(s): boolean` followed by `Number(s)`.
3. **Parse configuration once at startup into a typed object.** Required settings fail with their name, defaults apply only when a value is unset, a malformed value is reported, and a missing security setting never falls back to a permissive default (no limit means "unlimited" by accident). Rust: a `Config` built in `main` from arguments and environment. TypeScript: a `config.ts` that parses `process.env` into a typed object at startup.
4. **Be strict with files people write and lenient with records you keep raw.** A typo in a config file should fail loudly; a new upstream field should not stop ingestion. Rust: `#[serde(deny_unknown_fields)]` on config types, not on event types. TypeScript: a strict object schema for settings, a passthrough schema for upstream events.
5. **Put a precondition in the parameter type and move the check to the caller.** A doc comment that says a parameter MUST hold some property names a missing type. Rust: take `&Order`, not `Option<&Order>` with an early return. TypeScript: take `Extract<State, { status: "loaded" }>`, not the whole union.

## Concurrency and cancellation

1. **Give every outbound call a timeout or the caller's cancellation.** A call without one can hang its caller forever. Rust: `tokio::time::timeout(deadline, call)` or the client's request timeout. TypeScript: pass the caller's `AbortSignal`, joined with `AbortSignal.timeout(ms)`.
2. **Make every long-running task and subscription stoppable, and clean it up.** A stopped task leaves its saved progress (a cursor, an offset) at the last acknowledged write, so a restart neither loses nor repeats work. Rust: loops listen to a `CancellationToken`. TypeScript: an Effect that opens a socket returns the function that closes it.
3. **Bound every queue, channel, cache and pool, and decide whether a full one waits or drops and counts.** An unbounded queue turns a slow consumer into memory growth. Rust: `mpsc::channel(64)`, not `unbounded_channel()`. TypeScript: a cache with a size limit, not a module-level `Map` that only grows.
4. **Run independent work concurrently, with an explicit limit on parallelism.** Serial independent calls waste time, and unlimited ones exhaust a pool. Rust: a `Semaphore` permit per task, or `buffer_unordered(8)`. TypeScript: `Promise.all` over a chunk of eight.
5. **Make a deliberate fire-and-forget explicit, and say where its errors go.** An unawaited task's failure is otherwise lost without a trace. Rust: a spawned task's handle is tracked and its result read. TypeScript: `void prefetch().catch(report) // a failure shows in the page's own query`.
6. **Keep blocking and CPU-heavy work off the event loop or async runtime.** One blocked thread stalls every task that shares it. Rust: the runtime's async I/O, and a bounded thread pool for CPU work. TypeScript: a Web Worker for parsing that blocks the main thread in a profile.
7. **Give mutable shared state one owner that others message.** A lock shared by many tasks becomes the place they all wait. Rust: one task owns the map and others send it requests over a channel. TypeScript: one store module owns the state and exposes actions.

## Retries

1. **Retry only idempotent operations, and make a retried write idempotent with a key derived from its content.** A retried non-idempotent write runs twice. Rust: an insert carries a dedup token hashed from the batch. TypeScript: a POST carries an idempotency key derived from the form's content.
2. **Bound retries, back off with jitter, and repeat only failures that can pass.** Timeouts, refused connections, 429 and 503 can pass on a later try; a 400 or 413 fails the same way every time. Rust: `backon` with a `when` predicate. TypeScript: the query client's single `retry` function that checks the status.
3. **Keep one retry layer.** A hand-written loop over a client that already retries multiplies the attempts and ignores its cancellation. Rust: no loop around a client configured with retries. TypeScript: no retry loop around a query the client retries.
4. **Time out each attempt and the whole operation.** A per-attempt timeout alone lets retries run forever; a total timeout alone lets one attempt use it all. Rust: `timeout(total, retry(timeout(per_try, call)))`. TypeScript: `AbortSignal.timeout(perTry)` per attempt inside an `AbortSignal.timeout(total)`.

## Observability

1. **Let libraries emit structured events, and let only the program's entry point choose where they go.** A library that installs its own sink takes the choice from its caller. Rust: libraries use `tracing` macros; only the binary installs a subscriber. TypeScript: modules call the repo's logger; only the entry point configures transports.
2. **Give events and spans static names, put identifiers and data in fields, and keep the message a fixed phrase.** Fields can be queried and grouped; text in a message can't. Rust: `debug!(queue = %name, job_count = n, "batch claimed")`. TypeScript: `logger.info({ queue, jobCount }, "batch claimed")`.
3. **Put spans at phase and request boundaries at the default level, and detail inside them at debug.** The usual production filter drops debug spans, so an error inside a debug-level phase would print without the phase's fields. Rust: `#[instrument(skip_all, fields(..))]` at `info` on a request handler. TypeScript: one span per request at the default level.
4. **Never record whole arguments or bodies, and keep secrets out of every log, span and error message.** A recorded argument can hold a whole request body or a token. Rust: `skip_all` and named fields. TypeScript: log the ids, never the request object.
5. **Keep disabled events free.** An event's arguments are evaluated even when its level is off, unless the macro defers them. Rust: no `format!` or `collect()` in event arguments. TypeScript: no `JSON.stringify` in a debug call's arguments.
6. **Log through the repo's structured logger, with the ids needed to trace the event.** A stray print can't be filtered, sampled or traced. Rust: `tracing`, not `println!`. TypeScript: the logger, not `console.log`.

## Security

1. **Never index a plain object or an unprotected hash map with a key an attacker chooses.** A key such as `__proto__` changes every object's prototype, and chosen keys can flood a fast hash map. Rust: std's `HashMap` (SipHash) for keys from requests. TypeScript: a `Map` for user-keyed data.
2. **Compare secrets in constant time over fixed-length digests.** An early-exit comparison leaks how much of a guess was right, and a length mismatch can leak or throw. Rust: compare HMACs with `subtle::ConstantTimeEq`. TypeScript: `crypto.timingSafeEqual` on HMACs of both values.
3. **Take security randomness from the platform's cryptographic generator.** A general-purpose generator is predictable. Rust: `rand::rngs::OsRng` or `getrandom`. TypeScript: `crypto.randomUUID()` or `crypto.getRandomValues()`, never `Math.random`.
4. **Bind every value in a query, and never format one into the query text.** Formatting invites injection and breaks on quoting. Rust: `sqlx::query(…).bind(id)`. TypeScript: a parameterised query, never a template string.
5. **Keep patterns that run on input linear-time, or cap the input first.** Nested quantifiers can backtrack exponentially on a crafted string and freeze the process. Rust: the `regex` crate, which runs in linear time. TypeScript: no `(a+)+` on input, and a length cap before matching.
6. **Around a security decision, derive the type from a parse, never an assertion, and await every check before acting on it.** An assertion and an unawaited check both compile and both let the request through. Rust: `let claims = verify(token)?;` before the handler body. TypeScript: `await authorize(user)` before the write, with no `as Claims`.
7. **Carry integer ids beyond a format's exact range as strings.** JSON numbers above 2^53 lose precision silently. Rust: serialise a `u64` id as a string where a JavaScript client reads it. TypeScript: keep the id a `string` or a `BigInt`.

## Dependencies

1. **Add a library only when it earns its place.** It removes code you would otherwise maintain, enables something you can't reasonably write, gives a standard interface other tools speak, or brings a measured speed-up; another way to do what the standard library or a present dependency does is a cost. Rust: `backon` instead of a hand-written backoff loop. TypeScript: a schema library instead of hand-written guards for every payload.
2. **Before adding one, check the standard library, then what's already locked, then the candidate's maintenance, advisories, licence and cost.** A dependency the task didn't call for is the owner's decision: propose it in the handoff with the test it passes. Rust: `cargo tree` and `cargo deny check`. TypeScript: the lockfile, then the package's release history and install size.
3. **Declare each dependency version once, with only the features that are used.** One version per dependency keeps the lockfile small, and unused features cost build time. Rust: `[workspace.dependencies]` with `default-features = false` where the defaults pull in something unused. TypeScript: a workspace catalog entry.
4. **Use a library through its public entry points.** Internal paths change without notice, and a root barrel can pull the whole library into the bundle. Rust: `use crate_name::Item`, the paths its docs show. TypeScript: the package's `exports` entries and per-component entry points.
5. **Pin every tool exactly in the repo's tool config.** A floating pin gives two machines different tools and different results. Rust: `rust-toolchain.toml` and exact versions in the tool manager. TypeScript: `packageManager` and exact versions in the tool manager.

## API design

1. **Replace a boolean or optional argument that callers pass as a literal with an enum or an options object, or split the function.** `export(&orders, true, None)` tells the reader nothing. Rust: `export(&orders, Format::Csv)`. TypeScript: `relativeAge(ms, { style: "short" })`. (mechanical)
2. **Return a named record when a result has more than one non-trivial part.** A tuple of collections is a struct without field names. Rust: `struct Split { kept: Vec<Row>, dropped: Vec<Row> }`. TypeScript: `interface Split { kept: Row[]; dropped: Row[] }`. (mechanical)
3. **Change generated code at its source, never by hand or behind a forwarding wrapper.** A hand edit is lost at the next regeneration, and a wrapper doubles the surface. Rust: change the schema the code is generated from. TypeScript: change the API or the generator's config, then regenerate.
4. **Keep the public surface minimal, with one path to each public item.** Every public item is a contract other code may lean on. Rust: `pub(crate)` unless another crate uses it, and no glob re-exports. TypeScript: export only what other modules import, and no barrel files.
5. **Put a function on the type it builds or reads, and name a type for the data it holds, never a role.** A role name such as `Manager` or `Service` hides what the type holds. Rust: `File::open` and `Pool`, not `open_file` and `ConnectionManager`. TypeScript: `invoice.total()` where a class is used, and `InvoicePool`, not `InvoiceManager`.
6. **Push decisions up and loops down, and give a hot operation a batch signature.** Setup then runs once instead of once per item. Rust: `price_all(&orders)`, not `price(order)` in a loop. TypeScript: `priceAll(orders)`.
7. **Use one error channel per function: return the results or push them, never both.** Two channels let a caller read one and miss the other. Rust: return `Result<Report, E>`, not `Result<(), E>` plus a `&mut Vec<Warning>`. TypeScript: return the outcome union, not a value plus a mutated `warnings` array.
8. **Keep the core pure and the effects at the edges.** The clock, randomness and environment are read at the entry point and passed in, so tests and reruns control them. Rust: `fn is_expired(&self, now: DateTime<Utc>) -> bool`. TypeScript: `relativeAge(updatedAt, now)`.
9. **Make output deterministic.** Sort by a total, content-derived key before results reach output or a snapshot, order every query whose rows reach output on a unique key, and derive an id from content when a rerun must reproduce it. Task timing and query plans vary between runs. Rust: `rows.sort_by_key(|r| (r.day, r.id))`. TypeScript: `sorted.sort((a, b) => a.id.localeCompare(b.id))` after the main key.
10. **Define an interface or trait only for an open set with two or more real implementations.** One implementation behind an interface is indirection with nothing to choose; for one varying step, take a function. Rust: `impl Fn(&Row) -> bool`, not a one-method trait. TypeScript: a `(row: Row) => boolean` parameter, not an interface with one method.
11. **Write plain code before macros or type-level metaprogramming.** Generated code is harder to read, debug and change. Rust: a `macro_rules!` only when one block repeats five or more times. TypeScript: a conditional type only where it removes a cast or a duplicated declaration.

## Performance

1. **Do costly setup once per run, and write in batches.** Opening a connection, compiling a pattern or reading a file once per item multiplies the cost by the item count. Rust: compile the regex once in a `LazyLock`; insert thousands of rows per call. TypeScript: create each `Intl` formatter once at module level; send one request for a page of rows.
2. **Reach for a performance pattern only when a profile shows the cost it removes.** A pattern without a measured cost adds complexity for nothing. Rust: `Cow` or `SmallVec` after the profile shows the allocation. TypeScript: `useMemo` after a profile shows the render cost.
