# img2pptx

[![tests](https://github.com/scarletcx/img2pptx/actions/workflows/tests.yml/badge.svg)](https://github.com/scarletcx/img2pptx/actions/workflows/tests.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Turn a raster reference image into a **one-slide, editable, modular, auditable
PowerPoint** instead of pasting a flat bitmap onto a slide.

This repository is an [Agent Skill](https://agentskills.io/specification), not a
one-command CLI. The agent inspects the image, builds a component manifest,
reconstructs SVG modules, renders and compares them, generates the PPTX, and runs
the audits. It uses whatever image, SVG, and PPTX tools are already available in
the environment.

[中文说明](README.zh-CN.md)

## What you get

The agent produces a task workspace containing:

```text
final.pptx                  one slide with the complete SVG embedded
full.svg                    complete editable SVG
component_manifest.json     semantic units, hierarchy, bounds, constraints
modules/*.svg               standalone module exports
qa/                         structural, semantic, visual, and PPTX audits
```

The exact QA set depends on the source. Semantic-audit files are mandatory only
when the image contains meaning-bearing visual encoding such as chart colors,
axis sides, arrow directions, table order, or scientific symbols. Otherwise the
agent records `not_applicable` instead of fabricating an empty pass.

## What makes this different

Most image-to-PPT tools place a bitmap on a slide. This protocol instead:

- reconstructs semantic modules, not meaningless geometric fragments;
- keeps text as SVG `<text>` and graphics as vector shapes wherever practical;
- extracts semantic constraints before drawing (color meaning, direction,
  ordering, containment, connectivity, counts, and forbidden substitutions);
- preserves the module hierarchy so the slide can be ungrouped and edited;
- runs structural, containment, alignment, border, semantic, coverage, visual,
  and PPTX audits;
- applies bounded, reversible visual optimization only after hard gates pass;
- reports honestly what is editable, what is only embedded, and what depends on
  the PowerPoint SVG importer.

## What it is not

- **Not a one-click converter.** There is no fixed `convert.py`; the agent writes
  task-specific scripts in the task workspace because every image has different
  structure and constraints.
- **Not a chart-data extractor.** It does not invent values that are not legible.
  It preserves observed geometry and marks uncertain data for review.
- **Not a guarantee of native PowerPoint shapes.** "SVG embedded in full" is not
  the same as "every group survives Convert to Shape / Ungroup." The latter
  depends on the PowerPoint version and SVG importer and must be verified.
- **Not a substitute for human review** when semantics are ambiguous.
- **Not a tool installer.** The skill never installs packages or system tools
  without your consent.

## Requirements

You need an Agent Skills-compatible host with file and shell tools:

- Command Code
- Claude Code
- OpenAI Codex
- Gemini CLI
- Cursor
- GitHub Copilot
- other hosts that implement the Agent Skills standard

The skill itself is tool-agnostic. A practical setup usually has at least one
tool from each category:

| Job | Common options |
|---|---|
| Decode the source image | Pillow, ImageMagick, macOS `sips`, FFmpeg |
| Render SVG for comparison | resvg, librsvg (`rsvg-convert`), Inkscape, CairoSVG, headless Chromium/Firefox |
| Generate the PPTX | python-pptx, LibreOffice (`soffice`) |
| Verify PowerPoint conversion | Microsoft PowerPoint (recommended for the final check) |
| Compare images/metrics | Pillow + NumPy, OpenCV, ImageMagick, scikit-image |

Python 3.9+ is optional and is only needed for the bundled environment checker.
No network access is required by the skill itself.

### Check your environment

Run the bundled checker before starting a task:

```bash
python3 skills/img2pptx/scripts/check_environment.py
python3 skills/img2pptx/scripts/check_environment.py --json
python3 skills/img2pptx/scripts/check_environment.py --strict
```

`--strict` exits non-zero if Python is older than 3.9 or if there is no image
decoder, SVG renderer, or PPTX generator. Missing optional tools are reported,
not installed.

### Suggested installs

Use the commands that fit your platform and environment. These are examples, not
requirements.

```bash
# Python-side helpers
python3 -m pip install --user pillow cairosvg python-pptx numpy

# macOS (Homebrew)
brew install librsvg
brew install --cask libreoffice
brew install --cask inkscape

# Debian/Ubuntu
sudo apt-get install librsvg2-bin libreoffice

# Windows: install Python packages with pip, and Inkscape/LibreOffice/PowerPoint
# with your normal installer or winget.
```

If you use PowerPoint for the final check, open the generated `final.pptx` and
inspect **Convert to Shape** / **Ungroup** behavior. Do not claim it works
without actually testing it.

## Install

The skill lives in `skills/img2pptx/`. The commands below use the
`scarletcx` account; replace it with your own account if you fork the project.

### One location for most hosts

```bash
git clone https://github.com/scarletcx/img2pptx.git
cd img2pptx
mkdir -p ~/.agents/skills
ln -s "$(pwd)/skills/img2pptx" ~/.agents/skills/img2pptx
```

`~/.agents/skills/` is read by Command Code, Codex, Gemini CLI, Cursor, and
GitHub Copilot.

### Claude Code

Claude Code does not read `~/.agents/skills/`. Add a second link:

```bash
mkdir -p ~/.claude/skills
ln -s "$(pwd)/skills/img2pptx" ~/.claude/skills/img2pptx
```

### Project-local install

Commit the skill into the repository when the whole team should get it:

```bash
mkdir -p .agents/skills
cp -R /path/to/img2pptx/skills/img2pptx .agents/skills/img2pptx
```

Claude Code project install:

```bash
mkdir -p .claude/skills
cp -R /path/to/img2pptx/skills/img2pptx .claude/skills/img2pptx
```

### GitHub Copilot CLI

```bash
gh skill install scarletcx/img2pptx img2pptx
gh skill preview scarletcx/img2pptx img2pptx
```

Preview before installing third-party skills.

## Use

Invoke the skill with your host's skill command:

- Command Code, Claude Code, Gemini CLI, Cursor: `/img2pptx`
- Codex: `$img2pptx` or the skill picker
- GitHub Copilot: select the skill, or ask it to reconstruct the image

You can also describe the task naturally:

```text
Convert ./reference.png into an editable one-slide PPTX. Preserve text as
editable text and keep the chart semantics. Deliver final.pptx plus the QA files.
```

```text
Rebuild this architecture diagram as a single editable PPTX slide. Keep the
module hierarchy so I can ungroup it in PowerPoint.
```

```text
Vectorize this infographic, but do not invent any numbers that are not legible.
Mark uncertain labels for human review.
```

```text
Turn this screenshot into a one-slide deck that matches the original aspect
ratio. Use editable vector shapes and text; only use a raster crop where
vectorization would materially reduce fidelity.
```

## How it works

1. **Normalize the input.** Preserve the original; convert TIFF/HEIC or
   unreliable formats to a high-quality PNG baseline. Match the slide aspect
   ratio to the image unless the user asks for a standard ratio.
2. **Build the component manifest.** Classify semantic units, composite
   submodules, and atomic elements. Record bounds, hierarchy, export flags,
   representation, and audit mappings in `component_manifest.json`.
3. **Extract semantic constraints before drawing.** Crop and inspect
   meaning-bearing components. Record direct observations, visual invariants,
   negative constraints, and one audit check per hard constraint.
4. **Build the layout skeleton.** Establish panels, columns, rows, spacing, and
   primary arrows. Audit the skeleton before drawing details.
5. **Draw modules as SVG.** Keep editable text and vector shapes where practical.
   Use PowerPoint-friendly primitives and border layering.
6. **Assemble `full.svg`.** Preserve real parent-child hierarchy instead of
   flattening everything into sibling nodes.
7. **Audit structure.** Check standalone-module integrity, containment,
   alignment, spacing, and border layering.
8. **Audit semantics and visuals.** Run the semantic constraint/coverage audit,
   then render the SVG and compare it with the source using overlays, amplified
   diffs, component crops, and metrics. Do not let a low global MAE override a
   semantic failure.
9. **Generate the PPTX.** Embed the complete SVG in a one-slide PPTX; verify the
   package, preview, text readability, borders, and conversion readiness.
10. **Correct and re-audit.** Apply the correction loop until every hard gate
    passes. Then run at most three bounded visual-optimization attempts; keep the
    best valid state and report the actual result honestly.

The detailed protocol is in [SKILL.md](skills/img2pptx/SKILL.md). The semantic
and visual audit rules are in:

- [Semantic Constraint and Audit Protocol](skills/img2pptx/references/semantic-constraint-audit.md)
- [Visual Similarity Optimization](skills/img2pptx/references/visual-optimization.md)

## Output files

A typical completed task looks like this:

```text
final.pptx
full.svg
component_manifest.json
modules/
  panel_overview.svg
  panel_method.svg
  ...
qa/
  layout_skeleton_audit.json
  standalone_integrity_audit.json
  containment_audit.json
  alignment_audit.json
  border_layering_audit.json
  semantic_constraint_audit.json
  constraint_coverage_audit.json
  semantic_review_sheet.png
  semantic_masks/
  visual_similarity_audit.json
  full_overlay_diff.png
  amplified_diff.png
  component_diff_sheet.png
  pptx_slide_preview.png
  pptx_preview_audit.json
```

Some files are conditional. For example, semantic audits and masks are required
only when the source has meaning-bearing visual encoding. The agent should report
which checks were `not_applicable`, not pretend they passed.

## Quality gates

Hard gates include:

- layout skeleton;
- standalone module integrity;
- parent-child containment;
- alignment and spacing;
- border layering;
- semantic constraints and negative constraints;
- constraint coverage and required human review;
- SVG/PPTX package embedding;
- PPTX preview, text readability, and structural integrity.

Visual optimization is allowed only after these pass. The default optimization
budget is three attempts and a soft target of 10% relative MAE improvement. A
semantic correction can take precedence over global MAE, but the tradeoff must be
recorded.

## Tips for better results

- Use the highest-resolution source you have.
- Crop and zoom into small icons, labels, and legends before redrawing them.
- Keep text as text. Convert lettering to paths only when the source is stylized
  lettering or font substitution would visibly break it.
- Prefer simple SVG primitives (`text`, `rect`, `line`, `circle`, `ellipse`,
  `polygon`, `polyline`, `path`) over filters, `foreignObject`, and external
  resources.
- Preserve hierarchy. A flat SVG is harder to edit and audit.
- For charts, preserve only legible values; never invent missing data.
- Open the PPTX in PowerPoint before claiming that Convert to Shape or Ungroup
  works.
- Keep the original input untouched and keep task-specific scripts in the task
  workspace.

## Troubleshooting

### No SVG renderer

Install one of: `resvg`, `rsvg-convert` (librsvg), Inkscape, CairoSVG, or use a
headless browser. `check_environment.py --strict` will tell you what is missing.

### No PPTX generator

Install `python-pptx` or LibreOffice. `python-pptx` may require custom OOXML to
embed an SVG; LibreOffice is often useful for package conversion and previews.

### HEIC or TIFF does not decode

Convert the target frame to PNG with `heif-convert`, ImageMagick, FFmpeg, or a
platform tool. Keep the original and record both files in the manifest.

### The SVG looks right but PowerPoint differs

PowerPoint's SVG importer does not support every SVG feature. Simplify filters,
masks, clipping, and external resources; verify the preview in PowerPoint; keep a
PNG fallback if necessary. Do not claim full editability without testing.

### Text is not editable after conversion

PowerPoint may rasterize certain text during SVG import. For critical labels,
consider native text boxes or a hybrid layout; report the tradeoff honestly.

### Fonts shift

Use a common font, embed the font where possible, or convert stylized lettering
to paths. Record any font substitution in the manifest and QA notes.

### Very large images

Use a downscaled render for QA speed, but keep a consistent coordinate system
and record the scale. Do not lose the original dimensions.

## Repository layout

```text
skills/img2pptx/
  SKILL.md
  references/
    semantic-constraint-audit.md
    visual-optimization.md
  scripts/
    check_environment.py
  examples/
    prompt.md
  agents/
    openai.yaml             optional Codex UI metadata; other hosts ignore it
tests/
  test_check_environment.py
.github/workflows/tests.yml
```

## Development

```bash
python3 -m unittest discover -s tests -v
python3 skills/img2pptx/scripts/check_environment.py
```

The checker uses only the Python standard library. The skill itself is a protocol;
the agent creates task-specific scripts at runtime.

### Publishing

The repository uses the standard `skills/<name>/SKILL.md` layout:

```bash
gh skill publish --dry-run
gh skill publish --tag v1.0.0
```

`gh skill install` and `gh skill publish` discover the skill from
`skills/img2pptx/`.

## License

MIT. See [LICENSE](LICENSE).
