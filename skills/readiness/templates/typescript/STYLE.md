# TypeScript style

The TypeScript rules no formatter, linter or compiler checks, beyond the shared rules in the root `STYLE.md`. The tsconfig and the Oxlint config hold the rules a tool enforces; their comments say which. Read the root file and this one before implementing and before any style review.

Write TypeScript shapes: discriminated and literal unions, interfaces of required fields, and functions over plain data. Habits from other languages (enums, classes with setters, a base class with overrides) compile, but give up narrowing and structural checks.

A rule marked **(mechanical)** names a pattern a tool could find from syntax alone, a candidate for a future lint.

## Never

Mistakes that are costly once shipped and that the lint config doesn't catch.

- **Never pass outside data inward unparsed.** HTTP bodies, `fetch` responses, `JSON.parse`, files, env vars, CLI arguments, untyped database rows, `postMessage`, IPC, queue messages and SDK payloads typed `any` are `unknown` until a schema (or, without a schema library, a guard that checks every field) parses them, once, at the boundary (common Boundaries).
- **Never let a missing security setting fall back to a permissive default.** A missing limit never means "unlimited", nor a missing origin "allow all"; define what `0`, `""` and `-1` mean for each limit. Parse config once at startup; a missing required setting fails with its name.
- **Never swallow an error.** `catch { return [] }`, `?? []` and `|| {}` on data the caller requires hide the failure. Catch only to recover, to translate at a boundary or to clean up; a catch that logs and rethrows adds noise.
- **Never make an outbound call without a timeout or the caller's `AbortSignal`** (join them with `AbortSignal.any`), and never retry an operation that isn't idempotent. Retries are bounded and back off.
- **Never write `target[key] = value` with a key from input.** `__proto__`, `constructor` or `prototype` changes the prototype every object shares; store user-keyed data in a `Map`.
- **Never compare a secret, token or MAC with `===`.** It returns at the first differing byte and leaks how much of a guess was right. Compare fixed-length digests, such as HMACs of both values, in constant time, so a length difference neither leaks nor throws; Node's `crypto.timingSafeEqual` is one, and takes only equal-length buffers.
- **Never use `Math.random` for tokens, ids or nonces.** It is predictable; use `crypto.randomUUID()` or `crypto.getRandomValues()`.
- **Never read an id above 2^53 as a number.** `JSON.parse` loses its precision silently; keep it a string or a `BigInt`.

## Types

1. **Make illegal states unrepresentable.** When a comment would explain which field combinations are valid, split the type into a discriminated union; two booleans that must stay in sync become one union.

   ```ts
   // Before: { loading: boolean; data?: User; error?: Error }
   type UserState =
     | { readonly status: "loading" }
     | { readonly status: "loaded"; readonly user: User }
     | { readonly status: "failed"; readonly error: Error };
   ```

2. **Name a discriminant after what it distinguishes** (`status` for a lifecycle, `outcome` for a result, `channel` for a delivery route), so the field keeps its domain meaning. Use `kind` only when no domain word names the distinction, `type` for a reducer's actions, as react.dev writes them, and `_tag` in Effect code. Data from an API keeps the wire format's own field.
3. **Take the variant a function needs, not the whole union.** `render(state: Extract<UserState, { status: "loaded" }>)`, or the loaded value itself, so the caller narrows once.
4. **Build the shape so the bad value can't exist.** `[T, ...T[]]` for a non-empty list; `start` plus `duration` instead of two dates that must be ordered.
5. **Stop at the simplest total type.** Keep `T[]` while every operation works for all values. Strengthen a type only where the loose one forces a `!`, a cast or a "can't happen" throw; a conditional, mapped or template-literal type must remove a cast or a duplicated declaration.
6. **Derive types from the one canonical value.** When a schema, generated client, OpenAPI or protobuf definition or database schema owns a shape, infer the type from it. When the set must exist at run time, write it once `as const`, check it with `satisfies`, and derive the union; when the union is canonical, a table keyed by it uses `satisfies Record<Union, …>`, so a new member fails the build until the table has it.

   ```ts
   const PLANS = {
     free: { seats: 1 },
     team: { seats: 10 },
   } as const satisfies Record<string, { seats: number }>;
   type Plan = keyof typeof PLANS; // "free" | "team"
   // A list: const MODES = ["read", "write"] as const; type Mode = (typeof MODES)[number];
   ```

7. **Derive variants with utility types when they must change together; declare a separate type when it must stay stable** (a public response that must not gain every new column).

   | Need | Write |
   |---|---|
   | A subset or superset of fields | `Pick<T, K>`, `Omit<T, K>`, `interface B extends A` |
   | Every field optional or required | `Partial<T>`, `Required<T>` |
   | A total table keyed by a union | `Record<Union, V>` |
   | Some members of a union | `Extract<U, { kind: "a" }>`, `Exclude<…>` |
   | A function's inputs or output | `Parameters<typeof f>[0]`, `ReturnType<typeof f>`, `Awaited<…>` |
   | A nested field's type | `User["address"]`, `(typeof LIST)[number]` |
   | Drop `null` and `undefined` | `NonNullable<T>` |

8. **`Omit` doesn't check its keys and collapses a union; name past two nested utilities.** `Omit<User, "emial">` compiles and removes nothing: prefer `Pick` for small subsets or a checked helper, and drop a field from each variant with a distributive one. Give a result of more than two nested utilities a name and a one-line comment.

   ```ts
   type StrictOmit<TObject, TKey extends keyof TObject> = Omit<TObject, TKey>;
   type DistributiveOmit<TObject, TKey extends PropertyKey> = TObject extends unknown ? Omit<TObject, TKey> : never;
   ```

9. **Brand primitives that mean different things and travel side by side** (`UserId` and `OrderId`). Create a branded value in exactly one validating constructor, which holds the only `as`, under a disable that names the check above it. With a schema library, brand in the schema so parsing and branding are one step; otherwise use one shared `Brand` helper per repo. Brand units (`Milliseconds`, `Cents`) only when values in different units meet in arithmetic across modules; within one module a unit suffix on the name is enough.

   ```ts
   declare const brand: unique symbol;
   export type Brand<T, Name extends string> = T & { readonly [brand]: Name };
   export type UserId = Brand<string, "UserId">;
   export function parseUserId(raw: string): UserId {
     if (!/^usr_[a-z0-9]{12}$/.test(raw)) throw new Error(`not a user id: ${raw}`);
     // oxlint-disable-next-line typescript/no-unsafe-type-assertion -- checked by the pattern above
     return raw as UserId;
   }
   ```

10. **Write object types as `interface`, and compose them with `extends`, not `&`.** An interface is one flat type whose conflicts the compiler reports and whose relations it caches; an intersection is rechecked at each use and can collapse to `never`. Use `type` for unions, tuples, function types and types derived with `Pick`, `Omit` or `Awaited`. The lint enforces `interface`; review checks `extends`.
11. **Pass an options object instead of a `boolean` or optional positional parameter, and split a function whose boolean switches between two behaviours** (mechanical). `relativeAge(ms, true)` tells the reader nothing. Positional parameters suit one or two distinct values and hot paths.
12. **Return a named interface when a result has more than one non-trivial part.** A tuple fits a hook that mirrors `useState` (`[value, setValue]`) and a labelled pair whose order every reader knows (`[start: number, end: number]`).
13. **Key runtime collections with `Map` and `Set`.** Plain objects are for fixed shapes, and `Record<Union, T>` for a table that must list every member of a closed union. A `Map` keeps insertion order and never confuses a key with an inherited property.
14. **Make every type guard and assertion function check all it claims, and name a guard `isX` or `hasX`.** The compiler trusts `x is T` without reading the body, so a guard that checks one field of five is an unchecked cast with a reassuring name. Prefer the schema's `safeParse`; hand-write a guard only for a small local shape.
15. **Treat an interface as a minimum, not an exact shape.** A value typed `Session` may carry extra keys, because only a fresh object literal gets the excess-property check. Before storing or sending a value whose extra keys matter, parse it or copy the fields you mean.
16. **Write no enums.** `erasableSyntaxOnly` rejects them. A closed set is a literal union, written once `as const` when its values are needed at run time (Types 6).
17. **Write no classes, except an `Error` subclass a caller checks with `instanceof` and a type a library requires.** Behaviour lives in module functions and closures; a class with setters gives up the structural checks.

## Absence

Each empty state has one spelling, so readers can tell "not provided" from "provided as empty":

1. **`x?: T`: the key may be missing.** With `exactOptionalPropertyTypes` an explicit `undefined` is rejected; write `x?: T | undefined` only where callers pass `undefined` on purpose.
2. **`T | null`: the field is always present and known to be empty.** Make a field required and nullable when every caller passes it, even if the value can be empty; never make it optional so a test or fixture is shorter.
3. **`undefined`: what lookups return** (`Map.get`, `find`, `.at`, an optional key). Return it; store and send `null` or omit the key.
4. **When missing and empty mean different things, keep both and say so in the type,** as a patch does: absent means "leave as is", `null` means "clear".

   ```ts
   interface ProfilePatch {
     readonly name?: string;       // missing: keep current
     readonly bio?: string | null; // missing: keep current; null: clear it
   }
   const patch: ProfilePatch = { ...(bio === undefined ? {} : { bio }) }; // omit, don't assign undefined
   ```

5. **Keep `| null` and `| undefined` out of type aliases** (`type MaybeRow = Row | null`). Write them where the value is used, so each use shows it can be empty.
6. **`Partial<T>` makes `?:` keys and inherits the same rule; `"x" in obj` tests for the key and `obj.x !== undefined` for a value.** Use the one that matches the meaning, and convert between spellings once, in the boundary's mapper (a database `null` to a missing key in a public payload, or back).

## Boundaries

The general rules are common Boundaries 1–5. In TypeScript:

1. **Parse into a named domain type and keep wire and transport types out of a module's public interface.** Inside, no re-validation and no defensive checks for states the type rules out.
2. **Parse configuration (env vars, CLI arguments, config files) once, where the program loads it,** into a typed object: a URL becomes a `URL`, a number a checked number, a mode its literal union. That place is the entry point or the start of the function that receives the environment, never the callback that later uses the value. Request-scoped strings (headers, query parameters) are parsed at the request boundary the same way.
3. **Schemas before hand-written guards.** Use the repo's schema library and infer the type from the schema, so there is one definition instead of a schema, an interface and a guard that drift apart. With no schema library, hand-write a guard for one small shape; when a change needs several boundary parsers, propose a library that implements Standard Schema in the handoff instead of adding a dependency for one guard.
4. **Throwing parse where bad data is a bug** (config, internal service responses); **non-throwing parse where failure is an expected branch** (user input), returning the failure to the caller.
5. **Use an assertion function for an invariant whose failure is a bug, after which the caller continues on the narrowed value.** Declare it with `function` (an arrow assigned to a `const` needs an explicit type annotation to narrow).

   ```ts
   function assertNonEmpty<T>(xs: readonly T[], what: string): asserts xs is readonly [T, ...T[]] {
     if (xs.length === 0) throw new Error(`${what} must not be empty`);
   }
   ```

6. **Narrow in this order:** discriminant, `in`, `typeof` or `instanceof`, a verifying guard, then `as` only after validation the compiler can't follow.
7. **Let inline predicates narrow** (TypeScript 5.5+): `xs.filter((x) => x != null)` is already `T[]`. `.filter(Boolean)` still doesn't narrow.
8. **End a `switch` over a domain union with a `never` arm that throws,** so a new variant fails the build and a bad runtime value fails loudly. The `switch-exhaustiveness-check` lint allows the arm. Call the repo's `assertNever` helper there if it has one; an `if`/`else` chain over a union ends with a `never` assignment the same way; an open set (`string`, `number`) has nothing to exhaust, so handle the unknown case explicitly.

   ```ts
   default: {
     const unhandled: never = state;
     throw new Error(`unhandled state: ${JSON.stringify(unhandled)}`);
   }
   ```

## Escape hatches

Each one carries its reason (common Exceptions).

1. **`as` and `!` only right after a check the compiler can't follow, inside a brand constructor, or inside a small transform whose parameters and return type are fully typed.** Elsewhere, fix the type.
2. **A type parameter used only in the return type is an unchecked cast.** Boundary functions take a schema and return its output type, or return `unknown`:

   ```ts
   // Before: async function getJson<T>(url: string): Promise<T>
   async function getJson<S extends StandardSchemaV1>(url: string, schema: S): Promise<StandardSchemaV1.InferOutput<S>>
   // or, with no schema: async function getJson(url: string): Promise<unknown>
   ```

3. **Disable a lint rule on the next line only, naming each rule and the reason:** `// oxlint-disable-next-line typescript/no-unsafe-type-assertion -- checked by isFrame above`. A disable without a rule name, a file-wide disable or a block disable is rejected; an unused disable fails the lint, so remove it with the code that needed it. Oxlint can't require the `-- reason`, so review checks it.
4. **Compiler errors: `// @ts-expect-error -- <why>`, never `@ts-ignore` or `@ts-nocheck`.** The lint requires a description of at least 10 characters. List every disable in the handoff.
5. **Wrap wrong or `any` third-party types once, at the boundary:** one wrapper calls the SDK, parses the result with a schema and returns the domain type, so the `any` and its disables stay in one place.
6. **Loosen a compiler flag only as a task of its own, one flag at a time, with a comment giving the reason.** `exactOptionalPropertyTypes` is the flag most likely to clash with third-party types; wrap the library (rule 5) before loosening it.

## Errors

The general rules are common Errors 1–7. In TypeScript:

1. **Throw an `Error` for bugs, broken invariants and infrastructure faults, with the original as `cause`,** and let it reach the one boundary handler (the request handler, job runner, CLI entry point or route error boundary) that logs and responds. Subclass `Error` only when a caller checks for it with `instanceof`, set its `name`, and put identifiers in fields, not only in the message.
2. **Return expected outcomes the caller branches on** (not found, conflict, validation failed, quota reached) **as a discriminated union named for the domain,** each failure variant carrying the data the caller needs, not a message to parse. Use the repo's `Result` type if it has one; don't add a result library to a repo that lacks one. When every caller would turn the failure straight into a throw, throw at the source.

   ```ts
   type ReserveResult =
     | { readonly outcome: "reserved"; readonly reservation: Reservation }
     | { readonly outcome: "sold-out" }
     | { readonly outcome: "over-limit"; readonly limit: number };
   ```

3. **Narrow a caught value before reading it, and pass it on unchecked.** `catch (error)` is `unknown`, so `new Error("cannot open the feed", { cause: error })` needs no check, while reading `error.message` needs `error instanceof Error` first.
4. **Write the messages of thrown errors as lowercase fragments with no final period** that name the action and its operand: `cannot parse event 42` (mechanical).
5. **Clean up with `using` or `await using`** where the runtime and `lib` support it (TypeScript 5.2, `esnext.disposable`); otherwise `finally`.

## Functions and generics

1. **Infer by default.** Annotate the return type of an exported function other modules rely on (a parser, a query options builder, a hook that returns an object), of any function with several return paths or recursion, and of an exported function whose inferred type is large, which stops the checker re-deriving it at every use. Annotate empty collections and state that starts as `null`. Let inference type components and framework factories whose full type only inference can write.
2. **A generic preserves the relationship between input and output.** A type parameter appears in at least two positions; its constraint names only what the body reads (`T extends { id: string }`, not `T extends User`); callers shouldn't need type arguments, so if they do, pass a value that carries the type (a schema, a key, a factory). A parameter that appears once is its constraint: write the wide type.

   ```ts
   function pick<TObject, TKey extends keyof TObject>(obj: TObject, keys: readonly TKey[]): Pick<TObject, TKey> {
     // oxlint-disable-next-line typescript/consistent-type-assertions, typescript/no-unsafe-type-assertion -- the one cast, in a fully typed transform
     const out = {} as Pick<TObject, TKey>;
     for (const k of keys) out[k] = obj[k];
     return out;
   }
   ```

3. **A `const` type parameter keeps literal types without `as const` at the call site; `NoInfer<T>` checks an argument against `T` without widening it.** `NoInfer` fits defaults, fallbacks and "one of the values above" arguments. Skip `const` when the parameter only feeds a wide type such as `string[]`.

   ```ts
   function defineRoles<const R extends readonly string[]>(roles: R): R { return roles; }
   function machine<const S extends string>(states: readonly S[], initial: NoInfer<S>) { /* … */ }
   machine(["idle", "busy"], "idel"); // error; without NoInfer, S would widen to include "idel"
   ```

4. **Type-level programming only where it removes duplication or casts.** Reach for built-in utilities first. A conditional type over a bare type parameter distributes over a union (`IsString<string | number>` is `boolean`); wrap both sides (`[T] extends [U]`) to test the union whole. Give every non-trivial helper type a name and a one-line comment saying what it computes. Past a screen, generate the types from their source of truth instead. Overload a function only when its return type depends on which argument shape was passed and a union return would force callers to narrow.
5. **Write each named module-level function and component as a `function` declaration** (mechanical). Use arrows for callbacks, for handlers inside a component, and for a function typed as a whole (`const handleSearch: SearchHandler = (event) => …`). A declaration reads the same at every level, is hoisted, and needs no `<T,>` to be generic in a `.tsx` file.
6. **Avoid deep recursive conditional types and unions of tens of thousands of members.** Both show as slow checks and "type instantiation is excessively deep". Measure before changing anything: `tsc --extendedDiagnostics` for totals, `tsc --generateTrace <dir>` for what costs most.

## Functional

1. **Keep the core pure and the effects at the edges.** A rule is a function from values to values; the caller that wires it up does the I/O, reads the clock and logs, and passes in what it read (`now: Date`, the loaded rows). A rule you can test with plain values and no mocks is in the right place.
2. **Immutable by default.** `readonly` fields on domain types, `readonly T[]`, `ReadonlyMap`, `ReadonlySet` and `Readonly<T>` on parameters (React props excepted: React's rules already forbid changing them); return a new value instead of changing an argument. `readonly` is shallow: mark nested fields where they are declared, and reach for a recursive `DeepReadonly` only for config or fixture trees frozen whole. Skip it on local values being built and on library types you can't change. Freeze module-level tables with `as const`.
3. **Write small total functions.** A function returns a value for every input its parameter type allows; when some inputs have no answer, narrow the parameter (a non-empty tuple, a variant) or return the typed failure. A throw is for the bug case only.
4. **Pass a side effect a module needs (the clock, a socket opener, storage, randomness) as a parameter,** a function type or a narrow interface, so a test passes a fake without mocking modules. Take only what the module calls: `() => number` for the clock, not a `Clock` service; a function that reads the time once takes the value. Skip it when the framework already injects the dependency.

## Async

The general rules are common Concurrency and Retries. In TypeScript:

1. **Mark a deliberate fire-and-forget `void task()`, with a comment that says where its errors go.** The lint requires the `void`; only the comment tells a reader the dropped promise is safe.
2. **Run independent work concurrently with `Promise.all`,** or `Promise.allSettled` when partial failure is acceptable and you handle each outcome.
3. **Pass the caller's `AbortSignal` through to outbound work, and use `AbortSignal.timeout(ms)` for a deadline,** joined with the caller's by `AbortSignal.any([a, b])`.
4. **Await every validation or authorization check before acting on its result.** A missed `await` lets the next line run before the check finishes, and its rejection goes unhandled.
5. **Iterations that must await one after another, such as a paginated read, carry a `no-await-in-loop` disable with the reason;** the rest run concurrently.

## Security

The general rules are common Security 1–7. In TypeScript:

1. **Convert to numbers at the boundary and compare numbers.** `+` concatenates as soon as one side is a string, and `<` on two strings compares character by character (`"10" < "9"`).
2. **When a plain object for user keys is unavoidable, create it with `Object.create(null)` and reject `__proto__`, `constructor` and `prototype`.** Recursive merges and `Object.assign` from parsed JSON carry the same risk as `obj[key] =`. `key in obj` also finds inherited properties (`"toString" in {}`): test ownership with `Object.hasOwn`.
3. **Check a number string against a pattern such as `/^-?\d+$/` (or a schema's string regex followed by a transform) before calling `Number()`.** `Number("")`, `Number(" ")` and `Number(null)` all return 0, which passes `Number.isInteger`, so a cleared form field or a missing `localStorage` key reads as a real 0.
4. **Use `parseInt(s, 10)` only when a trailing suffix is expected.** `parseInt` stops at the first non-digit (`"12abc"` gives 12) and reads a `0x` prefix as hex.
5. **Keep patterns that run on input linear.** Nested quantifiers (`(a+)+`), overlapping alternatives (`(a|aa)+`) and adjacent greedy wildcards (`.*.*`) can backtrack exponentially and freeze the event loop; cap the input length first, or use a linear-time engine.
6. **Around security decisions, derive the type from a parse, never from an assertion.** `as`, `!`, `any` and a guard that returns `true` without checking all compile cleanly and fail at run time.

## Modules

1. **Import from the module that defines the symbol.** A package's public surface is its `package.json` `exports` entries, each a small entry file; import other packages only through those, never through their internal paths.
2. **Write no barrel file.** The barrel lint counts only `export *`, so review catches a re-export file built from `export { a } from`. A package's entry files are the exception.
3. **Inline a module, wrapper or layer that only forwards calls** (common Structure).

## Platform features

**Confirm the repo's tsconfig `target` and `lib` and its runtime version (`engines`, `.nvmrc`, `.tool-versions`, the tool config) include a feature before using it, then use the built-in instead of a helper or a dependency.** A newer `lib` only changes what type-checks: a bundler lowers syntax but adds no polyfills, so a built-in the runtime lacks throws with no type error to warn of it.

| Needs | Instead of | Use |
|---|---|---|
| TS 5.2, `esnext.disposable`, runtime support | `try`/`finally` that releases a handle | `using` / `await using` with `[Symbol.dispose]` |
| ES2023 `lib` | a copy, then `sort` | `xs.toSorted(f)`, `toReversed`, `with`, `findLast` |
| ES2024 `lib` | `let resolve; new Promise((r) => { resolve = r; })` | `Promise.withResolvers<T>()` |
| ES2024 `lib` | a `reduce` that builds groups | `Object.groupBy(items, keyOf)`, `Map.groupBy` for non-string keys |
| `esnext` `lib` | collecting an async iterable in a loop | `await Array.fromAsync(source)` |
| ES2025 `lib` | Set math with `filter` and `has` | `a.union(b)`, `intersection`, `difference`, `isSubsetOf` |
| ES2025 `lib` | `[...iter].filter().map()` over a large or lazy iterable | iterator helpers: `iter.filter(f).map(g).take(n).toArray()` |
| `DOM` `lib`, or Node 20 | a hand-made timeout signal | `AbortSignal.timeout(ms)`, joined by `AbortSignal.any([a, b])` |

## Data

1. **Keep wire timestamps as the API sends them** (ISO 8601 strings), parse them with `Date.parse` where they're compared, and format them for people with `Intl`. Create each `Intl` formatter once at module level.
2. **Sort only a list whose order isn't set upstream, by a total key,** breaking ties with a unique field so rows don't jump between refetches. Where `lib` lacks `toSorted`, copy the array and sort the copy in its own statement (`const sorted = [...rows]; sorted.sort(byNewest);`). The lint requires a comparator.
3. **Iterate a typed `Map` or a typed key list rather than casting `Object.keys` to `keyof T`.** `Object.keys` and `Object.entries` return `string` keys by design.

## Naming

The shared rules are in the root `STYLE.md`. In TypeScript:

1. **Write types, interfaces, components and type parameters in UpperCamelCase, values in lowerCamelCase, and module-level constants whose value is deeply immutable in CONSTANT_CASE** (`REFETCH_INTERVAL_MS`). An object with behaviour, such as an `Intl` formatter, stays lowerCamelCase, and so does a local constant; a name a framework requires keeps its form. Treat acronyms as words (`sessionUrl`, `SseEvent`). No `I` prefix on interfaces (mechanical).
2. **Name a type parameter `T` when there is one obvious parameter, and descriptively when there are two or more** (`TObject`, `TKey`). No lint checks it.
3. **Write no types in `@param` or `@returns`.** The signature has them.

## Tests

The general rules are in `TESTING.md`. In TypeScript:

1. **Put tests beside their module as `<name>.test.ts` or `<name>.test.tsx`, and type tests as `<name>.test-d.ts`.** The tsconfig `include` covers them, so they are type-checked like source.
2. **Test the type contract of utility types and public generic APIs** with `expectTypeOf(fn(x)).toEqualTypeOf<Expected>()`, run with type checking on, and assert what must not compile with `// @ts-expect-error -- <case>` on the offending line, which fails once the line starts compiling. Test the inference callers rely on, not only explicit type arguments.
3. **Build fixtures that satisfy the full production type,** as a typed literal or through a factory helper. Where a test needs a deliberately partial object (a large framework request), use the repo's existing helper; an `as` in a test carries a comment. Production types never loosen for test setup.
4. **Give a hand-written parser of outside input a fast-check property test that it never panics** (`TESTING.md`, property tests).
5. **Run tests under a pinned locale (`LC_ALL=en_US.UTF-8` in the test command) when assertions read text formatted with the default locale.**

## Design review

Review the types and signatures before implementation, and a finished change the same way. Answer each question with file and line evidence.

- **Data model:** does each concept have one type, derived from its schema or one `as const` value, and can any value hold an invalid state? (Types 1, 5, 6)
- **Boundaries:** is every outside value parsed once where it enters, and does nothing inside re-check it? (Never; Boundaries 1)
- **Errors:** does each error reach a place the user sees, and does each `catch` recover, translate or clean up? (Never; Errors)
- **Cancellation:** does every request and subscription end when its owner goes away? (Never; Async 3)
- **API shape:** is each module-level function a declaration, and each contract's return type annotated? (Functions 1, 5)
- **Tests:** does each test find elements as a user would, fake only the network and the clock, and fail if the code returned a constant? (`TESTING.md`)
- **Later patterns:** would a pattern below remove code, a cast or a measured cost?

## Patterns

Each pattern earns its place only where it removes a cast, a `!`, a duplicated declaration or a runtime check, or turns a likely mistake into a compile error (common Structure). A reviewer asks for that payoff; a pattern without one becomes the plain type. Check the TypeScript version the repo pins before using a feature: `satisfies` 4.9, `const` type parameters 5.0, `NoInfer` 5.4, inferred type predicates 5.5.

| Pattern | Use it when | Skip it when |
|---|---|---|
| Event map, keyed with `keyof` and indexed access | a payload, handler or result depends on a name or discriminant, in more than one place | two or three variants are handled in one `switch` |
| Mapped union over the event map | a message, action or job union must stay in step with that map | the union is written once and nothing else is derived from it |
| Generic over `keyof T` returning `T[K]` | the result type depends on which key the caller passes | the function treats the value opaquely: take the wide type |
| Labelled tuple, `NonEmpty<T>` | positions have fixed meanings, or a length guarantee removes a check | items are uniform (`readonly T[]`), or a reader would have to look up what a position means: a named interface |
| `const` type parameter | a declaration helper must keep the literal types callers pass | the parameter only feeds a wide type such as `string[]` |
| `NoInfer<T>` | a default or fallback argument must match another argument instead of widening it | one argument decides `T` alone |
| Assertion function (`asserts x is T`) | an invariant whose failure is a bug, after which the caller continues on the narrowed value | failure is an expected outcome: return a union |
| Branded unit (`Milliseconds`, `Cents`) | values in different units meet in arithmetic across modules | a unit suffix on the name is enough (`timeoutMs`) |
| Template literal type | a small closed set of structured strings: event names, CSS custom properties, `` `${Entity}.${Action}` `` | the set is open, or the cross product grows past a few hundred members: parse a `string` |
| Mapped type with key remapping (`as`) | many contracts follow one naming rule, such as an `onXChange` per field | one or two contracts: write them out |
| Conditional type with `infer` | a small, named transformation no built-in utility covers | `Awaited`, `ReturnType`, `Parameters`, `NonNullable` or `Extract` already does it |
| Typestate: one type per lifecycle step | calling a step out of order is a bug (draft, validated, submitted) | the flow has one step, or the server checks the order and the client only shows the state |
| Command type per operation | an operation may change only some fields (`RenameProject`) | the operation is a true patch: `Partial<Pick<T, …>>` |
| Patch field `x?: T \| null` | an update must tell "leave as is" (absent), "clear" (`null`) and "replace" apart | the field can't be cleared |
| Capability parameter (a function or narrow interface) | a module needs a side effect, such as the clock, a socket opener or storage, that a test must replace | the framework already injects it (React context, a query client, a DI container) |

Event map and mapped union: the map is the canonical value, so adding an event updates every derived type and a missing handler fails to compile. When a schema owns the event shapes, derive the map from it.

```ts
interface EventMap {
  "user.created": { readonly userId: UserId };
  "order.paid": { readonly orderId: OrderId; readonly amountCents: number };
}
type EventName = keyof EventMap;
// One { name, payload } pair per key; `{ name: EventName; payload: EventMap[EventName] }` would let them vary apart.
type AppEvent = { [K in EventName]: { readonly name: K; readonly payload: EventMap[K] } }[EventName];
type Handlers = { readonly [K in EventName]: (payload: EventMap[K]) => void };
declare function on<K extends EventName>(name: K, listener: (payload: EventMap[K]) => void): () => void;
```

Labelled tuple and non-empty list: build a `NonEmpty<T>` once, where the length is checked, and pass it inward.

```ts
type Range = readonly [startMs: number, endMs: number];
type NonEmpty<T> = readonly [T, ...T[]];
function first<T>(items: NonEmpty<T>): T {
  return items[0]; // T, not T | undefined, even under noUncheckedIndexedAccess
}
```

Key remapping: filter or rename keys inside a mapped type.

```ts
type Listeners<T> = { [K in keyof T & string as `on${Capitalize<K>}`]?: (value: T[K]) => void };
type OnlyHandlers<T> = { [K in keyof T as K extends `on${string}` ? K : never]: T[K] };
```

Typestate and command types: TypeScript compares types by shape, so brand each step type; otherwise an object literal of the right shape skips the transition. One function is the only place each step is made.

```ts
interface DraftInvoice { readonly lines: readonly Line[] }
type ValidatedInvoice = Brand<{ readonly lines: NonEmpty<Line>; readonly totalCents: number }, "ValidatedInvoice">;
type Validation =
  | { readonly outcome: "valid"; readonly invoice: ValidatedInvoice }
  | { readonly outcome: "invalid"; readonly problems: readonly string[] };
declare function validation(draft: DraftInvoice): Validation; // the one place a ValidatedInvoice is made
declare function issue(invoice: ValidatedInvoice): Promise<IssuedInvoice>; // a draft can't be issued
interface RenameProject { readonly projectId: ProjectId; readonly name: string } // touches the name only
```
