### Effect

For a package that imports `effect`. Where a rule here conflicts with the vanilla TypeScript rules above, this section wins; the rest apply unchanged. Names are Effect 4 (checked against 4.0.0-rc.110, `@effect/tsgo` 0.51, Oxlint 1.87), with the Effect 3 spelling where it differs.

#### First

1. **Name the installed version** (`effect` in `package.json`, the catalog or the lockfile), **read its bundled guide in full** (`node_modules/effect/AGENTS.md` in v4, with runnable examples under `node_modules/effect/ai-docs/`; `MIGRATION.md` for v3 → v4), and **confirm each API name in the installed source before writing it** (`grep -nE "^export (const|function|class) timeout\b" node_modules/effect/src/Effect.ts`; some exports are aliased, such as `catch_ as catch`). Docs and community guides mix versions and release candidates; v3 pattern collections are a source of ideas, not of names.
2. **Follow the module's convention where Effect offers several spellings:** how sibling modules model absence (`Option` or `T | null`), branch on unions (`Match`, `$match` or `switch`), define errors, write functions (`Effect.fn`, `Effect.fnUntraced` or `(…) => Effect.gen(…)`) and define services. Keep a vanilla form only where the file already uses it consistently for the same job.

#### Vanilla rule → Effect

1. **Decode at the edge with Effect Schema** (`Schema.decodeUnknownEffect`) and take the type from the schema (`typeof User.Type`); JSON text decodes through `Schema.fromJsonString(S)`; small runtime checks use the `Predicate` module, not hand-written `isString`.
2. **Brand with `Schema.brand("UserId")` after the schema's checks,** so decoding is the one constructor; the `Brand` module only for brands with no schema.
3. **Closed string sets are `Schema.Literals(["a", "b"])`,** typed with `typeof S.Type`.
4. **Unions tag with `_tag`:** `Schema.TaggedStruct` or `Schema.TaggedClass` members in `Schema.Union([...])` for data that crosses a boundary, `Data.TaggedEnum` with `$is` and `$match` for in-memory data.
5. **Expected failures are tagged errors in the error channel,** raised with `return yield* new NotFound({ id })` and recovered with `Effect.catchTag` or `catchTags`. Effect's `Result` only for synchronous helpers and for inspecting an outcome (`Effect.result`), never a hand-written `{ ok }` union.
6. **Bugs are defects:** `Effect.die`, or `Effect.orDie` on a failure no caller can handle. Effect code doesn't `throw`.
7. **A wrapped failure is a tagged error with a `cause` field** (`cause: Schema.Defect()` in a Schema error), built in the `catch` of `Effect.try` or `Effect.tryPromise`.
8. **Match with `Match.type<T>()` or `Match.value(x)`, `Match.tag(...)` and `Match.exhaustive`;** `Match.valueTags` or `Match.typeTags` for a handler object per tag. A `switch` on `_tag` with a `never` arm only where the module already uses `switch`.
9. **Absence in schemas: `Schema.optionalKey(S)` for a key that may be missing, `Schema.optional(S)` for `T | undefined`, `Schema.NullOr(S)` for present-but-empty;** in logic, `Option<T>` where the module uses it, converted once at the integration point (`Option.fromNullishOr` in, `Option.getOrNull` out).
10. **Configuration through `Config`** (`Config.string`, `Config.int`, `Config.port`, `Config.url`, `Config.redacted`, `Config.schema(S, "NAME")`), read in the layer or entry effect that needs it, never `process.env`. A missing or malformed value fails layer construction with the setting's name.
11. **HTTP through `HttpClient` from `effect/unstable/http/HttpClient`,** not `fetch`: `HttpClientResponse.schemaBodyJson(S)` decodes, `HttpClient.filterStatusOk` fails non-2xx responses, `HttpClient.retryTransient` retries network errors and 5xx. Provide `FetchHttpClient.layer` or the platform client. The `effect/unstable/*` modules are fine to use.
12. **Timeouts with `Effect.timeout`** (or `timeoutOption`, `timeoutOrElse`); interruption replaces the `AbortSignal`, and `HttpClient` requests abort with the fiber. A promise API takes Effect's signal:

    ```ts
    Effect.tryPromise({ try: (signal) => sdk.send(input, { signal }), catch: (cause) => new SendFailed({ cause }) })
    ```

13. **Retries with `Effect.retry` and a `Schedule`:** exponential, jittered, capped by `Schedule.recurs`, filtered to retryable errors.
14. **Resources with `Effect.acquireRelease` inside a `Scope`** (`Effect.scoped`, or acquired in a layer); `Effect.ensuring` or `Effect.onExit` for finalizers.
15. **Dependencies are services (`Context.Service`) provided by layers; functions that return effects are `Effect.fn("name")`, inline effects `Effect.gen`; collections run with `Effect.all` or `Effect.forEach` and an explicit `{ concurrency }`; wrap a promise or callback API once with `Effect.tryPromise` or `Effect.callback`; fork into a scope (`Effect.forkScoped`, `forkIn`, `forkChild`), and give a detached fork (`forkDetach`) a comment saying who stops it; read time and randomness through `Clock`, `DateTime` and `Random` (non-security only, `Random.withSeed` in tests), ids, tokens and nonces through the `Crypto` service (`randomUUIDv4`, `randomBytes`); log with `Effect.log*` and `Effect.annotateLogs`; keep pure rules plain functions over domain values,** returning an `Effect` only from code that does I/O, fails with a tagged error, needs a service or reads the clock.

#### Errors

1. **One tagged error per failure a caller handles differently,** carrying the fields a caller needs to respond (`id`, `limit`, `retryAfter`), not a message to parse. Where the repo groups failures as one class with a `reason` literal, add a reason instead of a class. Every `_tag` in a union is unique: two classes with one tag are caught together with no warning.
2. **Define them with the repo's constructor:** `Schema.TaggedError<Self>()("Tag", { … })` when the error crosses a wire or needs encoding, `Data.TaggedError("Tag")<{ … }>` otherwise. Confirm the constructor's exact name; some v4 docs spell it `Schema.TaggedErrorClass`.
3. **Recover narrowly.** `catchTag` or `catchTags` where you can act; `Effect.catch` only at a boundary that handles every failure; v4's `catchReason`, `catchReasons` and `unwrapReason` for an error whose `reason` is itself a tagged union. Mapping a failure to another tagged error at a layer boundary is fine; turning it into a default value is the same bug as `catch { return [] }`.
4. **`orDie` on failures no caller can handle** (a startup invariant). `catchCause` and `catchDefect` belong only at the outermost boundary, so interruption and defects reach it.
5. **Data returned to an external caller** (an API response with variants such as `requires_action`) **stays a Schema union in the success channel;** the error channel holds failures internal callers branch on.

#### Schema

1. **Decode once, at the boundary that owns the data,** mapping the decode failure to that boundary's tagged error, and encode on the way out with the same schema.
2. **Records are `Schema.Struct` or `Schema.Class`; contracts stay readonly; unknown payloads are `Schema.Unknown` or `Schema.Json`, never `Schema.Any`.**
3. **Brand ids and primitives that carry an invariant** (`Schema.String.check(…).pipe(Schema.brand("Sha256Digest"))`, exported with `export type X = typeof X.Type`). A plain label with no invariant and no confusable neighbour stays unbranded.
4. **Defaults applied on decode use `Schema.withDecodingDefault`.**
5. **Turn absence into the domain failure explicitly.** In v4 `yield* option` fails with `NoSuchElementError`, which no caller can tell from another missing value: use `Option.match`, `Option.isNone` plus `return yield* new NotFound(…)`, or `Effect.fromNullishOr(x).pipe(Effect.mapError(() => new NotFound(…)))`.

#### Unions and matching

1. **Pick the union's home by where it travels:** a Schema union of tagged members when it is decoded or encoded; `Data.TaggedEnum` when it lives only in memory; a plain `_tag` union type when the module already uses one.
2. **End a `Match` pipeline with `Match.exhaustive`, not `Match.orElse`,** so a new variant fails the build. Put `Match.withReturnType<T>()` first when every arm must return one type.
3. **A lookup table keyed by `_tag` or a literal uses `satisfies Record<Union["_tag"], …>`.**

#### Config

1. **Read configuration through `Config` in the layer that needs it, or in a config service whose layer yields the values;** tests provide a `Layer.succeed` with fixed values.
2. **Validate with `Config.schema(S, "NAME")` or a typed constructor.** Constructor case changed during the 4.0 betas (`Config.string` vs `Config.String`); use what the installed version exports.
3. **Default with `Config.withDefault`, which applies only when the value is unset;** `Config.orElse` also replaces a malformed value, hiding the error.
4. **Secrets are `Config.redacted`;** call `Redacted.value` only at the line that sends the secret.
5. **Settings with a sensible default that code reads anywhere** (feature flags, tunables) **are a `Context.Reference` with a `defaultValue`;** a layer chosen by configuration is built with `Layer.unwrap`.

#### Services and layers

1. **Code asks for a service; it doesn't construct one.** Each method has no requirements (`R = never`): the layer yields the service's own dependencies once, and each method is an `Effect.fn("Billing.charge")`. Get it with `yield* Billing` and call its methods on the bound value; v4 has no static accessors.

   ```ts
   class Billing extends Context.Service<Billing, { readonly charge: (order: Order) => Effect.Effect<Receipt, ChargeFailed> }>()("app/Billing") {
     static readonly layer = Layer.effect(Billing, Effect.gen(function* () {
       const client = yield* PaymentsClient;
       return Billing.of({ charge: Effect.fn("Billing.charge")(function* (order) { /* … */ }) });
     }));
   }
   ```

2. **Provide once, at the edge,** composing with `Layer.provide` and `Layer.provideMerge`. Keep a parameterised layer in a constant: layers memoize by reference, and v4 shares the memo map across `Effect.provide` calls (`Layer.fresh` forces a rebuild). Layer names follow the repo (`layer`, `layerTest`, `layerConfig` in the official examples).

#### Concurrency, timeouts and retries

1. **State every collection operation's concurrency:** `Effect.forEach(xs, f, { concurrency: 8 })`. The default is sequential; `"unbounded"` only for a small, known-size input.
2. **Collect every outcome with `Effect.all(effects, { mode: "result" })`** (confirm the option name) when partial failure is acceptable.
3. **Time out each attempt, retry the attempts, and time out the whole:** `call.pipe(Effect.timeout("2 seconds"), Effect.retry(schedule), Effect.timeout("10 seconds"))`.
4. **A production retry schedule backs off exponentially with jitter, caps attempts, and retries only retryable failures** (v4 `Schedule.while` on the input, `Schedule.setInputType<E>()`). Defects are never retried.

#### Resources and running

1. **Acquire with `Effect.acquireRelease`;** a resource a service holds is acquired inside its layer, so the layer's scope releases it. `Effect.callback` returns its cleanup as a finalizer.
2. **Run effects at the edge only.** A process entry point uses the platform's `runMain` (it handles signals and exit codes); a long-running server uses `Layer.launch`; a framework builds one `ManagedRuntime` from the app layer and runs each request through it. Code in the middle returns effects and never calls `runPromise` or `runSync`.
3. **Keep HTTP handlers thin:** decode, call services, map errors to responses.

#### Style, observability and tests

1. **`Effect.fn("name")` takes the binding's name,** which names the span and the stack frame. `Effect.fnUntraced` on hot paths and in library internals; annotate a contract with `Effect.fn.Return<A, E, R>`. v4 takes extra combinators as further arguments to `Effect.fn`, not as a `.pipe` on its result.
2. **Write inline effects as `Effect.gen` with behaviour added by `.pipe(...)`,** and lambdas in pipelines (`Effect.map((x) => f(x))`) rather than point-free references, which lose overloads and generics.
3. **v4 `Ref`, `Deferred` and `Fiber` aren't yieldable:** `Ref.get`, `Deferred.await`, `Fiber.join`.
4. **Spans and logs:** `Effect.fn("name")` and `Effect.withSpan` create spans, `Effect.annotateCurrentSpan` adds attributes, `Effect.annotateLogs` adds log fields, and `Effect.log*` writes inside the current trace. The repo's telemetry rules (no secrets, bounded metric labels) apply to span attributes and log fields.
5. **Tests:** with `@effect/vitest`, `it.effect` runs on a test clock that starts at 0 (move it with `TestClock.adjust`) and `it.live` uses real time and I/O. Provide test layers built on in-memory state (`Ref`, `Layer.succeed`) instead of mocks, with `Layer.provideMerge` to expose a leaf service. Assert failures by tag: run the effect with `Effect.result` or `Effect.exit` and compare against the tagged error.
6. **Use `Array<T>` and `ReadonlyArray<T>` throughout an Effect package.**

#### v3 → v4 names

Agents trained on v3 write the old names and can't infer the new ones.

| v3 | v4 |
|---|---|
| `Context.Tag`, `Context.GenericTag`, `Effect.Tag`, `Effect.Service` | `Context.Service` |
| `FiberRef` | `Context.Reference` |
| `Either`, `Effect.either` | `Result`, `Effect.result` |
| `Effect.catchAll`, `catchAllCause`, `catchAllDefect`, `catchSome` | `Effect.catch`, `catchCause`, `catchDefect`, `catchFilter` |
| `Effect.async` | `Effect.callback` |
| `Effect.fork`, `forkDaemon` | `Effect.forkChild`, `forkDetach` |
| `Layer.scoped` | `Layer.effect` |
| `Schema.decodeUnknown`, `decodeUnknownEither` | `Schema.decodeUnknownEffect`, `decodeUnknownExit` |
| `Schema.Literal("a", "b")`, `Schema.Union(A, B)` | `Schema.Literals(["a", "b"])`, `Schema.Union([A, B])` |
| `Schema.filter`, `Schema.transform`, `Schema.parseJson` | `Schema.check` / `refine`, `Schema.decodeTo`, `Schema.fromJsonString` |
| `Option.fromNullable` | `Option.fromNullishOr` |
| `@effect/platform`, `@effect/rpc`, `@effect/cli` | modules inside `effect`; HTTP, CLI, SQL, RPC and AI under `effect/unstable/*` |

v4 also changed what is an Effect: `Option`, `Result` and `Config` are yieldable in generators but not assignable to `Effect`; pass them to combinators with `Effect.fromOption` or `.asEffect()`.

#### Checks

Where the repo configures the Effect language service (the `oxlintrc.json` and `tsconfig.json` fragments beside this file), its diagnostics are part of the type check: fix them like type errors. It checks `yield*`, `return yield*` when raising, v3 names, sync decoders and `JSON.parse` in effects, and, in Effect packages, `process.env`, `Date`, `Math.random`, `fetch` and `crypto.randomUUID`. Where the repo doesn't run it, apply those by hand. Suppress one line with `// @effect-diagnostics-next-line <rule>:off -- <why>`.
