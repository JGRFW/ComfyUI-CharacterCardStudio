# -*- coding: utf-8 -*-
"""Simple linear Qwen Image 2.1 character-card pipeline."""

from __future__ import annotations

import json
from typing import Any

import folder_paths
import nodes as comfy_nodes
from comfy_extras.nodes_qwen import TextEncodeQwenImage21

from .asset_composer import compose_role_card
from PIL import Image, ImageDraw
from .renderer import fit_image_to_box, pil_to_tensor, pils_to_tensor, tensor_to_pil
from .splitter import _draw_label, report_json
from .templates import (
    DEFAULT_NEGATIVE,
    FIVE_TEMPLATE_OPTIONS,
    get_template,
    normalise_state,
    one_click_state,
    template_from_option,
)


def _preferred(options: list[str], needle: str) -> str:
    return next((item for item in options if needle.lower() in item.lower()), options[0])


CELL_ASSET_MAP = {
    "reference_profile_18": {
        "hero": 1, "front": 0, "profile": 2, "back": 3,
        "headshot_a": 6, "expression_a": 7, "expression_b": 8, "expression_c": 9,
        "detail_eye": 11, "detail_hand": 12, "detail_costume": 13,
        "detail_fabric_1": 14, "detail_fabric_2": 15, "detail_fabric_3": 16,
        "detail_fabric_4": 19, "detail_accessory": 17,
        "action_a": 4, "action_b": 5,
    },
    "turnaround_3": {"front": 0, "profile": 2, "back": 3},
    "turnaround_hero": {"hero": 1, "front": 0, "profile": 2, "back": 3},
    "costume_breakdown": {
        "hero": 1, "outer": 11, "inner": 12, "bottom": 13, "shoes": 18,
        "accessory_a": 17, "accessory_b": 19, "fabric": 14, "pattern": 16,
        "back_detail": 15,
    },
    "character_profile_12": {
        "hero": 1, "front": 0, "profile": 2, "back": 3, "face": 6,
        "happy": 7, "angry": 8, "sad": 9, "eye": 11, "hand": 12,
        "costume": 13, "prop": 17, "shoes": 18, "fabric": 14,
        "accessory": 15, "pose": 4, "atmosphere": 5,
    },
}


def _compose_individual_assets(assets: list, template: dict, fit_mode: str, show_labels: bool):
    defaults = template.get("defaults", {})
    width = int(template.get("width", 1920))
    height = int(template.get("height", 1080))
    canvas = Image.new("RGB", (width, height), (242, 243, 245))
    draw = ImageDraw.Draw(canvas)
    mapping = CELL_ASSET_MAP.get(template.get("id"), {})
    used = []
    for index, cell in enumerate(template.get("cells", [])):
        asset_index = mapping.get(str(cell.get("id")), index % len(assets))
        asset_index = max(0, min(len(assets) - 1, int(asset_index)))
        asset = assets[asset_index]
        role = str(cell.get("role") or "")
        fit = "contain" if role in {"hero", "turnaround"} or "填满" not in str(fit_mode) and role == "hero" else "cover"
        x = int(round(float(cell.get("x", 0)) * width))
        y = int(round(float(cell.get("y", 0)) * height))
        w = max(1, int(round(float(cell.get("w", 1)) * width)))
        h = max(1, int(round(float(cell.get("h", 1)) * height)))
        rect = (x, y, min(width - 1, x + w), min(height - 1, y + h))
        fitted = fit_image_to_box(asset, (rect[2] - rect[0], rect[3] - rect[1]), fit)
        canvas.paste(fitted, (rect[0], rect[1]))
        draw.rectangle(rect, outline=(211, 214, 219), width=2)
        if show_labels:
            _draw_label(draw, rect, str(cell.get("label") or f"画格 {index + 1}"))
        used.append({"cell": cell.get("id"), "asset": asset_index})
    report = {"mode": "individual-unique-assets", "template": template.get("id"), "mapping": used}
    normalized = [fit_image_to_box(asset, (768, 768), "contain") for asset in assets]
    return canvas, normalized, report


class CardSettingsFive:
    CATEGORY = "AICG3D/角色卡"
    FUNCTION = "build"
    RETURN_TYPES = ("STRING", "IMAGE")
    RETURN_NAMES = ("角色卡设置", "参考图")
    DESCRIPTION = "只提供五种固定角色卡版式。"

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        return {
            "required": {
                "card_type": (FIVE_TEMPLATE_OPTIONS, {"default": FIVE_TEMPLATE_OPTIONS[1]}),
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
        reference_image: Any = None,
    ):
        selected = template_from_option(card_type) or template_from_option(FIVE_TEMPLATE_OPTIONS[0])
        width = int(selected.get("width", 1920))
        height = int(selected.get("height", 1080))
        raw = one_click_state(selected, title, character_prompt, style, show_labels)
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
    DESCRIPTION = "单节点依次生成全身、动作、头像、表情和细节，并输出最终角色卡。"

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
        character = config.get("identity") or config.get("appearance") or "原创角色"
        style = config.get("style") or "电影级角色设定"
        negative = config.get("negativePrompt") or DEFAULT_NEGATIVE
        common = (
            f"同一角色。角色设定：{character}。统一画风：{style}。"
            "保持脸型、五官、瞳色、发型、发色、肤色、身材比例、服装版型和配饰完全一致。"
        )
        prompts = [
            (common + "正面全身，头顶到鞋底完整，纯浅灰白棚拍背景。", 768, 1152),
            (common + "角色主视觉全身，姿态自然，纯浅灰白棚拍背景。", 768, 1152),
            (common + "严格90度侧面全身，头顶到鞋底完整。", 768, 1152),
            (common + "严格180度背面全身，头顶到鞋底完整。", 768, 1152),
            (common + "动作姿态A，完整全身。", 768, 1152),
            (common + "动作姿态B，完整全身。", 768, 1152),
            (common + "正面头像特写，头部和肩部完整。", 768, 768),
            (common + "微笑表情头肩特写。", 768, 768),
            (common + "生气表情头肩特写。", 768, 768),
            (common + "难过表情头肩特写。", 768, 768),
            (common + "惊讶表情头肩特写。", 768, 768),
            (common + "眼睛和妆容细节特写。", 768, 768),
            (common + "手部和戒指细节特写。", 768, 768),
            (common + "服装领口和结构细节特写。", 768, 768),
            (common + "主面料纹理细节A。", 768, 768),
            (common + "面料褶皱细节B。", 768, 768),
            (common + "纽扣、缝线和五金细节。", 768, 768),
            (common + "标志性配饰和项链完整特写。", 768, 768),
            (common + "鞋履结构细节特写。", 768, 768),
            (common + "背部服装结构和接缝细节。", 768, 768),
        ]
        images = []
        anchor = None
        for index, (prompt, width, height) in enumerate(prompts):
            refs = None
            if index == 0 and reference_image is not None:
                refs = {"image_1": reference_image}
            elif index > 0:
                refs = {}
                if reference_image is not None:
                    refs["image_1"] = reference_image
                if anchor is not None:
                    refs["image_2"] = anchor
            encoded = TextEncodeQwenImage21.execute(clip, prompt, negative, vae, 1024, refs).result
            positive, neg, _ = encoded
            latent = {"samples": torch.zeros((1, 64, height // 16, width // 16), device=comfy.model_management.intermediate_device())}
            sampled = comfy_nodes.common_ksampler(model, seed, steps, cfg, sampler_name, scheduler, positive, neg, latent, denoise=1.0)[0]
            image = vae.decode(sampled["samples"])
            images.append(image)
            if index == 0:
                anchor = image
        pil_assets = [tensor_to_pil(image) for image in images]
        card, assets, report = _compose_individual_assets(
            pil_assets,
            template,
            str(config.get("fitMode") or "完整显示"),
            bool(config.get("showLabels", False)),
        )
        return pil_to_tensor(card), pils_to_tensor(pil_assets), report_json(report)


NODE_CLASS_MAPPINGS = {
    "AICG3D_CardSettingsFive": CardSettingsFive,
    "AICG3D_Qwen21ModelLoader": Qwen21ModelLoader,
    "AICG3D_CharacterCardGeneratorSingle": CharacterCardGeneratorSingle,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AICG3D_CardSettingsFive": "1 角色与卡型设置 · 5种卡版",
    "AICG3D_Qwen21ModelLoader": "2 千问 Image 2.1 模型选择",
    "AICG3D_CharacterCardGeneratorSingle": "3 角色卡生成与排版 · 一键完成",
}
