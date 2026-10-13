# Stimulus Controller Templates for CRMHub

> 10 production-ready controllers: appearance, magnetic, password-toggle, count-up, modal, tabs, calendar, chart, search, filter
> All follow the same conventions: `data-controller`, `static targets`, `static values`, `data-action`

---

## Convention Checklist

Every controller must:
1. Import `Controller` from `@hotwired/stimulus`
2. Declare `static targets = [...]` for referenced elements
3. Declare `static values = { ... }` for typed configuration
4. Implement `connect()` for initialization
5. Implement `disconnect()` for cleanup (clear intervals, remove listeners)
6. Use `this.{target}Target` / `this.{target}Targets` to access elements
7. Use `this.{value}Value` to read configuration
8. Bind event handlers via `data-action="event->controller#method"` in HTML

---

## 1. Appearance Controller (Dark/Light Mode Toggle)

Toggles between light and dark themes, persists choice in localStorage, and applies `dark` class to `<html>`.

```javascript
// app/javascript/controllers/appearance_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["icon", "label"]
  static values = {
    theme: { type: String, default: "light" },
    persist: { type: Boolean, default: true }
  }

  connect() {
    if (this.persistValue) {
      const saved = localStorage.getItem("crmhub-theme")
      if (saved) { this.themeValue = saved; return }
    }
    // Fall back to system preference
    if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
      this.themeValue = "dark"
    }
    this.applyTheme()
  }

  toggle() {
    this.themeValue = this.themeValue === "dark" ? "light" : "dark"
  }

  themeValueChanged() {
    this.applyTheme()
  }

  applyTheme() {
    const isDark = this.themeValue === "dark"
    document.documentElement.classList.toggle("dark", isDark)

    if (this.hasIconTarget) {
      this.iconTarget.textContent = isDark ? "☀️" : "🌙"
    }
    if (this.hasLabelTarget) {
      this.labelTarget.textContent = isDark ? "Light Mode" : "Dark Mode"
    }

    if (this.persistValue) {
      localStorage.setItem("crmhub-theme", this.themeValue)
    }
  }
}
```

**HTML:**
```html
<div data-controller="appearance"
     data-appearance-theme-value="light"
     data-appearance-persist-value="true">
  <button data-action="click->appearance#toggle"
          class="rounded-xl p-2 hover:bg-zinc-100 dark:hover:bg-zinc-800">
    <span data-appearance-target="icon">🌙</span>
    <span data-appearance-target="label" class="sr-only">Dark Mode</span>
  </button>
</div>
```

---

## 2. Magnetic Controller (Button Hover Effect)

Makes an element subtly follow the cursor on hover, creating a "magnetic" pull effect. Returns to original position on mouse leave.

```javascript
// app/javascript/controllers/magnetic_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static values = {
    strength: { type: Number, default: 0.3 },
    resetDelay: { type: Number, default: 200 }
  }

  connect() {
    this.boundMove = this.move.bind(this)
    this.boundReset = this.reset.bind(this)
    this.element.addEventListener("mousemove", this.boundMove)
    this.element.addEventListener("mouseleave", this.boundReset)
  }

  move(event) {
    const rect = this.element.getBoundingClientRect()
    const x = event.clientX - rect.left - rect.width / 2
    const y = event.clientY - rect.top - rect.height / 2
    this.element.style.transform =
      `translate(${x * this.strengthValue}px, ${y * this.strengthValue}px)`
  }

  reset() {
    this.element.style.transition = `transform ${this.resetDelayValue}ms ease-out`
    this.element.style.transform = ""
    setTimeout(() => { this.element.style.transition = "" }, this.resetDelayValue)
  }

  disconnect() {
    this.element.removeEventListener("mousemove", this.boundMove)
    this.element.removeEventListener("mouseleave", this.boundReset)
    this.element.style.transform = ""
    this.element.style.transition = ""
  }
}
```

**HTML:**
```html
<%= button_to "Book Appointment", new_appointment_path,
      data: {
        controller: "magnetic",
        magnetic_strength_value: "0.25"
      },
      class: "rounded-xl bg-teal-600 px-6 py-3 text-white transition-transform" %>
```

---

## 3. Password Toggle Controller (Show/Hide Password)

Toggles an input between `password` and `text` types, updating an icon.

```javascript
// app/javascript/controllers/password_toggle_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["input", "icon"]
  static values = { visible: { type: Boolean, default: false } }

  toggle() {
    this.visibleValue = !this.visibleValue
  }

  visibleValueChanged() {
    this.inputTarget.type = this.visibleValue ? "text" : "password"
    if (this.hasIconTarget) {
      this.iconTarget.textContent = this.visibleValue ? "🙈" : "👁️"
    }
  }
}
```

**HTML:**
```html
<div data-controller="password-toggle" class="relative">
  <%= f.password_field :password,
        data: { password_toggle_target: "input" },
        class: "w-full rounded-xl border border-zinc-300 px-4 py-2 pr-10" %>
  <button type="button"
          data-action="click->password-toggle#toggle"
          class="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-400">
    <span data-password-toggle-target="icon">👁️</span>
  </button>
</div>
```

---

## 4. Count-Up Controller (Animated Number Display)

Animates a number from 0 to a target value over a duration. Useful for dashboard stats.

```javascript
// app/javascript/controllers/count_up_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static values = {
    target: Number,
    duration: { type: Number, default: 1500 },
    decimals: { type: Number, default: 0 },
    prefix: { type: String, default: "" },
    suffix: { type: String, default: "" }
  }

  connect() {
    this.startTime = null
    this.animate()
  }

  animate() {
    const step = (timestamp) => {
      if (!this.startTime) this.startTime = timestamp
      const progress = Math.min((timestamp - this.startTime) / this.durationValue, 1)
      const eased = 1 - Math.pow(1 - progress, 3) // ease-out cubic
      const current = eased * this.targetValue
      this.element.textContent =
        this.prefixValue +
        current.toLocaleString(undefined, {
          minimumFractionDigits: this.decimalsValue,
          maximumFractionDigits: this.decimalsValue
        }) +
        this.suffixValue
      if (progress < 1) {
        this.rafId = requestAnimationFrame(step)
      }
    }
    this.rafId = requestAnimationFrame(step)
  }

  disconnect() {
    if (this.rafId) cancelAnimationFrame(this.rafId)
  }
}
```

**HTML:**
```html
<div class="rounded-xl border border-zinc-200 p-6 text-center">
  <p class="text-sm text-zinc-500">Total Revenue</p>
  <p class="text-3xl font-bold text-teal-600"
     data-controller="count-up"
     data-count-up-target-value="<%= @total_revenue %>"
     data-count-up-duration-value="2000"
     data-count-up-prefix-value="$"
     data-count-up-decimals-value="2">
    $0.00
  </p>
</div>
```

---

## 5. Modal Controller (Dialog Show/Hide)

Manages a modal dialog: open via link/button, close on backdrop click or Escape key, trap focus inside the modal.

```javascript
// app/javascript/controllers/modal_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["dialog", "backdrop"]
  static values = {
    open: { type: Boolean, default: false },
    closeOnBackdrop: { type: Boolean, default: true }
  }

  connect() {
    this.boundKeydown = this.keydown.bind(this)
    document.addEventListener("keydown", this.boundKeydown)
    if (this.openValue) this.show()
  }

  show() {
    this.openValue = true
    this.dialogTarget.classList.remove("hidden")
    if (this.hasBackdropTarget) {
      this.backdropTarget.classList.remove("hidden")
    }
    document.body.style.overflow = "hidden"
    this.focusFirst()
  }

  hide() {
    this.openValue = false
    this.dialogTarget.classList.add("hidden")
    if (this.hasBackdropTarget) {
      this.backdropTarget.classList.add("hidden")
    }
    document.body.style.overflow = ""
    // Clear the modal frame content so next open is fresh
    if (this.element.tagName === "TURBO-FRAME") {
      this.element.innerHTML = ""
    }
  }

  backdropClick(event) {
    if (this.closeOnBackdropValue && event.target === this.backdropTarget) {
      this.hide()
    }
  }

  keydown(event) {
    if (event.key === "Escape" && this.openValue) {
      event.preventDefault()
      this.hide()
    }
  }

  focusFirst() {
    const focusable = this.dialogTarget.querySelector(
      "input, select, textarea, button, [tabindex]:not([tabindex='-1'])"
    )
    if (focusable) focusable.focus()
  }

  disconnect() {
    document.removeEventListener("keydown", this.boundKeydown)
    document.body.style.overflow = ""
  }
}
```

**HTML (Layout):**
```html
<!-- Permanent modal frame in the layout, survives navigation -->
<%= turbo_frame_tag "modal",
      data: {
        controller: "modal",
        turbo_permanent: true,
        modal_close_on_backdrop_value: true
      } do %>
<% end %>
```

**Link that opens the modal:**
```html
<%= link_to "New Client", new_client_path,
      data: { turbo_frame: "modal" },
      class: "rounded-xl bg-teal-600 px-4 py-2 text-white" %>
```

**Modal content (rendered into the frame):**
```html
<%# app/views/clients/new.html.erb (modal version) %>
<%= turbo_frame_tag "modal" do %>
  <div data-modal-target="backdrop"
       data-action="click->modal#backdropClick"
       class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
    <div data-modal-target="dialog"
         class="w-full max-w-lg rounded-xl bg-white p-6 shadow-xl">
      <div class="mb-4 flex items-center justify-between">
        <h2 class="text-xl font-bold">New Client</h2>
        <button data-action="click->modal#hide"
                class="text-zinc-400 hover:text-zinc-600">×</button>
      </div>
      <%= render "form", client: @client %>
    </div>
  </div>
<% end %>
```

---

## 6. Tabs Controller (Tab Navigation)

Manages tab switching: shows/hides panels, updates active tab styling.

```javascript
// app/javascript/controllers/tabs_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["tab", "panel"]
  static values = {
    activeIndex: { type: Number, default: 0 },
    activeClass: { type: String, default: "border-teal-600 text-teal-600" },
    inactiveClass: { type: String, default: "border-transparent text-zinc-500" }
  }

  connect() {
    this.showPanel(this.activeIndexValue)
  }

  select(event) {
    const index = this.tabTargets.indexOf(event.currentTarget)
    if (index >= 0) {
      this.activeIndexValue = index
      this.showPanel(index)
    }
  }

  selectByIndex(event) {
    const index = parseInt(event.currentTarget.dataset.index)
    this.activeIndexValue = index
    this.showPanel(index)
  }

  showPanel(index) {
    this.tabTargets.forEach((tab, i) => {
      tab.className = tab.className.replace(this.activeClassValue, "")
        .replace(this.inactiveClassValue, "")
      tab.classList.add(i === index ? ...this.activeClassValue.split(" ") : ...this.inactiveClassValue.split(" "))
    })
    this.panelTargets.forEach((panel, i) => {
      panel.classList.toggle("hidden", i !== index)
    })
  }
}
```

**HTML:**
```html
<div data-controller="tabs" data-tabs-active-index-value="0">
  <div class="flex border-b border-zinc-200">
    <button data-tabs-target="tab"
            data-action="click->tabs#select"
            class="border-b-2 px-4 py-2 font-medium">
      Profile
    </button>
    <button data-tabs-target="tab"
            data-action="click->tabs#select"
            class="border-b-2 px-4 py-2 font-medium">
      Appointments
    </button>
    <button data-tabs-target="tab"
            data-action="click->tabs#select"
            class="border-b-2 px-4 py-2 font-medium">
      Notes
    </button>
  </div>

  <div data-tabs-target="panel" class="pt-4">Profile content…</div>
  <div data-tabs-target="panel" class="hidden pt-4">Appointments content…</div>
  <div data-tabs-target="panel" class="hidden pt-4">Notes content…</div>
</div>
```

---

## 7. Calendar Controller (Simple Month Navigation)

Renders a month calendar, navigates between months via Turbo Frame, highlights selected day.

```javascript
// app/javascript/controllers/calendar_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["grid", "title", "selected"]
  static values = {
    year: Number,
    month: Number,    // 0-indexed (0 = January)
    selectedDate: String  // ISO format YYYY-MM-DD
  }

  connect() {
    if (!this.hasYearValue || !this.hasMonthValue) {
      const now = new Date()
      this.yearValue = now.getFullYear()
      this.monthValue = now.getMonth()
    }
    this.render()
  }

  nextMonth() {
    if (this.monthValue === 11) {
      this.monthValue = 0
      this.yearValue++
    } else {
      this.monthValue++
    }
    this.render()
  }

  prevMonth() {
    if (this.monthValue === 0) {
      this.monthValue = 11
      this.yearValue--
    } else {
      this.monthValue--
    }
    this.render()
  }

  selectDay(event) {
    const day = event.currentTarget.dataset.day
    this.selectedDateValue = day
    this.element.dispatchEvent(new CustomEvent("calendar:select", {
      detail: { date: day },
      bubbles: true
    }))
    this.render()
  }

  render() {
    const months = ["January","February","March","April","May","June",
                    "July","August","September","October","November","December"]
    this.titleTarget.textContent = `${months[this.monthValue]} ${this.yearValue}`

    const firstDay = new Date(this.yearValue, this.monthValue, 1).getDay()
    const daysInMonth = new Date(this.yearValue, this.monthValue + 1, 0).getDate()
    const today = new Date().toISOString().slice(0, 10)

    let html = ""
    for (let i = 0; i < firstDay; i++) {
      html += `<div class="text-zinc-300"></div>`
    }
    for (let d = 1; d <= daysInMonth; d++) {
      const iso = `${this.yearValue}-${String(this.monthValue + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`
      const isSelected = iso === this.selectedDateValue
      const isToday = iso === today
      const classes = [
        "rounded-xl p-2 text-center cursor-pointer transition-colors",
        isSelected ? "bg-teal-600 text-white" : "hover:bg-zinc-100",
        isToday && !isSelected ? "ring-2 ring-teal-400" : ""
      ].filter(Boolean).join(" ")
      html += `<div class="${classes}" data-action="click->calendar#selectDay" data-day="${iso}">${d}</div>`
    }
    this.gridTarget.innerHTML = html
  }
}
```

**HTML:**
```html
<div data-controller="calendar"
     data-calendar-year-value="<%= @year %>"
     data-calendar-month-value="<%= @month %>"
     data-calendar-selected-date-value="<%= @selected_date&.iso8601 %>"
     class="rounded-xl border border-zinc-200 p-4">
  <div class="mb-4 flex items-center justify-between">
    <button data-action="click->calendar#prevMonth" class="rounded-xl p-2 hover:bg-zinc-100">←</button>
    <h3 data-calendar-target="title" class="font-bold"></h3>
    <button data-action="click->calendar#nextMonth" class="rounded-xl p-2 hover:bg-zinc-100">→</button>
  </div>
  <div class="grid grid-cols-7 gap-1 text-center text-xs text-zinc-500 mb-2">
    <div>Sun</div><div>Mon</div><div>Tue</div><div>Wed</div><div>Thu</div><div>Fri</div><div>Sat</div>
  </div>
  <div data-calendar-target="grid" class="grid grid-cols-7 gap-1"></div>
</div>
```

---

## 8. Chart Controller (Canvas-Based Rendering)

Renders a simple bar or line chart on a `<canvas>`, fetches data from a URL, and auto-refreshes at an interval.

```javascript
// app/javascript/controllers/chart_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["canvas"]
  static values = {
    url: String,
    type: { type: String, default: "bar" },
    interval: { type: Number, default: 0 },  // 0 = no auto-refresh
    color: { type: String, default: "#0D9488" }
  }

  connect() {
    this.fetchData()
    if (this.intervalValue > 0) {
      this.timer = setInterval(() => this.fetchData(), this.intervalValue * 1000)
    }
  }

  async fetchData() {
    try {
      const response = await fetch(this.urlValue)
      const data = await response.json()
      this.render(data)
    } catch (e) {
      console.error("Chart fetch failed:", e)
    }
  }

  render(data) {
    const canvas = this.canvasTarget
    const ctx = canvas.getContext("2d")
    const dpr = window.devicePixelRatio || 1
    const rect = canvas.getBoundingClientRect()
    canvas.width = rect.width * dpr
    canvas.height = rect.height * dpr
    ctx.scale(dpr, dpr)

    const w = rect.width
    const h = rect.height
    const padding = 40
    const chartW = w - padding * 2
    const chartH = h - padding * 2
    const max = Math.max(...data.map(d => d.value), 1)

    ctx.clearRect(0, 0, w, h)

    if (this.typeValue === "bar") {
      const barW = chartW / data.length * 0.7
      const gap = chartW / data.length * 0.3
      data.forEach((item, i) => {
        const barH = (item.value / max) * chartH
        const x = padding + i * (barW + gap)
        const y = h - padding - barH
        ctx.fillStyle = this.colorValue
        ctx.beginPath()
        ctx.roundRect(x, y, barW, barH, 6)
        ctx.fill()

        // Label
        ctx.fillStyle = "#71717A" // zinc-500
        ctx.font = "12px Geist, sans-serif"
        ctx.textAlign = "center"
        ctx.fillText(item.label, x + barW / 2, h - padding + 16)
      })
    } else if (this.typeValue === "line") {
      ctx.strokeStyle = this.colorValue
      ctx.lineWidth = 2
      ctx.beginPath()
      data.forEach((item, i) => {
        const x = padding + (i / (data.length - 1)) * chartW
        const y = h - padding - (item.value / max) * chartH
        if (i === 0) ctx.moveTo(x, y)
        else ctx.lineTo(x, y)
      })
      ctx.stroke()

      // Points
      data.forEach((item, i) => {
        const x = padding + (i / (data.length - 1)) * chartW
        const y = h - padding - (item.value / max) * chartH
        ctx.fillStyle = this.colorValue
        ctx.beginPath()
        ctx.arc(x, y, 4, 0, Math.PI * 2)
        ctx.fill()
      })
    }
  }

  disconnect() {
    if (this.timer) clearInterval(this.timer)
  }
}
```

**HTML:**
```html
<div data-controller="chart"
     data-chart-url-value="/dashboard/revenue.json"
     data-chart-type-value="bar"
     data-chart-interval-value="60"
     data-chart-color-value="#0D9488"
     class="rounded-xl border border-zinc-200 p-4">
  <canvas data-chart-target="canvas" class="w-full h-64"></canvas>
</div>
```

**Controller endpoint:**
```ruby
# app/controllers/dashboard_controller.rb
def revenue
  data = Appointment.this_week.group_by_day(:scheduled_at).sum(:price).map do |date, value|
    { label: date.strftime("%a"), value: value.to_f }
  end
  render json: data
end
```

---

## 9. Search Controller (Live Search with Debounce)

Debounces input and submits the search form via Turbo, updating results in a frame without a full page reload.

```javascript
// app/javascript/controllers/search_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["input", "form", "results", "status"]
  static values = {
    delay: { type: Number, default: 300 },
    minQuery: { type: Number, default: 2 },
    url: String
  }

  connect() {
    this.timer = null
    this.query = this.inputTarget.value
  }

  input() {
    clearTimeout(this.timer)
    this.query = this.inputTarget.value

    if (this.query.length === 0) {
      this.clearResults()
      return
    }

    if (this.query.length < this.minQueryValue) {
      this.showStatus(`Type at least ${this.minQueryValue} characters`)
      return
    }

    this.showStatus("Searching…")
    this.timer = setTimeout(() => this.search(), this.delayValue)
  }

  async search() {
    const url = new URL(this.urlValue, window.location.origin)
    url.searchParams.set("q", this.query)

    try {
      const response = await fetch(url, {
        headers: { "Accept": "text/vnd.turbo-stream.html" }
      })
      const html = await response.text()

      // Parse and apply turbo-stream elements
      const parser = new DOMParser()
      const doc = parser.parseFromString(html, "text/html")
      doc.querySelectorAll("turbo-stream").forEach(stream => {
        Turbo.renderStreamMessage(stream.outerHTML)
      })

      this.hideStatus()
    } catch (e) {
      this.showStatus("Search failed. Try again.")
      console.error(e)
    }
  }

  clear() {
    this.inputTarget.value = ""
    this.query = ""
    this.clearResults()
    this.inputTarget.focus()
  }

  clearResults() {
    if (this.hasResultsTarget) {
      this.resultsTarget.innerHTML = ""
    }
    this.hideStatus()
  }

  showStatus(message) {
    if (this.hasStatusTarget) {
      this.statusTarget.textContent = message
      this.statusTarget.classList.remove("hidden")
    }
  }

  hideStatus() {
    if (this.hasStatusTarget) {
      this.statusTarget.classList.add("hidden")
    }
  }

  // Keyboard shortcut: focus search on "/"
  keydown(event) {
    if (event.key === "/" && document.activeElement !== this.inputTarget) {
      event.preventDefault()
      this.inputTarget.focus()
    }
    if (event.key === "Escape" && this.query) {
      this.clear()
    }
  }

  disconnect() {
    clearTimeout(this.timer)
  }
}
```

**HTML:**
```html
<div data-controller="search"
     data-search-url-value="<%= search_clients_path %>"
     data-search-delay-value="300"
     data-search-min-query-value="2"
     class="relative">
  <div class="relative">
    <input type="text"
           data-search-target="input"
           data-action="input->search#input keydown->search#keydown"
           placeholder="Search clients… (press /)"
           class="w-full rounded-xl border border-zinc-300 px-4 py-2 pl-10" />
    <span class="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400">🔍</span>
    <button data-action="click->search#clear"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-zinc-600">×</button>
  </div>
  <p data-search-target="status" class="hidden mt-2 text-sm text-zinc-500"></p>

  <%= turbo_frame_tag "search_results", data: { search_target: "results" } do %>
    <!-- Results rendered here by Turbo Stream response -->
  <% end %>
</div>
```

---

## 10. Filter Controller (Faceted Filtering)

Manages filter state (checkboxes, selects, date ranges) and submits the filter form via Turbo, updating the results list in a frame.

```javascript
// app/javascript/controllers/filter_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["form", "results", "activeFilters", "clearButton"]
  static values = {
    delay: { type: Number, default: 500 },
    frameId: { type: String, default: "results" }
  }

  connect() {
    this.timer = null
    this.updateActiveFilters()
  }

  // Called when any filter input changes
  apply() {
    clearTimeout(this.timer)
    this.timer = setTimeout(() => this.submit(), this.delayValue)
  }

  // Immediate submit (for select changes)
  applyNow() {
    clearTimeout(this.timer)
    this.submit()
  }

  async submit() {
    const formData = new FormData(this.formTarget)
    const params = new URLSearchParams()

    for (const [key, value] of formData.entries()) {
      if (value) params.append(key, value)
    }

    const url = new URL(this.formTarget.action, window.location.origin)
    url.search = params.toString()

    try {
      const response = await fetch(url, {
        headers: { "Accept": "text/vnd.turbo-stream.html" }
      })
      const html = await response.text()
      Turbo.renderStreamMessage(html)
      this.updateActiveFilters()

      // Update URL for bookmarkability
      window.history.replaceState(null, "", url)
    } catch (e) {
      console.error("Filter failed:", e)
    }
  }

  clearAll() {
    this.formTarget.reset()
    this.submit()
  }

  clearField(event) {
    const field = event.currentTarget.dataset.field
    const inputs = this.formTarget.querySelectorAll(`[name*="${field}"]`)
    inputs.forEach(input => {
      if (input.type === "checkbox" || input.type === "radio") {
        input.checked = false
      } else {
        input.value = ""
      }
    })
    this.submit()
  }

  updateActiveFilters() {
    const active = []
    const formData = new FormData(this.formTarget)

    for (const [key, value] of formData.entries()) {
      if (value && value !== "all") {
        const label = this.formTarget.querySelector(`[name="${key}"]`)?.dataset?.filterLabel || key
        active.push({ key, value, label })
      }
    }

    if (this.hasActiveFiltersTarget) {
      if (active.length > 0) {
        this.activeFiltersTarget.innerHTML = active.map(f => `
          <span class="inline-flex items-center gap-1 rounded-xl bg-teal-100 px-3 py-1 text-sm text-teal-700">
            ${f.label}: ${f.value}
            <button data-action="click->filter#clearField" data-field="${f.key}" class="ml-1">×</button>
          </span>
        `).join("")
        this.clearButtonTarget?.classList.remove("hidden")
      } else {
        this.activeFiltersTarget.innerHTML = ""
        this.clearButtonTarget?.classList.add("hidden")
      }
    }
  }

  disconnect() {
    clearTimeout(this.timer)
  }
}
```

**HTML:**
```html
<div data-controller="filter"
     data-filter-delay-value="500"
     data-filter-frame-id-value="clients_list">
  <!-- Filter form -->
  <%= form_with url: clients_path, method: :get,
        data: { filter_target: "form" },
        class: "space-y-4" do |f| %>
    <div>
      <label class="block text-sm font-medium text-zinc-700 mb-1">Status</label>
      <select name="status"
              data-action="change->filter#applyNow"
              data-filter-label="Status"
              class="rounded-xl border border-zinc-300 px-3 py-2">
        <option value="all">All</option>
        <option value="active">Active</option>
        <option value="inactive">Inactive</option>
      </select>
    </div>
    <div>
      <label class="block text-sm font-medium text-zinc-700 mb-1">Tags</label>
      <% @tags.each do |tag| %>
        <label class="inline-flex items-center gap-2 mr-4">
          <%= check_box_tag "tags[]", tag.id, false,
                data: { action: "change->filter#apply", filter_label: tag.name } %>
          <span class="text-sm"><%= tag.name %></span>
        </label>
      <% end %>
    </div>
  <% end %>

  <!-- Active filter chips -->
  <div data-filter-target="activeFilters" class="flex flex-wrap gap-2 mt-4"></div>
  <button data-filter-target="clearButton"
          data-action="click->filter#clearAll"
          class="hidden text-sm text-zinc-500 hover:underline mt-2">
    Clear all filters
  </button>

  <!-- Results frame (updated by Turbo Stream response) -->
  <%= turbo_frame_tag "clients_list", data: { filter_target: "results" } do %>
    <% @clients.each do |client| %>
      <%= render "clients/client", client: client %>
    <% end %>
  <% end %>
</div>
```

---

## Summary: Controller Quick Reference

| Controller | Purpose | Key Targets | Key Values |
|---|---|---|---|
| `appearance` | Dark/light mode toggle | `icon`, `label` | `theme`, `persist` |
| `magnetic` | Cursor-following button hover | — | `strength`, `resetDelay` |
| `password-toggle` | Show/hide password input | `input`, `icon` | `visible` |
| `count-up` | Animated number counter | — | `target`, `duration`, `decimals`, `prefix`, `suffix` |
| `modal` | Dialog show/hide/focus trap | `dialog`, `backdrop` | `open`, `closeOnBackdrop` |
| `tabs` | Tab panel switching | `tab`, `panel` | `activeIndex`, `activeClass`, `inactiveClass` |
| `calendar` | Month calendar with day selection | `grid`, `title`, `selected` | `year`, `month`, `selectedDate` |
| `chart` | Canvas bar/line chart with auto-refresh | `canvas` | `url`, `type`, `interval`, `color` |
| `search` | Debounced live search | `input`, `form`, `results`, `status` | `delay`, `minQuery`, `url` |
| `filter` | Faceted filter form | `form`, `results`, `activeFilters`, `clearButton` | `delay`, `frameId` |
