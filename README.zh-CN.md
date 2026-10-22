# img2pptx

[![tests](https://github.com/scarletcx/img2pptx/actions/workflows/tests.yml/badge.svg)](https://github.com/scarletcx/img2pptx/actions/workflows/tests.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

把一个栅格参考图（截图、图表、架构图、论文插图、信息图）重建为**单页、可编辑、模块化、可审计的 PowerPoint**，而不是把一张位图贴在幻灯片上。

这是一个 [Agent Skill](https://agentskills.io/specification)（执行协议），不是一个“一条命令搞定”的 CLI。Agent 会检查图片、建立组件清单、重建 SVG 模块、渲染对比、生成 PPTX，并跑完审计；它使用当前环境里已有的图像、SVG 和 PPTX 工具。

[English](README.md)

## 最终产出

Agent 会在任务工作区生成：

```text
final.pptx                  单页 PPTX，内嵌完整 SVG
full.svg                    完整可编辑 SVG
component_manifest.json     语义单元、层级、边界、约束
modules/*.svg               可独立导出的模块
qa/                         结构、语义、视觉和 PPTX 审计
```

具体 QA 文件取决于源图。只有图中包含“颜色/方向/顺序/包含关系/符号”等承载语义的视觉编码时，语义审计文件才是必须的；否则 Agent 应记录 `not_applicable`，而不是伪造一个空的通过结果。

## 和其他方案的区别

大多数图片转 PPT 工具只是把位图放到幻灯片上。这个协议会：

- 按语义模块重建，而不是切成一堆没有意义的几何碎片；
- 尽量把文字保留为 SVG `<text>`，把图形保留为矢量形状；
- 在绘制前提取语义约束：颜色含义、方向、顺序、包含关系、连接关系、数量、禁止替换等；
- 保留模块层级，方便在 PowerPoint 里取消组合后继续编辑；
- 执行结构、包含、对齐、边框、语义、覆盖率和 PPTX 审计；
- 只有硬性检查全部通过后，才做有界、可回滚的视觉优化；
- 如实区分“SVG 完整嵌入”“可在 PowerPoint 中转换/取消组合”“转换后实际保真度”。

## 它不是什么

- **不是一键转换器。** 仓库里没有固定的 `convert.py`；每张图的结构和约束不同，Agent 会在任务工作区写针对当前任务的脚本。
- **不是图表数据提取器。** 看不清的数字不会编造；只保留可观察到的几何关系，并把不确定项标记为待人工复核。
- **不保证所有 SVG 都能变成 PowerPoint 原生形状。** “SVG 完整嵌入”不等于“每个组都能 Convert to Shape / Ungroup”；后者取决于 PowerPoint 版本和 SVG 导入器，必须实际验证。
- **不替代人工语义复核。** 语义有歧义时，需要人确认。
- **不会擅自安装工具。** 环境检查器只报告已有工具，不安装任何东西。

## 环境要求

需要一个支持 Agent Skills、并且能读写文件和执行命令的宿主：

- Command Code
- Claude Code
- OpenAI Codex
- Gemini CLI
- Cursor
- GitHub Copilot
- 其他实现 Agent Skills 标准的宿主

技能本身不绑定具体工具。一个实用的环境通常每类至少有一个：

| 用途 | 常见选择 |
|---|---|
| 解码源图 | Pillow、ImageMagick、macOS `sips`、FFmpeg |
| 渲染 SVG 做对比 | resvg、librsvg（`rsvg-convert`）、Inkscape、CairoSVG、无头 Chromium/Firefox |
| 生成 PPTX | python-pptx、LibreOffice（`soffice`） |
| 验证 PowerPoint 转换 | Microsoft PowerPoint（建议用于最终检查） |
| 图像对比/指标 | Pillow + NumPy、OpenCV、ImageMagick、scikit-image |

Python 3.9+ 是可选的，只用于仓库自带的环境检查器。技能本身不需要联网。

### 检查环境

开始任务前先运行：

```bash
python3 skills/img2pptx/scripts/check_environment.py
python3 skills/img2pptx/scripts/check_environment.py --json
python3 skills/img2pptx/scripts/check_environment.py --strict
```

`--strict` 在 Python 低于 3.9，或者缺少图像解码器/SVG 渲染器/PPTX 生成器时返回非零。缺失的可选工具只会被报告，不会被安装。

### 安装建议

以下只是示例，按你的平台和实际环境选择：

```bash
# Python 侧工具
python3 -m pip install --user pillow cairosvg python-pptx numpy

# macOS（Homebrew）
brew install librsvg
brew install --cask libreoffice
brew install --cask inkscape

# Debian/Ubuntu
sudo apt-get install librsvg2-bin libreoffice

# Windows：用 pip 安装 Python 包，用安装器或 winget 安装
# Inkscape / LibreOffice / PowerPoint。
```

如果要用 PowerPoint 做最终验证，必须打开生成的 `final.pptx` 实际检查 **Convert to Shape** / **Ungroup**，不能只看 SVG 预览就声称通过。

## 安装

技能位于 `skills/img2pptx/`。下面的命令使用 `scarletcx` 账号；如果你 fork 了项目，请替换成自己的账号。

### 大多数 agent 共用一处

```bash
git clone https://github.com/scarletcx/img2pptx.git
cd img2pptx
mkdir -p ~/.agents/skills
ln -s "$(pwd)/skills/img2pptx" ~/.agents/skills/img2pptx
```

`~/.agents/skills/` 会被 Command Code、Codex、Gemini CLI、Cursor、GitHub Copilot 读取。

### Claude Code

Claude Code 不读 `~/.agents/skills/`，需要再链接一次：

```bash
mkdir -p ~/.claude/skills
ln -s "$(pwd)/skills/img2pptx" ~/.claude/skills/img2pptx
```

### 项目内安装

希望团队共享时，把技能目录提交到仓库：

```bash
mkdir -p .agents/skills
cp -R /path/to/img2pptx/skills/img2pptx .agents/skills/img2pptx
```

Claude Code 项目内安装：

```bash
mkdir -p .claude/skills
cp -R /path/to/img2pptx/skills/img2pptx .claude/skills/img2pptx
```

### GitHub Copilot CLI

```bash
gh skill install scarletcx/img2pptx img2pptx
gh skill preview scarletcx/img2pptx img2pptx
```

安装第三方技能前建议先预览。

## 使用

用各家的技能命令调用：

- Command Code、Claude Code、Gemini CLI、Cursor：`/img2pptx`
- Codex：`$img2pptx` 或技能选择器
- GitHub Copilot：选择技能，或直接描述任务

也可以直接用自然语言：

```text
把 ./reference.png 转成可编辑的单页 PPTX。文字保持可编辑，保留图表的语义，
最后交付 final.pptx 和 QA 文件。
```

```text
把这张架构图重建为一张可编辑的 PPTX。保留模块层级，方便我在 PowerPoint 里
取消组合后继续编辑。
```

```text
把这张信息图矢量化，但不要编造任何看不清的数字；不确定的标签标记出来让我复核。
```

```text
把这张截图做成单页 PPT，比例和原图一致。尽量用可编辑的矢量形状和文字；
只有在矢量重建会明显损失保真度时，才使用最小的位图裁剪。
```

## 工作流程

1. **输入归一化。** 保留原图；把 TIFF/HEIC 或解码不稳定的格式转成高质量 PNG 基线。除非用户指定标准比例，否则 PPT 页面比例跟随原图。
2. **建立组件清单。** 区分语义单元、复合子模块和原子元素；在 `component_manifest.json` 中记录边界、层级、是否导出、表示方式和审计映射。
3. **先提取语义约束。** 对承载含义的组件做裁剪和放大检查，记录直接观察、视觉不变量、负向约束，并为每条硬性约束分配唯一的审计检查。
4. **搭布局骨架。** 先确定面板、列宽、行高、间距和主箭头；骨架审计通过后再画细节。
5. **逐模块绘制 SVG。** 尽量保留可编辑文字和矢量图形，使用 PowerPoint 友好的基础元素和边框分层。
6. **组装 `full.svg`。** 保留真实的父子层级，不要把所有元素拍平成兄弟节点。
7. **结构审计。** 检查独立模块完整性、父子包含、对齐、间距和边框分层。
8. **语义与视觉审计。** 跑语义约束/覆盖率审计，再渲染 SVG，用叠加图、放大差异图、组件裁剪和指标与源图对比。整体 MAE 低不能覆盖语义错误。
9. **生成 PPTX。** 把完整 SVG 嵌入单页 PPTX；检查包结构、预览、文字可读性、边框和转换准备度。
10. **修正并重新审计。** 所有硬性门槛通过后，才做最多三轮、可回滚的视觉优化；交付最佳有效版本并如实报告结果。

完整协议见 [SKILL.md](skills/img2pptx/SKILL.md)，语义与视觉审计细则见：

- [Semantic Constraint and Audit Protocol](skills/img2pptx/references/semantic-constraint-audit.md)
- [Visual Similarity Optimization](skills/img2pptx/references/visual-optimization.md)

## 输出文件

一个典型任务会生成：

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

部分文件是条件性的。例如源图没有承载语义的视觉编码时，语义审计和掩码不适用；Agent 应报告 `not_applicable`，不能假装通过。

## 硬性质量门槛

包括：

- 布局骨架；
- 独立模块完整性；
- 父子包含关系；
- 对齐和间距；
- 边框分层；
- 语义约束和负向约束；
- 约束覆盖率与必要的人工复核；
- SVG/PPTX 包嵌入完整性；
- PPTX 预览、文字可读性和结构完整性。

这些门槛全部通过后，才允许做视觉优化。默认最多三轮，软目标是相对 MAE 改善 10%。如果语义修正比全局 MAE 更重要，可以接受指标变差，但必须记录原因和证据。

## 提高成功率的建议

- 尽量使用最高分辨率的源图。
- 小图标、标签、图例先裁剪放大再画。
- 文字尽量保持为文字；只有艺术字或字体替换会明显破坏外观时，才转成路径。
- 优先使用 `text`、`rect`、`line`、`circle`、`ellipse`、`polygon`、`polyline`、`path` 等基础 SVG 元素，少用滤镜、`foreignObject` 和外部资源。
- 保留层级，不要拍平。
- 图表只保留看得清的数据，不要补造。
- 在 PowerPoint 里实际打开 PPTX 后，再声称 Convert to Shape / Ungroup 可用。
- 不要修改原图，任务脚本留在任务目录里，保证可复现。

## 常见问题

### 没有 SVG 渲染器

安装 `resvg`、`rsvg-convert`（librsvg）、Inkscape、CairoSVG，或使用无头浏览器。`check_environment.py --strict` 会告诉你缺什么。

### 没有 PPTX 生成器

安装 `python-pptx` 或 LibreOffice。`python-pptx` 嵌入 SVG 可能需要自定义 OOXML；LibreOffice 常用于打包转换和预览。

### HEIC/TIFF 解不开

用 `heif-convert`、ImageMagick、FFmpeg 或平台工具把目标帧转成 PNG。保留原图，并在清单里记录原文件和归一化文件。

### SVG 看着对，PowerPoint 里不一样

PowerPoint 的 SVG 导入器不支持所有特性。简化滤镜、遮罩、裁剪和外部资源；在 PowerPoint 里检查预览；必要时保留 PNG 兜底。没有实际验证就不要声称完全可编辑。

### 转换后文字不可编辑

PowerPoint 可能在 SVG 导入时把某些文字栅格化。关键标签可以考虑用原生文本框，或采用混合布局；如实报告取舍。

### 字体位移

使用常见字体、尽量嵌入字体，或把艺术字转成路径。任何字体替换都要记录在清单和 QA 备注里。

### 图片太大

QA 可以用缩小图提高速度，但坐标系统要一致，并记录缩放比例；不要丢失原始尺寸。

## 仓库结构

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
    openai.yaml             可选的 Codex UI 元数据；其他宿主会忽略
tests/
  test_check_environment.py
.github/workflows/tests.yml
```

## 开发

```bash
python3 -m unittest discover -s tests -v
python3 skills/img2pptx/scripts/check_environment.py
```

检查器只使用 Python 标准库。技能本身是协议；具体转换脚本由 Agent 在任务运行时生成。

### 发布

仓库使用标准的 `skills/<name>/SKILL.md` 结构：

```bash
gh skill publish --dry-run
gh skill publish --tag v1.0.0
```

`gh skill install` 和 `gh skill publish` 会从 `skills/img2pptx/` 发现这个技能。

## 许可证

MIT，见 [LICENSE](LICENSE)。
