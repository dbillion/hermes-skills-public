# Turbo Patterns for CRMHub

> Turbo Drive · Turbo Frames · Turbo Streams
> Rails 8 helpers: `turbo_frame_tag`, `turbo_stream_from`, `broadcast_*`

---

## 1. Turbo Drive Patterns

### 1.1 Default Behavior (Zero Config)

Turbo Drive is active by default. All `<a>` clicks and form submits are intercepted, fetched as HTML, and the `<body>` is swapped without a full page reload.

```erb
<%# This is automatically Turbo Drive — no data attributes needed %>
<%= link_to "Dashboard", dashboard_path, class: "text-teal-600 font-medium" %>
```

### 1.2 Opting Out

```erb
<%# Disable Turbo for this link only %>
<%= link_to "Download Report", report_path(format: :pdf), data: { turbo: false } %>

<%# Disable Turbo for an entire form %>
<%= form_with model: @upload, data: { turbo: false } do |f| %>
  <%# File upload that needs a full page reload %>
<% end %>

<%# Disable Turbo for a whole section %>
<div data-turbo="false">
  <%# All links/forms inside skip Turbo Drive %>
</div>
```

### 1.3 Programmatic Navigation

```javascript
// Navigate via JavaScript (still uses Turbo Drive)
import Turbo from "@hotwired/turbo"
Turbo.visit("/clients/42")

// Turbo.visit with action
Turbo.visit("/clients/42", { action: "advance" })   // Updates URL + history
Turbo.visit("/clients/42", { action: "replace" })   // Replaces current history entry
```

### 1.4 Progress Bar

Turbo shows a progress bar at the top of the page during navigation. Style it with CSS:

```css
/* app/assets/stylesheets/application.css */
.turbo-progress-bar {
  background-color: #0D9488; /* Teal */
  height: 3px;
}
```

### 1.5 Loading State

```erb
<%# Show loading state during Turbo Drive navigation %>
<%= link_to "Clients", clients_path,
      data: { turbo_prefetch: false },
      class: "group" do %>
  Clients
  <span class="hidden group-[.turbo-loading]:inline">⏳</span>
<% end %>
```

---

## 2. Turbo Frame Patterns

### 2.1 Basic Frame — List + Detail (Master-Detail)

The classic CRM pattern: a list on the left, a detail panel on the right. Clicking a list item updates only the detail frame.

```erb
<%# app/views/clients/index.html.erb %>
<div class="flex gap-6 min-h-[100dvh]">
  <!-- Left: client list -->
  <div class="w-1/3">
    <%= turbo_frame_tag "clients_list" do %>
      <div class="space-y-2">
        <% @clients.each do |client| %>
          <%= link_to client_path(client),
                data: { turbo_frame: "client_detail", turbo_action: "advance" },
                class: "block rounded-xl border border-zinc-200 p-4 hover:border-teal-500" do %>
            <h3 class="font-medium text-zinc-900"><%= client.name %></h3>
            <p class="text-sm text-zinc-500"><%= client.phone %></p>
          <% end %>
        <% end %>
      </div>
    <% end %>
  </div>

  <!-- Right: client detail -->
  <div class="w-2/3">
    <%= turbo_frame_tag "client_detail" do %>
      <div class="rounded-xl border border-zinc-200 p-6 text-center text-zinc-500">
        Select a client to view their details.
      </div>
    <% end %>
  </div>
</div>
```

```erb
<%# app/views/clients/show.html.erb — must include matching frame %>
<%= turbo_frame_tag "client_detail" do %>
  <div class="rounded-xl border border-zinc-200 p-6">
    <div class="flex items-start justify-between mb-4">
      <div>
        <h1 class="text-2xl font-bold text-zinc-900"><%= @client.name %></h1>
        <p class="text-zinc-500"><%= @client.email %></p>
      </div>
      <span class="rounded-xl bg-teal-100 px-3 py-1 text-sm font-medium text-teal-700">
        <%= @client.status.titleize %>
      </span>
    </div>
    <%= link_to "Edit", edit_client_path(@client),
          data: { turbo_frame: "client_detail" },
          class: "rounded-xl bg-teal-600 px-4 py-2 text-white hover:bg-teal-700" %>
  </div>
<% end %>
```

### 2.2 Inline Edit Frame — Click to Edit

Wrap a display value and its edit form in the same frame. The edit form renders into the same frame, replacing the display.

```erb
<%# app/views/clients/_client_name.html.erb %>
<%= turbo_frame_tag dom_id(@client, :name) do %>
  <% if params[:edit] == "name" %>
    <%= form_with model: @client, url: client_path(@client),
          data: { turbo_frame: dom_id(@client, :name) } do |f| %>
      <%= f.text_field :name, class: "rounded-xl border border-zinc-300 px-3 py-2" %>
      <%= f.submit "Save", class: "rounded-xl bg-teal-600 px-4 py-2 text-white" %>
      <%= link_to "Cancel", client_path(@client),
            data: { turbo_frame: dom_id(@client, :name) },
            class: "text-zinc-500" %>
    <% end %>
  <% else %>
    <h2 class="text-xl font-bold">
      <%= @client.name %>
      <%= link_to "✏️", client_path(@client, edit: "name"),
            data: { turbo_frame: dom_id(@client, :name) },
            class: "text-sm text-zinc-400" %>
    </h2>
  <% end %>
<% end %>
```

### 2.3 Lazy-Loaded Frame

Load expensive content (charts, activity feeds) only when the frame scrolls into view.

```erb
<%= turbo_frame_tag "activity_feed",
      src: activity_client_path(@client),
      loading: "lazy" do %>
  <div class="animate-pulse rounded-xl bg-zinc-100 p-8 text-center text-zinc-400">
    Loading activity…
  </div>
<% end %>
```

```ruby
# app/controllers/clients_controller.rb
def activity
  @client = Client.find(params[:id])
  @activities = @client.activities.recent.limit(20)
  render partial: "clients/activity", locals: { client: @client, activities: @activities }
end
```

### 2.4 Nested Frames

Frames can be nested. A parent frame can contain child frames, and each child can be updated independently.

```erb
<%= turbo_frame_tag "client_detail" do %>
  <div class="space-y-4">
    <h1><%= @client.name %></h1>

    <%= turbo_frame_tag "appointments_list" do %>
      <% @client.appointments.each do |apt| %>
        <div id="<%= dom_id(apt) %>"><%= apt.title %></div>
      <% end %>
    <% end %>

    <%= turbo_frame_tag "notes_list" do %>
      <% @client.notes.each do |note| %>
        <div id="<%= dom_id(note) %>"><%= note.body %></div>
      <% end %>
    <% end %>
  </div>
<% end %>
```

### 2.5 Breaking Out of a Frame

Use `data-turbo-frame="_top"` to navigate to a full page from within a frame.

```erb
<%= link_to "View Full Profile", client_path(@client),
      data: { turbo_frame: "_top" } %>
```

---

## 3. Turbo Stream Patterns

### 3.1 Create Action — Prepend New Item + Reset Form + Update Count

```ruby
# app/controllers/clients_controller.rb
def create
  @client = Client.new(client_params)
  if @client.save
    @clients = Client.active
    respond_to do |format|
      format.turbo_stream
      format.html { redirect_to @client, notice: "Client created." }
    end
  else
    render :new, status: :unprocessable_entity
  end
end
```

```erb
<%# app/views/clients/create.turbo_stream.erb %>

<%# 1. Prepend the new client card to the list %>
<%= turbo_stream.prepend "clients_list",
      partial: "clients/client",
      locals: { client: @client } %>

<%# 2. Replace the form with a fresh empty one %>
<%= turbo_stream.replace "new_client",
      partial: "clients/form",
      locals: { client: Client.new } %>

<%# 3. Update the client count badge %>
<%= turbo_stream.update "clients_count", @clients.count %>

<%# 4. Append a flash message %>
<%= turbo_stream.append "flash_messages",
      partial: "shared/flash",
      locals: { type: "notice", message: "Client created successfully." } %>
```

### 3.2 Update Action — Replace Existing Item + Flash

```ruby
def update
  @client = Client.find(params[:id])
  if @client.update(client_params)
    respond_to do |format|
      format.turbo_stream
      format.html { redirect_to @client, notice: "Client updated." }
    end
  else
    render :edit, status: :unprocessable_entity
  end
end
```

```erb
<%# app/views/clients/update.turbo_stream.erb %>

<%# Replace the client card with updated version %>
<%= turbo_stream.replace dom_id(@client),
      partial: "clients/client",
      locals: { client: @client } %>

<%# If editing inline, also replace the frame with the display version %>
<%= turbo_stream.replace dom_id(@client, :name),
      partial: "clients/name",
      locals: { client: @client } %>

<%# Flash %>
<%= turbo_stream.append "flash_messages",
      partial: "shared/flash",
      locals: { type: "notice", message: "Client updated." } %>
```

### 3.3 Destroy Action — Remove Item + Update Count + Flash

```ruby
def destroy
  @client = Client.find(params[:id])
  @client.destroy
  @clients = Client.active
  respond_to do |format|
    format.turbo_stream
    format.html { redirect_to clients_path, notice: "Client deleted." }
  end
end
```

```erb
<%# app/views/clients/destroy.turbo_stream.erb %>

<%# Remove the client card from the DOM %>
<%= turbo_stream.remove dom_id(@client) %>

<%# Update the count %>
<%= turbo_stream.update "clients_count", @clients.count %>

<%# Flash %>
<%= turbo_stream.append "flash_messages",
      partial: "shared/flash",
      locals: { type: "notice", message: "Client deleted." } %>

<%# If the detail panel was showing this client, clear it %>
<%= turbo_stream.update "client_detail",
      partial: "shared/empty_state",
      locals: { message: "Select a client to view details." } %>
```

### 3.4 Real-Time Broadcasts — Model Callbacks

```ruby
# app/models/client.rb
class Client < ApplicationRecord
  has_many :appointments
  has_many :notes

  # Broadcast to the clients collection channel
  after_create_commit  -> { broadcast_prepend_to "clients", target: "clients_list", partial: "clients/client", locals: { client: self } }
  after_update_commit  -> { broadcast_replace_to "clients", target: dom_id(self), partial: "clients/client", locals: { client: self } }
  after_destroy_commit -> { broadcast_remove_to "clients", target: dom_id(self) }

  # Broadcast to the individual client channel
  after_update_commit -> { broadcast_replace_to self, target: "client_detail", partial: "clients/detail", locals: { client: self } }
end
```

```ruby
# app/models/appointment.rb
class Appointment < ApplicationRecord
  belongs_to :client

  after_create_commit  -> { broadcast_prepend_to [client, :appointments], target: "appointments_list", partial: "appointments/appointment", locals: { appointment: self } }
  after_update_commit  -> { broadcast_replace_to [client, :appointments], target: dom_id(self), partial: "appointments/appointment", locals: { appointment: self } }
  after_destroy_commit -> { broadcast_remove_to [client, :appointments], target: dom_id(self) }
end
```

### 3.5 Subscribing on the Page

```erb
<%# Subscribe to all clients (for the index list) %>
<%= turbo_stream_from "clients" %>
<%= turbo_frame_tag "clients_list" do %>
  <% @clients.each do |client| %>
    <%= render client %>
  <% end %>
<% end %>

<%# Subscribe to a single client (for the show page) %>
<%= turbo_stream_from @client %>

<%# Subscribe to a nested resource (appointments for a client) %>
<%= turbo_stream_from @client, :appointments %>
<%= turbo_frame_tag "appointments_list" do %>
  <% @client.appments.each do |apt| %>
    <%= render apt %>
  <% end %>
<% end %>
```

### 3.6 Custom Turbo Stream Actions (via Stimulus)

If you need a custom action (e.g., morph), register it via JavaScript:

```javascript
// app/javascript/application.js
import { StreamActions } from "@hotwired/turbo"

StreamActions.morph = function () {
  const target = this.targetElements[0]
  const content = this.templateContent
  if (target && content) {
    // Use a morphing library like idiomorph
    Idiomorph.morph(target, content)
  }
}
```

```erb
<%# Use the custom action %>
<%= turbo_stream_action_tag "morph", target: "client_detail", template: render(@client) %>
```

### 3.7 Turbo Stream from a Job (Background Processing)

```ruby
# app/jobs/reminder_broadcast_job.rb
class ReminderBroadcastJob < ApplicationJob
  queue_as :default

  def perform(appointment_id)
    appointment = Appointment.find(appointment_id)
    Turbo::StreamsChannel.broadcast_append_to(
      [appointment.client, :appointments],
      target: "reminders",
      partial: "appointments/reminder",
      locals: { appointment: appointment }
    )
  end
end
```

### 3.8 Refresh Action (Rails 7.2+)

The `refresh` action re-fetches the target element's content from the server by making a fetch request to its `src` URL. Useful for auto-refreshing dashboard widgets.

```erb
<%# Auto-refresh dashboard every 30 seconds via a Stimulus controller %>
<div data-controller="refresh" data-refresh-interval-value="30">
  <%= turbo_frame_tag "revenue_chart",
        src: dashboard_revenue_path,
        data: { refresh_target: "frame" } do %>
    <div class="animate-pulse p-8 text-center text-zinc-400">Loading chart…</div>
  <% end %>
</div>
```

```javascript
// refresh_controller.js
import { Controller } from "@hotwired/stimulus"
import Turbo from "@hotwired/turbo"

export default class extends Controller {
  static values = { interval: { type: Number, default: 30 } }
  static targets = ["frame"]

  connect() {
    this.timer = setInterval(() => {
      Turbo.visit(this.frameTarget.src, { frame: this.frameTarget.id })
    }, this.intervalValue * 1000)
  }

  disconnect() { clearInterval(this.timer) }
}
```

---

## 4. Error Handling Patterns

### 4.1 Form Validation Errors (422 Unprocessable Entity)

When a form submission fails validation, render the form with errors using status `422`. Turbo Drive automatically swaps the frame content on 4xx responses.

```ruby
def create
  @client = Client.new(client_params)
  if @client.save
    respond_to { |f| f.turbo_stream; f.html { redirect_to @client } }
  else
    # 422 status is critical — Turbo treats 422 as "re-render the form"
    render :new, status: :unprocessable_entity
  end
end
```

```erb
<%# app/views/clients/_form.html.erb %>
<%= form_with model: client, id: dom_id(client, :form),
      data: { turbo_frame: "clients_list" } do |f| %>
  <% if client.errors.any? %>
    <div class="rounded-xl bg-red-50 p-4 text-red-600 mb-4">
      <ul>
        <% client.errors.full_messages.each do |msg| %>
          <li><%= msg %></li>
        <% end %>
      </ul>
    </div>
  <% end %>
  <%# form fields %>
<% end %>
```

### 4.2 Handling Turbo Frame Request Failures

```ruby
# Rescue from RecordNotFound and render a turbo stream that shows a message
rescue_from ActiveRecord::RecordNotFound do |e|
  respond_to do |format|
    format.turbo_stream do
      render turbo_stream: turbo_stream.update("client_detail",
        partial: "shared/error", locals: { message: "Record not found." })
    end
    format.html { redirect_to clients_path, alert: "Record not found." }
  end
end
```

---

## 5. Navigation Patterns

### 5.1 Breadcrumbs Within Frames

```erb
<nav class="flex items-center gap-2 text-sm text-zinc-500 mb-4">
  <%= link_to "Clients", clients_path, data: { turbo_frame: "_top" } %>
  <span>/</span>
  <%= link_to @client.name, client_path(@client),
        data: { turbo_frame: "client_detail", turbo_action: "advance" } %>
  <span>/</span>
  <span class="text-zinc-900">Edit</span>
</nav>
```

### 5.2 Cancel / Back Button

```erb
<%= link_to "Cancel", request.referrer || clients_path,
      data: { turbo_frame: "_top" },
      class: "rounded-xl px-4 py-2 text-zinc-600 hover:bg-zinc-100" %>
```

### 5.3 Modal Navigation (Frame-Based Modal)

```erb
<%# Link that opens a modal %>
<%= link_to "New Appointment", new_client_appointment_path(@client),
      data: { turbo_frame: "modal" },
      class: "rounded-xl bg-teal-600 px-4 py-2 text-white" %>

<%# Modal frame (in the layout, data-turbo-permanent so it survives navigation) %>
<%= turbo_frame_tag "modal", data: { turbo_permanent: true } %>
```

See `references/stimulus-controllers.md` for the `modal` Stimulus controller that manages show/hide/keyboard interactions.

---

## 6. Flash Messages Pattern

```erb
<%# app/views/layouts/application.html.erb %>
<%= turbo_frame_tag "flash_messages",
      data: { turbo_permanent: true },
      class: "fixed bottom-4 right-4 z-50 space-y-2" do %>
<% end %>
```

```erb
<%# app/views/shared/_flash.html.erb %>
<div class="rounded-xl px-4 py-3 shadow-lg
            <%= type == "notice" ? "bg-teal-600 text-white" : "bg-red-500 text-white" %>"
     data-controller="flash"
     data-flash-delay-value="4000">
  <%= message %>
  <button data-action="click->flash#close" class="ml-2 opacity-70 hover:opacity-100">×</button>
</div>
```

```javascript
// flash_controller.js
import { Controller } from "@hotwired/stimulus"
export default class extends Controller {
  static values = { delay: { type: Number, default: 4000 } }
  connect() {
    if (this.delayValue > 0) {
      this.timer = setTimeout(() => this.close(), this.delayValue)
    }
  }
  close() { this.element.remove() }
  disconnect() { clearTimeout(this.timer) }
}
```

---

## 7. Infinite Scroll Pattern

```erb
<div data-controller="scroll" data-scroll-url-value="<%= clients_path(page: @clients.next_page) %>">
  <%= turbo_frame_tag "clients_list" do %>
    <% @clients.each do |client| %>
      <%= render "clients/client", client: client %>
    <% end %>
  <% end %>

  <% if @clients.next_page %>
    <%= turbo_frame_tag "clients_pagination",
          loading: "lazy",
          src: clients_path(page: @clients.next_page, format: :turbo_stream) %>
  <% end %>
</div>
```

The lazy-loaded `clients_pagination` frame fetches the next page when scrolled into view. The response appends items to `clients_list` and replaces itself with the next pagination frame.
