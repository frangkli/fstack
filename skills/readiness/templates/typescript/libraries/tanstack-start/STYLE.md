### TanStack Start

For an app in SPA mode: the build renders only the root route, into a static shell that a server serves and the browser hydrates.

1. **Keep the root route and the shell deterministic.** The root route's `beforeLoad`, `loader` and components run at build time, so they fetch no API data, read no session or `localStorage`, and render no clock, locale-dependent text or random id; anything that differs on the first browser render breaks hydration.
2. **Write every other route as browser-only code.** Nothing below the root is prerendered, so route code needs no `ClientOnly`, `useHydrated` or `createClientOnlyFn`; browser APIs are read in Effects and handlers, as render purity requires.
3. **Set the error, not-found and pending components once, in the router factory** (`defaultErrorComponent`, `defaultNotFoundComponent`, `defaultPendingComponent`), and override one per route only where its message differs. The pending component is also what the shell shows until the bundle loads.
4. **Give each route its title through `head()`.** The deepest route's title and same-name meta tags win.
5. **Read build-time settings from `import.meta.env.VITE_*`, typed in `src/env.d.ts` and parsed once in one module.** Vite inlines the values at build, so anything that varies per deployment comes from the server at run time. Use `import.meta.env.DEV`, `PROD` or `MODE`, never `NODE_ENV` or `process.env`.
6. **Write no async component.** Async components need React Server Components, which an SPA doesn't run.
7. **Use the framework's file layout.** Pages are file routes under `src/routes/`, with the root route in `__root.tsx`; a page's own components sit beside it in a `-components/` folder, which the route generator skips (its `routeFileIgnorePrefix` defaults to `-`); `src/router.tsx` exports the router factory and `src/routeTree.gen.ts` is generated, committed and never edited. File names are kebab-case. `unicorn/filename-case` checks file names, not folders, and skips leading underscores, so `__root.tsx` passes; a route param's name is one lowercase word (`$id.tsx`), since the rule would rename `$orderId.tsx` to `$order-id.tsx`, which isn't a valid param name.
