### proptest

The general rules for property tests are in the root `TESTING.md`; these are proptest's forms.

1. **Use proptest for property tests:** a hand-written parser never panics on arbitrary input, `decode(encode(x)) == x`, an invariant holds for any input. Declare it with `default-features = false, features = ["std"]` to roughly halve the crates it pulls. Skip quickcheck (weaker shrinking, no regex strategies) and bolero (pays off only with its fuzz engines).

   ```rust
   proptest! {
       #[test]
       fn parser_never_panics(text in any::<String>()) {
           let _ = parse_header(&text);
       }
   }
   ```
