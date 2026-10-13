---
name: africana-corn-drop
description: "Research and build a 'corn drop' — a business case document + free-tech stack blueprint for selling AI/automation services to local African merchants (hair sellers, food merchants, event planners, dressers/MUA). Use when the user asks to research free APIs, build revenue projections, or create a pitch asset for African local business automation services."
version: 1.0.0
author: Hermes Agent / bornofGod
license: MIT
metadata:
  hermes:
    tags: [business-research, africa, automation, go-to-market, pitch]
---

# African Local Business Corn Drop

## Overview

A "corn drop" is a complete business case + tech stack document you build to sell automation/AI services to local service merchants in Africa. The target clients are technician-run micro-businesses: hair braiders, food merchants, event planners, dressers/MUA, barbers, tailors.

The corn drop contains everything needed to onboard a paying merchant: free API stack, setup steps, cost projections, revenue projections per merchant type, and advertising copy — all framed around **money the merchant is losing**, not technology.

## When to Use

- User asks to "build a corn drop," "create a pitch," "research free APIs for [merchant type]"
- User wants revenue projections for local business automation services
- User is building a go-to-market asset for African micro-business SaaS/automation
- User asks to compare free vs paid API options for messaging, CRM, payments in Africa

## Research Methodology

### 1. Free API Research (always lead with free)

For each layer of the stack, find the cheapest/free option:

| Layer | Primary Free Option | Backup (cheap paid) |
|---|---|---|
| Client database | Google Sheets API (free) | Zoho CRM Free (3 users) |
| Merchant interface | Telegram Bot API (free via BotFather) | WhatsApp Business App (free) |
| WhatsApp messaging | WhatsApp Business App broadcast (free, 256 contacts) | Termii Starter ($0/agent), Africa's Talking |
| SMS fallback | Termii Starter (free tier, then $0.025/SMS) | Africa's Talking ($0.008-0.07/msg) |
| Notes/CRM | Google Sheets | Zoho CRM Free, HubSpot Free (1000 contacts, 2 users) |
| Automation engine | n8n self-hosted (free) or Hermes cron jobs | Zapier free tier, Make free tier |
| Hosting | Oracle Cloud free tier, Railway free | Render free tier |
| Payments (merchant receives) | Paystack (Nigeria, 1.5%), Flutterwave | MTN MoMo API (Ghana, Uganda) |
| AI content gen | OpenRouter (Claude Haiku ~$0.01/msg) | NLM via Hermes |
| Landing page | GitHub Pages (free HTML) | Carrd free tier |

### 2. Pricing Research

Always include real local pricing. Search for:
- Average service price per merchant type per country (braiding, catering, event planning)
- WhatsApp message costs per country via Africa's Talking or Termii
- Mobile money transaction fees per country

Default country focus: **Nigeria** (₦), **Ghana** (GH¢), **Kenya** (KES) — adjust per user.

### 3. Revenue Projections (the core of the corn drop)

Build a table per merchant type with:
- Average service price
- Client database size assumption (50-200 for hair, 20-50 for events)
- Without-AI rebooking rate (~15%)
- With-AI rebooking rate (~35-50%)
- Monthly/quarterly/yearly extra revenue
- System cost for the same period
- ROI multiple

Always frame: **"You're losing ₦X/month to clients who forgot about you"** — this is the hook.

### 4. Copy Angle

Advertising copy for the corn drop MUST:
- Lead with money lost, not technology
- Use the merchant's name and business type
- Include specific local currency amounts
- End with a call to action that costs nothing ("Set up is free")

Template:
> "[Name], how many of your old clients haven't called you in 3 months? If even 5 came back for [service] at [price], that's [amount] you left on the table. We set up a free system that messages them for you automatically — you just chat with our bot on Telegram. First rebooking is usually within 2 weeks."

## Corn Drop Output Structure

Every corn drop document should have:

1. **The Problem** — money merchant is losing to forgetful clients
2. **The Fix** — automated follow-up system via Telegram
3. **The Free Stack** — table of free APIs with costs
4. **The Math** — per-merchant-type revenue projections (table format)
5. **ROI Timeline** — day 1 to day 90, when first rebooking hits
6. **Your Setup Workflow** — steps to onboard a merchant (2-4 hours first one)
7. **Pricing Models** — how you charge the merchant (setup fee, monthly, revenue share)
8. **Free API Questions** — what you need the user to decide before building
9. **Advertising Copy** — ready-to-send pitch message

## Common Pitfalls

1. **Leading with tech, not money.** The merchant cares about "how many clients come back," not "AI-powered automation." Always translate features into revenue.

2. **Ignoring WhatsApp Business App limits.** The free app caps broadcast at 256 contacts. For larger lists, you need WAHA self-hosted or a paid API. Call this out in the stack table.

3. **Forgetting SMS fallback.** Not all clients have WhatsApp. Africa's Talking SMS at $0.008-0.03/msg is the cheapest fallback. Always include it.

4. **Using USD when the merchant thinks in local currency.** Convert everything. In Nigeria, merchants think in ₦, not dollars.

5. **No ROI timeline.** Merchants want to know "when do I see money back?" Always include a week-by-week timeline showing first rebooking.

6. **Overcomplicating the stack.** Start with Google Sheets + Telegram + free WhatsApp. That's enough for the first 10 merchants. Don't add n8n/Zapier unless the user specifically wants automation beyond cron jobs.

## Related Frameworks

Load these ~/.gemini/skills/ references for the corn drop methodology:
- leads-mastery — Core Four lead gen, lead magnets, referral systems
- offers-mastery — Grand Slam Offer, value equation, pricing anchors, guarantees
- emyth-mastery — Systems-dependent business design (you're building a franchise prototype)
- trend-to-strategy — Market discovery + NLM synthesis for content/trend alerts

## API Pricing Reference

See `references/api-pricing.md` for current free/cheap API pricing across Africa:
- WhatsApp, SMS, CRM, payments, hosting tiers
- Local service pricing per merchant type (for revenue projections)
- Updated: May 2026 — re-verify pricing before each corn drop
