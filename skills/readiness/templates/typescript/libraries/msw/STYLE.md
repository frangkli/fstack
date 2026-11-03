### MSW

1. **Fake the network with MSW, never `fetch` or the API client.** Each test file calls `server.listen({ onUnhandledFrame: "error" })` before its tests, `server.resetHandlers()` after each one and `server.close()` at the end. Each test installs the responses it needs with `server.use(…)`: a generated mock handler, or `http.get(…)` for an error status the generated handlers don't mock. Assert on what the UI shows, not on which requests were made.
2. **MSW 3 doesn't patch timers,** so a test that fakes `setTimeout` advances it for delayed responses.
