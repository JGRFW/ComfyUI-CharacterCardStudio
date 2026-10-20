# -*- coding: utf-8 -*-
"""Pillow rendering helpers for the character card studio."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageOps

try:
    import torch
except Exception:  # Isolated renderer tests can still use NumPy.
    torch = None

try:
    import folder_paths
except Exception:  # Allows isolated renderer tests.
    folder_paths = None


def _input_root() -> Path:
    if folder_paths is not None:
        return Path(folder_paths.get_input_directory()).resolve()
    return Path.cwd().resolve()


def _safe_input_path(image: str, subfolder: str = "") -> Path | None:
    image = str(image or "").replace("\\", "/").strip()
    subfolder = str(subfolder or "").replace("\\", "/").strip()
    if not image:
        return None
    relative = Path(subfolder) / image if subfolder else Path(image)
    if relative.is_absolute():
        return None
    root = _input_root()
    path = (root / relative).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        return None
    if not path.is_file():
        return None
    return path


def _load_image(image: str, subfolder: str = "") -> Image.Image | None:
    path = _safe_input_path(image, subfolder)
    if path is None:
        return None
    try:
        with Image.open(path) as opened:
            return ImageOps.exif_transpose(opened).convert("RGB")
    except Exception:
        return None


def _rgb(value: Any, fallback: str = "#f3f4f6") -> tuple[int, int, int]:
    try:
        return ImageColor.getrgb(str(value))
    except (ValueError, TypeError):
        return ImageColor.getrgb(fallback)


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, max(8, int(size)))
        except Exception:
            continue
    return ImageFont.load_default()


def _draw_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    *,
    size: int,
    fill: tuple[int, int, int],
    bold: bool = False,
    anchor: str = "la",
) -> None:
    if not text:
        return
    draw.text(xy, text, font=_font(size, bold), fill=fill, anchor=anchor)


def _fit_image(
    image: Image.Image,
    box_size: tuple[int, int],
    fit: str,
    zoom: float,
    offset_x: float,
    offset_y: float,
    background: tuple[int, int, int],
) -> Image.Image:
    box_w, box_h = max(1, box_size[0]), max(1, box_size[1])
    img_w, img_h = image.size
    if img_w <= 0 or img_h <= 0:
        return Image.new("RGB", (box_w, box_h), background)

    zoom = max(0.5, min(3.0, float(zoom or 1.0)))
    if fit == "contain":
        scale = min(box_w / img_w, box_h / img_h) * zoom
    else:
        scale = max(box_w / img_w, box_h / img_h) * zoom
    new_w = max(1, int(round(img_w * scale)))
    new_h = max(1, int(round(img_h * scale)))
    resized = image.resize((new_w, new_h), Image.Resampling.LANCZOS)

    if fit == "contain":
        canvas = Image.new("RGB", (box_w, box_h), background)
        left = (box_w - new_w) // 2
        top = (box_h - new_h) // 2
        canvas.paste(resized, (left, top))
        return canvas

    slack_x = max(0, new_w - box_w)
    slack_y = max(0, new_h - box_h)
    left = int(round(slack_x / 2 - float(offset_x or 0) * slack_x / 2))
    top = int(round(slack_y / 2 - float(offset_y or 0) * slack_y / 2))
    left = max(0, min(slack_x, left))
    top = max(0, min(slack_y, top))
    return resized.crop((left, top, left + box_w, top + box_h))


def _draw_cell(
    board: Image.Image,
    draw: ImageDraw.ImageDraw,
    cell: dict[str, Any],
    slot: dict[str, Any],
    *,
    show_labels: bool,
    accent: tuple[int, int, int],
    muted: tuple[int, int, int],
    border: tuple[int, int, int],
) -> None:
    width, height = board.size
    x = int(round(float(cell.get("x", 0)) * width))
    y = int(round(float(cell.get("y", 0)) * height))
    w = max(1, int(round(float(cell.get("w", 1)) * width)))
    h = max(1, int(round(float(cell.get("h", 1)) * height)))
    rect = (x, y, min(width - 1, x + w), min(height - 1, y + h))
    draw.rounded_rectangle(rect, radius=max(4, int(min(w, h) * 0.02)), fill=(245, 246, 248))

    padding = max(4, int(min(w, h) * 0.018))
    image_box = (x + padding, y + padding, x + w - padding, y + h - padding)
    image_w = max(1, image_box[2] - image_box[0])
    image_h = max(1, image_box[3] - image_box[1])
    source = _load_image(slot.get("image", ""), slot.get("subfolder", ""))

    if source is not None and cell.get("mirror"):
        # 右侧面格：自动水平镜像，保证左右侧面方向相反（不依赖模型自觉）
        source = ImageOps.mirror(source)

    if source is not None:
        fitted = _fit_image(
            source,
            (image_w, image_h),
            str(slot.get("fit") or "cover"),
            float(slot.get("zoom") or 1.0),
            float(slot.get("offsetX") or 0.0),
            float(slot.get("offsetY") or 0.0),
            (233, 235, 238),
        )
        board.paste(fitted, (image_box[0], image_box[1]))
    else:
        draw.rounded_rectangle(
            image_box,
            radius=max(3, int(min(image_w, image_h) * 0.025)),
            fill=(232, 234, 237),
            outline=(216, 219, 224),
            width=max(1, int(min(width, height) / 1400)),
        )
        label = str(slot.get("label") or "参考画格")
        _draw_text(
            draw,
            (image_box[0] + image_w // 2, image_box[1] + image_h // 2),
            label,
            size=max(14, int(min(image_w, image_h) * 0.08)),
            fill=(132, 137, 145),
            bold=True,
            anchor="mm",
        )

    if show_labels:
        caption_h = max(22, int(h * 0.075))
        caption_top = y + h - caption_h
        draw.rounded_rectangle(
            (x, caption_top, x + w, y + h),
            radius=max(3, int(caption_h * 0.25)),
            fill=(255, 255, 255),
        )
        label = str(slot.get("label") or "画格")
        _draw_text(
            draw,
            (x + padding, caption_top + caption_h // 2),
            label,
            size=max(12, int(caption_h * 0.53)),
            fill=(52, 55, 61),
            bold=True,
            anchor="lm",
        )

    draw.rounded_rectangle(
        rect,
        radius=max(4, int(min(w, h) * 0.02)),
        outline=border,
        width=max(1, int(min(width, height) / 1200)),
    )


def render_layout(state: dict[str, Any], template: dict[str, Any]) -> Image.Image:
    width = max(512, min(4096, int(state.get("width") or template.get("width") or 2048)))
    height = max(512, min(4096, int(state.get("height") or template.get("height") or 1152)))
    board = Image.new("RGB", (width, height), _rgb(state.get("background")))
    draw = ImageDraw.Draw(board)
    border = (210, 213, 218)
    muted = (118, 123, 131)
    accent = _rgb(state.get("accent"), "#d86b73")
    show_labels = bool(state.get("showLabels", False))

    # A restrained accent rule gives the layout a clear visual top edge.
    rule_h = max(3, int(height * 0.006))
    draw.rectangle((0, 0, width, rule_h), fill=accent)

    if show_labels:
        title = str(state.get("title") or "未命名角色")
        subtitle = str(state.get("subtitle") or template.get("name") or "角色设定卡")
        _draw_text(
            draw,
            (int(width * 0.025), int(height * 0.035)),
            title,
            size=max(22, int(height * 0.034)),
            fill=(36, 39, 45),
            bold=True,
            anchor="lm",
        )
        _draw_text(
            draw,
            (int(width * 0.975), int(height * 0.04)),
            subtitle,
            size=max(16, int(height * 0.021)),
            fill=muted,
            anchor="rm",
        )

    slots = state.get("slots") if isinstance(state.get("slots"), list) else []
    for index, cell in enumerate(template.get("cells", [])):
        slot = slots[index] if index < len(slots) and isinstance(slots[index], dict) else {}
        if slot and not slot.get("enabled", True):
            slot = {}
        _draw_cell(
            board,
            draw,
            cell,
            slot,
            show_labels=show_labels,
            accent=accent,
            muted=muted,
            border=border,
        )
    return board


def _identity_sources(state: dict[str, Any]) -> list[tuple[str, str, str]]:
    result: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str]] = set()
    library = state.get("library") if isinstance(state.get("library"), list) else []
    for item in library:
        if not isinstance(item, dict) or not item.get("useForIdentity", True):
            continue
        image = str(item.get("image") or "")
        subfolder = str(item.get("subfolder") or "")
        key = (subfolder, image)
        if not image or key in seen:
            continue
        seen.add(key)
        result.append((image, subfolder, str(item.get("name") or image.rsplit("/", 1)[-1])))

    for slot in state.get("slots") or []:
        if not isinstance(slot, dict) or not slot.get("lockIdentity", True):
            continue
        image = str(slot.get("image") or "")
        subfolder = str(slot.get("subfolder") or "")
        key = (subfolder, image)
        if not image or key in seen:
            continue
        seen.add(key)
        result.append((image, subfolder, str(slot.get("label") or image.rsplit("/", 1)[-1])))
    return result[:12]


def render_identity_sheet(state: dict[str, Any], fallback: Image.Image) -> Image.Image:
    sources = _identity_sources(state)
    if not sources:
        return fallback.copy()

    width, height = 2048, 1024
    columns = 4
    rows = max(1, math.ceil(len(sources) / columns))
    rows = min(3, rows)
    gap = 18
    pad = 24
    cell_w = (width - pad * 2 - gap * (columns - 1)) // columns
    cell_h = (height - pad * 2 - gap * (rows - 1)) // rows
    sheet = Image.new("RGB", (width, height), (246, 247, 248))
    draw = ImageDraw.Draw(sheet)

    for index, (image_name, subfolder, label) in enumerate(sources[: columns * rows]):
        row = index // columns
        column = index % columns
        x = pad + column * (cell_w + gap)
        y = pad + row * (cell_h + gap)
        draw.rounded_rectangle(
            (x, y, x + cell_w, y + cell_h),
            radius=8,
            fill=(232, 234, 237),
            outline=(207, 211, 216),
            width=2,
        )
        source = _load_image(image_name, subfolder)
        if source is not None:
            fitted = _fit_image(
                source,
                (cell_w - 10, cell_h - 10),
                "contain",
                1.0,
                0.0,
                0.0,
                (232, 234, 237),
            )
            sheet.paste(fitted, (x + 5, y + 5))
        else:
            _draw_text(
                draw,
                (x + cell_w // 2, y + cell_h // 2),
                label,
                size=28,
                fill=(120, 125, 132),
                anchor="mm",
            )
    return sheet


def pil_to_tensor(image: Image.Image) -> Any:
    array = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
    if torch is not None:
        return torch.from_numpy(array).unsqueeze(0)
    return np.expand_dims(array, axis=0)


def pils_to_tensor(images: Iterable[Image.Image]) -> Any:
    rgb_images = [image.convert("RGB") for image in images]
    if rgb_images:
        target_size = rgb_images[0].size
        rgb_images = [
            image if image.size == target_size else _fit_image(image, target_size, "contain", 1.0, 0.0, 0.0, (0, 0, 0))
            for image in rgb_images
        ]
    arrays = [np.asarray(image, dtype=np.float32) / 255.0 for image in rgb_images]
    if not arrays:
        return pil_to_tensor(Image.new("RGB", (64, 64), (0, 0, 0)))
    batch = np.stack(arrays, axis=0)
    if torch is not None:
        return torch.from_numpy(batch)
    return batch


def tensor_to_pil(tensor: Any) -> Image.Image:
    value = tensor
    if hasattr(value, "detach"):
        value = value.detach().cpu().numpy()
    array = np.asarray(value, dtype=np.float32)
    if array.ndim == 4:
        array = array[0]
    if array.ndim != 3:
        raise ValueError("Expected an IMAGE tensor with shape [1, H, W, C]")
    if array.shape[-1] == 1:
        array = np.repeat(array, 3, axis=-1)
    array = np.clip(array * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(array[..., :3], mode="RGB")


def fit_image_to_box(image: Image.Image, box_size: tuple[int, int], fit: str = "cover") -> Image.Image:
    return _fit_image(image, box_size, fit, 1.0, 0.0, 0.0, (243, 244, 246))


def load_source_images(items: Iterable[dict[str, Any]]) -> list[Image.Image]:
    images: list[Image.Image] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        image = _load_image(str(item.get("image") or ""), str(item.get("subfolder") or ""))
        if image is not None:
            images.append(image)
    return images
