### sqlx

1. **One crate owns the database drivers.** Row structs that derive the driver's traits live there, converted from the domain types with `From`, so domain crates don't compile the driver. The orphan rule also stops that crate from implementing the driver's trait on another crate's types.
2. **Choose compile-time checked or runtime queries.** sqlx's `query!` macros check SQL against a live database or a committed `.sqlx/` cache, at the cost of a database or a JSON file per query, a `cargo sqlx prepare --check` step in CI, and `DATABASE_URL` or `SQLX_OFFLINE` in every build: choose them when many queries have no test of their own. Choose `sqlx::query_as::<_, T>()` with `#[derive(FromRow)]` when every query runs against a real database in an integration test, which is the check the macros add. sqlx's `macros` feature is still needed for `migrate!` and `#[sqlx::test]`. Bind every value.

   ```rust
   let orders = sqlx::query_as::<_, OrderRow>("SELECT id, total_cents FROM orders WHERE customer_id = $1 ORDER BY id")
       .bind(customer_id)
       .fetch_all(&pool)
       .await?;
   ```
