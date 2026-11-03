### TanStack Query

1. **Pass no type arguments to `useQuery` or generated hooks.** Types flow from the query function; an explicit generic breaks the inference of the others.
2. **Branch on `status` with an exhaustive `switch`.** Use `isFetching` for a background refresh indicator, never as a reason to hide data already shown.
3. **Derive a slice with `select`, written as a stable module-level function.** `select` re-runs whenever its identity changes, and it must not throw: a failure belongs in the query function.
4. **Read query results by property, never with rest destructuring** (mechanical). Query tracks which properties a component reads and re-renders only for those; `...rest` subscribes to all of them.
5. **Set freshness per query from how fast its data changes:** `refetchInterval` for live numbers, `staleTime` for data that changes rarely. Change the `QueryClient` defaults in one place only.
6. **Disable a query that lacks an input with `enabled: false`, or `skipToken` in a hand-written query,** never with a conditional Hook call.
7. **In a mutation, invalidate the queries whose data it changed in `onSuccess`, and return that promise,** so the mutation stays pending until the fresh data arrives.
8. **Write a hand-written query with `queryOptions`:** a key that starts with its domain and lists every input, a function that reads Query's `signal`, and each streamed item parsed with its schema before it's yielded.
9. **Outside a component, use `queryClient.query`,** which replaces `ensureQueryData`, `prefetchQuery` and `fetchQuery` (deprecated in Query 5.105). Read the cache or fetch once with `query({ ...opts, staleTime: "static" })`. A prefetch is `void queryClient.query({ ...opts, staleTime: "static" }).catch(noop)` (`noop` from `@tanstack/react-query`) under a comment that says where a failure shows, since `query` rejects on failure where `prefetchQuery` didn't (mechanical).
10. **Poll with `refetchInterval`, not `setInterval`.** Query pauses polling in a background tab, dedupes it with other fetches and stops it on unmount.
11. **Retry only through Query, with one retry policy on the `QueryClient`** that retries only failures that can pass (common Retries). A hand-written retry loop doubles the attempts and ignores cancellation.
12. **Close the source of an async iterator that feeds `streamedQuery` when the signal aborts.** The query checks for cancellation only between items, so an idle stream would never end.
13. **Never mutate query data.** Query compares by reference, so an in-place change shows stale UI; return a new value.
14. **Give each test a new `QueryClient` with `retry: false`,** so a failure shows at once and no cache leaks between tests.
