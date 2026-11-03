### axum and tower

1. **Raise axum's request body cap per route with `DefaultBodyLimit::max(n)`.** axum caps a body at 2 MiB by default, and `DefaultBodyLimit` is the one mechanism that lifts that cap; it applies to the decompressed body, so size it for that.
2. **Take standard middleware from tower-http:** `TraceLayer`, `TimeoutLayer::with_status_code` (`new` is deprecated) and request decompression, which answers an unsupported `Content-Encoding` with 415.
3. **Serve server-sent events from a broadcast channel through tokio-stream's `BroadcastStream`,** which turns the receiver into the `Stream` axum's `Sse` takes.
