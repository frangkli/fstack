### serde

1. **Derive `Serialize` and `Deserialize`** instead of writing parsers for JSON, TOML or YAML: serde is the standard interface for serialisation.
2. **Put `deny_unknown_fields` and `rename_all` on every config and spec type,** so a misspelt key fails loudly. Never combine `deny_unknown_fields` with `flatten`: serde doesn't support the pair. Use `#[serde(default)]` on optional config keys.
3. **Parse records you keep raw anyway leniently:** leave `deny_unknown_fields` off types that read upstream data (events, logs, third-party payloads), so a new upstream field doesn't stop ingestion.
4. **Choose an enum's tagging by its format and readers.** Externally tagged (serde's default) works in every format. Internally tagged, `#[serde(tag = "kind")]` with the repo's discriminant name, gives the flat JSON objects other languages expect, but needs a self-describing format and allows no tuple variants. Never use `untagged`: its only error is "data did not match any variant of untagged enum".
5. **Parse JSON into typed structs with serde_json;** reach for `serde_json::Value` only where the shape is open, such as an attributes map. A typed parse skips the fields you don't read and is about twice as fast as building a `Value`. Switch to simd-json or sonic-rs only after measuring on your own data: on typed structs serde_json is often as fast.
6. **Use toml for config files a person edits.**
7. **Borrow strings in a zero-copy struct as `Cow<'a, str>` with `#[serde(borrow)]`:** a `&'a str` field fails to deserialise when the JSON string has an escape. The struct is a short-lived view: copy out what outlives the buffer.

   ```rust
   #[derive(Deserialize)]
   struct LogLine<'a> {
       level: Level,
       #[serde(borrow)]
       message: Cow<'a, str>,
   }
   ```
