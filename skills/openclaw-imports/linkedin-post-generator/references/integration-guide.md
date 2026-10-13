# LinkedIn Post Generator - Integration Guide

This guide shows how to integrate the LinkedIn Post Generator into your workflows and publishing pipelines.

## Python Integration

### Basic Usage

```python
from scripts.generate import LinkedInPostGenerator

gen = LinkedInPostGenerator()

# Simple generation
post = gen.create(
    topic="Claude Cowork collaboration features",
    pattern="psb",
    tone="professional",
)

print(post.render_full())
print("Engagement drivers:", post.engagement_drivers)
```

### Advanced Usage with Highlights

```python
# With specific benefits to highlight
post = gen.create(
    topic="Real-time context sync",
    pattern="fuv",
    tone="conversational",
    highlights=[
        "Eliminates context switching",
        "40% faster shipping",
        "Async teams move at network speed"
    ],
    solution_type="tool"
)

print(post.to_dict())  # Get as structured JSON
```

### Batch Generation with Variations

```python
# Generate multiple variations automatically
posts = []
for i in range(3):
    post = gen.create(
        topic="Engineering productivity",
        pattern=random.choice(list(gen.patterns.keys())),
        tone=random.choice(list(gen.tones.keys())),
    )
    posts.append(post)

# Export as JSON for further processing
import json
with open('posts.json', 'w') as f:
    json.dump([p.to_dict() for p in posts], f, indent=2)
```

---

## CLI Integration

### Command-Line Usage

Generate a single post:
```bash
python scripts/generate.py --topic "Real-time collaboration" --pattern psb --tone professional
```

Generate multiple variations:
```bash
python scripts/generate.py \
  --topic "Context management" \
  --pattern dia \
  --tone thought-leader \
  --highlights "async clarity,decision docs,knowledge retention" \
  --variations 3
```

Generate from use case:
```bash
python scripts/generate.py \
  --use-case "Engineering teams losing productivity to context switching" \
  --solution-type tool \
  --tone conversational
```

Output as JSON for processing:
```bash
python scripts/generate.py \
  --topic "AI-assisted development" \
  --pattern fuv \
  --tone founder \
  --output json > posts.json
```

---

## Pattern Selection Guide

Choose your pattern based on your goal:

| Pattern | Best For | Example |
|---------|----------|---------|
| **psb** | Feature launches, solution emphasis | "Shipping faster with real-time sync" |
| **journey** | Personal stories, learning narratives | "How I discovered async was broken" |
| **dia** | Data-backed insights, trend discussion | "Teams with better context ship 40% faster" |
| **fuv** | Feature announcements, product highlights | "Just shipped: real-time collaboration" |
| **list** | Frameworks, common mistakes, tips | "5 ways teams waste productivity" |

---

## Tone Selection Guide

Match tone to your audience:

| Tone | Audience | Voice |
|------|----------|-------|
| **professional** | Executives, enterprises, formal | Metric-driven, authoritative |
| **conversational** | Engineers, peers, relatable | Personal, "been there" |
| **thought-leader** | Industry leaders, trendsetters | Contrarian, framework-focused |
| **founder** | Startup community, builders | Scrappy, outcome-focused |
| **creator** | Community, behind-the-scenes | Process-transparent, relatable |

---

## Publishing Workflow

### 1. Generate Posts

```bash
python scripts/generate.py \
  --topic "Your topic here" \
  --pattern psb \
  --tone professional \
  --output json > generated_posts.json
```

### 2. Review & Edit

Posts are structured to allow easy editing:
- **hook**: Change if needed for your voice
- **body**: Expand with additional context
- **cta**: Customize to your specific goal
- **hashtags**: Adjust based on your network

### 3. Publish

Posts can be posted directly to LinkedIn, or integrated with scheduling tools:

```python
import json

with open('generated_posts.json') as f:
    posts = json.load(f)

for post in posts:
    # Send to LinkedIn via API or copy-paste
    full_text = post['full_post']
    print(full_text)
```

### 4. Monitor & Learn

Track engagement on generated posts:
- Which patterns resonated most?
- Which tones got highest engagement?
- What audience segments engaged?

Use these insights to refine future generations:
```bash
# Next time, use the pattern/tone that performed best
python scripts/generate.py --pattern "highest_performer" --tone "best_tone"
```

---

## Integration with LinkedIn Scheduling Tools

### For Postiz / Buffer / Later

Export posts as text for copying:

```bash
python scripts/generate.py --topic "Your topic" --output text
```

Then copy the `full_post` into your scheduling tool.

### For LinkedIn API Integration

Export as JSON and integrate with LinkedIn's official API:

```python
import json
import requests

with open('posts.json') as f:
    posts = json.load(f)

for post in posts:
    # Format for LinkedIn API
    payload = {
        'content': post['full_post'],
        'media': [],  # Add media if needed
    }
    
    # POST to LinkedIn endpoint
    # response = requests.post(linkedin_endpoint, json=payload, headers=headers)
```

---

## Best Practices

### 1. **Don't Just Use Default Output**
- Edit hooks to be more specific to your product/audience
- Add data points from your own experience
- Customize CTAs to match your actual goals

### 2. **Test Pattern & Tone Combinations**
- Professional + psb = formal feature launch
- Conversational + journey = relatable peer story
- Thought-leader + dia = trend insight
- Founder + journey = personal learning

### 3. **Use Highlights to Add Specificity**
```bash
# Generic (okay)
python scripts/generate.py --topic "Productivity"

# Specific (better)
python scripts/generate.py --topic "Productivity" \
  --highlights "30% faster shipping,async clarity,decision history"
```

### 4. **Campaign Strategy**
Create a series of complementary posts:
- Post 1: Hook with a problem (dia pattern)
- Post 2: Solution announcement (fuv pattern)
- Post 3: Social proof / journey (journey pattern)
- Post 4: Direct CTA / call-to-action (psb pattern)

### 5. **Track What Works**
Note which patterns/tones get:
- Most saves
- Most comments
- Most shares
- Best audience fit

Then bias toward those in future generations.

---

## Common Use Cases

### Product Launch

```bash
python scripts/generate.py \
  --topic "Claude Cowork real-time sync feature" \
  --pattern fuv \
  --tone professional \
  --highlights "eliminates context lag,enables async shipping,40% faster" \
  --variations 1
```

### Thought Leadership

```bash
python scripts/generate.py \
  --topic "Why async collaboration beats synchronous" \
  --pattern dia \
  --tone thought-leader \
  --variations 1
```

### Community Engagement

```bash
python scripts/generate.py \
  --use-case "Engineers exhausted by context switching" \
  --pattern journey \
  --tone conversational \
  --solution-type tool
```

### Founder Updates

```bash
python scripts/generate.py \
  --topic "Scaling our engineering culture with better tooling" \
  --pattern journey \
  --tone founder \
  --highlights "learned the hard way","40% efficiency gain"
```

### Campaign Series

```bash
for pattern in psb journey dia fuv list; do
  python scripts/generate.py \
    --topic "Real-time engineering collaboration" \
    --pattern $pattern \
    --tone professional
done
```

---

## Customization

### Extend with Custom Tones

Edit `TONE_PROFILES` in `scripts/generate.py`:

```python
TONE_PROFILES['academic'] = {
    'hooks_prefix': ['Research shows...', 'Studies indicate...'],
    'body_style': 'research-backed, evidence-based',
    'cta_style': 'scholarly question',
}
```

### Add Custom Patterns

Add new pattern definitions:

```python
PATTERNS['case-study'] = {
    'name': 'Case Study Pattern',
    'description': 'Company context → challenge → solution → results',
    'structure': ['hook', 'body', 'cta'],
}
```

### Customize Hashtag Database

Add domain-specific hashtags:

```python
HASHTAG_SUGGESTIONS['devtools'] = [
    '#devtools', '#developer', '#engineering',
    '#productivity', '#ide', '#programming'
]
```

---

## Troubleshooting

### Posts Feel Generic

Add more specific highlights:
```bash
# Before: Generic output
--topic "Productivity"

# After: Specific with details
--topic "Engineering productivity" \
--highlights "async decision-making,code review speed,onboarding"
```

### Tone Doesn't Match Brand

Choose tone first, then customize output:
```bash
# Generate with closest tone
python scripts/generate.py --tone professional

# Then edit to match brand voice
```

### Need Different Pattern Focus

Use `--use-case` for more targeted generation:
```bash
python scripts/generate.py \
  --use-case "Specific problem you're solving" \
  --pattern psb
```

---

## Next Steps

1. **Generate**: Create posts using your topic and audience
2. **Edit**: Customize for your brand voice
3. **Publish**: Share on LinkedIn
4. **Monitor**: Track engagement metrics
5. **Iterate**: Use learnings to improve future posts

The generator is a starting point. Your voice and specific examples are what make posts resonate.
