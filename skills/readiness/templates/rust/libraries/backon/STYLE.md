### backon

1. **Retry with backon instead of a hand-written loop:** exponential backoff with jitter, a cap on attempts, and a `when` that retries only errors that can pass (a timeout, a refused connection, HTTP 429 or 503 and their gRPC equivalents), never a 400 or 413, which fail again the same way. Retry only idempotent operations (common Retries). Skip the `backoff` crate: it is unmaintained (RUSTSEC-2025-0012).

   ```rust
   let status = (|| fetch_status(&client, &url))
       .retry(ExponentialBuilder::default().with_jitter())
       .when(FetchError::is_transient)
       .await?;
   ```
