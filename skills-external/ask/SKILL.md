---
name: ask
description: Ask questions about the codebase, AI will search and answer
---
{{#if args}}
# ❓ Ask About Codebase

**Question:** {{args}}

## Instructions:

1. **Search the codebase** to find relevant files and code
2. **Analyze** the code structure and patterns
3. **Answer** the question based on actual code

## Search Strategy:
- Look for files related to the question keywords
- Read relevant source files
- Check imports and dependencies
- Look at tests for usage examples

## Answer Format:

### 📋 Answer
[Direct answer to the question]

### 📁 Relevant Files
- `file1.ts` - [description]
- `file2.ts` - [description]

### 💡 Code Examples
```typescript
// relevant code snippets
```

### 🔗 Related
- [other related concepts or files]

---

Now search the codebase and answer: "{{args}}"
{{else}}
# ❓ Ask About Codebase

Ask any question about the codebase and get AI-powered answers.

## Usage:
```
/ask <your question>
```

## Examples:
```
/ask How does authentication work?
/ask Where is the user model defined?
/ask What API endpoints are available?
/ask How do I add a new route?
/ask Where are database queries made?
```

## What it does:
1. Searches codebase for relevant files
2. Analyzes code structure and patterns
3. Provides answer based on actual code
4. Shows relevant code snippets

Ask your question!
{{/if}}
