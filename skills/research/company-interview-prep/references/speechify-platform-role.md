# Speechify Platform Role — Research Reference

## Company Snapshot
- **What they do**: Voice AI platform — text-to-speech, voice assistant, voice agents
- **Scale**: 50M+ users, 161B characters synthesized/month, ~1000 req/s
- **Stage**: Growth-stage, ~200 people, fully remote, profitable
- **Awards**: 2025 Apple Design Award (Inclusivity), Chrome Extension of the Year (Google)

## Tech Stack
| Layer | Tech |
|---|---|
| Backend | TypeScript/Node.js, Go, Python |
| Frontend | React, TypeScript |
| Mobile | Swift (iOS), Kotlin (Android), Kotlin Multiplatform |
| Cloud | GCP (primary), AWS, Azure |
| Inference | Baseten (model serving), vLLM |
| AI/ML | Proprietary SIMBA voice models, Python |
| Infra | Docker, Kubernetes, Cloudflare Workers |

## Platform Team Owns
- Payments & subscriptions
- Analytics
- TTS API (public + internal)
- Auth, consumption tracking
- B2B/enterprise solutions
- External APIs

## Key Open Source (GitHub: SpeechifyInc, 64 repos)
- Meta-voicebox (594 stars) — generative speech model
- speechify-api-sdk-python, speechify-api-sdk-typescript
- speechify-api-cookbook (updated Jun 2026)
- Cloudflare Workers for agent tracking
- Forks: olmocr, SpecForge, textract, epub-lib

## Engineering Insights
- Migrated from self-managed 940 GPUs to Baseten → 44% cost reduction, 30-50% latency improvement
- SIMBA 3.0: <250ms latency, 1000+ voices, 60+ languages
- LiveKit partnership for real-time voice agents
- Vertically integrated AI Research Lab (no third-party voice models)

## Role Requirements (from job posting)
- Required: TS/Node.js, GCP (AWS/Azure ok)
- Preferred: Docker, Kubernetes, high availability deployments
- Culture: "Extreme ownership, no micromanagement, move fast"

## Salary Range
- $140K–$200K/year (US-based, remote worldwide)

## Interview Process
- Several technical interviews, completed within 1 week
- Application questions: "Why Speechify?", "Hard technical problem", "How did you hear about this?"

## Where Candidate (bornofGod) Fits
- Go + Python + TS = exact backend stack
- GCP experience = primary cloud
- Scale experience (40% latency reduction, 99.9% reliability)
- AI system building (MCP-driven agents, greenfield)
- Telecom experience (Ericsson) = relevant domain
- EU-based, remote-ready

## Sources Researched
- GitHub: https://github.com/SpeechifyInc
- Careers: https://speechify.com/careers/
- Job posting: https://job-boards.greenhouse.io/speechify/jobs/5058944004
- Baseten case study: https://www.baseten.co/resources/customers/speechify-real-time-text-to-speech/
- Speechify blog: https://speechify.com/blog/inside-simba-3-voice-model-powering-speechify/
- LiveKit partnership: https://speechify.com/news/speechify-launches-partnership-with-livekit-to-power-ai-voice-agents/
- Himalayas tech stack: https://himalayas.app/companies/speechify/tech-stack
