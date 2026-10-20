# -*- coding: utf-8 -*-
"""ComfyUI nodes for automatic character-card generation and slicing."""

from __future__ import annotations

import json
import folder_paths
import nodes as comfy_nodes
from typing import Any

from .renderer import (
    pil_to_tensor,
    pils_to_tensor,
    render_identity_sheet,
    render_layout,
    tensor_to_pil,
)
from .asset_composer import compose_role_card
from comfy_extras.nodes_qwen import TextEncodeQwenImage21
from .splitter import recompose_card, report_json
from .templates import (
    FIVE_TEMPLATE_OPTIONS,
    DEFAULT_TEMPLATE_OPTION,
    DEFAULT_NEGATIVE,
    TEMPLATE_OPTIONS,
    compile_prompt,
    get_template,
    normalise_state,
    one_click_state,
    template_from_option,
)


class CharacterCardStudio:
    CATEGORY = "AICG3D/角色卡"
    FUNCTION = "build"
    RETURN_TYPES = ("STRING", "STRING", "IMAGE", "IMAGE", "STRING", "INT", "INT")
    RETURN_NAMES = ("提示词", "负面提示词", "排版参考图", "身份参考图", "卡版JSON", "宽度", "高度")
    DESCRIPTION = "可视化角色卡排版、参考图复用、画格重排与千问 Image 2.1 提示词编译。"

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        return {
            "required": {
                "card_state": (
                    "STRING",
                    {"default": "{}", "multiline": False, "dynamicPrompts": False},
                ),
                "width": ("INT", {"default": 1920, "min": 512, "max": 4096, "step": 16}),
                "height": ("INT", {"default": 1080, "min": 512, "max": 4096, "step": 16}),
            }
        }

    @classmethod
    def IS_CHANGED(cls, card_state: str, width: int, height: int, **_: Any) -> str:
        return f"{width}x{height}:{card_state}"

    def build(
        self, card_state: str, width: int, height: int
    ) -> tuple[str, str, Any, Any, str, int, int]:
        state, template = normalise_state(card_state, width, height)
        prompt = compile_prompt(state, template)
        negative = str(state.get("negativePrompt") or DEFAULT_NEGATIVE)
        layout = render_layout(state, template)
        identity = render_identity_sheet(state, layout)
        card_json = json.dumps(state, ensure_ascii=False, separators=(",", ":"))
        return (
            prompt,
            negative,
            pil_to_tensor(layout),
            pil_to_tensor(identity),
            card_json,
            int(state["width"]),
            int(state["height"]),
        )


class CharacterCardOneClick:
    CATEGORY = "AICG3D/角色卡"
    FUNCTION = "build"
    RETURN_TYPES = ("STRING", "STRING", "IMAGE", "STRING", "INT", "INT", "STRING")
    RETURN_NAMES = ("提示词", "负面提示词", "版式引导图", "卡版JSON", "宽度", "高度", "卡版选项")
    DESCRIPTION = "一张参考图或一段人物提示词，集中控制卡版、排序、全身显示和输出尺寸。"

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        return {
            "required": {
                "template": (TEMPLATE_OPTIONS, {"default": DEFAULT_TEMPLATE_OPTION}),
                "character_prompt": (
                    "STRING",
                    {
                        "default": "原创角色，写实电影级半写实3D风格，五官清晰，服装与配饰设计完整。",
                        "multiline": True,
                    },
                ),
                "title": ("STRING", {"default": "未命名角色"}),
                "style": (
                    "STRING",
                    {"default": "统一角色设定卡，电影级角色资产，干净背景，柔和棚拍光，专业排版"},
                ),
                "show_labels": ("BOOLEAN", {"default": False}),
                "panel_order": ("STRING", {"default": "1-17"}),
                "fit_mode": (["完整显示", "填满裁切"], {"default": "完整显示"}),
                "inset": (
                    "FLOAT",
                    {"default": 0.008, "min": 0.0, "max": 0.12, "step": 0.002},
                ),
            }
        }

    def build(
        self,
        template: str,
        character_prompt: str,
        title: str,
        style: str,
        show_labels: bool,
        panel_order: str,
        fit_mode: str,
        inset: float,
    ) -> tuple[str, str, Any, str, int, int, str]:
        selected = template_from_option(template) or template_from_option(TEMPLATE_OPTIONS[0])
        width = int(selected.get("width", 2048))
        height = int(selected.get("height", 1152))
        raw_state = one_click_state(selected, title, character_prompt, style, show_labels)
        state, resolved = normalise_state(raw_state, width, height)
        state["identity"] = character_prompt
        state["appearance"] = character_prompt
        state["title"] = title or "未命名角色"
        state["showLabels"] = bool(show_labels)
        state["panelOrder"] = panel_order
        state["fitMode"] = fit_mode
        state["inset"] = float(inset)
        prompt = compile_prompt(state, resolved)
        negative = str(state.get("negativePrompt") or DEFAULT_NEGATIVE)
        guide = render_layout(state, resolved)
        card_json = json.dumps(state, ensure_ascii=False, separators=(",", ":"))
        template_option = f"{resolved['id']} | {resolved['name']}"
        return (
            prompt,
            negative,
            pil_to_tensor(guide),
            card_json,
            int(state["width"]),
            int(state["height"]),
            template_option,
        )


class CharacterSheetSplitter:
    CATEGORY = "AICG3D/角色卡"
    FUNCTION = "split"
    RETURN_TYPES = ("IMAGE", "IMAGE", "STRING")
    RETURN_NAMES = ("重排角色卡", "切片批次", "切分报告")
    DESCRIPTION = "自动读取首节点的卡版配置，完成切片、全身完整显示和重组，无需额外参数。"

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        return {
            "required": {
                "images": ("IMAGE",),
                "card_config": (
                    "STRING",
                    {"default": "{}", "forceInput": True},
                ),
            }
        }

    def split(self, images: Any, card_config: str) -> tuple[Any, Any, str]:
        config: dict[str, Any] = {}
        try:
            parsed = json.loads(str(card_config or "{}"))
            if isinstance(parsed, dict):
                config = parsed
        except (TypeError, ValueError):
            config = {}
        template = get_template(config.get("templateId"))
        panel_order = str(config.get("panelOrder") or "1-99")
        fit_mode = str(config.get("fitMode") or "完整显示")
        inset = float(config.get("inset") or 0.008)
        show_labels = bool(config.get("showLabels", False))
        source_image = tensor_to_pil(images)
        card, panels, report = recompose_card(
            source_image,
            template,
            template,
            panel_order,
            inset,
            show_labels,
            fit_mode,
        )
        return pil_to_tensor(card), pils_to_tensor(panels), report_json(report)


NODE_CLASS_MAPPINGS = {
    "AICG3D_CharacterCardStudio": CharacterCardStudio,
    "AICG3D_CharacterCardOneClick": CharacterCardOneClick,
    "AICG3D_CharacterSheetSplitter": CharacterSheetSplitter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AICG3D_CharacterCardStudio": "角色卡工作台 · Qwen Image 2.1",
    "AICG3D_CharacterCardOneClick": "一键角色卡提示词 · Qwen Image 2.1",
    "AICG3D_CharacterSheetSplitter": "角色卡自动切片 · 无需设置",
}


class CharacterCardAssetPrompt:
    CATEGORY = "AICG3D/角色卡"
    FUNCTION = "build"
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "IMAGE", "INT", "INT")
    RETURN_NAMES = ("正面全身", "侧面全身", "背面全身", "头像", "动作A", "动作B", "表情组", "细节组", "负面提示词", "卡版配置", "版式引导图", "宽度", "高度")
    DESCRIPTION = "分别生成全身、头像、表情和细节资产提示词，再按设计卡版组合。"

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        return {
            "required": {
                "template": (TEMPLATE_OPTIONS, {"default": DEFAULT_TEMPLATE_OPTION}),
                "character_prompt": ("STRING", {"default": "原创角色，写实电影级半写实3D风格，五官清晰，服装与配饰设计完整。", "multiline": True}),
                "title": ("STRING", {"default": "未命名角色"}),
                "style": ("STRING", {"default": "电影级角色设定，干净背景，柔和棚拍光，专业角色资产"}),
                "show_labels": ("BOOLEAN", {"default": False}),
                "fit_mode": (["完整显示", "填满裁切"], {"default": "完整显示"}),
            }
        }

    def build(self, template: str, character_prompt: str, title: str, style: str, show_labels: bool, fit_mode: str):
        selected = template_from_option(template) or template_from_option(TEMPLATE_OPTIONS[0])
        width = int(selected.get("width", 2048))
        height = int(selected.get("height", 1152))
        raw_state = one_click_state(selected, title, character_prompt, style, show_labels)
        state, resolved = normalise_state(raw_state, width, height)
        state["fitMode"] = fit_mode
        state["panelOrder"] = "role-aware"
        state["inset"] = 0.008
        common = (
            f"同一原创角色，角色名：{title}。角色设定：{character_prompt}。"
            f"统一画风：{style}。保持脸型、五官、瞳色、发型、发色、肤色、身材比例、服装版型和配饰完全一致。"
        )
        full_front = common + "正面全身角色资产图。人物从头顶到鞋底完整出现在画面中，头顶和脚底留有安全边距，不能裁切头部、鞋子或脚部，纯浅灰白棚拍背景，平视，双臂自然下垂。"
        full_profile = common + "严格90度侧面全身角色资产图。人物从头顶到鞋底完整出现在画面中，不能裁切头部、鞋子或脚部，纯浅灰白棚拍背景，身体比例与正面一致。"
        full_back = common + "严格180度背面全身角色资产图。人物从头顶到鞋底完整出现在画面中，不能裁切头部、鞋子或脚部，完整展示背部服装结构，纯浅灰白棚拍背景。"
        headshot = common + "正面头像特写。只拍头部与肩部，脸居中，平视镜头，五官、妆容、发型和耳饰清晰，浅灰白棚拍背景，不要全身，不要裁掉头顶。"
        action_a = common + "角色动态站姿A。完整全身，从头顶到鞋底全部可见，动作自然有个性，服装结构清晰，纯浅灰白棚拍背景。"
        action_b = common + "角色动态站姿B。完整全身，从头顶到鞋底全部可见，动作与站姿A明显不同，服装和配饰保持一致，纯浅灰白棚拍背景。"
        expression = common + "生成2行3列表情资产网格。六个画格全部是同一角色的头肩特写，分别是平静、开心、生气、难过、惊讶、害羞。每格构图统一、脸部清晰、表情差异明确，细白分隔线，无文字、无水印。"
        detail = common + "生成3行3列角色细节资产网格。九个画格分别是眼睛特写、嘴巴或妆容、手部、面料纹理A、面料纹理B、纽扣或缝线、服装图案、鞋履、标志性配饰。每格内容不同、单独完整、细白分隔线，无文字、无水印。"
        negative = str(state.get("negativePrompt") or DEFAULT_NEGATIVE) + "，裁头，裁脚，半身替代全身，错误格子内容，表情格出现全身，全身格出现头像"
        guide = render_layout(state, resolved)
        card_config = json.dumps(state, ensure_ascii=False, separators=(",", ":"))
        return full_front, full_profile, full_back, headshot, action_a, action_b, expression, detail, negative, card_config, pil_to_tensor(guide), int(state["width"]), int(state["height"])


class CharacterCardAssetComposer:
    CATEGORY = "AICG3D/角色卡"
    FUNCTION = "compose"
    RETURN_TYPES = ("IMAGE", "IMAGE", "STRING")
    RETURN_NAMES = ("角色卡", "资产批次", "组合报告")
    DESCRIPTION = "把独立生成的正侧面全身、头像、表情组和细节组按角色卡版式组合。"

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        return {
            "required": {
                "full_front": ("IMAGE",),
                "full_profile": ("IMAGE",),
                "full_back": ("IMAGE",),
                "action_a": ("IMAGE",),
                "action_b": ("IMAGE",),
                "headshot": ("IMAGE",),
                "expression_sheet": ("IMAGE",),
                "detail_sheet": ("IMAGE",),
                "card_config": ("STRING", {"default": "{}", "forceInput": True}),
            }
        }

    def compose(self, full_front: Any, full_profile: Any, full_back: Any, action_a: Any, action_b: Any, headshot: Any, expression_sheet: Any, detail_sheet: Any, card_config: str):
        config: dict[str, Any] = {}
        try:
            parsed = json.loads(str(card_config or "{}"))
            if isinstance(parsed, dict):
                config = parsed
        except (TypeError, ValueError):
            config = {}
        template = get_template(config.get("templateId"))
        card, assets, report = compose_role_card(
            full_front=tensor_to_pil(full_front),
            full_profile=tensor_to_pil(full_profile),
            full_back=tensor_to_pil(full_back),
            action_a=tensor_to_pil(action_a),
            action_b=tensor_to_pil(action_b),
            headshot=tensor_to_pil(headshot),
            expression_sheet=tensor_to_pil(expression_sheet),
            detail_sheet=tensor_to_pil(detail_sheet),
            template=template,
            fit_mode=str(config.get("fitMode") or "完整显示"),
            show_labels=bool(config.get("showLabels", False)),
        )
        return pil_to_tensor(card), pils_to_tensor(assets), report_json(report)

NODE_CLASS_MAPPINGS.update({
    "AICG3D_CharacterCardAssetPrompt": CharacterCardAssetPrompt,
    "AICG3D_CharacterCardAssetComposer": CharacterCardAssetComposer,
})

NODE_DISPLAY_NAME_MAPPINGS.update({
    "AICG3D_CharacterCardAssetPrompt": "角色卡分项提示词 · Qwen Image 2.1",
    "AICG3D_CharacterCardAssetComposer": "角色卡专业排版 · 全身/表情/头像自动归位",
})

from .simple_nodes import NODE_CLASS_MAPPINGS as SIMPLE_NODE_CLASS_MAPPINGS
from .simple_nodes import NODE_DISPLAY_NAME_MAPPINGS as SIMPLE_NODE_DISPLAY_NAME_MAPPINGS

NODE_CLASS_MAPPINGS.update(SIMPLE_NODE_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(SIMPLE_NODE_DISPLAY_NAME_MAPPINGS)
