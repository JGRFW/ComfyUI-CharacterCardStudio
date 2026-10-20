# -*- coding: utf-8 -*-
"""Split a generated character sheet and recompose it as another card layout."""

from __future__ import annotations

import json
import re
from typing import Any

from PIL import Image, ImageColor, ImageDraw

from .renderer import fit_image_to_box


def _rgb(value: Any, fallback: str = "#f3f4f6") -> tuple[int, int, int]:
    try:
        return ImageColor.getrgb(str(value))
    except (TypeError, ValueError):
        return ImageColor.getrgb(fallback)


def _rect_for_cell(
    image: Image.Image,
    cell: dict[str, Any],
    inset: float,
) -> tuple[int, int, int, int]:
    width, height = image.size
    inset = max(0.0, min(0.12, float(inset or 0.0)))
    x = int(round((float(cell.get("x", 0.0)) + inset) * width))
    y = int(round((float(cell.get("y", 0.0)) + inset) * height))
    right = int(round((float(cell.get("x", 0.0)) + float(cell.get("w", 1.0)) - inset) * width))
    bottom = int(round((float(cell.get("y", 0.0)) + float(cell.get("h", 1.0)) - inset) * height))
    x = max(0, min(width - 1, x))
    y = max(0, min(height - 1, y))
    right = max(x + 1, min(width, right))
    bottom = max(y + 1, min(height, bottom))
    return x, y, right, bottom


def crop_template_panels(
    image: Image.Image,
    template: dict[str, Any],
    inset: float = 0.01,
) -> list[Image.Image]:
    panels: list[Image.Image] = []
    for cell in template.get("cells", []):
        panels.append(image.crop(_rect_for_cell(image, cell, inset)).convert("RGB"))
    return panels


def parse_panel_order(raw: Any, panel_count: int) -> list[int]:
    text = str(raw or "").strip()
    if not text:
        return list(range(1, panel_count + 1))
    result: list[int] = []
    pattern = re.compile(r"(\d+)\s*[-~至]\s*(\d+)|(\d+)")
    for match in pattern.finditer(text):
        if match.group(3):
            values = [int(match.group(3))]
        else:
            start = int(match.group(1))
            end = int(match.group(2))
            step = 1 if end >= start else -1
            values = list(range(start, end + step, step))
        for value in values:
            if 1 <= value <= panel_count and value not in result:
                result.append(value)
    return result or list(range(1, panel_count + 1))


def _draw_label(
    draw: ImageDraw.ImageDraw,
    rect: tuple[int, int, int, int],
    label: str,
) -> None:
    x1, y1, x2, y2 = rect
    height = max(1, y2 - y1)
    width = max(1, x2 - x1)
    caption_h = max(20, int(height * 0.07))
    draw.rectangle((x1, y2 - caption_h, x2, y2), fill=(255, 255, 255))
    from .renderer import _draw_text

    _draw_text(
        draw,
        (x1 + max(6, width // 55), y2 - caption_h // 2),
        label,
        size=max(12, int(caption_h * 0.5)),
        fill=(42, 45, 51),
        bold=True,
        anchor="lm",
    )


def recompose_card(
    source_image: Image.Image,
    source_template: dict[str, Any],
    target_template: dict[str, Any],
    panel_order: str,
    inset: float = 0.01,
    show_labels: bool = False,
    fit_mode: str = "完整显示",
) -> tuple[Image.Image, list[Image.Image], dict[str, Any]]:
    source_panels = crop_template_panels(source_image, source_template, inset)
    order = parse_panel_order(panel_order, len(source_panels))
    target_fit = "cover" if "填满" in str(fit_mode) else "contain"
    target_cells = target_template.get("cells", [])
    defaults = target_template.get("defaults", {})
    width = int(defaults.get("width") or target_template.get("width") or 2048)
    height = int(defaults.get("height") or target_template.get("height") or 1152)
    canvas = Image.new("RGB", (width, height), _rgb(defaults.get("background"), "#f3f4f6"))
    draw = ImageDraw.Draw(canvas)
    accent = _rgb(defaults.get("accent"), "#d86b73")
    draw.rectangle((0, 0, width, max(3, int(height * 0.006))), fill=accent)

    mapping: list[dict[str, Any]] = []
    for target_index, cell in enumerate(target_cells):
        if not source_panels:
            break
        source_index = order[target_index % len(order)] - 1
        source_index = max(0, min(len(source_panels) - 1, source_index))
        rect = _rect_for_cell(canvas, cell, 0.003)
        box_w = max(1, rect[2] - rect[0])
        box_h = max(1, rect[3] - rect[1])
        fitted = fit_image_to_box(source_panels[source_index], (box_w, box_h), target_fit)
        canvas.paste(fitted, (rect[0], rect[1]))
        draw.rectangle(rect, outline=(211, 214, 219), width=max(1, int(min(width, height) / 1400)))
        if show_labels:
            _draw_label(draw, rect, str(cell.get("label") or f"画格 {target_index + 1}"))
        mapping.append(
            {
                "target": target_index + 1,
                "source": source_index + 1,
                "label": str(cell.get("label") or f"画格 {target_index + 1}"),
            }
        )

    normalized: list[Image.Image] = []
    for panel in source_panels:
        normalized.append(fit_image_to_box(panel, (768, 768), "contain"))
    report = {
        "sourceTemplate": source_template.get("id"),
        "targetTemplate": target_template.get("id"),
        "sourcePanels": len(source_panels),
        "targetPanels": len(target_cells),
        "order": order,
        "fitMode": "填满裁切" if target_fit == "cover" else "完整显示",
        "mapping": mapping,
    }
    return canvas, normalized, report


def report_json(report: dict[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, separators=(",", ":"))
