# CRMHub — Active Rails 8 Build for Hair Practitioner CMS

> **Source:** `/home/deeone/crmhub_session_state.md` (session state, updated 2026-06-27)
> **Stitch project:** `1925252542517546774`

## What Exists

### Architecture (Rails 8 + Hotwire)
```
app/
  controllers/     # Thin. Delegates to services. Renders responses.
  models/          # Persistence: validations, associations, scopes, simple predicates.
  views/           # ERB markup only. No logic.
  services/        # Business logic. Orchestrates models, APIs, side effects.
  queries/         # Complex database queries. Returns relations or hashes.
  forms/           # Multi-model form objects.
  policies/        # Pundit authorization. Default deny.
  presenters/      # View formatting (SimpleDelegator).
  components/      # ViewComponents (reusable UI with tests).
  jobs/            # Background jobs (Solid Queue). Must be idempotent.
  mailers/         # Email delivery. Always HTML + text templates.
```

### Tech Stack
- **Ruby** 3.3, **Rails** 8.1, **SQLite** (dev) / **PostgreSQL** (prod)
- **Frontend:** Hotwire (Turbo + Stimulus), Tailwind CSS 4, ViewComponent
- **Auth:** `has_secure_password` (Rails 8 built-in) + Pundit (NOT JWT)
- **Background Jobs:** Solid Queue (database-backed, no Redis)
- **Caching:** Solid Cache | **WebSockets:** Solid Cable
- **Assets:** Propshaft + Import Maps (no Node.js)
- **Deployment:** Kamal 2 + Thruster

### Design System (Stitch)
- Project ID: `1925252542517546774`
- Color: teal `#0D9488`
- Font: Geist
- Neutrals: Zinc
- Border-radius: 12px

### Roles
`owner`, `manager`, `stylist`, `receptionist`, `admin` (5 roles — NOT the 4 in the generic CMS planner)

### 25 Pages Across 11 Functional Areas (per Stitch design)
Manager Dashboard, Stylist Dashboard, Receptionist Dashboard, Admin Dashboard, Staff Management, Analytics & Reports, Account Settings (new screen), Client Portal (new screen), + more.

## What's In Progress (as of last session)
1. Stitch screen edits: repurposing 6 duplicate screens → Manager/Stylist/Receptionist/Admin Dashboards + Staff Management + Analytics
2. Generating 2 new Stitch screens: Account Settings, Client Portal
3. Downloading final page HTML + screenshots from Stitch

## What's Next
1. Load skills: `stitch-to-rails-erb`, `lightpanda-browser`, `hermes-agent`
2. Use `mcp_stitch_*` tools to edit_screens and generate_screen_from_text
3. Generate C4 diagrams, ER diagram, user journey diagrams
4. Write PRD
5. Build Rails app scaffold
6. Implement: auth → client CRUD → appointment booking

## Key Conventions
- **Skinny everything:** Controllers orchestrate. Models persist. Services contain business logic.
- **Services:** `.call` class method, return Result objects, namespace by domain (`Entities::CreateService`).
- **No JWT:** Auth is session-based only.
- **CLI-first:** Rails generators before manual editing.

## Directory Structure
- Stitch designs: `/home/deeone/projects/.stitch/designs/`
- DESIGN.md: `/home/deeone/projects/.stitch/DESIGN.md`
- Skill: `stitch-to-rails-erb` at `~/.hermes/skills/frontend/stitch-to-rails-erb/`