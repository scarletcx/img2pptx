# Example prompts

Replace the path with your own image. The agent will create a task workspace
with the deliverables and QA files.

## General screenshot or diagram

```text
Convert ./reference.png into a one-slide, editable PPTX. Keep the original
aspect ratio, preserve text as editable text, and keep graphics as vector
shapes wherever practical. Do not modify the original image. Deliver
final.pptx, full.svg, component_manifest.json, modules, and the QA files.
```

## Architecture or workflow diagram

```text
Rebuild this architecture diagram as a single editable PPTX slide. Preserve the
module hierarchy and arrow topology so I can ungroup it in PowerPoint. Check
that every submodule stays inside its parent and that no connector crosses text.
```

## Chart, infographic, or scientific figure

```text
Vectorize this figure. Treat color, axis side, direction, ordering, and symbol
choice as semantic constraints. Do not invent numbers that are not legible.
Mark uncertain labels for human review and fail the semantic audit if a hard
constraint cannot be verified.
```

## Editability-focused request

```text
I care more about editability than pixel-perfect MAE. Prefer simple SVG
primitives, preserve text as <text>, and keep semantic modules as named groups.
Only use a raster crop where vectorization would materially reduce fidelity.
```

## Expected output

```text
final.pptx
full.svg
component_manifest.json
modules/*.svg
qa/
```
