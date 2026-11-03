### Vitest

1. **Fake only the clock the test needs, and restore it after each test:** `vi.useFakeTimers({ toFake: ["Date"] })`. Faking `setTimeout` also stops delayed network fakes, so a test that fakes it advances it.
2. **Compare values, not whole-DOM snapshots.**
3. **Inject what the test environment lacks through a capability parameter,** such as a fake stream opener for code that opens an `EventSource`.
4. **Test a type contract in `<name>.test-d.ts` with `expectTypeOf`,** and assert that something must not compile with `// @ts-expect-error -- <why>`.
5. **Run the tests under a pinned locale** (`LC_ALL=en_US.UTF-8 vitest run`) when assertions read text formatted with the default locale.
6. **A shared component library adds a Vitest browser project** (`@vitest/browser-playwright`, or `vite-plus/test/browser-playwright` under Vite+) with one Chromium instance and `headless: true`, which runs axe-core over every component; CI runs it on Linux. App pages get their real-browser axe scan from the `verify` skill instead.
