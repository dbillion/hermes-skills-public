---
name: cms-frontend
description: "Frontend patterns for hair practitioner CMS — Hotwire/Rails for CRMHub; React/Next.js for greenfield"
version: 1.1.0
author: bornofGod
tags: [cms, frontend, hotwire, rails, hair-practitioner, dashboard]
---

# CMS Frontend — Hair Practitioner

## Two Distinct Stacks

> **Check project before choosing stack.** CRMHub (`/home/deeone/projects/crm_hub/`) uses Stack A. Greenfield projects may use Stack B.

### Stack A — Hotwire/Rails (CRMHub, in active build)
- **Framework:** Rails 8 + Hotwire (Turbo 8 + Stimulus)
- **Styling:** Tailwind CSS 4 (user explicitly rejected React/Vue)
- **Asset pipeline:** Propshaft + Import Maps (no Node.js bundler)
- **No JWT:** Session-based auth only
- **Components:** ViewComponent for reusable UI pieces
- **Design tokens (CRMHub):** Teal `#0D9488`, Geist font, Zinc neutrals, 12px border-radius, white cards, hover shadow
- **Pattern:** Controllers stay thin; business logic lives in `app/services/`; Turbo Streams for dynamic updates
- **Files:** `/home/deeone/projects/.stitch/DESIGN.md` defines all visual rules; `/home/deeone/projects/crm_hub/app/views/` has all ERB templates

### Stack B — React/Next.js (alternative / greenfield)
- **Framework:** React 18+ with Next.js 14 (App Router)
- **Styling:** Tailwind CSS v4 + shadcn/ui components
- **State:** Zustand (lightweight) or React Query for server state
- **Forms:** React Hook Form + Zod validation
- **Calendar:** react-big-calendar or FullCalendar
- **Charts:** Recharts or Chart.js

## Core Pages / Components

### Dashboard
- Today's appointments overview
- Revenue snapshot (week/month)
- Quick actions (book appointment, add client)
- Low stock alerts
- Recent reviews

### Booking / Scheduling
- Calendar view (day/week/month)
- Drag-and-drop appointment creation
- Staff availability display
- Service selection with duration
- Client lookup / creation

### Client Management
- Client list with search/filter
- Client profile page:
  - Contact info
  - Visit history
  - Formula history
  - Photo gallery (before/after)
  - Notes & allergies
  - Spending summary

### Staff Management
- Staff profiles
- Schedule/availability management
- Commission tracking
- Performance metrics

### Services & Products
- Service catalog CRUD
- Product inventory
- Low stock alerts

### Formula Manager
- Formula list per client
- Formula detail view
- Color picker / ratio calculator
- History tracking

### Reports
- Revenue charts
- Client retention metrics
- Popular services
- Staff performance

## Component Library
- Use shadcn/ui for consistent UI
- Custom calendar component for booking
- Photo upload with compression
- Search/select components for clients/staff

## Responsive Design
- Mobile-first (practitioners often work on tablets)
- Touch-friendly calendar
- Swipe gestures for navigation
