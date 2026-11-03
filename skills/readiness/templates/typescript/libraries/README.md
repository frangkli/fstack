## Libraries

How to choose a package, then one section per library the repo uses. The general rules are common Dependencies 1–5.

1. **Check, in order: the platform (the `lib` and runtime the repo targets, Platform features), a package already in the lockfile, then the candidate's maintenance, advisories, licence and install cost.** A dependency the task didn't ask for is the owner's decision: propose it in the handoff with the check it passes.
2. **Use a schema library that implements Standard Schema,** and infer types from its schemas. A repo without one gets a proposal in the handoff once a change needs several boundary parsers, not a dependency for one guard.
3. **Import a library through its public entry points** (its `package.json` `exports`), and import icons and components from their own entry points rather than a root barrel, unless the build optimises that package's imports.
4. **Pin exact versions in the workspace catalog or `package.json`, and keep the pnpm guards on** (`pnpm-workspace.yaml`).

| Job | Default pick | Section |
|---|---|---|
| UI | React 19 | react |
| Server state | TanStack Query | tanstack-query |
| Routing | TanStack Router | tanstack-router |
| App framework (SPA) | TanStack Start in SPA mode | tanstack-start |
| API client from OpenAPI | Orval (fetch client, Query hooks, Zod schemas, MSW mocks) | orval |
| Schemas | Zod 4 | zod |
| Effect systems | Effect 4, only where a package already uses it | effect |
| Test runner | Vitest | vitest |
| Network fakes | MSW | msw |
| Component queries | Testing Library | testing-library |
| DOM environment | happy-dom | happy-dom |
| Generated test data | faker | faker |
| Unused exports, files and dependencies | knip | knip |
| Design-system lint | `@shadcn/lint`, only with shadcn/ui | shadcn |
| Lint and type-aware lint | Oxlint with tsgolint (config in `oxlintrc.json`) | — |
| Property tests | fast-check | — |
