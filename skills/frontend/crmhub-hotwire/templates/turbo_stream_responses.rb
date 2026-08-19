# frozen_string_literal: true

# =============================================================================
# CRMHub Turbo Stream Controller Response Templates
# =============================================================================
# Copy these patterns into your Rails controllers. Each pattern shows the
# correct Turbo Stream response for create/update/destroy actions.
#
# Key rules:
# 1. NEVER redirect on Turbo Stream requests — respond with turbo_stream format
# 2. Use 422 Unprocessable Entity for validation errors (Turbo re-renders form)
# 3. Broadcasts from model callbacks handle real-time; controller handles the
#    initial response to the submitting client
# 4. Always update count badges and append flash messages
# 5. Use dom_id(record) for target IDs — ensures consistency
# =============================================================================

# =============================================================================
# 1. CREATE — New record
# =============================================================================
module CreatePattern
  # Example: ClientsController#create
  def create
    @client = Client.new(client_params)
    @client.current_user = Current.user

    if @client.save
      @clients = Client.active.recent

      respond_to do |format|
        # Turbo Stream response: prepend new card, reset form, update count, flash
        format.turbo_stream
        # HTML fallback (non-Turbo request or direct navigation)
        format.html { redirect_to @client, notice: "Client created successfully." }
      end
    else
      # 422 is critical — Turbo treats 422 as "re-render the current frame"
      render :new, status: :unprocessable_entity
    end
  end
end

# Corresponding view: app/views/clients/create.turbo_stream.erb
# <%= turbo_stream.prepend "clients_list",
#       partial: "clients/client",
#       locals: { client: @client } %>
# <%= turbo_stream.replace "new_client",
#       partial: "clients/form",
#       locals: { client: Client.new } %>
# <%= turbo_stream.update "clients_count", @clients.count %>
# <%= turbo_stream.append "flash_messages",
#       partial: "shared/flash",
#       locals: { type: "notice", message: "Client created successfully." } %>

# =============================================================================
# 2. UPDATE — Edit existing record
# =============================================================================
module UpdatePattern
  # Example: ClientsController#update
  def update
    @client = Client.find(params[:id])

    if @client.update(client_params)
      respond_to do |format|
        # Turbo Stream: replace the card with updated version
        format.turbo_stream
        format.html { redirect_to @client, notice: "Client updated." }
      end
    else
      render :edit, status: :unprocessable_entity
    end
  end
end

# Corresponding view: app/views/clients/update.turbo_stream.erb
# <%= turbo_stream.replace dom_id(@client),
#       partial: "clients/client",
#       locals: { client: @client } %>
# <%# If inline edit frame exists, replace it with display version %>
# <%= turbo_stream.replace dom_id(@client, :name),
#       partial: "clients/name",
#       locals: { client: @client } %>
# <%= turbo_stream.append "flash_messages",
#       partial: "shared/flash",
#       locals: { type: "notice", message: "Client updated." } %>

# =============================================================================
# 3. DESTROY — Delete record
# =============================================================================
module DestroyPattern
  # Example: ClientsController#destroy
  def destroy
    @client = Client.find(params[:id])
    @client.destroy!
    @clients = Client.active

    respond_to do |format|
      format.turbo_stream
      format.html { redirect_to clients_path, notice: "Client deleted." }
    end
  end
end

# Corresponding view: app/views/clients/destroy.turbo_stream.erb
# <%= turbo_stream.remove dom_id(@client) %>
# <%= turbo_stream.update "clients_count", @clients.count %>
# <%= turbo_stream.append "flash_messages",
#       partial: "shared/flash",
#       locals: { type: "notice", message: "Client deleted." } %>
# <%# If detail panel was showing this client, show empty state %>
# <%= turbo_stream.update "client_detail",
#       partial: "shared/empty_state",
#       locals: { message: "Select a client to view details." } %>

# =============================================================================
# 4. INLINE UPDATE — Update a single field via inline edit
# =============================================================================
module InlineUpdatePattern
  # Example: ClientsController#update_field (custom action for inline edits)
  def update_field
    @client = Client.find(params[:id])

    if @client.update(client_params)
      respond_to do |format|
        format.turbo_stream do
          render turbo_stream:
            turbo_stream.replace(
              dom_id(@client, params[:field]),
              partial: "clients/#{params[:field]}",
              locals: { client: @client }
            )
        end
        format.html { redirect_to @client }
      end
    else
      render :edit, status: :unprocessable_entity
    end
  end
end

# =============================================================================
# 5. CREATE VIA MODAL — Create record from a modal form
# =============================================================================
module ModalCreatePattern
  # Example: ClientsController#create when form is in a modal
  def create
    @client = Client.new(client_params)

    if @client.save
      @clients = Client.active.recent

      respond_to do |format|
        format.turbo_stream do
          render turbo_stream: [
            # Prepend new card to list
            turbo_stream.prepend("clients_list",
              partial: "clients/client",
              locals: { client: @client }),
            # Update count badge
            turbo_stream.update("clients_count", @clients.count),
            # Close the modal by clearing the modal frame
            turbo_stream.update("modal", ""),
            # Flash message
            turbo_stream.append("flash_messages",
              partial: "shared/flash",
              locals: { type: "notice", message: "Client created." })
          ]
        end
        format.html { redirect_to @client, notice: "Client created." }
      end
    else
      # Re-render the form inside the modal with errors (422 status)
      render :new, status: :unprocessable_entity
    end
  end
end

# =============================================================================
# 6. NESTED RESOURCE CREATE — e.g., Appointment within Client
# =============================================================================
module NestedCreatePattern
  # Example: AppointmentsController#create (nested under Client)
  def create
    @client = Client.find(params[:client_id])
    @appointment = @client.appointments.build(appointment_params)

    if @appointment.save
      respond_to do |format|
        format.turbo_stream do
          render turbo_stream: [
            # Prepend to the appointments list frame
            turbo_stream.prepend("appointments_list",
              partial: "appointments/appointment",
              locals: { appointment: @appointment }),
            # Reset the form
            turbo_stream.replace("new_appointment",
              partial: "appointments/form",
              locals: { client: @client, appointment: @client.appointments.build }),
            # Update appointment count
            turbo_stream.update("appointments_count", @client.appointments.count),
            # Flash
            turbo_stream.append("flash_messages",
              partial: "shared/flash",
              locals: { type: "notice", message: "Appointment scheduled." })
          ]
        end
        format.html { redirect_to @client, notice: "Appointment scheduled." }
      end
    else
      render :new, status: :unprocessable_entity
    end
  end
end

# =============================================================================
# 7. ARCHIVE / STATUS CHANGE — Toggle status without destroying
# =============================================================================
module StatusChangePattern
  # Example: ClientsController#activate / #deactivate
  def activate
    @client = Client.find(params[:id])
    @client.update!(status: :active)

    respond_to do |format|
      format.turbo_stream do
        render turbo_stream:
          turbo_stream.replace(
            dom_id(@client),
            partial: "clients/client",
            locals: { client: @client }
          )
      end
      format.html { redirect_to @client, notice: "Client activated." }
    end
  end

  def deactivate
    @client = Client.find(params[:id])
    @client.update!(status: :inactive)

    respond_to do |format|
      format.turbo_stream do
        render turbo_stream:
          turbo_stream.replace(
            dom_id(@client),
            partial: "clients/client",
            locals: { client: @client }
          )
      end
      format.html { redirect_to @client, notice: "Client deactivated." }
    end
  end
end

# =============================================================================
# 8. SEARCH RESULTS — Return filtered results as Turbo Stream
# =============================================================================
module SearchPattern
  # Example: ClientsController#search
  def search
    @clients = if params[:q].present?
      Client.where("name ILIKE ?", "%#{params[:q]}%").limit(20)
    else
      Client.none
    end

    respond_to do |format|
      format.turbo_stream do
        render turbo_stream:
          turbo_stream.update(
            "search_results",
            partial: "clients/search_results",
            locals: { clients: @clients }
          )
      end
      format.html { render :index }
    end
  end
end

# =============================================================================
# 9. FILTER RESULTS — Return filtered list as Turbo Stream
# =============================================================================
module FilterPattern
  # Example: ClientsController#index with filter params
  def index
    base = Client.active
    base = base.where(status: params[:status]) if params[:status].present? && params[:status] != "all"
    base = base.joins(:tags).where(tags: { id: params[:tags] }) if params[:tags].present?

    @clients = base.recent.page(params[:page])

    respond_to do |format|
      format.html
      format.turbo_stream do
        render turbo_stream:
          turbo_stream.update(
            "clients_list",
            partial: "clients/list",
            locals: { clients: @clients }
          )
      end
    end
  end
end

# =============================================================================
# 10. ERROR HANDLING — Record not found, authorization failed
# =============================================================================
module ErrorHandlingPattern
  rescue_from ActiveRecord::RecordNotFound do |exception|
    respond_to do |format|
      format.turbo_stream do
        render turbo_stream: turbo_stream.update(
          "client_detail",
          partial: "shared/error",
          locals: { message: "Record not found." }
        )
      end
      format.html { redirect_to clients_path, alert: "Record not found." }
    end
  end
end

# =============================================================================
# MODEL BROADCAST CALLBACKS — For real-time updates across tabs
# =============================================================================
# Place these in your model files:
#
# class Client < ApplicationRecord
#   after_create_commit  -> { broadcast_prepend_to "clients", target: "clients_list",
#     partial: "clients/client", locals: { client: self } }
#   after_update_commit  -> { broadcast_replace_to "clients", target: dom_id(self),
#     partial: "clients/client", locals: { client: self } }
#   after_destroy_commit -> { broadcast_remove_to "clients", target: dom_id(self) }
# end
#
# class Appointment < ApplicationRecord
#   belongs_to :client
#   after_create_commit  -> { broadcast_prepend_to [client, :appointments],
#     target: "appointments_list", partial: "appointments/appointment",
#     locals: { appointment: self } }
#   after_update_commit  -> { broadcast_replace_to [client, :appointments],
#     target: dom_id(self), partial: "appointments/appointment",
#     locals: { appointment: self } }
#   after_destroy_commit -> { broadcast_remove_to [client, :appointments],
#     target: dom_id(self) }
# end
