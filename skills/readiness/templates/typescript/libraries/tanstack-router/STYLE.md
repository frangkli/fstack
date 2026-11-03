### TanStack Router

1. **Validate search params with a schema passed straight to `validateSearch`.** Zod's `.default()` fills a missing value but sends a malformed one to the route's `errorComponent`; chain `.catch()` where a bad value should fall back instead. Read them with `Route.useSearch()`, never from `window.location`.
2. **Give a loader only the search params it uses, through `loaderDeps`, and put the same values in the query key.** `loaderDeps` is the loader's cache key, so returning the whole search object reloads on every change.
3. **Navigate with `<Link>` for anything a user clicks, and with `useNavigate` only after a side effect.** Pass `from` to router-wide hooks and links: `Route.fullPath` inside the route's file, the literal path elsewhere, or `getRouteApi("/orders")`'s hooks, since importing `Route` from another file makes an import cycle. Without `from`, the types are checked against every route, which costs type-check time.
4. **Export nothing from a route file but `Route`.** The router splits each route's component into its own chunk only when the component isn't exported.
5. **Write route options in inference order:** `params` and `validateSearch`, then `loaderDeps`, `context`, `beforeLoad`, `loader`, then the components. Each option's types flow from the ones before it.
6. **Throw `notFound()` or `redirect()` from a loader or `beforeLoad`, not from a component,** so the route never renders with missing data. The `only-throw-error` lint rejects both until it allows Router's `Redirect` and `NotFoundError`; until then each throw carries `// oxlint-disable-next-line typescript/only-throw-error -- Router's notFound() and redirect() are control flow`.
7. **Start every query a route's page reads in the route's `loader`, without awaiting it, and read it in the component with the same hook and parameters,** branching on `status`. The fetch then starts on hover or navigation, alongside the route's code chunk, and each panel keeps its own loading and error state, so one failing endpoint doesn't blank the page. `staleTime: "static"` fetches only what isn't cached; the hook refreshes stale data when the page mounts. Leave out a query the page disables until it has an input: `query` ignores `enabled`. The loader reads the `queryClient` from the router context (`createRootRouteWithContext<{ queryClient: QueryClient }>()`).

   ```tsx
   export const Route = createFileRoute("/orders")({
     loader: ({ context: { queryClient } }) => {
       // A failure shows in the page's useOrders; the prefetch only starts the fetch.
       void queryClient.query({ ...getOrdersQueryOptions(), staleTime: "static" }).catch(noop);
     },
     component: OrdersPage,
   });
   ```

8. **Await in the loader and read with `useSuspenseQuery` only when the route has nothing to show without the data,** such as a detail page whose id may not exist: `await queryClient.query({ ...opts, staleTime: "static" })`, and turn a 404 rejection into `throw notFound()`. This blocks the navigation and sends a failure to the route's `errorComponent`.
9. **Let Query decide freshness:** keep `defaultPreloadStaleTime: 0`, and set no router `staleTime`, `preloadStaleTime` or `shouldReload`; otherwise the router skips the loader while its own cache is fresh, and the fetch waits for the component to mount.

Reach for a pathless `_authed` layout route whose `beforeLoad` throws `redirect` when the app gains sign-in; never on a root route that runs at build time.
