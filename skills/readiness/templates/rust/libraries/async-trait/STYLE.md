### async-trait

1. **Use a native `async fn` in a trait that is never a trait object.** In a public trait, the `async_fn_in_trait` lint warns because callers can't require the future to be `Send`: declare the method as `fn run(&self) -> impl Future<Output = Report> + Send` (impls may still write `async fn`).
2. **Use `#[async_trait]` when the trait is used as `dyn`:** an `async fn` in a trait can't be called through `dyn`. It boxes each future, one allocation per call, which is fine per job or per connection, not per item. Put the attribute on the trait and on each impl. When leaf crates may depend only on a core crate, re-export the macro from it (`pub use async_trait::async_trait;`). Don't hand-write `Pin<Box<dyn Future<..> + Send + '_>>`: it is the code the macro generates.
