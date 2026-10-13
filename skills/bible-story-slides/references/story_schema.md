# story.json schema

`generate_deck.py` reads a single JSON file describing the deck. Structure:

```json
{
  "title": "David and Goliath",
  "big_idea": "God helps us be brave, even when we feel small.",
  "beats": [
    "The Israelite army was scared of a giant soldier named Goliath.",
    "Goliath was huge, and no one dared to fight him.",
    "David was just a young shepherd boy visiting his brothers.",
    "David told the king he was not afraid to fight Goliath.",
    "David picked five smooth stones from a stream.",
    "Goliath laughed because David was so small.",
    "David said, 'I come to you in the name of God.'",
    "David threw one stone from his sling.",
    "The stone hit Goliath, and the giant fell down.",
    "The Israelite army cheered because David trusted God."
  ],
  "takeaways": [
    "We can be brave even when we feel small.",
    "God is with us when we feel afraid."
  ],
  "discussion_questions": [
    "When have you felt small like David?",
    "What is one brave thing you can do this week?"
  ]
}
```

## Field notes

- `title` (string, required) — story name, shown on the title slide.
- `big_idea` (string, required) — one sentence, shown under the title.
- `beats` (array of strings, required) — one sentence per slide, 8-12 words
  each, present tense, concrete. Aim for 6-10 beats. Each becomes its own
  slide with a placeholder illustration frame above it.
- `takeaways` (array of strings, required) — 1-2 short lessons, shown
  together on one recap slide.
- `discussion_questions` (array of strings, required) — 1-2 questions, shown
  together on the closing slide.

Only very short (<10 word) phrasing may echo a Bible translation's wording;
write beats as an original paraphrase, not a copied verse.
