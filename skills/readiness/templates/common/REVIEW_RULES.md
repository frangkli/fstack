# Review rules

Flag only with a concrete case: this input or situation leads to this wrong result. Leave what the Enforced table covers to its checks, and skip everything under Known non-issues.

1. Test integrity: a diff that changes code and tests together keeps assertions, expected values and test inputs as they were, unless it says why.
2. Tests that would still pass if the subject returned `undefined` or a constant (loose matchers, asserting only that a mock was called).
3. Broad `catch`, swallowed errors, success-shaped fallbacks, or silent defaults on required data.
4. A new entry point (HTTP handler, CLI, queue consumer, env or config read) without parsing and validation; or re-validation deep inside code a boundary already validated.
5. An abstraction with one caller or one implementation, a pass-through layer, or an option nobody sets.
6. Compatibility shims, deprecated aliases or dual paths kept only for internal callers.
7. Near-duplicate logic that must change together. Similar-looking code that changes for different reasons is fine.
8. Unrelated refactors or formatting mixed into a behaviour change.

For a repo that runs services:

9. An outbound call without a timeout or cancellation; retries without a bound and backoff, or retries of non-idempotent work.
10. A retried, queued or scheduled operation that isn't idempotent.
11. An unbounded queue, cache, pool, result set or in-memory list.
12. A schema, API or event change that breaks old data, old clients or in-flight messages.

## Enforced

| Rule | Enforced by |
|---|---|
| <rule> | <the type, lint rule, test or CI job, and the command in AGENTS.md that runs it> |

## Known non-issues

### <short pattern name>

- Skip when: <conditions that must all hold>
- Do not skip when: <risk boundaries>
- Example signal: <phrases or code shapes that identify it>
- Why it is correct: <the line, guarantee or decision that makes it intended>
- Pinned by: <the test that fails if this stops being true>
- Source: <PR or comment URL>
