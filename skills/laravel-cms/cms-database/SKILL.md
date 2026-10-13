---
name: cms-database
description: "Database schema design and optimization for hair practitioner CMS — PostgreSQL, migrations, indexing"
version: 1.0.0
author: bornofGod
tags: [cms, database, postgresql, hair-practitioner, migrations]
---

# CMS Database Design — Hair Practitioner

## Schema Design

### Core Tables
```sql
-- Users & Authentication
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'stylist', 'receptionist', 'client')),
  full_name VARCHAR(255) NOT NULL,
  phone VARCHAR(50),
  avatar_url TEXT,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Staff Profiles (extends users)
CREATE TABLE staff_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  bio TEXT,
  specialties TEXT[], -- array of specialties
  commission_rate DECIMAL(5,2),
  hire_date DATE,
  schedule JSONB -- availability schedule
);

-- Client Profiles (extends users)
CREATE TABLE client_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  allergies TEXT[],
  preferences JSONB,
  notes TEXT,
  total_visits INT DEFAULT 0,
  total_spent DECIMAL(10,2) DEFAULT 0,
  last_visit DATE
);

-- Services
CREATE TABLE services (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  category VARCHAR(100) NOT NULL,
  description TEXT,
  duration_minutes INT NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Appointments
CREATE TABLE appointments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID REFERENCES users(id),
  staff_id UUID REFERENCES users(id),
  service_id UUID REFERENCES services(id),
  scheduled_at TIMESTAMPTZ NOT NULL,
  duration_minutes INT NOT NULL,
  status VARCHAR(50) DEFAULT 'scheduled',
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Formulas (hair color, treatments)
CREATE TABLE formulas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID REFERENCES users(id),
  staff_id UUID REFERENCES users(id),
  name VARCHAR(255),
  formula JSONB NOT NULL, -- {brand, color_code, ratios, developer, notes}
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Products & Inventory
CREATE TABLE products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  brand VARCHAR(255),
  sku VARCHAR(100) UNIQUE,
  quantity INT DEFAULT 0,
  reorder_level INT DEFAULT 5,
  cost_price DECIMAL(10,2),
  supplier VARCHAR(255),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Photos (before/after gallery)
CREATE TABLE photos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID REFERENCES users(id),
  appointment_id UUID REFERENCES appointments(id),
  url TEXT NOT NULL,
  type VARCHAR(20) CHECK (type IN ('before', 'after', 'progress')),
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Reviews
CREATE TABLE reviews (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID REFERENCES users(id),
  staff_id UUID REFERENCES users(id),
  appointment_id UUID REFERENCES appointments(id),
  rating INT CHECK (rating BETWEEN 1 AND 5),
  comment TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Indexing Strategy
```sql
-- Performance indexes
CREATE INDEX idx_appointments_date ON appointments(scheduled_at);
CREATE INDEX idx_appointments_staff ON appointments(staff_id, scheduled_at);
CREATE INDEX idx_appointments_client ON appointments(client_id);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_services_category ON services(category);
CREATE INDEX idx_formulas_client ON formulas(client_id);
CREATE INDEX idx_photos_client ON photos(client_id);
```

## Migration Patterns
- Use UUID primary keys for portability
- Use JSONB for flexible data (schedules, preferences, formulas)
- Always include `created_at` and `updated_at`
- Use soft deletes where appropriate (is_active flag)
- Plan for multi-tenant if serving multiple salons
- For CRMHub/Rails: use `bin/rails generate model` and `bin/rails generate migration` — CLI-first, never hand-edit migrations

## Reference Files
- `references/crmhub-rails-context.md` — Live CRMHub schema (15 tables, roles, gaps, current build state as of 2026-06-28)

## Pitfalls
- **Cron-mode restriction:** Inline Python/Ruby in `terminal` is blocked. Write scripts to disk with `write_file`, then run with `terminal`. Never embed credentials inline.
