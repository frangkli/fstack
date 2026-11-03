### Zod

1. **Brand a hand-written schema's output with `.brand<"X">()` in the same step,** so parsing and branding are one constructor.
2. **Parse before storing or sending a value whose extra keys matter.** `z.object` strips unknown keys, while a value typed by an interface may carry extras.
3. **Parse a numeric string with a string regex followed by a transform** (`z.string().regex(/^-?\d+$/).transform(Number)`): `Number("")` is 0, so the regex rejects blank input first.
