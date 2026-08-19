---
name: design-to-rails-workflow
description: >-
  Complete workflow for going from zero to implemented Rails views using AI
  design generation. Combines Mermaid diagramming, Stitch screen generation,
  and taste-skill frontend implementation. Use when the user wants to build a
  complete web app UI with professional design quality. Trigger: build app
  design, generate all screens, design-first development, Stitch to Rails.
---

# Design-to-Rails Workflow

A complete pipeline for building production-quality Rails app UIs from scratch.

## Phase Sequence (MUST follow in order)

### Phase 0: Architecture Diagrams (BEFORE any code)

Generate three Mermaid diagrams as the project's design contract:

1. **C4 System Context** — Who connects to the system (users, external services)
2. **C4 Container Level** — App server, workers, DB, cache, storage
3. **Database ER Diagram** — All tables, relationships, key columns

Render to PNG using `mmdc` (Mermaid CLI):
```bash
mmdc -i diagram.mmd -o diagram.png -b white -w 1600 -s 2
```

### Phase 1: BPMN Process Flows

Generate for each major user journey:
- Booking/transaction flows
- Campaign/notification flows
- Retention/automation flows

### Phase 2: Design System (Stitch)

1. Create `.stitch/DESIGN.md` — taste-informed design tokens (colors, fonts, spacing, anti-patterns)
2. Create Stitch project via MCP API
3. Upload DESIGN.md (base64 encode, use `upload_design_md`)
4. Create design system from uploaded file (`create_design_system_from_design_md`)
5. Get assetId for use in screen generation

### Phase 3: Screen Generation (Stitch)

For each screen needed:
1. `generate_screen_from_text` with designSystem=assetId
2. Download both `.png` (screenshot) and `.html` (code) to `.stitch/designs/`
3. Screens to generate: Landing, Dashboard, List views, Detail views, Forms, Settings

**Performance**: Each generation takes 60-120s. Run sequentially.

### Phase 4: Taste Implementation

Apply taste-skill to convert Stitch HTML into Rails views. See [Stitch API Reference](references/stitch-api-reference.md) for the curl-based workflow when MCP tools aren't directly available.:
- Extract design tokens from generated HTML
- Implement with Tailwind CSS v4 + Hotwire (Turbo + Stimulus)
- Apply anti-slop pre-flight checks
- Ensure dark mode, accessibility, responsive behavior

### Phase 5: Backend Implementation (Ponytail Mode)

Generate Rails scaffolding from ER diagram:
- Models with validations and associations
- Controllers (CRUD + domain-specific actions)
- Migrations with indexes and foreign keys
- Services for complex business logic

## Key Principle

**Design → Stitch → Taste → Rails** — never skip steps. The design system
in Stitch ensures visual consistency. The taste-skill ensures anti-slop quality.
Ponytail ensures minimal, working backend code.

## Stitch MCP via HTTP (curl workaround)

When the Stitch MCP HTTP endpoint doesn't expose named tools directly (common with OpenRouter and other HTTP MCP proxies), call tools via `tools/call` method with raw curl:

```bash
# Create project
curl -s -X POST "https://stitch.googleapis.com/mcp" \
  -H "X-Goog-Api-Key: $API_KEY" -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"create_project","arguments":{"title":"My App"}}}'

# Upload DESIGN.md (base64 encode first)
DESIGN_B64=$(base64 -w0 .stitch/DESIGN.md)
curl -s -X POST "https://stitch.googleapis.com/mcp" \
  -H "X-Goog-Api-Key: $API_KEY" -H "Content-Type: application/json" \
  -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",\"params\":{\"name\":\"upload_design_md\",\"arguments\":{\"projectId\":\"$PROJECT_ID\",\"designMdBase64\":\"$DESIGN_B64\"}}}"

# Generate screen
curl -s -X POST "https://stitch.googleapis.com/mcp" \
  -H "X-Goog-Api-Key: $API_KEY" -H "Content-Type: application/json" \
  -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",\"params\":{\"name\":\"generate_screen_from_text\",\"arguments\":{\"projectId\":\"$PROJECT_ID\",\"designSystem\":\"assets/$ASSET_ID\",\"deviceType\":\"DESKTOP\",\"prompt\":\"...\"}}}"
```

**Response parsing:** The response nests JSON inside `result.content[0].text` — parse that string again to get `outputComponents[0].design.screens[0].screenshot.downloadUrl` and `.htmlCode.downloadUrl`.

**API key validation:** Test with a simple web search first (`https://google.serper.dev/search`) before attempting Stitch calls. A 403 means bad key.

## Rails Auth + Multi-Tenancy Pattern

Standard gem stack for production Rails apps with roles and multi-tenancy:

```ruby
# Gemfile
gem "devise"                    # core auth (sign in/up, password reset, confirmation)
gem "devise-i18n"               # i18n views
gem "rolify"                    # role-based access: owner, admin, staff, client
gem "pundit"                    # authorization policy layer
gem "omniauth"                  # OmniAuth core
gem "omniauth-google-oauth2"    # Google sign-up
gem "omniauth-apple"            # Apple sign-up
gem "acts_as_tenant"            # multi-tenancy scoping by account
```

**Tenant scoping pattern:**
```ruby
class ApplicationController < ActionController::Base
  set_current_tenant_through_filter
  before_action :set_tenant

  private
  def set_tenant
    ActsAsTenant.current_tenant = current_user.account if user_signed_in?
  end
end

class Client < ApplicationRecord
  acts_as_tenant(:account)  # auto-scopes all queries
  belongs_to :user
end
```

**Devise + OmniAuth callback:**
```ruby
class Users::OmniauthCallbacksController < Devise::OmniauthCallbacksController
  def google_oauth2
    @user = User.from_omniauth(request.env["omniauth.auth"])
    if @user.persisted?
      sign_in_and_redirect @user, event: :authentication
    else
      redirect_to new_user_registration_url
    end
  end
end
```

**User.from_omniauth (handles first-time social sign-up):**
```ruby
def self.from_omniauth(auth)
  where(provider: auth.provider, uid: auth.uid).first_or_create do |user|
    user.email = auth.info.email
    user.password = Devise.friendly_token[0, 20]
    user.first_name = auth.info.first_name || ""
    user.last_name = auth.info.last_name || ""
    user.skip_confirmation!
  end
end
```

## Pitfalls

- **CRITICAL: Don't start coding before ER diagram is approved.** User explicitly requires C4 + ER + BPMN before any migration or controller is written. This is non-negotiable.
- Don't put hex codes in Stitch generation prompts (design system handles it)
- Don't generate Stitch screens in parallel (rate limited, ~60-120s each)
- Don't use docker-compose for production (use Kamal accessories)
- Don't skip taste-skill pre-flight checks before shipping frontend
- Don't fight docker-compose port conflicts — check `ss -tlnp` first and use non-standard ports (5435, 6382)
- Don't run `chown` on host for Docker-created files — use `docker run --rm -v /project:/p alpine sh -c "chown -R 1000:1000 /p"`
- Don't skip Devise `:recoverable` and `:confirmable` — users need password reset and email confirmation
