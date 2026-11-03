### Orval

For a client generated from an OpenAPI document: a fetch client, TanStack Query hooks and options, Zod schemas and MSW mocks.

1. **Change the client by changing the API or `orval.config.ts`, then regenerate.** Generated files are never edited, and nothing the generator produces is wrapped in a second layer that only forwards calls.
2. **Pick a generator whose output passes the same strict tsconfig as hand-written code,** `exactOptionalPropertyTypes` included, and keep it type-checked under that config.
3. **API shapes and value sets come from the generated client and its `zod.enum`s; never redeclare one by hand.**
4. **Call the generated hook (`useOrders`) or spread the generated options (`getOrdersQueryOptions()`), and pass per-use settings through `{ query: { … } }`.** Build no key by hand for a generated endpoint; read and invalidate the cache with `opts.queryKey`, which carries the data type.
5. **Annotate values from the client with the `XOutput` type,** the shape after the schema has parsed it. `X` is the input shape, for request bodies and mocks.
6. **Treat a generated query's `error` as wider than its declared type.** The generated `XQueryError` promises an `Error` with `info` and `status`, but a non-JSON error body arrives as a `SyntaxError`, a 2xx body that fails its schema as a `ZodError`, and a network failure as a `TypeError`. Parse `error.info` with the problem schema's `safeParse` before showing it. The client rejects on every non-2xx response.
7. **Never pass `fetch: { signal }` to the generated query functions.** They forward Query's signal already, and yours would replace it.
8. **Pass explicit values to generated mocks for every enum field.** Orval's faker draws enum values from the Zod schema object and produces invalid ones, which the client's validation rejects. Fixtures satisfy the full generated type, as a typed literal or through `getXResponseMock(overrides)` when only top-level fields change (its overrides are shallow), never with `as`.
9. **The first route that awaits data with `useSuspenseQuery` turns on Orval's `useSuspenseQuery: true`,** since the generated options don't type-check with `useSuspenseQuery` otherwise.

Reach for these when their trigger appears: hierarchical query keys (`shouldSplitQueryKey`) when a mutation must invalidate a family of queries by prefix; branded API ids (`override.zod.useBrandedTypes`) when ids of different kinds travel side by side; `zod/mini` (`override.zod.variant`) when bundle size or startup time measures too high.
