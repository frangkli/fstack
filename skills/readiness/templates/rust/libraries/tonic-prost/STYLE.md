### tonic and prost

1. **Set `max_decoding_message_size` on each tonic service that receives large messages.** tonic caps a decoded message at 4 MiB by default. gzip needs both the `gzip` feature and `.accept_compressed(CompressionEncoding::Gzip)`; with only the feature, a compressed request gets `UNIMPLEMENTED`.
2. **Give a tonic client its deadline with `Endpoint::timeout`.** Retry `Code::Unavailable` with backoff, and never `ResourceExhausted`, which means the message is too large, like HTTP 413.
3. **Check a message against a size cap with prost's `encoded_len` before sending it.** Build `opentelemetry-proto` with `default-features = false`: its `full` default also turns on zpages and internal logs.
