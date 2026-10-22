#!/usr/bin/env python3
"""Report locally available tools for the img2pptx skill.

The script never installs anything and never modifies the project. It only
inspects what is already available so the agent can choose a toolchain.

Examples:
    python3 <skill-dir>/scripts/check_environment.py
    python3 <skill-dir>/scripts/check_environment.py --json
    python3 <skill-dir>/scripts/check_environment.py --strict
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import platform
import shutil
import sys
from pathlib import Path

MIN_PYTHON = (3, 9)

MODULES = (
    ("PIL", "Pillow image decoding"),
    ("cairosvg", "SVG rendering"),
    ("pptx", "python-pptx PPTX generation"),
    ("lxml", "XML processing"),
    ("numpy", "array and metric work"),
    ("cv2", "OpenCV image analysis"),
    ("fitz", "PyMuPDF rasterization"),
    ("skimage", "scikit-image analysis"),
    ("scipy", "scientific metrics"),
)

TOOLS = (
    ("magick", "ImageMagick 7"),
    ("convert", "ImageMagick 6"),
    ("sips", "macOS image conversion"),
    ("rsvg-convert", "librsvg SVG renderer"),
    ("resvg", "resvg SVG renderer"),
    ("inkscape", "Inkscape SVG renderer"),
    ("chromium", "Chromium SVG renderer"),
    ("chromium-browser", "Chromium SVG renderer"),
    ("google-chrome", "Google Chrome SVG renderer"),
    ("google-chrome-stable", "Google Chrome SVG renderer"),
    ("firefox", "Firefox SVG renderer"),
    ("libreoffice", "LibreOffice"),
    ("soffice", "LibreOffice"),
    ("pdftoppm", "Poppler PDF rasterizer"),
    ("pdfinfo", "Poppler PDF information"),
    ("ffmpeg", "FFmpeg"),
    ("heif-convert", "HEIC decoder"),
    ("powershell", "Windows PowerShell"),
    ("pwsh", "PowerShell 7"),
)

IMAGE_DECODERS = ("PIL", "magick", "convert", "sips", "ffmpeg", "heif-convert")
SVG_RENDERERS = (
    "cairosvg",
    "rsvg-convert",
    "resvg",
    "inkscape",
    "chromium",
    "chromium-browser",
    "google-chrome",
    "google-chrome-stable",
    "firefox",
)
PPTX_GENERATORS = ("pptx", "libreoffice", "soffice")


def module_available(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        return False


def find_powerpoint() -> str | None:
    candidates = (
        Path("/Applications/Microsoft PowerPoint.app"),
        Path("/Applications/Microsoft PowerPoint.app/Contents/MacOS/Microsoft PowerPoint"),
        Path(r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE"),
        Path(r"C:\Program Files (x86)\Microsoft Office\root\Office16\POWERPNT.EXE"),
        Path(r"C:\Program Files\Microsoft Office\root\Office15\POWERPNT.EXE"),
    )
    for path in candidates:
        if path.exists():
            return str(path)
    for name in ("powerpnt", "POWERPNT.EXE"):
        found = shutil.which(name)
        if found:
            return found
    return None


def build_report() -> dict:
    modules = {name: module_available(name) for name, _ in MODULES}
    tools = {name: shutil.which(name) for name, _ in TOOLS}
    python_ok = sys.version_info >= MIN_PYTHON

    image_decoder = any(modules.get(name, False) for name in IMAGE_DECODERS if name in modules) or any(
        tools.get(name) for name in IMAGE_DECODERS if name in tools
    )
    svg_renderer = any(
        modules.get(name, False) for name in SVG_RENDERERS if name in modules
    ) or any(tools.get(name) for name in SVG_RENDERERS if name in tools)
    pptx_generator = any(
        modules.get(name, False) for name in PPTX_GENERATORS if name in modules
    ) or any(tools.get(name) for name in PPTX_GENERATORS if name in tools)
    powerpoint = find_powerpoint()

    summary = {
        "image_decoder": bool(image_decoder),
        "svg_renderer": bool(svg_renderer),
        "pptx_generator": bool(pptx_generator),
        "powerpoint_app": bool(powerpoint),
    }

    recommendations: list[str] = []
    if not python_ok:
        recommendations.append("Use Python 3.9 or newer for the bundled checker.")
    if not summary["image_decoder"]:
        recommendations.append(
            "Install Pillow or ImageMagick, or use a platform image tool such as sips."
        )
    if not summary["svg_renderer"]:
        recommendations.append(
            "Install resvg, librsvg (rsvg-convert), Inkscape, CairoSVG, "
            "or use a headless browser for SVG rendering."
        )
    if not summary["pptx_generator"]:
        recommendations.append(
            "Install python-pptx or LibreOffice to generate the PPTX package."
        )
    if not summary["powerpoint_app"]:
        recommendations.append(
            "Microsoft PowerPoint was not found. You can still build the PPTX, "
            "but do not claim that Convert to Shape or Ungroup was verified."
        )

    return {
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "python": {
            "version": platform.python_version(),
            "executable": sys.executable,
            "minimum": ".".join(str(part) for part in MIN_PYTHON),
            "ok": python_ok,
        },
        "modules": modules,
        "tools": tools,
        "powerpoint": powerpoint,
        "summary": summary,
        "recommendations": recommendations,
    }


def print_report(report: dict) -> None:
    system = report["platform"]
    python = report["python"]
    summary = report["summary"]

    print("img2pptx environment check")
    print(
        f"Platform: {system['system']} {system['release']} "
        f"({system['machine']})"
    )
    print(
        f"Python: {python['version']} "
        f"[{'ok' if python['ok'] else 'requires 3.9+'}]"
    )

    print("\nPython modules:")
    for name, description in MODULES:
        state = "[ok]" if report["modules"][name] else "[--]"
        print(f"  {state} {name:<14} {description}")

    print("\nTools:")
    for name, description in TOOLS:
        path = report["tools"][name]
        state = "[ok]" if path else "[--]"
        suffix = f" -> {path}" if path else ""
        print(f"  {state} {name:<20} {description}{suffix}")

    print("\nPowerPoint:")
    print(f"  {report['powerpoint'] or 'not found'}")

    print("\nSummary:")
    for key in ("image_decoder", "svg_renderer", "pptx_generator", "powerpoint_app"):
        state = "[ok]" if summary[key] else "[--]"
        print(f"  {state} {key}")

    if report["recommendations"]:
        print("\nRecommendations:")
        for item in report["recommendations"]:
            print(f"  - {item}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report locally available tools for the img2pptx skill."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print a machine-readable JSON report.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "Exit non-zero unless Python 3.9+, an image decoder, an SVG renderer, "
            "and a PPTX generator are available."
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report()

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_report(report)

    summary = report["summary"]
    missing = [
        name
        for name in ("image_decoder", "svg_renderer", "pptx_generator")
        if not summary[name]
    ]
    if args.strict and (not report["python"]["ok"] or missing):
        if missing:
            print(
                "strict check failed; missing: " + ", ".join(missing),
                file=sys.stderr,
            )
        else:
            print("strict check failed; Python 3.9+ is required", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
