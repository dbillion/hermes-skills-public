# CRMHub Project Reference

## Project Status
- **Location**: `/home/deeone/projects/crm_hub`
- **Stack**: Rails 8, SQLite, Hotwire (Turbo+Stimulus), Kamal, Docker Compose
- **Dev login**: owner@glowhair.com / password123
- **Run**: `rails server -b 0.0.0.0 -p 3000`

## Session State (2026-06-27)
- All 15 models generated and seeded
- All 14 controllers generated
- All key views written
- Hotwire skill created
- 8 Stitch screens designed and downloaded to `.stitch/final/`
- Diagrams created in `.stitch/diagrams/`

## Known Issues (Resolve in Next Session)
1. **Seed failing**: `acts_as_tenant` needs `account: account` passed explicitly on ALL tenant-scoped records in seeds.rb. `Current.account` alone is insufficient.
2. **Views not tested**: App not yet booted in browser. Need to verify pages render without ERB errors.
3. **Stitch HTML not yet converted**: The 16 original Stitch screens still need HTML→ERB conversion per stitch-to-rules skill rules.

## File Inventory
```
app/controllers/
├── application_controller.rb (Pundit + auth + acts_as_tenant)
├── pages_controller.rb
├── dashboard_controller.rb
├── clients_controller.rb
├── bookings_controller.rb
├── campaigns_controller.rb
├── services_controller.rb
├── loyalty_controller.rb
├── staff_controller.rb
├── analytics_controller.rb
├── security_controller.rb
├── settings_controller.rb
└── portal_controller.rb

app/views/
├── layouts/application.html.erb (sidebar + Geist + Tailwind)
├── application/_sidebar.html.erb
├── dashboard/index.html.erb
├── pages/landing.html.erb
├── clients/index.html.erb, show.html.erb, new.html.erb, edit.html.erb
├── bookings/index.html.erb
├── campaigns/index.html.erb
├── services/index.html.erb
├── loyalty/index.html.erb
├── staff/index.html.erb
├── analytics/index.html.erb
├── security/show.html.erb
├── settings/show.html.erb
└── portal/show.html.erb

app/models/
├── account.rb, user.rb (Devise + rolify), client.rb, service.rb
├── booking.rb, campaign.rb, campaign_message.rb
├── drip_step.rb, drip_enrollment.rb
├── loyalty_account.rb, loyalty_transaction.rb
├── communication.rb, note.rb, tag.rb, client_tag.rb
└── current.rb (ActiveSupport::CurrentAttributes)

db/seeds.rb (10 users/clients/services/bookings configured)
docker-compose.yml + Dockerfile
config/routes.rb
app/assets/tailwind/application.css (design system tokens)
```
