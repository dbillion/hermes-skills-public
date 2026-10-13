# Quasar App Extensions Guide

## Architecture
App Extensions (AE) are the primary way to share reusable code.
- **AE Kit**: Logic only (no components).
- **UI Kit**: Components + Directives + Dev App.

## Core Files
- `index.js`: Modifies the Quasar configuration.
- `install.js`: Runs during `quasar ext add`.
- `prompts.js`: Asks user questions during installation.
- `uninstall.js`: Cleanup logic.

## Development Workflow
1. Create extension directory.
2. Run `npm link` in the extension folder.
3. In your Quasar app, run `quasar ext add [my-ext-name]`.
4. Use `api.compatibleWith()` to ensure version safety.
