# CRMHub Actual Schema (Rails 8, as of 2026-06-28)

**Project:** `/home/deeone/projects/crm_hub/`  
**Design:** `/home/deeone/projects/.stitch/DESIGN.md`  
**Stack:** Rails 8.1, SQLite dev / PostgreSQL prod, Devise + Rolify + Pundit, Hotwire, Active Storage, ActsAsTenant (multi-tenancy)

## Actual Tables (15 + support)

| Table | Purpose | Key Columns |
|---|---|---|
| `accounts` | Multi-tenant salon org | `name`, `timezone`, `currency` |
| `users` | Staff/stylist login | `email`, `encrypted_password`, `role` (int enum), `account_id` FK |
| `clients` | Client profiles | `first_name`, `last_name`, `email`, `phone`, `status`, `account_id`, `user_id` FK |
| `bookings` | Appointments | `starts_at`, `ends_at`, `status` (enum), `account/client/staff/service FK` |
| `services` | Catalog items | `name`, `category`, `duration` (minutes), `price`, `active`, `account_id` |
| `campaigns` | Email/SMS drip | `name`, `status`, `account/user FK` |
| `campaign_messages` | Individual sends | `channel` (email/sms), `subject`, `body`, FK to campaign/client/account |
| `drip_steps` | Campaign sequence | `step_number`, `delay_days`, `subject`, `body`, `campaign_id` |
| `drip_enrollments` | Client in campaign | `status`, `current_step`, FK campaign/client/account |
| `loyalty_accounts` | Points per client | `points`, `tier`, `account/client FK` |
| `loyalty_transactions` | Points ledger | `points`, `kind` (earn/redeem), `description`, FK loyalty_account |
| `communications` | Message log | `channel`, `direction` (in/out), `content`, FK client/user/account |
| `invoices` | Billing | `number`, `status`, `subtotal`, `tax`, `total`, `due_date`, FK booking/client |
| `notes` | Client notes | `body`, FK client/user/account |
| `tags` | Client labeling | `name`, `account_id` |
| `client_tags` | Tag assignment | FK client + tag + account |
| `roles` | Rolify roles | `name`, `resource_type`, `resource_id` (polymorphic) |
| `users_roles` | Role assignment | `user_id`, `role_id` (no ID pk) |
| `active_storage_*` | File uploads | Standard Rails |

**Missing from schema (noted gaps):**
- `formulas` table — hair color formulas, NOT YET MIGRATED (critical for hair domain)
- `photos` table — before/after gallery, NOT YET MIGRATED
- `reviews` table — client feedback, NOT YET MIGRATED

## Actual 5 Roles
`owner`, `manager`, `stylist`, `receptionist`, `admin` (via Rolify)

## Current State
- Schema complete: ✅ 20 migrations, all tables wired with FK + indexes
- Models exist: ✅ All 17 models
- Controllers exist: ✅ 15 controllers (most need method bodies completed)
- Views exist: ✅ 35+ ERB templates across 11 functional areas
- Auth: ✅ Devise + Rolify + Pundit configured
- Seeds: ✅ "Glow Hair Studio" demo data
- Hotwire: ⚠️ Views exist but NOT wired to Turbo streams yet
- BookingsController create/update/destroy: ⚠️ Method bodies missing (stubbed)
- Design styling: ⚠️ ERB rendered raw, not yet matching DESIGN.md spec

## Design Tokens (from DESIGN.md)
- Teal accent: `#0D9488`
- Hover: `#0F766E`
- Subtle: `#CCFBF1`
- Font: Geist (not Inter)
- Border radius: 12px
- Cards: white fill, 1px border, 20px padding, hover shadow