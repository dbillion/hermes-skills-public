# QA Checklist

## Clarity

- Is the main idea visible within 5 seconds?
- Are there too many objects on screen?
- Does every animation explain something?

## Continuity

- Do objects preserve identity?
- Are transforms used instead of arbitrary cuts?
- Does the viewer know where the object went?

## Technique fit

- Algebra uses TransformMatchingTex?
- Generated curves use TracedPath?
- Cancelled terms are struck, not deleted?
- Group motion uses lag_ratio?

## Timing

- Are pauses long enough?
- Is the narration synchronized?
- Do rotations use linear rate_func?
- Do arrivals ease out?

## Visual design

- Is contrast strong?
- Are labels readable?
- Are colors meaningful?

## Camera

- Does every camera move have a reason?
- Is 3D framing around phi 70-80, theta -30 to -60?
- Is ambient orbit stopped before the payoff?

## Math correctness

- Are axes labeled?
- Are symbols consistent?
- Are edge cases handled?
