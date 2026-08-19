---
name: remotion-video-ads
description: Create multi-scene video advertisements using Remotion (React-based video framework). Use when building promo videos, ads, or marketing content with Remotion. Covers project scaffolding, TransitionSeries for scene transitions, per-scene animation patterns with useCurrentFrame/interpolate, and rendering. For general Remotion best practices (audio, captions, 3D, etc.) see the remotion-best-practices skill.
metadata:
  tags: [remotion, video, ads, marketing, react, animation, transitions]
---

# Remotion Video Ads

Create multi-scene video advertisements using Remotion — a React-based programmatic video framework.

## When to use

Use this skill when:
- Building a video advertisement or promo video in Remotion
- Creating multi-scene compositions with transitions between scenes
- Animating text, cards, and UI elements for video output
- Rendering Remotion compositions to MP4

For general Remotion patterns (audio, captions, 3D, Lottie, etc.), load the `remotion-best-practices` skill.

## Project Scaffolding

```bash
npx create-video@latest --yes --blank --no-tailwind <project-name>
cd <project-name>
npm install
npx remotion add @remotion/transitions
```

Always use `--no-tailwind` — CSS transitions and Tailwind animation classes are FORBIDDEN in Remotion and will not render correctly.

## Architecture

```
src/
├── Root.tsx                    # Composition registration
├── <ProjectName>.tsx           # Main composition with TransitionSeries
├── scenes/
│   ├── Scene1Hook.tsx          # Individual scene components
│   ├── Scene2Problem.tsx
│   └── ...
└── index.css                   # Google Fonts import
```

## Root.tsx — Composition Registration

```tsx
import "./index.css";
import { Composition } from "remotion";
import { MainComposition } from "./MainComposition";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="MainComposition"
      component={MainComposition}
      durationInFrames={540}   // Total duration (account for transition overlap)
      fps={30}
      width={1920}
      height={1080}
    />
  );
};
```

## Main Composition — TransitionSeries

Use `TransitionSeries` from `@remotion/transitions` to sequence scenes with transitions:

```tsx
import { AbsoluteFill } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";

const TRANSITION_DURATION = 12; // 0.4s at 30fps

export const MainComposition: React.FC = () => {
  return (
    <AbsoluteFill style={{ background: "#08080c" }}>
      <TransitionSeries>
        <TransitionSeries.Sequence durationInFrames={105}>
          <Scene1Hook />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: TRANSITION_DURATION })}
        />

        <TransitionSeries.Sequence durationInFrames={120}>
          <Scene2Problem />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition
          presentation={slide({ direction: "from-right" })}
          timing={linearTiming({ durationInFrames: TRANSITION_DURATION })}
        />

        {/* More scenes... */}
      </TransitionSeries>
    </AbsoluteFill>
  );
};
```

## Duration Calculation

**Critical:** Transitions overlap adjacent scenes, reducing total duration.

```
total = sum(scene durations) - sum(transition durations)
```

Example: 3 scenes × 60 frames with 15-frame transitions = `180 - 30 = 150 frames`

## Scene Component Pattern

Each scene uses `useCurrentFrame()` (starts at 0 within each Sequence) and `interpolate()`:

```tsx
import { AbsoluteFill, interpolate, useCurrentFrame, Easing } from "remotion";

export const MyScene: React.FC = () => {
  const frame = useCurrentFrame();
  const SCENE_DURATION = 105;

  // Entrance
  const opacity = interpolate(frame, [0, 20], [0, 1], {
    easing: Easing.bezier(0.16, 1, 0.3, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Exit
  const exitOpacity = interpolate(
    frame,
    [SCENE_DURATION - 15, SCENE_DURATION],
    [1, 0],
    {
      easing: Easing.in(Easing.cubic),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }
  );

  // Staggered child elements
  const childY = interpolate(frame, [10, 25], [40, 0], {
    easing: Easing.bezier(0.16, 1, 0.3, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ opacity: opacity * exitOpacity }}>
      <div style={{ transform: `translateY(${childY}px)` }}>
        Content here
      </div>
    </AbsoluteFill>
  );
};
```

## Transition Selection

| Transition | Best For |
|------------|----------|
| `fade()` | General purpose, smooth continuity |
| `slide({ direction: "from-right" })` | Forward momentum, progression |
| `slide({ direction: "from-bottom" })` | Reveals, upward energy |
| `wipe()` | Directional reveals |
| `clockWipe()` | Brand moments, hero reveals |

Vary transitions across scenes — don't use the same one everywhere.

## Timing Guidelines

- **Scene duration**: 3-5 seconds (90-150 frames at 30fps)
- **Transition duration**: 10-15 frames (0.3-0.5s)
- **Entrance stagger**: 8-12 frames between elements within a scene
- **Exit speed**: 1.5-2× faster than entrance (Easing.in for exits, Easing.out for entrances)
- **Hold time**: 40-60% of scene duration should be static hold after entrances complete

## Fonts

Import Google Fonts in `index.css`:

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=block');
```

## Rendering

```bash
# Preview in browser
npx remotion studio

# Render to MP4
npx remotion render <CompositionId> ../output.mp4

# Render with quality
npx remotion render <CompositionId> ../output.mp4 --quality 100
```

## Common Pitfalls

1. **CSS transitions/animations don't work** — always use `interpolate()` + `useCurrentFrame()`
2. **Missing `extrapolateLeft/Right: "clamp"`** — values will overshoot bounds
3. **Forgetting transition overlap** — total duration is less than sum of scenes
4. **Using `useVideoConfig()` for fps in scenes** — each Sequence's frame counter starts at 0; use relative frame values
5. **Padding shorthand in JSX** — `padding: "32px 24px"` causes TypeScript errors. Always use individual properties: `paddingTop: 32, paddingBottom: 32, paddingLeft: 24, paddingRight: 24`
6. **Unused imports** — `Sequence`, `interpolate`, `useCurrentFrame`, `useVideoConfig`, `Easing` from `remotion` are only needed in scene files, not in the main composition file. Keep imports minimal per file to avoid TS errors.

## Browser Integration

For Lightpanda headless browser configuration with Hermes Agent, see [references/lightpanda.md](references/lightpanda.md).
5. **Padding shorthand in JSX** — use `paddingTop`/`paddingBottom`/`paddingLeft`/`paddingRight` separately, not `padding: "32px 24px"` (causes TS errors)
