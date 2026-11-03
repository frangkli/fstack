### faker

1. **Seed faker (`faker.seed(n)`) when a test reads generated values,** so a failure reproduces.
2. **Pass explicit values for fields with schema constraints.** A generator can draw values the schema rejects, as Orval's mocks do for enums.
