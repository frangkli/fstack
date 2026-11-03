### clickhouse

1. **Bind parameters with `Query::param` and `{name:Type}` placeholders,** never formatted into SQL. Bind an instant as integer nanoseconds, `fromUnixTimestamp64Nano({start_ns:Int64}, 'UTC')`: ClickHouse rejects chrono's RFC 3339 text for a `DateTime64` parameter. Write a `DateTime64(9)` field with `#[serde(with = "clickhouse::serde::chrono::datetime64::nanos")]`.
2. **When a retried batch must not count twice, write each planned range as one `Insert` with `.with_setting("insert_deduplication_token", ..)` derived from the range.** Leave the crate's `inserter` feature off then: it ends a batch on a timer, so a retry can cut the range differently and get a different token.
3. **Call `clear_cached_metadata()` after a migration:** the client validates rows against each table's schema and caches it.
4. **Turn the client's default compression (`lz4`) off when the database runs on the same host,** where it costs CPU and saves no transfer time; keep it for a remote server.
5. **Row structs live in the crate that owns the driver** (the sqlx section's rule 1), one per table.
