# -*- coding: utf-8 -*-
"""Role-aware composition for separately generated character assets."""

from __future__ import annotations

from typing import Any

from PIL import Image, ImageColor, ImageDraw

from .renderer import fit_image_to_box
from .splitter import _draw_label


def _rgb(value: Any, fallback: str = "#ffffff") -> tuple[int, int, int]:
    try:
        return ImageColor.getrgb(str(value))
    except (TypeError, ValueError):
        return ImageColor.getrgb(fallback)


def crop_equal_grid(image: Image.Image, rows: int = 2, cols: int = 3, inset: float = 0.008) -> list[Image.Image]:
    width, height = image.size
    cell_w = width / cols
    cell_h = height / rows
    inset_x = int(round(cell_w * max(0.0, min(0.1, inset))))
    inset_y = int(round(cell_h * max(0.0, min(0.1, inset))))
    panels: list[Image.Image] = []
    for row in range(rows):
        for col in range(cols):
            left = int(round(col * cell_w)) + inset_x
            top = int(round(row * cell_h)) + inset_y
            right = int(round((col + 1) * cell_w)) - inset_x
            bottom = int(round((row + 1) * cell_h)) - inset_y
            panels.append(image.crop((left, top, max(left + 1, right), max(top + 1, bottom))).convert("RGB"))
    return panels


def _contains_any(text: str, words: tuple[str, ...]) -> bool:
    return any(word in text for word in words)


def _fullbody_for_cell(cell: dict[str, Any], full_front: Image.Image, full_profile: Image.Image, full_back: Image.Image) -> Image.Image:
    text = f"{cell.get('id', '')} {cell.get('label', '')}".lower()
    if _contains_any(text, ("back", "背面", "后视", "背部")):
        return full_back
    if _contains_any(text, ("profile", "side", "侧面", "侧视", "右侧", "左侧")):
        return full_profile
    return full_front


def _expression_for_cell(
    cell: dict[str, Any],
    expressions: list[Image.Image],
    headshot: Image.Image,
    fallback_index: int,
) -> Image.Image:
    text = f"{cell.get('id', '')} {cell.get('label', '')} {cell.get('prompt', '')}"
    if _contains_any(text, ("neutral", "平静", "中性", "基础胸像")):
        return headshot
    mapping = [
        (("happy", "开心", "微笑", "快乐", "喜"), 0),
        (("angry", "生气", "愤怒", "怒"), 1),
        (("sad", "难过", "悲伤", "哀"), 2),
        (("surprised", "惊讶", "吃惊"), 3),
        (("shy", "害羞", "委屈", "撒娇"), 4),
        (("thinking", "沉思", "冷漠", "放空"), 5),
    ]
    for words, index in mapping:
        if _contains_any(text, words):
            return expressions[index % len(expressions)]
    return expressions[fallback_index % len(expressions)]


def _detail_for_cell(cell: dict[str, Any], details: list[Image.Image], fallback_index: int) -> Image.Image:
    text = f"{cell.get('id', '')} {cell.get('label', '')} {cell.get('prompt', '')}"
    mapping = [
        (("eye", "眼部", "眼睛", "瞳"), 0),
        (("hand", "手部", "手"), 1),
        (("costume", "服装", "衣", "材质", "面料", "fabric"), 2),
        (("pattern", "图案", "纹样", "徽"), 3),
        (("shoes", "鞋"), 4),
        (("accessory", "配饰", "道具", "项链", "耳"), 5),
    ]
    for words, index in mapping:
        if _contains_any(text, words):
            return details[index % len(details)]
    return details[fallback_index % len(details)]


def compose_role_card(
    *,
    full_front: Image.Image,
    full_profile: Image.Image,
    full_back: Image.Image,
    action_a: Image.Image,
    action_b: Image.Image,
    headshot: Image.Image,
    expression_sheet: Image.Image,
    detail_sheet: Image.Image,
    template: dict[str, Any],
    panel_order: str = "",
    fit_mode: str = "完整显示",
    show_labels: bool = False,
) -> tuple[Image.Image, list[Image.Image], dict[str, Any]]:
    expressions = crop_equal_grid(expression_sheet, rows=2, cols=3, inset=0.01)
    details = crop_equal_grid(detail_sheet, rows=3, cols=3, inset=0.01)
    defaults = template.get("defaults", {})
    width = int(template.get("width", 2048))
    height = int(template.get("height", 1152))
    canvas = Image.new("RGB", (width, height), _rgb(defaults.get("background"), "#ffffff"))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, width, max(3, int(height * 0.006))), fill=_rgb(defaults.get("accent"), "#d86b73"))

    expression_index = 0
    detail_index = 0
    mapping: list[dict[str, Any]] = []
    all_assets: list[Image.Image] = [full_front, full_profile, full_back, action_a, action_b, headshot, *expressions, *details]

    for target_index, cell in enumerate(template.get("cells", [])):
        role = str(cell.get("role") or "custom").lower()
        text = f"{cell.get('id', '')} {cell.get('label', '')} {cell.get('prompt', '')}".lower()
        if "action_a" in text:
            asset = action_b
            fit = "contain"
        elif "action_b" in text:
            asset = action_a
            fit = "contain"
        elif cell.get("id") == "hero":
            asset = action_a
            fit = "contain"
        elif role in {"turnaround", "hero"} or _contains_any(text, ("全身", "站姿", "主视觉", "整体造型")):
            asset = _fullbody_for_cell(cell, full_front, full_profile, full_back)
            fit = "contain"
        elif role in {"portrait"} or _contains_any(text, ("头像", "胸像", "大头贴")):
            asset = headshot
            fit = "cover"
        elif role in {"expression"}:
            asset = _expression_for_cell(cell, expressions, headshot, expression_index)
            expression_index += 1
            fit = "cover"
        elif role in {"detail"}:
            asset = _detail_for_cell(cell, details, detail_index)
            detail_index += 1
            fit = "cover"
        elif _contains_any(text, ("表情", "开心", "生气", "难过", "惊讶", "微笑")):
            asset = _expression_for_cell(cell, expressions, headshot, expression_index)
            expression_index += 1
            fit = "cover"
        elif _contains_any(text, ("细节", "眼部", "手部", "材质", "鞋", "配饰", "道具")):
            asset = _detail_for_cell(cell, details, detail_index)
            detail_index += 1
            fit = "cover"
        else:
            asset = full_front
            fit = "contain"

        target_fit = "contain" if fit == "contain" or "填满" not in str(fit_mode) and role in {"turnaround", "hero"} else "cover"
        x = int(round(float(cell.get("x", 0)) * width))
        y = int(round(float(cell.get("y", 0)) * height))
        w = max(1, int(round(float(cell.get("w", 1)) * width)))
        h = max(1, int(round(float(cell.get("h", 1)) * height)))
        rect = (x, y, min(width - 1, x + w), min(height - 1, y + h))
        box_w = max(1, rect[2] - rect[0])
        box_h = max(1, rect[3] - rect[1])
        fitted = fit_image_to_box(asset, (box_w, box_h), target_fit)
        canvas.paste(fitted, (rect[0], rect[1]))
        draw.rectangle(rect, outline=(211, 214, 219), width=max(1, int(min(width, height) / 1400)))
        if show_labels:
            _draw_label(draw, rect, str(cell.get("label") or f"画格 {target_index + 1}"))
        mapping.append(
            {
                "target": target_index + 1,
                "role": role,
                "label": str(cell.get("label") or f"画格 {target_index + 1}"),
                "fit": target_fit,
            }
        )

    normalized = [fit_image_to_box(asset, (768, 768), "contain") for asset in all_assets]
    report = {
        "mode": "role-aware-assets",
        "template": template.get("id"),
        "fitMode": fit_mode,
        "expressionPanels": len(expressions),
        "detailPanels": len(details),
        "mapping": mapping,
    }
    return canvas, normalized, report
