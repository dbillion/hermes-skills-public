---
name: chrome-devtools
description: Professional browser automation and inspection using the Chrome DevTools Protocol (CDP). Use for advanced web interactions including file uploads, downloads, network monitoring, and recording complex workflows that require a live Chrome instance.
---

# Chrome DevTools Automation

This skill provides procedural guidance for using the `chrome-devtools` MCP server to automate complex browser tasks.

## Core Workflows

### 1. Navigating and Recording
Always start by navigating to the target URL and verifying the page state.
- **Tool**: `navigate`
- **Verification**: Use `capture_screenshot` or `get_html` after navigation to ensure the page has loaded correctly.

### 2. Complex Interactions (Clicks & Input)
- Use `click_element` for standard buttons.
- For dynamic or hidden elements, use `evaluate_javascript` to trigger events or inspect element visibility.
- **Recording**: When asked to "record," manually perform steps and document the exact selectors (ID, Class, XPath) used at each step.

### 3. File Uploads
To upload a file (e.g., a PDF for transformation):
1. Locate the file input element (usually `<input type="file">`).
2. Use `upload_file` (if available in the MCP) or `evaluate_javascript` to set the input value.
3. Note: Ensure the file path is absolute and accessible to the browser.

### 4. Handling Downloads
1. Before triggering a download, ensure the download directory is set or monitored.
2. After clicking the "Download" button, use `list_network_requests` to verify the download started or wait for the file to appear in the expected directory using filesystem tools.

### 5. Troubleshooting
- **Flaky Elements**: Use `wait_for_selector` or a small delay before interacting.
- **Console Errors**: Use `get_console_logs` to diagnose site-side issues.
- **Network Issues**: Use `list_network_requests` to check if API calls are failing.

## Best Practices
- **Prefer Selectors**: Use robust ID selectors over fragile text-based or positional selectors.
- **State Management**: Always check for "Loading" overlays or spinners before proceeding to the next action.
- **Context Efficiency**: Capture only the necessary part of the page with `capture_screenshot` when possible.
