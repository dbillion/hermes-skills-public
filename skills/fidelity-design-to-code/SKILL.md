---
name: fidelity-design-to-code
description: Workflow for converting Google Stitch designs into high-fidelity, production-ready React applications using shadcn/ui, Three.js (WebGPU), and modern motion libraries (GSAP, Theatre.js).
---

# Fidelity Design to Code

This skill provides a structured workflow for taking an AI-native design (like one from Google Stitch) and transforming it into a living, high-fidelity production project.

## Core Workflow

### 1. Design Ingestion (Google Stitch)
Analyze the initial Google Stitch design for "vibe" and structure.
- **Identify tokens**: Colors, typography, and spacing.
- **Extract intention**: Is it "warm and cozy" or "high-tech/minimal"?
- **Export to Figma**: If available, use Fusion (Builder.io) to bridge the design into a codebase-aware environment.

### 2. UI Foundation (shadcn/ui + Tailwind)
Build the core UI using `shadcn/ui` components for accessibility and speed.
- **Customize theme**: Update `tailwind.config.js` with the extracted design tokens.
- **Modular components**: Use Radix UI primitives for complex interactions (drawers, dialogs, dropdowns).

### 3. Motion & Animation (GSAP + Theatre.js)
Apply professional-grade motion to bring the UI to life.
- **GSAP**: Use for scroll-driven storytelling and complex timelines.
- **Theatre.js**: Use as a "Visual Director" to animate 3D scenes and UI transitions visually.
- **Transition MPAs**: Use `Barba.js` to create a seamless SPA-like feel for multi-page sites.

### 4. 3D Immersion (Three.js + WebGPU)
Integrate interactive 3D elements for high-impact visual engagement.
- **Three.js**: Use `WebGPURenderer` for low-overhead, high-performance scenes.
- **Fragment Shaders**: Leverage GLSL for procedural patterns and pixel-perfect effects that run in parallel on the GPU.

### 5. AI Agent Alignment (`DESIGN.md`)
Create a `DESIGN.md` file in the project root to ensure that AI coding agents (like Gemini CLI) maintain brand and design consistency.

## Resources

- **Tech Stack**: See [tech-stack.md](references/tech-stack.md) for details on the recommended libraries.
- **Workflow Guide**: See [stitch-to-code.md](references/stitch-to-code.md) for a step-by-step conversion guide.
