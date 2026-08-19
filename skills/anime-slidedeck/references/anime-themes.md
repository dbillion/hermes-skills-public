# Anime / Cartoon-Genre Focus Prompts for NotebookLM Slide Decks

Each file below is a ready-to-use `--focus` prompt. They are STATIC slide-deck art
direction (cartoon genre visuals), not animation. All include the no-gore / friendly-tone
guardrails. Replace `<TOPIC>` and `<SOURCE_HINTS>` with the actual subject.

Copy a file's contents into: `nlm slides create "$NB" --format detailed_deck --length default --confirm --focus "$(cat references/themes/<theme>.focus.txt)"`

---

## references/themes/ghibli.focus.txt
Act as a Studio Ghibli background artist and a warm, patient computer-science teacher.
CREATE A VISUAL WONDER slide deck teaching <TOPIC> in the soft, hand-painted Ghibli
storybook style. ART DIRECTION: lush pastoral scenery (rolling hills, gentle wind,
wildflowers, warm wooden cottages), a small friendly forest spirit or village child as a
recurring mascot who guides the learner slide by slide. Soft sage-green, cream, sky-blue and
warm-brown palette; watercolor texture; rounded, calming shapes; generous whitespace. Each
technical concept becomes a tiny storybook scene the viewer can picture and remember (e.g. a
neat row of labeled jars on a shelf = a hash table; a winding forest path = tree traversal).
Narration voice: calm, encouraging, mindful — like a kind grandfather explaining by the fire.
TONE GUARDRAILS: absolutely NO gore, blood, horror, violence or unsettling imagery. Show
difficult ideas (worst case, failure, cache miss) only as mild, cute metaphors (a sleepy
cloud, a puzzled mascot). One clear idea per slide, max 3-4 short bullets. Use the uploaded
sources (<SOURCE_HINTS>) for technical accuracy. Make it beautiful, peaceful, and easy to
recall.

## references/themes/naruto.focus.txt
Act as a Naruto/Shōnen anime art director and an energetic, motivating CS mentor.
CREATE A VISUAL WONDER slide deck teaching <TOPIC> in the bright, dynamic Naruto cartoon
style. ART DIRECTION: a cheerful leafy-village world, a small headband-wearing ninja mascot
as the recurring guide who "trains" the learner through each concept; scroll-and-seal
motifs, warm parchment textures, leafy greens. Palette: orange, blue, green, parchment with
bold outlines and expressive characters. Each concept is a fun "training mission" with a
tiny scene the learner can visualize (a stack of mission scrolls = a stack/queue; a map of
connected villages = a graph). Narration voice: upbeat, encouraging, "you've got this!"
TONE GUARDRAILS: absolutely NO gore, blood, horror, graphic fighting or unsettling imagery.
Keep any battle/conflict metaphors purely playful (friendly sparring, a race). One clear idea
per slide, max 3-4 short bullets. Use the uploaded sources (<SOURCE_HINTS>) for accuracy. Make
it colorful, energetic, and memorable.

## references/themes/superbook.focus.txt
Act as an 80s storybook-anime art director (Superbook / World Masterpiece Theater) and a
gentle, curious CS guide. CREATE A VISUAL WONDER slide deck teaching <TOPIC> in the cozy
retro storybook-cartoon style. ART DIRECTION: a glowing magical book that opens into each
lesson, a small friendly elf or child mascot who travels through the pages; warm lamplight,
cozy fantasy villages, starry nights. Palette: amber, teal, violet, warm gold with soft
graphical shading and rounded, storybook characters. Each concept is a page in the living
book with a charming scene to remember (a library of labeled shelves = an array; a web of
glowing threads = a graph). Narration voice: wondering, kind, mindful — discovery through a
friendly tale. TONE GUARDRAILS: absolutely NO gore, blood, horror or unsettling imagery.
Show hard ideas only as gentle puzzles (a locked page, a sleepy star). One clear idea per
slide, max 3-4 short bullets. Use the uploaded sources (<SOURCE_HINTS>) for accuracy. Make it
warm, nostalgic, and easy to recall.
