// =============================================================================
// CRMHub Stimulus Controller Template
// =============================================================================
// Copy this file as a starting point for any new Stimulus controller.
// Follow the conventions below — they are enforced by code review.
//
// Naming: snake_case in filename (e.g., status_badge_controller.js),
//         PascalCase → camelCase for the class (imported automatically by
//         @hotwired/stimulus via the stimulus-rails autoload path).
//
// Registration: stimulus-rails auto-registers controllers in
//   app/javascript/controllers/ — no manual registration needed.
//
// Convention:
//   1. Import Controller from @hotwired/stimulus
//   2. Declare static targets = [...] for DOM element references
//   3. Declare static values = { ... } for typed configuration
//   4. Implement connect() for initialization
//   5. Implement disconnect() for cleanup (CRITICAL — avoid memory leaks)
//   6. Use this.{name}Target (singular) or this.{name}Targets (plural)
//   7. Use this.{name}Value for reading config, this.{name}Value = x to set
//   8. Bind event handlers in HTML: data-action="event->controller#method"
// =============================================================================

import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  // ===========================================================================
  // Static declarations — these define the controller's API
  // ===========================================================================

  // DOM element references. Access via:
  //   this.exampleTarget      — single element (throws if missing)
  //   this.exampleTargets     — array of elements
  //   this.hasExampleTarget   — boolean check
  static targets = [
    "container",   // Wrapping element for this controller's scope
    "output",      // Element where results are rendered
    "trigger",     // Element that triggers actions (button, link)
    "input"        // Input element for user data
  ]

  // Typed configuration values. Access via:
  //   this.urlValue            — read the value (auto-cast to declared type)
  //   this.urlValue = "..."    — set the value (triggers {name}ValueChanged callback)
  //   this.hasUrlValue         — boolean check
  // Declared types: String, Number, Boolean, Object, Array
  static values = {
    url: String,                                    // data-{controller}-url-value="/api/endpoint"
    interval: { type: Number, default: 0 },         // data-{controller}-interval-value="30"
    active: { type: Boolean, default: false },       // data-{controller}-active-value="true"
    options: { type: Object, default: {} },           // data-{controller}-options-value='{"key":"val"}'
    items: { type: Array, default: [] }               // data-{controller}-items-value='[1,2,3]'
  }

  // ===========================================================================
  // Lifecycle callbacks
  // ===========================================================================

  /**
   * Called when the controller is connected to the DOM.
   * Use for: initialization, adding global listeners, starting intervals,
   * fetching initial data.
   *
   * IMPORTANT: Turbo Drive and Turbo Frames can connect/disconnect controllers
   * multiple times during a session. Always make connect() idempotent and
   * ensure disconnect() fully cleans up.
   */
  connect() {
    // Store bound references for cleanup in disconnect()
    this.boundHandleKeydown = this.handleKeydown.bind(this)
    this.boundHandleResize = this.handleResize.bind(this)

    // Add document-level listeners (must be removed in disconnect)
    document.addEventListener("keydown", this.boundHandleKeydown)
    window.addEventListener("resize", this.boundHandleResize)

    // Start interval if configured
    if (this.intervalValue > 0) {
      this.timer = setInterval(() => this.refresh(), this.intervalValue * 1000)
    }

    // Dispatch a custom event to notify other controllers
    this.dispatch("connected", { detail: { element: this.element } })

    // Fetch initial data if URL is provided
    if (this.hasUrlValue && this.urlValue) {
      this.refresh()
    }
  }

  /**
   * Called when the controller is disconnected from the DOM.
   * Use for: removing listeners, clearing intervals/timers, nullifying
   * references, canceling animations.
   *
   * CRITICAL: Failing to clean up causes memory leaks and zombie listeners
   * that fire after the element is gone.
   */
  disconnect() {
    // Remove document-level listeners
    document.removeEventListener("keydown", this.boundHandleKeydown)
    window.removeEventListener("resize", this.boundHandleResize)

    // Clear intervals and timers
    if (this.timer) clearInterval(this.timer)
    if (this.rafId) cancelAnimationFrame(this.rafId)
    if (this.debounceTimer) clearTimeout(this.debounceTimer)

    // Nullify large references to help GC
    this.boundHandleKeydown = null
    this.boundHandleResize = null
  }

  // ===========================================================================
  // Value change callbacks (auto-called when a static value changes)
  // ===========================================================================

  /**
   * Called when `activeValue` changes (via this.activeValue = true or
   * data attribute mutation).
   * Use for: responding to state changes declaratively.
   */
  activeValueChanged(value, previousValue) {
    this.element.classList.toggle("active", value)
    if (this.hasTriggerTarget) {
      this.triggerTarget.setAttribute("aria-expanded", value.toString())
    }
    this.dispatch("toggle", { detail: { active: value } })
  }

  // ===========================================================================
  // Action methods — called via data-action="event->controller#method"
  // ===========================================================================

  /**
   * Primary action. Example usage:
   *   <button data-action="click->template#toggle">Toggle</button>
   */
  toggle(event) {
    event?.preventDefault()
    this.activeValue = !this.activeValue
  }

  /**
   * Refresh data from the server. Example usage:
   *   <button data-action="click->template#refresh">Refresh</button>
   * Or called automatically by the interval timer.
   */
  async refresh() {
    if (!this.hasUrlValue) return

    try {
      const response = await fetch(this.urlValue, {
        headers: {
          "Accept": "application/json",
          "X-CSRF-Token": document.querySelector('meta[name="csrf-token"]')?.content
        }
      })

      if (!response.ok) throw new Error(`HTTP ${response.status}`)

      const data = await response.json()
      this.render(data)
    } catch (error) {
      console.error(`[${this.identifier}] Refresh failed:`, error)
      this.dispatch("error", { detail: { error } })
    }
  }

  /**
   * Render data to the DOM. Override this in subclasses.
   */
  render(data) {
    if (this.hasOutputTarget) {
      this.outputTarget.innerHTML = this.formatData(data)
    }
  }

  // ===========================================================================
  // Private helper methods (not called from HTML, only internally)
  // ===========================================================================

  /**
   * Debounce a function call. Useful for input handlers.
   *   this.debounce(() => this.search(), 300)
   */
  debounce(callback, delay = 300) {
    clearTimeout(this.debounceTimer)
    this.debounceTimer = setTimeout(callback, delay)
  }

  /**
   * Dispatch a custom event on the controller element.
   * Other Stimulus controllers can listen via:
   *   data-action="template:toggle@window->other#handleToggle"
   */
  dispatch(eventName, { detail = {}, prefix = this.identifier } = {}) {
    const namespacedEvent = prefix ? `${prefix}:${eventName}` : eventName
    this.element.dispatchEvent(
      new CustomEvent(namespacedEvent, {
        bubbles: true,
        cancelable: true,
        detail
      })
    )
  }

  /**
   * Check if a target exists before accessing it.
   * Use this.has{Name}Target before this.{name}Target to avoid errors.
   */
  hasElement(targetName) {
    return this[`has${this.capitalize(targetName)}Target`]
  }

  capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1)
  }

  // ===========================================================================
  // Event handlers (bound in connect(), removed in disconnect())
  // ===========================================================================

  handleKeydown(event) {
    // Example: Close on Escape
    if (event.key === "Escape" && this.activeValue) {
      event.preventDefault()
      this.activeValue = false
    }
  }

  handleResize() {
    // Re-render on viewport resize (e.g., canvas charts)
    if (this.rafId) cancelAnimationFrame(this.rafId)
    this.rafId = requestAnimationFrame(() => this.refresh())
  }

  // ===========================================================================
  // Format helpers
  // ===========================================================================

  formatData(data) {
    // Override in subclass to format API response as HTML
    return JSON.stringify(data, null, 2)
  }
}

// =============================================================================
// HTML USAGE EXAMPLE
// =============================================================================
//
// <div data-controller="template"
//      data-template-url-value="/api/stats"
//      data-template-interval-value="30"
//      data-template-active-value="false"
//      data-template-options-value='{"format":"currency"}'>
//
//   <button data-action="click->template#toggle"
//           data-template-target="trigger"
//           class="rounded-xl px-4 py-2 bg-teal-600 text-white">
//     Toggle
//   </button>
//
//   <button data-action="click->template#refresh"
//           class="rounded-xl px-4 py-2 border border-zinc-300">
//     Refresh
//   </button>
//
//   <div data-template-target="output"
//        class="rounded-xl border border-zinc-200 p-4 mt-4">
//     <!-- Rendered output goes here -->
//   </div>
//
// </div>
//
// =============================================================================
// INTER-CONTROLLER COMMUNICATION
// =============================================================================
//
// Controller A dispatches:  this.dispatch("selected", { detail: { id: 42 } })
// Controller B listens:     data-action="template:selected@window->receiver#handleSelect"
//
// <div data-controller="receiver"
//      data-action="template:selected@window->receiver#handleSelect">
// </div>
//
// =============================================================================
// TURBO INTEGRATION
// =============================================================================
//
// When Turbo Drive swaps content, controllers are disconnected and reconnected.
// Use data-turbo-permanent to preserve a controller's element across navigation:
//
//   <div data-controller="audio-player" data-turbo-permanent id="player">
//   </div>
//
// The connect() will NOT fire again because the element is preserved.
// Use data-turbo-before-render event to handle state transfer if needed.
// =============================================================================
