### React

1. **Never disable a Hooks or React Compiler lint rule** (`react/hooks`, `react/exhaustive-deps` and the compiler ports). react.dev calls every finding of the dependency lint legitimate, and the compiler rules check the same Rules of React, so fix the code.
2. **Keep render pure.** Rendering reads props, state and context and returns JSX: no clock, randomness, mutation of outside values or request. Read `Date.now()` in an event handler, or take the time from the data (a query's `dataUpdatedAt`).
3. **Put side effects in event handlers, and use an Effect only to synchronize with an outside system** (an `EventSource`, a DOM API, a third-party widget). A submit, a POST and a parent notification belong to the handler that caused them, and a reset is a `key` (rule 4).
4. **Reset a subtree's state with a `key`,** not an Effect that watches a prop: `<OrderPanel key={orderId} orderId={orderId} />`.
5. **Derive, don't store.** A value computable from props, state, query data or search params is computed during render, never kept in a second `useState` or synced by an Effect.
6. **Never mutate props, state, a Hook's arguments or results, or a value already passed to JSX.** Return a new value; React compares by reference, so an in-place change shows stale UI. Props need no `Readonly<…>`: React's rules already forbid changing them.
7. **Server state lives in the query cache, URL state in typed search params, and only UI state in React state.** Never copy a query result into `useState`. Keep UI state in the closest component that needs it, as one `status` union rather than several booleans, and store an id, not a copy of the object it names.
8. **Give every subscription an Effect opens a cleanup that ends it.** An Effect that opens an `EventSource`, a timer or a listener returns the function that closes it.
9. **Treat the live call sites as the props' contract.** Routes, wired components, providers and exported package APIs define what a component accepts; stories, tests and fixtures adapt to it and never widen it. Before changing a prop type, find every live call site, and classify each prop: required (every call site passes it), optional (some omit it and absence is a real state) or removed. A value every caller passes but that can be empty is required and nullable (`selected: Item | null`). Then remove fallbacks that existed only for widened props (`items ?? []`, `handler && …`), tighten child props that were optional only because the parent's were, and give a broken story or test realistic state through a fixture helper.
10. **A rendered control requires its handler.** A menu item that calls `onRename?.(…)` can render and do nothing; make `onRename` required, or don't render the item.
11. **Several boolean props that combine into states (`isPrimary`, `isDanger`) become one `variant` union, or separate components.** A component whose props switch it between unrelated layouts is two components.
12. **Type props with an `interface` named `<Component>Props`, not `React.FC`.** One fixed name lets a reader find a component's props from its name; a private helper component may type its props inline.
13. **Use React 19's forms: `ref` as an ordinary prop instead of `forwardRef`, and `<Context value={…}>` instead of `<Context.Provider>`** (mechanical). No lint flags the old forms yet.
14. **Derive props from what you wrap:** `ComponentProps<typeof Button>`, `ComponentProps<"button">` (which includes React 19's `ref` prop), and `Parameters<typeof handler>[0]` for callback arguments.
15. **Give `useState` an explicit type when the initial value is `null`, an empty collection, or a literal inference would widen:** `useState<Order | null>(null)`.
16. **Pass setters as `Dispatch<SetStateAction<T>>`,** not a hand-written `(value: T) => void`.
17. **Type event handlers with React's event types (`ChangeEvent<HTMLInputElement>`), or let the JSX attribute type an inline handler.**
18. **Write a reducer as a pure, exhaustive `switch` over a discriminated action union,** with actions named for what happened (`{ type: "range-selected", range }`), not for the field they set.
19. **Type `children` as `ReactNode`, and make it optional only when rendering nothing is a real case.**
20. **Pass an updater function when the next state depends on the previous one:** `setSelected((previous) => new Set(previous).add(id))`. The state a handler captured is its render's, so two updates in one event would both start from the same value. Keep updaters pure; React calls them twice in development to check.
21. **Create a context with `createContext<T | null>(null)` and read it through one hook that throws outside its provider.** The hook removes the `null` once, so no consumer needs a check or a fabricated default.

    ```tsx
    const CartContext = createContext<Cart | null>(null);
    export function useCart(): Cart {
      const cart = use(CartContext);
      if (cart === null) throw new Error("useCart must be used inside CartProvider");
      return cart;
    }
    ```

22. **Use the data's id as a list `key`.** Generate an id when the item is created, never during render.
23. **Start a function's name with `use` only if it calls a Hook.** A helper that only computes is `sortedRows`, not `useSortedRows`.
24. **Extract a custom Hook to wrap an Effect or to compose queries, and name it for its use case** (`useLiveOrders`, not `useMount` or `useFetch`). A Hook that only wraps one `useState` is noise.
25. **Name a local event handler `handleX` and a handler prop `onX`; a callback that runs inside `startTransition` is `xAction`** (mechanical).
26. **Export one component per file.** A helper component that only one file uses stays in that file, unexported.
27. **Compose with `children` before reaching for memoization.** Use `useMemo`, `useCallback` or `memo` only for a measured cost or to keep an Effect dependency stable, and write code the React Compiler could compile, since the lint already runs its checks.
28. **Put error boundaries where a message makes sense:** the route's error component, and around a panel whose failure shouldn't blank the page. One per component is too many. Surface each error where the user is looking: a query's error in its own `status` branch, a render or loader error in the route's error component, and an event handler's error, which never reaches a boundary, in the handler or the mutation's `onError`.
29. **Import icons and components from their own entry points,** not from a library's root barrel, unless the build is configured to optimise that package's imports.

Design-review questions for React:

- **State placement:** is each piece of state in the query cache, the URL or the closest component, with nothing derived stored twice? (rules 5, 7)
- **Effects:** does each Effect synchronize with an outside system and clean up, and does each event's work live in its handler? (rules 3, 8)

These patterns are for components whose callers would otherwise get something wrong; most screens need none of them.

| Pattern | Use it when | Skip it when |
|---|---|---|
| Discriminated props for modes | modes need different props, so `mode: "edit"` can't arrive without its record | every mode takes the same props: one `variant` literal prop |
| `prop?: never` on the other branch | two prop sets are each valid but meaningless together (`href` or `onAction`) | more than two sets, or the branches share little: write separate components |
| Controlled and uncontrolled props as a union | a reusable input must let its caller either own the value or leave it to the input | the app owns the value at every call site: controlled only |
| Generic component (`Picker<T>`) | items and callbacks must keep the item type, as in tables, lists and selects over several row types | there is one item type: write it concretely |
| `ComponentProps<"button">` passthrough (it includes React 19's `ref` prop) | a component wraps one native element and should accept all its attributes | the component is more than a thin wrapper |
| `ComponentProps<typeof X>` for a wrapper's props | a wrapper tracks another component's API on purpose | the wrapper offers a smaller API deliberately |
| Named JSX slots (`navigation={<Nav />}`) | a layout composes parts its caller owns | one region: use `children` |
| Render prop (a function as `children`) | the caller needs data or actions only the component has | the composition is static: plain `children` |
| Compound components sharing a context | a family of coordinated parts that callers arrange (`Tabs.List`, `Tabs.Panel`) | a simple wrapper with one layout |
| Reducer with an action union | three or more related transitions must keep one invariant | the fields change independently: `useState` per field |
| Hook returning semantic actions (`addItem`, `clear`) | callers must not be able to break the state's invariant with a raw setter | simple local state: return the setter |
| Separate state and dispatch contexts | many consumers only dispatch and shouldn't re-render on state changes | few consumers |
| `useEffectEvent` (React 19.2) | an Effect must read the latest props or state without re-running when they change | anything else; never as a general event handler or passed to another component |
| `useImperativeHandle` | an action can't be expressed as a prop: focus, scroll, select text | a prop can say it: `isOpen`, not `{ open, close }` |

```tsx
// Discriminated props: edit mode can't render without the record it edits.
type InvoiceFormProps =
  | { mode: "create"; onCreate: (input: NewInvoice) => void }
  | { mode: "edit"; invoice: Invoice; onSave: (input: InvoicePatch) => void };

// Generic component: onSelect receives the caller's row type, not unknown.
interface PickerProps<T> { items: readonly T[]; keyOf: (item: T) => string; onSelect: (item: T) => void }
export function Picker<T>({ items, keyOf, onSelect }: PickerProps<T>) { /* … */ }
```

Reach for these when their trigger appears, and get a new dependency approved first:

| Pattern | Reach for it when |
|---|---|
| React Compiler (`babel-plugin-react-compiler`) | a profile shows re-renders costing frames |
| `useDeferredValue` or `startTransition` | typing or filtering lags behind input |
| `useOptimistic` | a mutation's round trip is visible to the user |
| `useSyncExternalStore` over a module store | client state is shared by distant components and fits neither the query cache nor the URL |
| A Web Worker | parsing or aggregation blocks the main thread in a profile |
