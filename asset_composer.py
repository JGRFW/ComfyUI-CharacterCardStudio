# -*- coding: utf-8 -*-
"""Role-aware composition for separately generated character assets."""

from __future__ import annotations

from typing import Any

from PIL import Image, ImageColor, ImageDraw, ImageOps

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


def _fit(image: Image.Image, size: tuple[int, int], fit: str, background: tuple[int, int, int]) -> Image.Image:
    width, height = max(1, size[0]), max(1, size[1])
    if fit == "contain":
        fitted = ImageOps.contain(image.convert("RGB"), (width, height), Image.Resampling.LANCZOS)
    else:
        fitted = ImageOps.fit(image.convert("RGB"), (width, height), Image.Resampling.LANCZOS, centering=(0.5, 0.42))
    canvas = Image.new("RGB", (width, height), background)
    canvas.paste(fitted, ((width - fitted.width) // 2, (height - fitted.height) // 2))
    return canvas


def _head_crop(image: Image.Image) -> Image.Image:
    width, height = image.size
    left = int(width * 0.17)
    right = int(width * 0.83)
    bottom = max(1, int(height * 0.38))
    return image.crop((left, 0, max(left + 1, right), bottom)).convert("RGB")


def _body_for_cell(
    cell: dict[str, Any],
    full_front: Image.Image,
    full_profile: Image.Image,
    full_back: Image.Image,
    action_a: Image.Image,
    action_b: Image.Image,
) -> tuple[Image.Image, str]:
    cell_id = str(cell.get("id", "")).lower()
    text = f"{cell.get('id', '')} {cell.get('label', '')} {cell.get('prompt', '')}".lower()
    if _contains_any(text, ("back", "背面", "后视", "背部")):
        return full_back, "full_back"
    if cell_id == "body_right" or _contains_any(text, ("朝左",)):
        return ImageOps.mirror(full_profile), "full_profile_mirrored"
    if cell_id == "body_left":
        return full_profile, "full_profile"
    if _contains_any(text, ("left", "左侧", "侧面", "侧视", "profile", "side")):
        return full_profile, "full_profile"
    if _contains_any(text, ("action_b", "动作b")):
        return action_b, "action_b"
    if _contains_any(text, ("action", "动作", "行走", "动态")):
        return action_a, "action_a"
    if cell.get("role") == "hero":
        return action_a, "hero_action"
    return full_front, "full_front"


def _portrait_for_cell(
    cell: dict[str, Any],
    headshot: Image.Image,
    full_front: Image.Image,
    full_profile: Image.Image,
    full_back: Image.Image,
    action_a: Image.Image,
    portraits: list[Image.Image],
    fallback_index: int,
) -> tuple[Image.Image, str]:
    text = f"{cell.get('id', '')} {cell.get('label', '')} {cell.get('prompt', '')}".lower()
    if _contains_any(text, ("back", "后脑", "背面")):
        return _head_crop(full_back), "full_back_head_crop"
    if _contains_any(text, ("right", "右侧")):
        return ImageOps.mirror(_head_crop(full_profile)), "full_profile_head_crop_mirrored"
    if _contains_any(text, ("side", "profile", "侧脸", "侧面")):
        return _head_crop(full_profile), "full_profile_head_crop"
    if _contains_any(text, ("three_quarter", "斜侧", "四分之三", "三分之四")):
        return _head_crop(action_a), "action_head_crop"
    if text.strip() and "正面" in text:
        return headshot, "headshot"
    if portraits:
        index = fallback_index % len(portraits)
        return portraits[index], f"portrait_{index + 1}"
    return headshot, "headshot"


def _expression_for_cell(cell: dict[str, Any], expressions: list[Image.Image], fallback_index: int) -> tuple[Image.Image, str]:
    text = f"{cell.get('id', '')} {cell.get('label', '')} {cell.get('prompt', '')}"
    mapping = [
        (("neutral", "平静", "中性"), 0),
        (("angry", "生气", "愤怒", "蹙眉", "冷峻"), 2),
        (("surprised", "惊讶", "吃惊"), 4),
        (("thinking", "沉思", "闭眼"), 5),
        (("happy", "开心", "微笑", "快乐"), 1),
        (("sad", "难过", "悲伤"), 3),
        (("shy", "害羞", "温柔"), 5),
    ]
    for words, index in mapping:
        if _contains_any(text, words):
            return expressions[index % len(expressions)], f"expression_{index + 1}"
    index = fallback_index % len(expressions)
    return expressions[index], f"expression_{index + 1}"


def _detail_for_cell(cell: dict[str, Any], details: list[Image.Image], fallback_index: int) -> tuple[Image.Image, str]:
    text = f"{cell.get('id', '')} {cell.get('label', '')} {cell.get('prompt', '')}"
    mapping = [
        (("eye", "眼部", "眼睛", "瞳"), 0),
        (("hand", "手部", "手"), 1),
        (("shoes", "鞋履", "鞋"), 4),
        (("costume", "服装", "衣料", "材质", "面料", "fabric"), 2),
        (("pattern", "图案", "纹样", "徽"), 3),
        (("accessory", "配饰", "道具", "项链", "耳"), 5),
    ]
    for words, index in mapping:
        if _contains_any(text, words):
            return details[index % len(details)], f"detail_{index + 1}"
    index = fallback_index % len(details)
    return details[index], f"detail_{index + 1}"


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
    if str(template.get("kind") or "") == "scene":
        raise ValueError("Scene templates must use the per-cell scene generator, not the character AssetComposer.")
    expressions = crop_equal_grid(expression_sheet, rows=2, cols=3, inset=0.01)
    details = crop_equal_grid(detail_sheet, rows=3, cols=3, inset=0.01)
    portraits = [headshot, *expressions]
    defaults = template.get("defaults", {})
    width = int(template.get("width", 2048))
    height = int(template.get("height", 1152))
    background = _rgb(defaults.get("background"), "#ffffff")
    canvas = Image.new("RGB", (width, height), background)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, width, max(3, int(height * 0.006))), fill=_rgb(defaults.get("accent"), "#d86b73"))

    expression_index = 0
    detail_index = 0
    portrait_index = 0
    mapping: list[dict[str, Any]] = []
    target_fit = "cover" if "填满" in str(fit_mode) else "contain"

    for target_index, cell in enumerate(template.get("cells", [])):
        role = str(cell.get("role") or "custom").lower()
        source_name = ""
        if role in {"turnaround", "hero"}:
            asset, source_name = _body_for_cell(cell, full_front, full_profile, full_back, action_a, action_b)
        elif role == "portrait":
            asset, source_name = _portrait_for_cell(
                cell,
                headshot,
                full_front,
                full_profile,
                full_back,
                action_a,
                portraits,
                portrait_index,
            )
            portrait_index += 1
        elif role == "expression":
            asset, source_name = _expression_for_cell(cell, expressions, expression_index)
            expression_index += 1
        elif role == "detail":
            asset, source_name = _detail_for_cell(cell, details, detail_index)
            detail_index += 1
        else:
            asset, source_name = full_front, "full_front"

        x = int(round(float(cell.get("x", 0)) * width))
        y = int(round(float(cell.get("y", 0)) * height))
        w = max(1, int(round(float(cell.get("w", 1)) * width)))
        h = max(1, int(round(float(cell.get("h", 1)) * height)))
        rect = (x, y, min(width - 1, x + w), min(height - 1, y + h))
        fitted = _fit(asset, (rect[2] - rect[0], rect[3] - rect[1]), target_fit, background)
        canvas.paste(fitted, (rect[0], rect[1]))
        draw.rectangle(rect, outline=(211, 214, 219), width=max(1, int(min(width, height) / 1400)))
        if show_labels:
            _draw_label(draw, rect, str(cell.get("label") or f"画格 {target_index + 1}"))
        mapping.append(
            {
                "target": target_index + 1,
                "role": role,
                "label": str(cell.get("label") or f"画格 {target_index + 1}"),
                "source": source_name,
                "fit": target_fit,
            }
        )

    source_assets = [
        full_front,
        full_profile,
        full_back,
        action_a,
        action_b,
        headshot,
        *expressions,
        *details,
    ]
    normalized = [_fit(asset, (768, 768), "contain", background) for asset in source_assets]
    report = {
        "mode": "role-aware-unique-assets",
        "template": template.get("id"),
        "fitMode": fit_mode,
        "expressionPanels": len(expressions),
        "detailPanels": len(details),
        "mapping": mapping,
    }
    return canvas, normalized, report
