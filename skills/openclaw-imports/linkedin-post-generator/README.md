# LinkedIn Post Generator - Start Here

Welcome to the LinkedIn Post Generator skill! This guide tells you what to read first.

## 📖 Reading Order

### 1. **Start Here: SKILL.md** (5 min read)
This is the main skill documentation. It explains:
- What the skill does
- The 5 reverse-engineered patterns
- Quick start commands
- When to use this skill

→ Read this first to understand the skill's purpose and capabilities.

### 2. **See It In Action: references/post-examples.md** (10 min read)
This file shows working examples of all 5 patterns with:
- Real post examples for each pattern
- Claude Cowork-style posts throughout
- How different tones sound
- What makes posts engage

→ Read this to see what the skill actually produces.

### 3. **Understand Your Audience: references/linkedin-styles.md** (10 min read)
This file covers:
- 5 voice profiles (Professional, Conversational, Thought-Leader, Founder, Creator)
- How to write for different audiences (Engineers, Managers, Founders, etc.)
- Tone shifts for different contexts
- What resonates with each audience

→ Read this before generating posts for a specific audience.

### 4. **Publish & Integrate: references/integration-guide.md** (15 min read)
This file explains:
- How to use the Python API
- CLI command examples
- Integration with publishing tools
- Best practices
- Common use cases with ready-to-copy commands

→ Read this when you're ready to generate posts or integrate with other tools.

## 🚀 Quick Start (30 seconds)

Generate your first post:
```bash
cd /path/to/linkedin-post-generator
python scripts/generate.py --topic "Your topic here" --pattern psb --tone professional
```

## 🎯 Common Scenarios

### "I want to generate a post about my product launch"
1. Read: SKILL.md (understanding patterns)
2. Run: `python scripts/generate.py --topic "Your product" --pattern fuv --tone professional`
3. Read: references/linkedin-styles.md (audience section)
4. Customize the output to match your brand voice
5. Publish to LinkedIn

### "I want to write a thought leadership post"
1. Read: references/linkedin-styles.md (Thought-Leader profile)
2. Run: `python scripts/generate.py --topic "Your insight" --pattern dia --tone thought-leader`
3. Review: references/post-examples.md (DIA pattern section)
4. Edit and refine
5. Publish

### "I need multiple post variations for a campaign"
1. Read: references/integration-guide.md (Campaign Strategy section)
2. Run: `python scripts/generate.py --topic "Campaign theme" --variations 5 --output json`
3. Export to JSON for scheduling
4. Customize each variation
5. Publish across days/weeks

## 📁 File Guide

| File | Purpose | Read When |
|------|---------|-----------|
| **SKILL.md** | Main documentation | First - understand what it does |
| **OVERVIEW.md** | Quick reference | Want a 2-minute summary |
| **references/post-examples.md** | Working examples | Want to see actual output |
| **references/linkedin-styles.md** | Voice & audience | Writing for specific audience |
| **references/integration-guide.md** | Integration & API | Ready to use in your workflow |
| **scripts/generate.py** | The actual script | Using Python or CLI |
| **VALIDATION.md** | Quality report | Want to verify everything works |
| **COMPLETION_REPORT.md** | What was built | Want the full details |

## 💡 Pro Tips

### Tip 1: Choose Pattern First
Different patterns work for different goals:
- **psb** (Problem → Solution → Benefit) = Feature launches
- **journey** ("I used to...") = Personal stories
- **dia** (Data + Insight) = Thought leadership
- **fuv** (Feature → Use Case → Value) = Product highlights
- **list** (Items + Insight) = Frameworks & tips

### Tip 2: Match Tone to Audience
- **professional** → Executives, enterprises
- **conversational** → Engineers, peers
- **thought-leader** → Industry leaders
- **founder** → Startup community
- **creator** → Community, behind-the-scenes

### Tip 3: Use Highlights for Specificity
```bash
# Generic (okay)
--topic "Productivity"

# Specific (better - posts will be more targeted)
--topic "Productivity" \
--highlights "40% faster shipping,reduced meetings,shared context"
```

### Tip 4: Generate JSON for Scheduling
```bash
# Generate multiple variations as JSON
python scripts/generate.py --topic "X" --variations 3 --output json > posts.json

# Then use with scheduling tools (Postiz, Buffer, etc.)
```

## 🎓 Learning Path

**Beginner (30 minutes)**
1. Read SKILL.md
2. Try one CLI command
3. Read references/post-examples.md

**Intermediate (1 hour)**
1. Read all of SKILL.md
2. Try multiple patterns and tones
3. Read references/linkedin-styles.md
4. Practice with your own topics

**Advanced (2+ hours)**
1. Deep dive into references/integration-guide.md
2. Read references/linkedin-styles.md for your audience
3. Use Python API for automation
4. Integrate with scheduling tools

## ❓ FAQs

**Q: Which pattern should I use?**
A: Read SKILL.md "Core Patterns" section for a quick overview. For details, see references/post-examples.md.

**Q: How do I make posts more specific to my product?**
A: Use the `--highlights` parameter with your specific benefits: `--highlights "feature1,benefit2,outcome3"`

**Q: Can I use this with LinkedIn's scheduling tools?**
A: Yes! Use `--output json` to export posts for Postiz, Buffer, or other scheduling tools. See references/integration-guide.md for details.

**Q: How do I integrate this with my own code?**
A: Read references/integration-guide.md "Python Integration" section for examples.

**Q: What if the output doesn't match my brand voice?**
A: The skill generates a starting point. Edit freely! See references/linkedin-styles.md for voice guidance.

## 🤔 Still Have Questions?

- **Understanding patterns?** → SKILL.md + references/post-examples.md
- **Writing for specific audience?** → references/linkedin-styles.md
- **Using in your workflow?** → references/integration-guide.md
- **Technical details?** → VALIDATION.md or look at scripts/generate.py

---

**Ready?** Start with SKILL.md, then try your first command!

```bash
python scripts/generate.py --topic "Your topic" --pattern psb --tone professional
```
