### Testing Library

1. **Test what a user sees.** Find elements by role and accessible name first, then by label or text, and by test id last, so a control with no accessible name fails a test; use `findBy…` to wait for something to appear. Assert on rendered output, never on a component's state or which Hooks it called, and render the real component: a test that mocks React's Hooks checks call order, not what a user sees.
2. **With Vitest's globals off, call `cleanup()` after each test.** Testing Library cleans up by itself only when it finds a global `afterEach`.
