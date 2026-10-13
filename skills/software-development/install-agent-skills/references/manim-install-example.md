# Worked example: installing the manim / iart-ai / yusuke skill repos

Drove the creation of the `install-agent-skills` skill. Recorded so the trap is
reproducible.

## Request
User pasted 3 URLs: `adithya-s-k/manim_skill`, `Yusuke710/manim-skill`,
`iart-ai` (an org). Intent: install their Agent Skills.

## What the repos contain
- `adithya-s-k/manim_skill/skills/` -> 3 skills: `manim-composer`,
  `manimce-best-practices`, `manimgl-best-practices`.
- `Yusuke710/manim-skill/skills/manim-skill/` -> 1 skill: `manim-skill`.
- `iart-ai/manim-skills/skills/manim/` -> 1 skill: `manim`.

## Collision found (the trap)
The local library already had `manimce-best-practices` and `manimgl-best-practices`
wired in — but NOT as real dirs under `~/.hermes/skills/`. They were **symlinks**:

```
~/.hermes/skills/manimce-best-practices -> ../../.agents/skills/manimce-best-practices
~/.hermes/skills/manimgl-best-practices -> ../../.agents/skills/manimgl-best-practices
```

`npx skills add` had written the real content to `~/.agents/skills/<name>/` and
symlinked it. The real `manimce-best-practices` was **stale**: only `SKILL.md`
+ `LICENSE.txt` (no rules/, examples/, templates/).

Copying the fresh repo skill into `~/.hermes/skills/creative/adithya-manimce-best-practices`
created a SECOND real dir with the same `name:` -> loader returned
"Ambiguous skill name 'manimce-best-practices': 2 skills match ... Refusing to guess."

## Diagnostic that caught it
- `find ~/.hermes/skills/manimce-best-practices -type f` -> empty (symlink,
  find does not descend without `-L`).
- `readlink -f ~/.hermes/skills/manimce-best-practices` ->
  `/home/deeone/.agents/skills/manimce-best-practices` (the real dir).
- `diff -rq` of that real dir vs the cloned repo skill -> "DIRS DIFFER"
  (stale vs fresh).

## Resolution
1. Copy fresh repo content onto the CANONICAL realpath (the symlink target),
   not a new parallel dir:
   `cp -rT "$REPO/manimce-best-practices/." "$HOME/.agents/skills/manimce-best-practices/"`
   -> now 23 rules + examples + templates.
2. Delete the stray parallel copy under `creative/`:
   `rm -rf ~/.hermes/skills/creative/adithya-manimce-best-practices`.
3. Re-run collision scan -> "NO COLLISIONS".
4. `skill_view(name=manimce-best-practices)` -> `readiness_status: available`.

## Final installed set
| name | source | result |
|------|--------|--------|
| manimce-best-practices | adithya | refreshed canonical (.agents) + upgraded |
| manimgl-best-practices | adithya | refreshed |
| manim-composer | adithya | refreshed |
| manim-skill | Yusuke710 | new install |
| manim | iart-ai | refreshed |

## Lesson encoded
Never trust the directory name as the identity. Always map `name:` -> realpath
(resolving symlinks) BEFORE copying. `npx skills add` installs to
`~/.agents/skills/` and symlinks; refresh the canonical target, don't fork a
second real directory.
