# React

Read when the code is React. This covers typing component contracts; rendering and bundle performance belong to the repo's React performance skill or docs when it has one.

## Props are the live call sites' contract

The app's real call sites (routes, wired components, providers, hooks, exported package APIs) define what a component accepts. Stories, tests, fixtures and demos adapt to that contract; they never widen it.

1. Before changing a prop type, find every live call site; use stories and tests only as supporting evidence.
2. Classify each prop. **Required:** every live call site passes it. **Optional:** some live call site omits it and that absence is a real state. **Removed:** no live call site uses it.
3. If every caller passes a value that can be empty, make it required and nullable (`selected: Item | null`), not optional.
4. A rendered control requires its handler. A menu item that calls `onRename?.(…)` can render and do nothing; make `onRename` required, or don't render the item.
5. Remove fallbacks that existed only for widened props (`items ?? []`, `count ?? 0`, `handler && …`) once the props are required.
6. Tighten the props of child components that received optional values only because the parent's were optional.
7. When a story or test breaks, give it realistic state and handlers through a fixture helper in support code.

## Variants over booleans

Several boolean props that combine into states (`isPrimary`, `isDanger`, `isGhost`) become one discriminated `variant` prop or separate components. A component whose props switch it between unrelated layouts is two components.

## Typing

- Props are a plain `interface` on a function component. No `React.FC`.
- React 19: `ref` is an ordinary prop; no `forwardRef`.
- Derive props from what you wrap: `ComponentProps<typeof Button>`, `ComponentProps<"button">` (which includes React 19's `ref` prop), and `Parameters<typeof handler>[0]` for callback arguments.
- `useState<T>()` with an explicit type when the initial value is `null`, an empty collection, or a literal that inference would widen.
- Pass setters as `Dispatch<SetStateAction<T>>`, not a hand-written `(value: T) => void`.
- Reducer actions are a discriminated union, handled by an exhaustive `switch`.
- Event handlers use React's event types (`ChangeEvent<HTMLInputElement>`), or let the JSX attribute type the inline handler.

## Patterns

These are for components whose callers would otherwise get something wrong; most screens need none of them.

| Pattern | Use it when | Skip it when |
|---|---|---|
| Discriminated props for modes | modes need different props, so `mode: "edit"` can't arrive without its record | every mode takes the same props: one `variant` literal prop |
| `prop?: never` on the other branch | two prop sets are each valid but meaningless together (`href` or `onAction`) | more than two sets, or the branches share little: write separate components |
| Controlled and uncontrolled props as a union | a reusable input must let its caller either own the value or leave it to the input | the app owns the value at every call site: controlled only |
| Generic component (`Picker<T>`) | items and callbacks must keep the item type, as in tables, lists and selects over several row types | there is one item type: write it concretely |
| `ComponentProps<"button">` passthrough (React 19, where `ref` is a prop) | a component wraps one native element and should accept all its attributes | the component is more than a thin wrapper |
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
interface PickerProps<T> {
  items: readonly T[];
  keyOf: (item: T) => string;
  onSelect: (item: T) => void;
}
export function Picker<T>({ items, keyOf, onSelect }: PickerProps<T>) { /* … */ }
```

## Imports

Import icons and components from their own entry points, not from a library's root barrel, unless the build is configured to optimise that package's imports.
