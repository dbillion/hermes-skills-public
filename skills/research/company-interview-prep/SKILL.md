---
name: company-interview-prep
description: "Deep company research + interview preparation. Research a target company across GitHub, engineering blogs, job boards, case studies, and news — then map the candidate's experience to the company's needs, generate STAR stories, and prepare application answers. Triggers on: research company for interview, company deep dive, prepare for interview at X, what should I know before interviewing at X, company research + interview prep."
---

# Company Deep-Dive + Interview Prep

Research a target company thoroughly, then produce a complete interview preparation package: company profile, tech stack analysis, value mapping, STAR stories, and application question answers.

## Research Pipeline (Multi-Source)

Run these searches **in parallel** to gather data efficiently:

### Phase 1: Company Fundamentals
```
web_search: "{Company} tech stack engineering architecture 2025 2026"
web_search: "{Company} engineering blog infrastructure backend"
web_search: "{Company} open source GitHub contributions"
web_search: "{Company} company size funding revenue 2025 2026"
web_extract: "{Company careers page URL}"
```

### Phase 2: Product & Technology Deep Dive
```
web_extract: "{Company GitHub org URL}"
web_search: "{Company} API platform developer SDK"
web_search: "{Company} case study engineering challenges"
web_search: "{Company} infrastructure AWS GCP Azure"
```

### Phase 3: Role-Specific Intelligence
```
web_extract: "{Job posting URL from Greenhouse/LinkedIn/etc}"
web_search: "{Company} interview process experience"
web_search: "{Company} team structure engineering culture"
```

### Phase 4: Recent News & Context
```
web_search: "{Company} latest news product launch partnership"
web_search: "{Company} competitors market position"
```

## Output Structure

Produce a comprehensive research document with these sections:

### 1. Company Profile
- What they do (1-2 sentences)
- Size, stage, funding
- Key products and users
- Mission/values (from careers page)

### 2. Tech Stack Breakdown
- Languages & frameworks
- Cloud & infrastructure
- AI/ML stack (if applicable)
- Architecture patterns (microservices, serverless, etc.)

### 3. What They're Building (from GitHub + blogs)
- Key repositories and what they indicate
- Engineering blog themes
- Recent technical wins or challenges

### 4. Platform/Backend Team Specifics
- What the team owns
- Key responsibilities from job postings
- Required vs preferred skills
- Tech stack for the role

### 5. Where the Candidate Brings Value
Map the candidate's specific experience to the company's needs:
- Direct skill matches (language, cloud, framework)
- Domain experience (telecom, AI, scale, etc.)
- Differentiators (unique combinations)
- Growth areas (where they'd have most impact)

### 6. STAR Stories (3-5 stories)
Generate stories using the STAR format:
- **S**ituation: Context
- **T**ask: What needed to happen
- **A**ction: What the candidate did
- **R**esult: Measurable outcome
- **Why it fits**: Explicit connection to what the company needs

Story types to cover:
1. Owning a system end-to-end (ownership)
2. Building something from scratch (greenfield)
3. Performance optimization at scale (backend depth)
4. Cross-functional collaboration (teamwork)
5. Learning fast under pressure (adaptability)

### 7. Application Question Answers
Draft answers for common required questions:
- "Why [Company]?"
- "Hard technical problem you've worked on"
- "Tell me about yourself"
- "How did you hear about this?"

### 8. Questions the Candidate Should Ask
Prepare 5-6 strategic questions that show deep research:
- Team structure and biggest challenge
- Tech stack decisions
- Growth opportunities
- Culture and working style

## Best Practices

- **Cross-reference sources**: Don't trust a single source. Verify tech stack across GitHub, job postings, and engineering blogs.
- **Look for case studies**: Companies often publish infrastructure migration stories (e.g., "How we reduced latency by X%") — these reveal real challenges.
- **Check GitHub org activity**: Recent commits, active repos, and fork patterns reveal engineering priorities.
- **Read the CEO/founder blog**: Often reveals company direction and cultural values.
- **Salary benchmarks**: Research rates for the role/region if not in the posting.
- **Competitor awareness**: Know who they compete with — it shows strategic thinking.

## Pitfalls

- **Don't just summarize Wikipedia**: The value is in connecting the dots between what they build and what the candidate can do.
- **Don't fabricate experience**: Only use real projects from the candidate's history. Infer from past sessions or ask.
- **Don't ignore culture**: A company's cultural values (from careers page) should shape how stories are told.
- **Don't skip the "why"**: Every story must explicitly connect back to why it matters to THIS company.

## Tool Usage

Use `web_search` for broad discovery, `web_extract` for deep content from specific URLs. Run searches in parallel (multiple web_extract calls in one block) for speed.

For generating artifacts (slides, reports, audio), chain with `nlm` CLI after compiling research into a source document.
