# LinkedIn Post Generator Skill - Summary

**Status:** ✅ Complete and tested

## What This Skill Does

Generates compelling LinkedIn posts using reverse-engineered patterns from high-performing content (like Claude Cowork examples). Posts are structured to highlight tools, solutions, and user benefits with proven engagement frameworks.

## Key Files

### Core Files
- **SKILL.md** - Main skill documentation with pattern overview and quick start
- **scripts/generate.py** - Python script for programmatic post generation (tested and working)

### Reference Documentation
- **references/post-examples.md** - Detailed working examples of all patterns with Claude Cowork-style demonstrations
- **references/linkedin-styles.md** - Voice profiles, audience adaptations, tone guidance, and success metrics
- **references/integration-guide.md** - How to integrate with publishing tools, APIs, and workflows

## Capabilities

### 5 Reverse-Engineered Patterns
1. **PSB (Problem → Solution → Benefit)** - Feature/solution focus
2. **Journey** - Personal story and discovery
3. **DIA (Data + Insight + Action)** - Metric-driven insights
4. **FUV (Feature → Use Case → Value)** - Product highlights
5. **List + Insight** - Frameworks and tips

### 5 Tone Profiles
- Professional (enterprise, authoritative)
- Conversational (peers, relatable)
- Thought-Leader (frameworks, contrarian)
- Founder (scrappy, outcome-focused)
- Creator (behind-the-scenes, community)

### Smart Features
- Automatic engagement driver identification
- Relevant hashtag suggestions
- Structured JSON output for integration
- CLI and Python API interfaces
- Batch generation with variations
- Use-case to topic inference

## Example Outputs

### Professional Post (Claude Cowork style)
```
Enterprise leaders report Claude Cowork real-time collaboration.

The key: shared context, real-time sync, async shipping. This changes how teams approach collaboration.

How would this change your team's workflow?

#devtools #productivity #leadership #tech #innovation
```

### Conversational Post
```
I used to think context switching was a minor problem.

Then I realized:
• Real-time sync eliminates friction
• Shared context enables async shipping
• Decision history prevents repeated arguments

That changed everything about my approach.
```

## Quick Start

```bash
# Generate a single post
python scripts/generate.py --topic "Your topic" --pattern psb --tone professional

# Generate with specific benefits
python scripts/generate.py \
  --topic "Claude Cowork collaboration" \
  --pattern fuv \
  --highlights "real-time sync,async shipping,shared context"

# Generate multiple variations
python scripts/generate.py \
  --topic "Engineering productivity" \
  --variations 3 \
  --output json

# Use from Python
from scripts.generate import LinkedInPostGenerator
gen = LinkedInPostGenerator()
post = gen.create(topic="Real-time collaboration", pattern="psb", tone="professional")
print(post.render_full())
```

## Why This Skill Works

✅ **Based on reverse-engineering** - Patterns extracted from high-performing LinkedIn posts
✅ **Emphasizes benefits** - Posts lead with user value, not features
✅ **Multiple frameworks** - 5 patterns for different situations and audiences
✅ **Tone flexibility** - 5 voice profiles for different audiences and contexts
✅ **Integration-ready** - JSON output, Python API, CLI support
✅ **Customizable** - Easy to extend with new patterns, tones, or hashtags
✅ **Quality-focused** - Engagement drivers identified, hashtags suggested, CTA included

## Testing Results

All patterns tested and working:
- ✅ PSB pattern: Professional tone, specific benefits
- ✅ Journey pattern: Conversational tone, personal story
- ✅ DIA pattern: Thought-leader tone, metric-driven
- ✅ FUV pattern: Conversational tone, use-case focus
- ✅ List pattern: Multiple variations, engagement questions
- ✅ JSON output: Structured for downstream processing
- ✅ CLI interface: Easy command-line usage
- ✅ Batch generation: Multiple variations working correctly

## File Structure

```
linkedin-post-generator/
├── SKILL.md                               # Main skill documentation
├── scripts/
│   └── generate.py                        # Executable post generator
└── references/
    ├── post-examples.md                   # Working examples of each pattern
    ├── linkedin-styles.md                 # Voice profiles & audience guidance
    └── integration-guide.md               # Publishing & API integration
```

## Next Steps for Users

1. **Read SKILL.md** - Understand the patterns and when to use each
2. **Review references/post-examples.md** - See working examples
3. **Try the CLI** - Generate posts for your topics
4. **Customize** - Edit outputs to match your brand voice
5. **Publish** - Use with LinkedIn API or scheduling tools
6. **Iterate** - Learn what resonates and optimize future posts

## Design Principles

- **Concise**: Every sentence earns its place
- **Specific**: Generic advice is ignored; specificity is magnetic
- **Relatable**: Abstract concepts don't convert; relatable problems do
- **Actionable**: Posts end with something readers can think about or do
- **Tool-integrated**: Ready for automation, APIs, and publishing workflows

---

**Ready to generate high-quality LinkedIn posts that emphasize your tools, solutions, and user benefits.**
