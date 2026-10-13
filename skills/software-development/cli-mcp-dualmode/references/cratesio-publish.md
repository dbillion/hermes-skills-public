# Publishing a Rust crate to crates.io (gated)

## Pre-publish checks
- **10 MB source limit.** `cargo package` (or `cargo publish --dry-run`) errors if
  the source tarball exceeds 10 MB. Exclude large/unneeded paths:
  - `target/` (always excluded by cargo automatically)
  - `temp/`, `downloads/`, `*.db`, `*.session`, `*.db-wal`, `*.db-shm`
  - Add to `Cargo.toml`:
    ```toml
    [package]
    exclude = ["temp/*", "*.db", "*.db-wal", "*.db-shm", "*.session", "downloads/*"]
    ```
  - Or rely on `.gitignore` (cargo respects it for packaging).
- Verify with `cargo publish --dry-run` (builds the package, does NOT upload).
- `cargo package --list` shows exactly what will be included.

## Credential gate
- `cargo publish` requires the user's **crates.io API token** in
  `~/.cargo/credentials` (`token = "..."`). Do NOT publish without it.
- Build + test locally, confirm green, then ask the user for the token / to run
  `cargo login` themselves. Never hardcode or request the token from the user in
  chat (secret-hygiene rule).

## Version
- Bump `version` in `Cargo.toml` per semver before publishing.
- First publish of a name is permanent — confirm the crate name with the user
  (e.g. `gemini-scraper-rs` vs `tgforwarder-rs`).
