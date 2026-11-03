### shadcn/ui

When the repo uses shadcn/ui (`components.json` exists), `@shadcn/lint` rejects restyling a component through `className` beyond its contract, raw palette colours, arbitrary values, inline styles, classes Tailwind can't generate and class strings it can't read statically. Its config is the `oxlintrc.json` fragment beside this file.
