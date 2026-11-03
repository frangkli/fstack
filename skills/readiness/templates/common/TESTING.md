# Testing

When each kind of test earns its place and what a good one looks like. Each language's style file names the tools that run them. `REVIEW_RULES.md` holds the bug rules a review checks tests against.

## What every test does

1. **Fail when the code is wrong.** A test that would still pass if the function under test returned a constant or an empty list protects nothing. Assert on outcomes: the value returned, the output rendered, the row written. Never assert on internals, call counts or which mocks were called.
2. **Name the behaviour it protects.** A failing test's name is the first line of its bug report: `skips_a_range_already_inserted`, not `test_insert_2`.
3. **Keep its assertions when the code changes.** A change to code and its tests together keeps the assertions, expected values and test inputs as they were, unless the change says why the behaviour changed. Loosening a test to make it pass is never the fix.
4. **Run the same way every time.** Seed every random generator, sort output by a content key before comparing it, pin the locale when an assertion reads formatted text, and compare values rather than whole snapshots of output that varies between runs.

## Where tests live

- **Unit tests** sit beside the code they test (an inline test module, or `<name>.test.ts` next to `<name>.ts`), so a reader finds them from the code.
- **Integration tests** sit in the package's test folder and drive the package through its public interface.
- **Fixtures** are synthetic and live beside the tests that read them, so the repo never holds real user data.
- **Helpers** are defined once, in a test-only module or feature, never once per test file.

## Kinds of test

### Unit tests

Earn their place for logic with branches: a parser, a state transition, a calculation, a mapping. A good one calls a pure function with plain values and checks the returned value. Logic that reads the clock, the network or storage takes those as parameters, so the test passes plain values instead of mocks.

### Integration tests against real services

Earn their place where the behaviour lives in the service: a query's results, a migration, a transaction's isolation, a client's wire format. A mock of the service tests the mock.

- Mark a test that needs an outside service (a database, a container) and run those tests in their own command, so the default test run is fast and passes with nothing running.
- Give each worktree its own test database, named from a validated slug that fits the database's name limit (63 bytes in Postgres, which truncates longer names silently), so parallel worktrees never share or truncate a database.
- Run the queries a release runs. A query checked only by a macro or a type, never executed, is untested.

### Snapshot tests

Earn their place for large or structured output: rendered text, a JSON document, a report, a diagnostic. For a small exact value, an equality assertion reads more plainly.

- Review a snapshot change as a behaviour change: read the diff, then accept it.
- Give each snapshot a stable name. Snapshots numbered in a loop shift when a case is added; name them, or generate one per fixture file.
- Normalise the parts that vary between runs (timestamps, paths, ids) with the tool's filters or redactions.
- Make CI fail on an orphaned snapshot (one no test references) and on an unwritten one (a new snapshot nobody accepted).
- Keep snapshots out of tests that CI skips, such as tests that need services: their snapshots look orphaned to the check.

### Property tests

Earn their place where a rule holds for every input:

- A hand-written parser of outside input never panics or throws: arbitrary bytes or strings in, a value or a typed error out. A per-record mapper of outside input is a hand-written parser too. Parsers derived from a schema or an argument-parser library are exempt.
- A round trip holds: `decode(encode(x)) == x`.
- An invariant holds for any input: sorted output stays sorted, a merge never loses a key.

A good property test states the property in its name, lets the tool shrink a failure to the smallest input, and keeps the failing seed as a regression case.

### Fuzzing

Earns its place for parsers of untrusted input, where coverage-guided search finds inputs a property test's random generator rarely reaches, such as an exponential parse blowup.

- Keep the fuzz harness outside the main build, so its toolchain and dependencies don't reach the product, and lint it in the check command, so its targets don't break unseen.
- Run it on a schedule, or in a CI job filtered to the paths of the fuzzed code, never on every pull request: a useful run takes minutes.
- Fuzz the dependency versions you ship: the CI job takes the main lockfile.
- Fail the job on a crash artifact, and keep each crashing input as a regression test.

### Mutation testing

Earns its place as the check a coverage figure can't make: it changes the code (a function returns a constant, a condition flips) and reports each change no test catches.

- Run it on the change's diff, once per change, before the final review round, not on every push and not in CI: a run takes minutes.
- Run one at a time per machine: a run copies the tree and builds it, and parallel runs starve each other.
- Treat each surviving mutant as a missing assertion, or as dead code to delete.

### Compile-time contract tests

Earn their place for public generic APIs and utility types, where the contract is what compiles. A good one asserts what must compile and what must not, and checks the inference callers rely on, not only explicit type arguments.

## Fixtures and fakes

- **Fixtures satisfy the full production type**, built by typed builders, factory helpers or literal files, never by text replacement on YAML or JSON, which breaks silently when the text shifts. Production types never loosen for test setup: the live call sites define the contract.
- **Fake only what the test environment lacks or what isn't deterministic**: the network at its edge, the clock only as far as the test needs. Pass the fake in as a capability parameter rather than mocking a module, so the code under test stays a plain function of its inputs.
- **Generated fakes can break schema constraints.** Pass explicit values for constrained fields (enums, formats) instead of trusting a generator.

## Continuous integration

- Run every test without stopping at the first failure, so one run reports every failure.
- Write machine-readable results (JUnit) and upload them even when the job fails.
- Run the same commands CI runs locally before pushing; CI holds no test logic of its own.
