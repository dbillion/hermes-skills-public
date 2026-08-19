---
name: cms-api
description: "REST API patterns and endpoint design for hair practitioner CMS — auth, CRUD, scheduling"
version: 1.0.0
author: bornofGod
tags: [cms, api, rest, hair-practitioner, endpoints]
---

# CMS API Design — Hair Practitioner

## Authentication

> **⚠️ Auth differs by stack:**
> - **Rails stack (CRMHub):** Session-based auth via `has_secure_password` + Pundit. No JWT. Controllers use `authenticate_user!` via Devise/Pundit. Password resets via Rails mailer.
> - **Node.js stack:** JWT-based auth (access + refresh tokens). Role-based access control (admin, stylist, receptionist, client). Password reset flow via token email link.

## CRMHub Rails API Reference

> **CRMHub is NOT a separate API-mode app.** It is a Rails monolith. Authentication routes are standard Devise session routes (`/users/sign_in`, `/users/sign_up`, `/users/sign_out`). All CRUD is through Rails resourceful routing. Do NOT design or expect `/api/*` JWT endpoints for CRMHub.

For CRMHub, controllers live at `app/controllers/` and routes are standard RESTful Rails routes. Hotwire Turbo handles the frontend reactivity — no separate API json endpoints needed for internal use.

The endpoints listed below apply to **Stack B (Node.js/greenfield)** only.

## Core Endpoints

### Auth
```
POST /api/auth/register
POST /api/auth/login
POST /api/auth/refresh
POST /api/auth/forgot-password
```

### Users / Staff
```
GET /api/staff
GET /api/staff/:id
PUT /api/staff/:id
GET /api/staff/:id/schedule
PUT /api/staff/:id/schedule
GET /api/staff/:id/appointments
GET /api/staff/:id/clients
```

### Clients
```
GET /api/clients
GET /api/clients/:id
POST /api/clients
PUT /api/clients/:id
GET /api/clients/:id/history
GET /api/clients/:id/formulas
GET /api/clients/:id/photos
```

### Services
```
GET /api/services
POST /api/services
PUT /api/services/:id
DELETE /api/services/:id
```

### Appointments
```
GET /api/appointments
GET /api/appointments/:id
POST /api/appointments
PUT /api/appointments/:id
PATCH /api/appointments/:id/status
DELETE /api/appointments/:id
GET /api/appointments/slots?date=&staff_id=
```

### Formulas
```
GET /api/formulas?client_id=
POST /api/formulas
PUT /api/formulas/:id
DELETE /api/formulas/:id
```

### Products / Inventory
```
GET /api/products
POST /api/products
PUT /api/products/:id
GET /api/products/low-stock
POST /api/products/:id/adjust
```

### Photos
```
POST /api/photos
GET /api/photos?client_id=
DELETE /api/photos/:id
```

### Reviews
```
GET /api/reviews?staff_id=
POST /api/reviews
PUT /api/reviews/:id
```

### Reports
```
GET /api/reports/revenue?from=&to=
GET /api/reports/retention
GET /api/reports/popular-services
GET /api/reports/staff-performance
```

## API Patterns
- Use query params for filtering: `?page=1&limit=20&sort=created_at&order=desc`
- Return pagination metadata: `{ data, page, limit, total, totalPages }`
- Use appropriate HTTP status codes
- Validate input at the boundary
- Rate limiting on auth endpoints
- CORS configured for frontend domain
