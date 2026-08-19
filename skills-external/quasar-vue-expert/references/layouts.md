# Quasar Layouts & Gallery

## Layout Builder
The [Layout Builder](https://quasar.dev/layout-builder) allows you to visually configure your application's shell.
- **Top Bar (Header)**: Sticky or fixed.
- **Side Drawer**: Left or right side, overlay or persistent.
- **Footer**: Optional bottom navigation.
- **View Selection**: Configure the `view` property (e.g., `lHh Lpr lFf`) which determines how components overlap.

## Layout Gallery
Common patterns from the [Layout Gallery](https://quasar.dev/layout/gallery):
- **Youtube**: Focused on sidebar and video content.
- **Google Play**: Centered layout with tabs.
- **Quasar Framework**: The documentation's own layout (sidebar + secondary sidebar).

## Best Practices
- **MainLayout.vue**: Keep this file as a shell. Move specific page content into `src/pages`.
- **Breakpoints**: Use `$q.screen` to make layouts responsive programmatically or `gt-sm`, `lt-md` classes in templates.
