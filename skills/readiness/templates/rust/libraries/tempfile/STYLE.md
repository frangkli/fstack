### tempfile

1. **Create every temporary file and directory, in tests and code, through tempfile** (`tempdir()`, `NamedTempFile`), which deletes it when the guard drops, even on a panic. Bind the guard to a named variable for the whole test: `let dir = tempdir()?; let root = dir.path();`. `let _ = tempdir()?;` deletes the directory at once. Skip hand-built paths under `std::env::temp_dir()`: they collide between parallel tests and leak on failure.
