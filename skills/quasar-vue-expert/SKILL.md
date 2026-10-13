---
name: quasar-vue-expert
description: Expert guide for building high-fidelity, high-performance Quasar Vue 3 applications. Covers best practices, CLI setup, theme/layout building, app extensions, and modern 2026 architectural patterns.
---

# Quasar Vue Expert

This skill provides a structured workflow and expert guidance for developing production-ready applications with the Quasar Framework (Vue 3).

## Core Philosophy (2026 Standards)
- **Architect with Intent**: Move beyond "vibe coding." Plan layouts and features before implementation.
- **Performance First**: Prioritize `shallowRef` for large data, Composition API, and preparations for Vapor Mode.
- **Modular Excellence**: Use Boot Files for initialization and App Extensions for reusable logic.

## 1. Project Initialization & CLI
Use the Quasar CLI (Vite-based) for the best developer experience.
- **Template**: `npm init quasar` (Select Vue 3, Vite, Composition API, Script Setup).
- **Organization**: Adopt Domain-Driven Design (DDD). Group by feature (e.g., `src/features/Auth`) rather than technical type.

## 2. Layout & Theme Building
- **Layout Builder**: Use the [Quasar Layout Builder](https://quasar.dev/layout-builder) to generate the `MainLayout.vue` structure (Header, Footer, Drawer).
- **Theme Builder**: Define brand colors in `src/css/quasar.variables.scss` or via the [Theme Builder](https://quasar.dev/style/theme-builder).
- **Modernization**: For Material Design 3, consider integrating **UnoCSS** or custom SCSS overrides to move beyond MD2 defaults.

## 3. Application Initialization (Boot Files)
Never clutter `main.js`. Use `src/boot/`.
- **Pattern**: Export initialization logic (Axios, i18n, guards) from boot files.
- **Example**: `export default boot(({ app, router, store }) => { ... })`.

## 4. State & Reactivity
- **Global State**: Use **Pinia 3**.
- **Local State**: Use shared composables for branch-level state.
- **Optimization**: Use `shallowRef()` for large, immutable datasets (e.g., API results) to save memory and CPU.

## 5. Extensions & Plugins
- **App Extensions**: Use the **AE Kit** for logic-only and **UI Kit** for component-based extensions.
- **Core Scripts**: Implement `prompts.js` (user input), `install.js` (templates), and `index.js` (config modification).

## 6. Best Practice Examples
- **Component Pattern**:
  ```vue
  <script setup>
  import { ref, shallowRef, onMounted } from 'vue'
  import { useQuasar } from 'quasar'

  const $q = useQuasar()
  const data = shallowRef([]) // Optimization for large data

  onMounted(async () => {
    // Fetch and set data
  })
  </script>
  ```

## Resources
- **CLI Reference**: See [cli-commands.md](references/cli-commands.md)
- **Layout Gallery**: See [layouts.md](references/layouts.md)
- **Extension Guide**: See [app-extensions.md](references/app-extensions.md)
