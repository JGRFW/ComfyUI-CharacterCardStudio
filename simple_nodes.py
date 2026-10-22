# -*- coding: utf-8 -*-
"""Simple linear Qwen Image 2.1 character-card pipeline."""

from __future__ import annotations

import json
from typing import Any

import folder_paths
import nodes as comfy_nodes
from comfy_extras.nodes_qwen import TextEncodeQwenImage21
from PIL import Image, ImageDraw, ImageColor, ImageOps

from .renderer import load_source_images, pil_to_tensor, pils_to_tensor, tensor_to_pil
from .splitter import _draw_label, report_json
from .templates import (
    DEFAULT_NEGATIVE,
    FIVE_TEMPLATE_OPTIONS,
    active_slots,
    get_template,
    normalise_state,
    one_click_state,
    template_from_option,
)


def _preferred(options: list[str], needle: str) -> str:
    return next((item for item in options if needle.lower() in item.lower()), options[0])


def _generation_size(cell: dict[str, Any], card_width: int, card_height: int) -> tuple[int, int]:
    """Return a 16-pixel-aligned generation size matching the target cell ratio."""
    target_w = max(1.0, float(cell.get("w", 1.0)) * card_width)
    target_h = max(1.0, float(cell.get("h", 1.0)) * card_height)
    ratio = target_w / target_h

    if ratio >= 1.0:
        width, height = 768.0 * ratio, 768.0
    else:
        width, height = 768.0, 768.0 / max(0.05, ratio)

    scale = min(1.0, 1536.0 / max(width, height))
    width = max(512.0, width * scale)
    height = max(512.0, height * scale)

    def aligned(value: float) -> int:
        return max(512, min(1536, int(round(value / 16.0) * 16)))

    return aligned(width), aligned(height)


def _cell_generation_prompt(cell: dict[str, Any], slot: dict[str, Any], common: str) -> str:
    role = str(cell.get("role") or slot.get("role") or "custom")
    label = str(slot.get("label") or cell.get("label") or "素材")
    detail = str(slot.get("prompt") or cell.get("prompt") or "保持主体一致")

    framing = {
        "hero": (
            "单张角色资产图，只生成一个人物，完整正面全身，从头顶到鞋底全部入镜，"
            "主体居中并留出安全边距。不要拼贴，不要多视图，不要画框。"
        ),
        "turnaround": (
            "单张角色资产图，只生成一个人物，完整全身，从头顶到鞋底全部入镜，"
            "主体居中并留出安全边距。不要拼贴，不要多视图，不要画框。"
        ),
        "portrait": (
            "单张头肩肖像素材，只生成一个人物，头部到肩部完整入镜，"
            "脸部清晰居中。不要全身，不要拼贴，不要画框。"
        ),
        "expression": (
            "单张表情头肩素材，只生成一个人物，头部到肩部完整入镜，"
            "表情明确且与角色默认表情不同。不要全身，不要拼贴，不要画框。"
        ),
        "detail": (
            "单张局部微距素材，只展示指定的服饰、眼睛或配饰细节，"
            "不出现完整人物头部和全身，不拼贴，不要画框。"
        ),
        "scene_anchor": (
            "生成一张场景正面主视图。保持自然透视，完整展示主要地形、建筑、道路、植被或物件，"
            "场景为主，不新增人物或动物，不拼贴，不要画框。"
        ),
        "scene_view": (
            "生成同一场景的单张空间视图。严格延续参考图的空间结构、主要物件、材质和光照，"
            "只改变相机朝向；场景为主，不新增人物或动物，不拼贴，不要画框。"
        ),
        "scene_detail": (
            "生成同一场景的单张环境材质微距，只展示材质、纹理、植被、建筑构件或装饰局部，"
            "不生成完整场景，不新增人物或动物，不拼贴，不要画框。"
        ),
    }.get(role, "单张资产图，只生成一个主体，不要拼贴或多视图。")

    return (
        f"{common}"
        f"当前素材名称：{label}。{detail}。"
        f"{framing}"
        "不要生成设定卡分格，不要生成文字、编号、标签、边框或水印。"
    )

def _fit_asset(
    image: Image.Image,
    size: tuple[int, int],
    *,
    contain: bool,
    background: tuple[int, int, int] = (255, 255, 255),
) -> Image.Image:
    width, height = max(1, size[0]), max(1, size[1])
    source = image.convert("RGB")
    if contain:
        fitted = ImageOps.contain(source, (width, height), Image.Resampling.LANCZOS)
    else:
        fitted = ImageOps.fit(source, (width, height), Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    canvas = Image.new("RGB", (width, height), background)
    canvas.paste(fitted, ((width - fitted.width) // 2, (height - fitted.height) // 2))
    return canvas


def _compose_individual_assets(
    assets: list[Image.Image],
    template: dict[str, Any],
    state: dict[str, Any],
) -> tuple[Image.Image, list[Image.Image], dict[str, Any]]:
    defaults = template.get("defaults", {})
    width = int(state.get("width") or template.get("width") or 1920)
    height = int(state.get("height") or template.get("height") or 1080)
    background = str(state.get("background") or defaults.get("background") or "#ffffff")
    accent = str(state.get("accent") or defaults.get("accent") or "#d86b73")
    try:
        canvas_color = ImageColor.getrgb(background)
        accent_color = ImageColor.getrgb(accent)
    except (ValueError, TypeError):
        canvas_color = (255, 255, 255)
        accent_color = (216, 107, 115)

    canvas = Image.new("RGB", (width, height), canvas_color)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, width, max(3, int(height * 0.006))), fill=accent_color)

    slots = active_slots(state)
    fit_cover = "填满" in str(state.get("fitMode") or "")
    mapping: list[dict[str, Any]] = []
    asset_cursor = 0

    for slot_index, slot in enumerate(slots):
        cell = next(
            (item for item in template.get("cells", []) if item.get("id") == slot.get("cellId")),
            template.get("cells", [])[slot_index] if slot_index < len(template.get("cells", [])) else {},
        )
        if not cell or asset_cursor >= len(assets):
            continue
        role = str(cell.get("role") or "custom")
        x = int(round(float(cell.get("x", 0.0)) * width))
        y = int(round(float(cell.get("y", 0.0)) * height))
        w = max(1, int(round(float(cell.get("w", 1.0)) * width)))
        h = max(1, int(round(float(cell.get("h", 1.0)) * height)))
        rect = (x, y, min(width - 1, x + w), min(height - 1, y + h))
        box_w = max(1, rect[2] - rect[0])
        box_h = max(1, rect[3] - rect[1])
        fitted = _fit_asset(
            assets[asset_cursor],
            (box_w, box_h),
            contain=not fit_cover,
            background=canvas_color,
        )
        canvas.paste(fitted, (rect[0], rect[1]))
        draw.rectangle(rect, outline=(211, 214, 219), width=max(1, int(min(width, height) / 1400)))
        if state.get("showLabels"):
            _draw_label(draw, rect, str(slot.get("label") or cell.get("label") or f"画格 {slot_index + 1}"))
        mapping.append(
            {
                "target": slot_index + 1,
                "cell": cell.get("id"),
                "asset": asset_cursor + 1,
                "role": role,
                "label": str(slot.get("label") or cell.get("label") or ""),
            }
        )
        asset_cursor += 1

    normalized = [_fit_asset(asset, (768, 768), contain=True) for asset in assets]
    report = {
        "mode": "one-asset-per-cell",
        "template": template.get("id"),
        "canvas": [width, height],
        "cellCount": len(slots),
        "uniqueAssets": len(assets),
        "mapping": mapping,
    }
    return canvas, normalized, report


class CardSettingsFive:
    CATEGORY = "AICG3D/角色卡"
    FUNCTION = "build"
    RETURN_TYPES = ("STRING", "IMAGE")
    RETURN_NAMES = ("角色卡设置", "参考图")
    DESCRIPTION = "提供八种角色卡版式和一套通用场景多视图；节点 ID 保留旧名称以兼容已有工作流。"

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        return {
            "required": {
                "card_type": (FIVE_TEMPLATE_OPTIONS, {"default": FIVE_TEMPLATE_OPTIONS[3]}),
                "character_prompt": (
                    "STRING",
                    {
                        "default": "原创角色，写实电影级半写实3D风格，五官清晰，服装与配饰设计完整。",
                        "multiline": True,
                    },
                ),
                "title": ("STRING", {"default": "未命名角色"}),
                "style": ("STRING", {"default": "电影级角色设定，干净背景，柔和棚拍光，专业角色资产"}),
                "show_labels": ("BOOLEAN", {"default": False}),
                "fit_mode": (["完整显示", "填满裁切"], {"default": "完整显示"}),
                "scene_prompt": (
                    "STRING",
                    {
                        "default": "完整场景，空间结构清晰，地形、建筑、道路、植被或主要物件关系明确，真实材质与统一光照。",
                        "multiline": True,
                    },
                ),
            },
            "optional": {"reference_image": ("IMAGE", {"forceInput": True})},
        }

    def build(
        self,
        card_type: str,
        character_prompt: str,
        title: str,
        style: str,
        show_labels: bool,
        fit_mode: str,
        scene_prompt: str,
        reference_image: Any = None,
    ):
        selected = template_from_option(card_type) or template_from_option(FIVE_TEMPLATE_OPTIONS[0])
        width = int(selected.get("width", 1920))
        height = int(selected.get("height", 1080))
        is_scene = str(selected.get("kind") or "") == "scene"
        subject_prompt = scene_prompt if is_scene else character_prompt
        subject_title = "未命名场景" if is_scene and title in {"", "未命名角色"} else title
        raw = one_click_state(selected, subject_title, subject_prompt, style, show_labels)
        state, _ = normalise_state(raw, width, height)
        state["fitMode"] = fit_mode
        return json.dumps(state, ensure_ascii=False, separators=(",", ":")), reference_image


class Qwen21ModelLoader:
    CATEGORY = "AICG3D/角色卡"
    FUNCTION = "load"
    RETURN_TYPES = ("MODEL", "CLIP", "VAE", "STRING", "IMAGE")
    RETURN_NAMES = ("MODEL", "CLIP", "VAE", "角色卡设置", "参考图")
    DESCRIPTION = "主线中的千问 Image 2.1 模型、文本编码器和 VAE 选择。"

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        unets = folder_paths.get_filename_list("diffusion_models")
        clips = folder_paths.get_filename_list("text_encoders")
        vaes = folder_paths.get_filename_list("vae")
        return {
            "required": {
                "settings": ("STRING", {"forceInput": True}),
                "unet_name": (unets, {"default": _preferred(unets, "qwen_image_2.1")}),
                "clip_name": (clips, {"default": _preferred(clips, "qwen3vl_8b_int8")}),
                "vae_name": (vaes, {"default": _preferred(vaes, "qwen_image_2.1_vae")}),
                "weight_dtype": (["default", "fp8_e4m3fn", "fp8_e4m3fn_fast", "fp8_e5m2"], {"default": "default"}),
                "device": (["default", "cpu"], {"default": "default"}),
            },
            "optional": {"reference_image": ("IMAGE", {"forceInput": True})},
        }

    def load(
        self,
        settings: str,
        unet_name: str,
        clip_name: str,
        vae_name: str,
        weight_dtype: str,
        device: str,
        reference_image: Any = None,
    ):
        model = comfy_nodes.UNETLoader().load_unet(unet_name, weight_dtype)[0]
        clip = comfy_nodes.CLIPLoader().load_clip(clip_name, "qwen_image", device)[0]
        vae = comfy_nodes.VAELoader().load_vae(vae_name)[0]
        return model, clip, vae, settings, reference_image


class CharacterCardGeneratorSingle:
    CATEGORY = "AICG3D/角色卡"
    FUNCTION = "generate"
    RETURN_TYPES = ("IMAGE", "IMAGE", "STRING")
    RETURN_NAMES = ("角色卡", "资产批次", "生成报告")
    DESCRIPTION = "每个启用画格独立生成一张素材，再按同一份模板坐标精确拼回角色卡。"

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        return {
            "required": {
                "settings": ("STRING", {"forceInput": True}),
                "model": ("MODEL",),
                "clip": ("CLIP",),
                "vae": ("VAE",),
                "seed": ("INT", {"default": 42, "min": 0, "max": 0xffffffffffffffff}),
                "steps": ("INT", {"default": 8, "min": 1, "max": 100}),
                "cfg": ("FLOAT", {"default": 3.0, "min": 0.0, "max": 20.0, "step": 0.1}),
                "sampler_name": (["euler", "euler_ancestral", "dpmpp_2m", "sa_solver"], {"default": "euler"}),
                "scheduler": (["simple", "normal", "karras", "beta"], {"default": "simple"}),
            },
            "optional": {"reference_image": ("IMAGE", {"forceInput": True})},
        }

    def generate(
        self,
        settings: str,
        model: Any,
        clip: Any,
        vae: Any,
        seed: int,
        steps: int,
        cfg: float,
        sampler_name: str,
        scheduler: str,
        reference_image: Any = None,
    ):
        import torch
        import comfy.model_management

        config = json.loads(settings)
        template = get_template(config.get("templateId"))
        state, _ = normalise_state(config, int(template.get("width", 1920)), int(template.get("height", 1080)))
        state["fitMode"] = str(config.get("fitMode") or "完整显示")
        slots = active_slots(state)
        if not slots:
            raise ValueError("CharacterCardStudio: no enabled card cells")

        is_scene = str(template.get("kind") or "") == "scene"
        cell_by_id = {cell["id"]: cell for cell in template.get("cells", [])}
        anchor_slot = next(
            (slot for slot in slots if cell_by_id.get(str(slot.get("cellId") or ""), {}).get("role") == "scene_anchor"),
            None,
        )
        anchor_pil = None
        anchor_ref = None
        anchor_source = ""
        if is_scene and anchor_slot and anchor_slot.get("image"):
            loaded = load_source_images([anchor_slot])
            if loaded:
                anchor_pil = loaded[0]
                anchor_ref = pil_to_tensor(anchor_pil)
                anchor_source = "uploaded_cell"
        elif is_scene and reference_image is not None:
            anchor_pil = tensor_to_pil(reference_image)
            anchor_ref = reference_image
            anchor_source = "reference_input"

        subject = state.get("identity") or state.get("appearance") or "原创主体"
        style = state.get("style") or "电影级角色设定"
        negative = str(state.get("negativePrompt") or DEFAULT_NEGATIVE)
        if is_scene:
            negative += "，新增人物，新增动物，场景结构漂移，地形变化，建筑位置错乱，主要物件形变，材质不一致，视角重复"
            common = (
                f"同一个场景。场景设定：{subject}。统一风格：{style}。"
                "参考图是唯一空间锚点，必须保持地形、建筑、道路、植被、主要物件、材质、颜色和主光方向一致。"
                "只改变相机朝向，场景为主，不新增人物或动物，视角之间不能重复使用同一张构图。"
            )
        else:
            identity_lock = (
                "参考图是同一人，严格复刻其脸型、五官、瞳色、发型发色、肤色、服装和配饰。"
                if reference_image is not None
                else ""
            )
            common = (
                f"同一角色。角色设定：{subject}。统一画风：{style}。{identity_lock}"
                "保持脸型、五官、瞳色、发型、发色、肤色、身材比例、服装版型和配饰完全一致。"
            )
        images = []

        for index, slot in enumerate(slots):
            cell = cell_by_id.get(str(slot.get("cellId") or ""))
            if not cell:
                continue
            role = str(cell.get("role") or "")
            if is_scene and role == "scene_anchor" and anchor_pil is not None:
                images.append(anchor_pil)
                continue
            width, height = _generation_size(cell, int(state["width"]), int(state["height"]))
            prompt = _cell_generation_prompt(cell, slot, common)
            refs = {}
            reference_for_cell = anchor_ref if is_scene and anchor_ref is not None else reference_image
            if reference_for_cell is not None:
                refs["image_1"] = reference_for_cell
            encoded = TextEncodeQwenImage21.execute(clip, prompt, negative, vae, 1024, refs).result
            positive, neg, _ = encoded
            cell_seed = (int(seed) + index * 0x9E3779B1) & 0xFFFFFFFFFFFFFFFF
            latent = {
                "samples": torch.zeros(
                    (1, 64, height // 16, width // 16),
                    device=comfy.model_management.intermediate_device(),
                )
            }
            sampled = comfy_nodes.common_ksampler(
                model,
                cell_seed,
                int(steps),
                float(cfg),
                sampler_name,
                scheduler,
                positive,
                neg,
                latent,
                denoise=1.0,
            )[0]
            image = vae.decode(sampled["samples"])
            images.append(image)
            if is_scene and role == "scene_anchor" and anchor_ref is None:
                anchor_ref = image
                anchor_pil = tensor_to_pil(image)
                anchor_source = "generated_anchor"

        assets = [tensor_to_pil(image) for image in images]
        card, normalized, report = _compose_individual_assets(assets, template, state)
        report["sceneMode"] = is_scene
        report["anchorSource"] = anchor_source if is_scene else ""
        return pil_to_tensor(card), pils_to_tensor(normalized), report_json(report)


NODE_CLASS_MAPPINGS = {
    "AICG3D_CardSettingsFive": CardSettingsFive,
    "AICG3D_Qwen21ModelLoader": Qwen21ModelLoader,
    "AICG3D_CharacterCardGeneratorSingle": CharacterCardGeneratorSingle,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AICG3D_CardSettingsFive": "1 角色/场景卡型设置 · 9种卡版",
    "AICG3D_Qwen21ModelLoader": "2 千问 Image 2.1 模型选择",
    "AICG3D_CharacterCardGeneratorSingle": "3 角色/场景逐格生成与排版 · 一键完成",
}
