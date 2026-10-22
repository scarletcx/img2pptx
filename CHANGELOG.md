# Changelog

## 1.0.0 - 2026-10-22

- Published the existing img2pptx reconstruction protocol as a portable Agent
  Skills package.
- Kept the protocol tool-agnostic: no hard-coded OS, browser, Python, or
  PowerPoint automation path.
- Added `skills/img2pptx/scripts/check_environment.py` to report available
  image decoders, SVG renderers, PPTX generators, and PowerPoint installations
  without installing anything.
- Added standard frontmatter (`license`, `compatibility`, `metadata`) and
  bilingual trigger phrases.
- Added English and Chinese READMEs, a prompt example, tests, and a CI workflow.
- Added the standard `skills/img2pptx/SKILL.md` layout for `gh skill
  install/publish` compatibility.
