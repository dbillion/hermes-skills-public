# npx wrapper + cross-platform GitHub release (pattern that worked)

Use when shipping a Rust binary "easy for AI to call": an `npx <name>` package that downloads the
right prebuilt binary per platform, plus a GitHub Actions workflow that builds for linux/mac/windows
× x86_64/aarch64, publishes the binaries to a GitHub Release, and runs `cargo publish` + `npm publish`.

## npx wrapper layout (`npm/` in the repo)
- `npm/package.json`: `{ "name": "<name>", "bin": { "<name>": "./bin.js" }, "files": ["bin.js"], "engines": { "node": ">=18" } }`.
  Keep `version` in lockstep with the crate version (the wrapper hardcodes it to pick the release tag).
- `npm/bin.js`: a tiny Node script that maps `process.platform`/`process.arch` -> a rust target triple,
  downloads `https://github.com/<owner>/<repo>/releases/download/v<VERSION>/<bin>-<target>.tar.gz`,
  extracts the single binary (a ~30-line ustar walker over `zlib.gunzipSync`), caches it in
  `~/.cache/<name>/`, `chmod 755`, then `execFileSync(bin, process.argv.slice(2), { stdio: 'inherit' })`.
  AI-agent registration: `{ "mcpServers": { "<name>": { "command": "npx", "args": ["<name>", "serve-mcp"] } } }`.

### platform -> rust target triple map
- linux/x64 -> `x86_64-unknown-linux-gnu`
- linux/arm64 -> `aarch64-unknown-linux-gnu`
- darwin/x64 -> `x86_64-apple-darwin`
- darwin/arm64 -> `aarch64-apple-darwin`
- win32/x64 -> `x86_64-pc-windows-msvc`

## Release asset naming (wrapper and workflow MUST agree)
`<bin>-<target>.tar.gz` containing the binary `<bin>` (or `.exe` on windows).
Tag the release `v0.1.0` so the wrapper's `VERSION` matches.

## GitHub Actions (`release.yml`) — matrix
Triggers on `push: tags: ['v*']`.
- Matrix over targets; `aarch64-unknown-linux-gnu` uses `cross` (`cargo install cross --locked`, then
  `cross build --release --target <t>`); all others use native `cargo build --release --target <t>`.
- Package: unix `tar czf`; windows `7z a ... .tar.gz <bin>.exe` (7z is on windows runners).
- Upload each asset via `actions/upload-artifact@v4` (merge-multiple), then a `release` job
  `softprops/action-gh-release@v2` with `files: artifacts/*.tar.gz`.
- `publish-crate` job: `cargo publish --token ${{ secrets.CARGO_REGISTRY_TOKEN }}` (needs repo secret).
- `publish-npm` job: `npm publish --access public` from `npm/` with `NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}`.

## Secrets the user MUST set in the repo (publish jobs fail without them)
- `CARGO_REGISTRY_TOKEN` — crates.io token (from crates.io/settings/tokens). NOT committed.
- `NPM_TOKEN` — npm automation token (from npmjs.com/settings/tokens).
The cross-platform build + GitHub Release succeed without these; only the publish jobs need them.

## Gotchas observed
- `cargo login --token <x>` is NOT valid syntax; use `CARGO_REGISTRY_TOKEN` env or `~/.cargo/credentials`.
- If the token was never persisted (no `~/.cargo/credentials`, no env var), `cargo publish` errors
  `no token found` — don't guess the token; ask the user to set the secret or run `cargo login`.
- The wrapper's `download()` must follow 301/302 redirects (GitHub release URLs redirect to
  objects.githubusercontent.com / S3) or the fetch 200s-but-empty.
