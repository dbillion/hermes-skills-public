# Free API Pricing Reference — African Local Business Stack

## Updated: May 2026

---

## Messaging APIs

### WhatsApp Business App (Meta — FREE)
- Cost: $0 forever
- Broadcast limit: 256 contacts per list
- API access: No — use for manual only or small lists
- Best for: Starting out, <256 contacts

### Termii (termii.com)
- Starter plan: $0/agent/mo (limited contacts, unlimited sender IDs)
- SMS: $0.0250/transaction
- WhatsApp: $0.0060/transaction
- Email: $0.001/transaction
- Voice: $0.0102/minute
- Fraud Guard: $0.001/check
- Covers: Nigeria + West Africa primarily
- Best for: API-first, scaling from free

### Africa's Talking (africastalking.com)
- No permanent free tier (pay-as-you-go)
- Nigeria SMS: varies by volume, ~$0.008-0.07/msg
- Nigeria WhatsApp: $0.012-0.072/msg
- Kenya SMS: KES 0.25-1.50/msg
- Covers: Kenya, Nigeria, Uganda, Ghana, Tanzania, Rwanda, Zambia, South Africa + more
- Best for: Pan-African coverage, USSD

### WAHA (WhatsApp HTTP API — self-hosted, FREE)
- Cost: $0 (self-hosted in Docker)
- Requires: Second phone number with WhatsApp
- Best for: Full automation at zero ongoing cost
- Tutorial: https://www.freecodecamp.org/news/how-to-build-a-self-hosted-whatsapp-bot-with-n8n-and-waha/

---

## CRM

### Google Sheets (FREE)
- Cost: $0
- API: Full REST API via Google Apps Script or gcloud
- Best for: Primary database for <500 clients
- Hack: Use Apps Script + `UrlFetchApp` to trigger WhatsApp/SMS from Sheet

### Zoho CRM Free
- Cost: 0 forever (max 3 users)
- Limits: No workflow automation, no mass email, 10MB storage
- Best for: When you need a real CRM feel

### HubSpot CRM Free
- Cost: $0 forever (max 2 users, 1000 contacts)
- Limits: 2000 marketing emails/mo, basic automation only
- Best for: If merchant needs email marketing built in

---

## Automation

### n8n (self-hosted, FREE)
- Cost: $0 (Docker on any server)
- Integrations: 1000+ apps including Telegram, Google Sheets, WhatsApp
- Telegram trigger: Built-in node
- Best for: Visual workflow automation

### Hermes Cron Jobs (FREE)
- Already available in this environment
- Best for: Simple scheduled reads from Sheets → send messages

### Zapier Free Tier
- Cost: $0 (100 tasks/mo)
- Best for: Non-technical merchants managing their own automations

### Make (Integromat) Free Tier
- Cost: $0 (1000 operations/mo)
- Best for: More complex multi-step automations

---

## Payments

### Paystack (Nigeria)
- Transaction fee: 1.5% (Naira), 3.9% (International)
- Payout: Next business day
- API: Free to integrate
- Best for: Nigerian merchants

### Flutterwave
- Transaction fee: 1.5% domestic, 3.9% international
- Covers: Nigeria, Ghana, Kenya, Uganda, South Africa + 30+ countries
- Best for: Pan-African payouts

### MTN MoMo API
- Developer access: Free via MTN developer portal
- Transaction fees: Standard telco rates apply
- Covers: Ghana, Uganda, Rwanda, Nigeria + 10+ countries
- Best for: Mobile money-first markets

---

## Hosting (FREE tiers)

### Oracle Cloud Free Tier
- Cost: $0 forever (ARM VM, 1GB RAM)
- Best for: Self-hosting n8n + WAHA + bot

### Railway
- Cost: $5/mo free credit (enough for small deployments)
- Best for: Easy Docker deploys

### GitHub Pages
- Cost: $0
- Best for: Static HTML landing pages

### Render Free Tier
- Cost: $0 (spins down after 15min inactivity)
- Best for: Lightweight webhooks

---

## Local Service Pricing (for Revenue Projections)

### Hair Braiding / Styling (Nigeria)
- Box braids: ₦5,000 - ₦25,000
- Cornrows: ₦2,000 - ₦8,000
- Senegalese twist: ₦6,000 - ₦20,000
- Goddess braids: ₦8,000 - ₦50,000
- Touch-up cycle: 45-60 days

### Hair Braiding (Ghana)
- Box braids: GH¢70 - GH¢300
- Cornrows: GH¢35 - GH¢90
- Touch-up cycle: 45-60 days

### Food / Catering (Nigeria)
- Average meal/plate: ₦1,500 - ₦5,000
- Weekly order cycle: 7 days
- Catering event: ₦50,000 - ₦500,000

### Event Planning (Nigeria)
- Small event: ₦100,000 - ₦500,000
- Wedding: ₦500,000 - ₦5,000,000+
- Booking lead time: 1-6 months

### MUA / Event Dresser (Nigeria)
- Bridal makeup: ₦30,000 - ₦150,000
- Event glam: ₦10,000 - ₦50,000
- Touch-up cycle: per event (irregular)
