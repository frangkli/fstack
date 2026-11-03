### happy-dom

1. **Run DOM tests in happy-dom and pure logic in the `node` environment** (`// @vitest-environment node` at the top of the file). Neither has `EventSource`, so a test of code that opens one passes a fake opener.
