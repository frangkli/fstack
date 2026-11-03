### utoipa

1. **Set the OpenAPI document's version explicitly,** to the version the client generators read.
2. **Put `#[schema(required = true)]` on an `Option` field that serde always sends,** so the field is required and nullable rather than optional in the document.
3. **Give every response a description,** or the document fails validation.
4. **Keep `u64` wire integers within 2^53, or annotate them:** OpenAPI types a `u64` as `int64`, which some generators map to `bigint`.
