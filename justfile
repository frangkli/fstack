# Each sample under tests/readiness-templates/ runs in a scratch copy with readiness's template configs.

# Check that readiness's templates run
templates: templates-rust templates-typescript

templates-rust:
    bash tests/readiness-templates/rust/check.sh

templates-typescript:
    bash tests/readiness-templates/typescript/check.sh
