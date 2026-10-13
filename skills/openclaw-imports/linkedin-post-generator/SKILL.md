---
name: linkedin-post-generator
description: Generate compelling LinkedIn posts based on reverse-engineered style patterns and structures. Tailored for highlighting tools, solutions, and user benefits using frameworks inspired by top performers like Claude Cowork. Use when: (1) creating LinkedIn content for product launches, tool showcases, or solution pitches, (2) crafting posts that emphasize benefits and practical value, (3) needing structured posts with consistent engagement hooks, or (4) generating multiple post variations from a core message or use case.
---

# LinkedIn Post Generator Skill

Generate professional, engagement-optimized LinkedIn posts using reverse-engineered style patterns from high-performing content. This skill helps you craft posts that highlight tools, solutions, and user benefits with proven structural frameworks.

## When to Use This Skill

- **Product/Tool Showcases**: Launching or highlighting a tool or feature
- **Solution-Focused Posts**: Explaining how something solves a real problem
- **Benefit-Driven Content**: Emphasizing user value and practical outcomes
- **Engagement Optimization**: Structuring posts for maximum reach and interaction
- **Content Variation**: Generating multiple post versions from one core idea

## Core Patterns

LinkedIn posts that perform well typically follow one of these reverse-engineered patterns:

### Pattern 1: Problem → Solution → Benefit (PSB)
```
Hook: Highlight the pain point
Body: Describe the solution concisely
CTA: Show the user benefit
```

### Pattern 2: "I Used to..." → "Then I discovered..." (Journey Pattern)
```
Hook: Relatable frustration or mistake
Body: The turning point or discovery
CTA: Outcome and learning
```

### Pattern 3: Data + Insight + Action (DIA)
```
Hook: Striking statistic or observation
Body: What it means (the insight)
CTA: What to do about it
```

### Pattern 4: Feature → Use Case → Value (FUV)
```
Hook: What the tool/feature does
Body: Real-world scenario where it helps
CTA: Why it matters (ROI, speed, quality)
```

### Pattern 5: List + Insight Pattern
```
Hook: "X ways to..." or "X common mistakes..."
Body: Concise list (3-5 items with brief explanations)
CTA: Meta-insight or invitation to share
```

## Quick Start

Use the CLI to generate posts:

```bash
linkedin-post-generator --topic "Claude Cowork collaboration" --pattern psb --tone professional
```

Or generate from a use case:

```bash
linkedin-post-generator --use-case "Engineering team struggling with context switching" --solution-type tool --highlights ["real-time sync", "AI-assisted focus"]
```

## Parameters

- `--topic`: Main subject for the post
- `--pattern`: Which framework to use (psb, journey, dia, fuv, list)
- `--tone`: Voice style (professional, conversational, thought-leader, founder)
- `--highlights`: Key benefits or features to emphasize (comma-separated or array)
- `--use-case`: Specific problem or scenario (auto-generates topic if not provided)
- `--solution-type`: Type of solution (tool, process, framework, insight)
- `--length`: Post length (short: <100 words, medium: 100-250, long: 250+)
- `--variations`: Number of post versions to generate (default: 1)

## Output

Each post includes:
- **Hook**: Opening line designed to stop scrolling
- **Body**: 2-4 sentences of substance
- **CTA**: Call-to-action or closing thought
- **Metadata**: Pattern used, estimated engagement drivers, suggested hashtags

## Style Principles

Posts generated follow these proven engagement drivers:

1. **Specificity over vagueness** - Use concrete examples, not abstractions
2. **Benefit-first** - Lead with user value, not features
3. **Relatability** - Connect to common pain points or goals
4. **Brevity** - Respect reader attention; every sentence earns its place
5. **Action-oriented** - End with a clear thought or question for engagement
6. **White space** - Use line breaks strategically for readability

## Examples

See [references/post-examples.md](references/post-examples.md) for detailed examples of each pattern in action, including Claude Cowork-style posts that emphasize collaboration and team benefits.

See [references/linkedin-styles.md](references/linkedin-styles.md) for voice profiles, tone variations, and how to adapt posts for different audiences (founders, engineers, managers, creators).

## Advanced Usage

### Tone Profiles

- **Professional**: Authoritative, well-researched, enterprise-ready
- **Conversational**: Friendly, personal story, "been there" energy
- **Thought-Leader**: Contrarian, forward-thinking, industry insights
- **Founder**: Scrappy, outcome-focused, hands-on learning
- **Creator**: Behind-the-scenes, process-focused, relatable journey

### Combining Patterns

For longer posts (250+ words), combine two patterns:
- PSB + DIA: Problem, solution, data insight
- Journey + List: Personal story + actionable takeaways
- FUV + DIA: Feature value + statistical backing

### Post Sequencing

Generate complementary posts for a campaign:
- Post 1 (Hook): Problem awareness + surprising stat
- Post 2 (Value): How the tool/solution works
- Post 3 (Story): Real user experience or case study
- Post 4 (CTA): Direct benefit or invitation to try

## Scripts

Use `scripts/generate.py` to programmatically create posts:

```python
from generate import LinkedInPostGenerator

gen = LinkedInPostGenerator()
post = gen.create(
    topic="Real-time collaboration",
    pattern="psb",
    highlights=["sync", "context preservation", "AI-assisted"]
)
print(post)
```

## Integration

Posts are returned as structured JSON with:
- `hook`: Opening line
- `body`: Main content
- `cta`: Closing or call-to-action
- `pattern_used`: Which framework was applied
- `suggested_hashtags`: Relevant tags for reach
- `engagement_drivers`: Why this post should perform well

Use this structure to integrate with publishing tools, scheduling systems, or further editing workflows.
