# Multi-Scene Ad Composition — Complete Code Reference

## Full Working Example: 5-Scene Ad (18 seconds, 1920x1080)

### Root.tsx
```tsx
import "./index.css";
import { Composition } from "remotion";
import { CodemasterAd } from "./CodemasterAd";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="CodemasterAd"
      component={CodemasterAd}
      durationInFrames={540}
      fps={30}
      width={1920}
      height={1080}
    />
  );
};
```

### CodemasterAd.tsx (Main Composition)
```tsx
import React from "react";
import { AbsoluteFill } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { Scene1Hook } from "./scenes/Scene1Hook";
import { Scene2Problem } from "./scenes/Scene2Problem";
import { Scene3Solution } from "./scenes/Scene3Solution";
import { Scene4Languages } from "./scenes/Scene4Languages";
import { Scene5CTA } from "./scenes/Scene5CTA";

const SCENE_1_END = 105;
const SCENE_2_END = 225;
const SCENE_3_END = 360;
const SCENE_4_END = 450;
const TRANSITION_DURATION = 12;

export const CodemasterAd: React.FC = () => {
  return (
    <AbsoluteFill style={{ background: "#08080c" }}>
      <TransitionSeries>
        <TransitionSeries.Sequence durationInFrames={SCENE_1_END}>
          <Scene1Hook />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: TRANSITION_DURATION })}
        />
        <TransitionSeries.Sequence durationInFrames={SCENE_2_END - SCENE_1_END}>
          <Scene2Problem />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={slide({ direction: "from-right" })}
          timing={linearTiming({ durationInFrames: TRANSITION_DURATION })}
        />
        <TransitionSeries.Sequence durationInFrames={SCENE_3_END - SCENE_2_END}>
          <Scene3Solution />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: TRANSITION_DURATION })}
        />
        <TransitionSeries.Sequence durationInFrames={SCENE_4_END - SCENE_3_END}>
          <Scene4Languages />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={slide({ direction: "from-bottom" })}
          timing={linearTiming({ durationInFrames: TRANSITION_DURATION })}
        />
        <TransitionSeries.Sequence durationInFrames={540 - SCENE_4_END}>
          <Scene5CTA />
        </TransitionSeries.Sequence>
      </TransitionSeries>
    </AbsoluteFill>
  );
};
```

### Scene Component Template
```tsx
import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, Easing } from "remotion";

export const MyScene: React.FC = () => {
  const frame = useCurrentFrame();

  // Entrance
  const opacity = interpolate(frame, [5, 20], [0, 1], {
    easing: Easing.bezier(0.16, 1, 0.3, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const y = interpolate(frame, [5, 20], [20, 0], {
    easing: Easing.bezier(0.16, 1, 0.3, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Staggered children
  const child1Opacity = interpolate(frame, [15, 30], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const child2Opacity = interpolate(frame, [25, 40], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Exit (adjust 90 to your scene duration)
  const exitOpacity = interpolate(frame, [75, 90], [1, 0], {
    easing: Easing.in(Easing.cubic),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ background: "#08080c", opacity: opacity * exitOpacity }}>
      <div style={{ transform: `translateY(${y}px)`, opacity: child1Opacity }}>
        First element
      </div>
      <div style={{ opacity: child2Opacity }}>
        Second element
      </div>
    </AbsoluteFill>
  );
};
```

### index.css
```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display:block');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  font-family: 'Inter', sans-serif;
  -webkit-font-smoothing: antialiased;
}
```

## Easing Cheat Sheet

| Easing | Use Case |
|--------|----------|
| `Easing.bezier(0.16, 1, 0.3, 1)` | Crisp UI entrance (default for elements entering) |
| `Easing.bezier(0.34, 1.56, 0.64, 1)` | Playful overshoot (big numbers, logos) |
| `Easing.in(Easing.cubic)` | Exit animations (accelerating away) |
| `Easing.out(Easing.sin)` | Gentle reveals |
| `Easing.inOut(Easing.cubic)` | Smooth symmetric motion |

## Color Palette for Dark Tech Ads

```css
--bg-primary: #08080c;
--bg-secondary: #0d1117;
--accent-blue: #3b82f6;
--accent-purple: #8b5cf6;
--accent-red: #ef4444;
--accent-cyan: #22d3ee;
--accent-green: #4ade80;
--text-primary: #ffffff;
--text-secondary: rgba(255,255,255,0.65);
--text-muted: rgba(255,255,255,0.35);
--border-subtle: rgba(255,255,255,0.06);
```
