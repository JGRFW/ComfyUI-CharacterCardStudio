# -*- coding: utf-8 -*-
"""Character card templates and prompt compilation."""

from __future__ import annotations

import copy
import json
import re
from typing import Any


DEFAULT_NEGATIVE = (
    "低质量，模糊，畸形，多余肢体，错误手指，身份漂移，脸部崩坏，性别漂移，"
    "服装结构错误，配饰缺失，面板布局混乱，重复人物，文字乱码，水印，logo"
    "，头部裁切，脚部裁切，鞋履裁切，半身构图，断脚，切头"
)


def _cell(
    cell_id: str,
    label: str,
    role: str,
    prompt: str,
    x: float,
    y: float,
    w: float,
    h: float,
) -> dict[str, Any]:
    return {
        "id": cell_id,
        "label": label,
        "role": role,
        "prompt": prompt,
        "x": x,
        "y": y,
        "w": w,
        "h": h,
    }


TEMPLATES: list[dict[str, Any]] = [
    {
        "id": "turnaround_3",
        "name": "标准三视图",
        "description": "正面、侧面、背面同尺度全身转面。",
        "width": 1920,
        "height": 1080,
        "defaults": {
            "title": "未命名角色",
            "subtitle": "全身三视图",
            "style": "电影级角色设定，柔和棚拍光，真实皮肤与布料纹理，统一色调",
            "background": "#f2f3f5",
            "accent": "#d86b73",
        },
        "cells": [
            _cell(
                "front",
                "正面全身",
                "turnaround",
                "严格正面全身站姿，平视镜头，双臂自然下垂，完整展示鞋履与服装正面结构。",
                0.025,
                0.13,
                0.30,
                0.82,
            ),
            _cell(
                "profile",
                "侧面全身",
                "turnaround",
                "严格 90 度侧面全身站姿，身体比例、服装版型与正面完全一致，完整展示侧面轮廓。",
                0.35,
                0.13,
                0.30,
                0.82,
            ),
            _cell(
                "back",
                "背面全身",
                "turnaround",
                "严格 180 度背面全身站姿，完整展示背部服装结构、发型后侧与鞋履后跟。",
                0.675,
                0.13,
                0.30,
                0.82,
            ),
        ],
    },
    {
        "id": "turnaround_hero",
        "name": "主视觉三视图",
        "description": "左侧主视觉，右侧正面、侧面、背面全身。",
        "width": 2048,
        "height": 1152,
        "defaults": {
            "title": "未命名角色",
            "subtitle": "角色视觉设定",
            "style": "高端角色设定卡，电影级 CG 质感，清晰轮廓，统一棚拍光",
            "background": "#f4f4f2",
            "accent": "#cf6f5a",
        },
        "cells": [
            _cell(
                "hero",
                "主视觉",
                "hero",
                "角色主视觉半身或三分之二身构图，视线平视，气质明确，服装与配饰完整可读。",
                0.025,
                0.13,
                0.34,
                0.82,
            ),
            _cell(
                "front",
                "正面全身",
                "turnaround",
                "严格正面全身站姿，完整展示脸、发型、服装、鞋履和身体比例。",
                0.39,
                0.13,
                0.185,
                0.82,
            ),
            _cell(
                "profile",
                "侧面全身",
                "turnaround",
                "严格 90 度侧面全身站姿，服装轮廓与配饰结构清晰，比例与正面一致。",
                0.59,
                0.13,
                0.185,
                0.82,
            ),
            _cell(
                "back",
                "背面全身",
                "turnaround",
                "严格 180 度背面全身站姿，完整展示后脑发型、背部服装和鞋履后侧。",
                0.79,
                0.13,
                0.185,
                0.82,
            ),
        ],
    },
    {
        "id": "expression_10",
        "name": "表情十宫格",
        "description": "五列两行，统一头肩构图与光线。",
        "width": 2048,
        "height": 1152,
        "defaults": {
            "title": "未命名角色",
            "subtitle": "表情设定",
            "style": "角色表情资产卡，统一头肩构图，柔和面部棚拍光，真实皮肤质感",
            "background": "#f6f5f3",
            "accent": "#d58b64",
        },
        "cells": [
            _cell("neutral", "平静", "expression", "中性平静，放松眉眼，嘴唇自然闭合。", 0.025, 0.14, 0.185, 0.36),
            _cell("happy", "开心", "expression", "自然开心，眼睛含笑，嘴角上扬，不夸张。", 0.218, 0.14, 0.185, 0.36),
            _cell("angry", "生气", "expression", "克制生气，眉头轻压，目光锐利，嘴唇微收。", 0.411, 0.14, 0.185, 0.36),
            _cell("sad", "难过", "expression", "安静难过，眉心轻蹙，眼睑微垂，不流泪。", 0.604, 0.14, 0.185, 0.36),
            _cell("surprised", "惊讶", "expression", "轻微惊讶，眼睛稍睁大，嘴唇微张，保留角色气质。", 0.797, 0.14, 0.178, 0.36),
            _cell("shy", "害羞", "expression", "害羞，视线略微避开镜头，脸颊轻微泛红。", 0.025, 0.53, 0.185, 0.36),
            _cell("thinking", "沉思", "expression", "沉思，目光偏离镜头，表情专注而克制。", 0.218, 0.53, 0.185, 0.36),
            _cell("smile", "微笑", "expression", "温柔微笑，眼神柔和，面部肌肉自然。", 0.411, 0.53, 0.185, 0.36),
            _cell("cold", "冷漠", "expression", "冷淡平静，直视镜头，面部张力极低。", 0.604, 0.53, 0.185, 0.36),
            _cell("upset", "委屈", "expression", "轻微委屈，眉尾下垂，嘴唇轻抿，不夸张。", 0.797, 0.53, 0.178, 0.36),
        ],
    },
    {
        "id": "character_profile_12",
        "name": "角色设定卡",
        "description": "主视觉、三视图、表情、五官和服装细节的综合版式。",
        "width": 2400,
        "height": 1500,
        "defaults": {
            "title": "未命名角色",
            "subtitle": "角色设定集",
            "style": "高级游戏与影视角色设定表，统一色彩管理，精细材质，专业资产卡排版",
            "background": "#f2f3f5",
            "accent": "#b85f68",
        },
        "cells": [
            _cell("hero", "角色主视觉", "hero", "完整角色主视觉，展示脸、发型、服装和标志性配饰。", 0.025, 0.13, 0.25, 0.55),
            _cell("front", "正面全身", "turnaround", "正面全身，完整服装与鞋履结构。", 0.29, 0.13, 0.12, 0.26),
            _cell("profile", "侧面全身", "turnaround", "严格 90 度侧面全身。", 0.42, 0.13, 0.12, 0.26),
            _cell("back", "背面全身", "turnaround", "严格 180 度背面全身。", 0.55, 0.13, 0.12, 0.26),
            _cell("face", "正面头像", "portrait", "正面头像特写，平视镜头，五官与妆容清晰。", 0.69, 0.13, 0.13, 0.26),
            _cell("happy", "表情 开心", "expression", "自然开心，眼神与嘴角同时变化。", 0.83, 0.13, 0.14, 0.26),
            _cell("angry", "表情 生气", "expression", "克制生气，眉眼张力明确。", 0.69, 0.42, 0.13, 0.26),
            _cell("sad", "表情 难过", "expression", "安静难过，眼睑微垂，不夸张流泪。", 0.83, 0.42, 0.14, 0.26),
            _cell("eye", "眼部细节", "detail", "眼睛与睫毛极近特写，保留瞳色和眼型。", 0.29, 0.44, 0.12, 0.24),
            _cell("hand", "手部细节", "detail", "手部自然姿态特写，皮肤质感与配饰一致。", 0.42, 0.44, 0.12, 0.24),
            _cell("costume", "服装细节", "detail", "标志性服装材质、剪裁、图案和五金细节。", 0.55, 0.44, 0.12, 0.24),
            _cell("prop", "配饰与道具", "detail", "角色标志性配饰或道具特写，结构准确，材质真实。", 0.025, 0.71, 0.25, 0.24),
            _cell("shoes", "鞋履细节", "detail", "鞋履侧面、材质与鞋带结构细节。", 0.29, 0.69, 0.12, 0.26),
            _cell("fabric", "材质纹理", "detail", "主面料与辅料纹理微距特写。", 0.42, 0.69, 0.12, 0.26),
            _cell("accessory", "标志配饰", "detail", "标志性配饰结构与佩戴位置特写。", 0.55, 0.69, 0.12, 0.26),
            _cell("pose", "标志动作", "hero", "角色标志性动作或动态站姿，保持完整人物比例与服装结构。", 0.69, 0.69, 0.13, 0.26),
            _cell("atmosphere", "氛围镜头", "hero", "角色氛围镜头，展示性格气质与服装整体效果，背景简洁。", 0.83, 0.69, 0.14, 0.26),
        ],
    },
    {
        "id": "costume_breakdown",
        "name": "服装拆解",
        "description": "左侧全身，右侧九项服装、配饰和材质细节。",
        "width": 2200,
        "height": 1400,
        "defaults": {
            "title": "未命名角色",
            "subtitle": "服装与配饰拆解",
            "style": "服装设计设定卡，真实布料纹理，专业产品级棚拍，干净统一背景",
            "background": "#f4f3f0",
            "accent": "#4f8078",
        },
        "cells": [
            _cell("hero", "整体造型", "hero", "完整角色造型，正面自然站姿，展示全部服装层级。", 0.025, 0.13, 0.30, 0.82),
            _cell("outer", "外层服装", "detail", "外层服装正面结构、领口、袖型和下摆。", 0.35, 0.13, 0.20, 0.25),
            _cell("inner", "内搭", "detail", "内搭面料、领型与层次关系。", 0.56, 0.13, 0.20, 0.25),
            _cell("bottom", "下装", "detail", "下装版型、腰头、口袋与褶皱。", 0.77, 0.13, 0.20, 0.25),
            _cell("shoes", "鞋履", "detail", "鞋履侧面与材质细节，左右结构一致。", 0.35, 0.39, 0.20, 0.25),
            _cell("accessory_a", "配饰 A", "detail", "第一件标志性配饰的结构与材质。", 0.56, 0.39, 0.20, 0.25),
            _cell("accessory_b", "配饰 B", "detail", "第二件标志性配饰的结构与材质。", 0.77, 0.39, 0.20, 0.25),
            _cell("fabric", "材质细节", "detail", "主面料与辅料纹理微距特写。", 0.35, 0.65, 0.20, 0.30),
            _cell("pattern", "图案与徽记", "detail", "服装图案、徽记或纹样局部特写。", 0.56, 0.65, 0.20, 0.30),
            _cell("back_detail", "背部结构", "detail", "背部服装结构和关键接缝细节。", 0.77, 0.65, 0.20, 0.30),
        ],
    },
    {
        "id": "reference_profile_18",
        "name": "参考角色卡18格",
        "description": "按最早参考图设计的综合角色卡：主视觉、三视图、头像、表情、细节和动作。",
        "width": 1920,
        "height": 1080,
        "defaults": {
            "title": "未命名角色",
            "subtitle": "角色设定卡",
            "style": "高级角色设定集，统一棚拍光，真实材质，专业卡版排版",
            "background": "#f1f2f4",
            "accent": "#c86464",
        },
        "cells": [
            _cell("hero", "角色主视觉", "hero", "完整角色主视觉，全身姿态，服装和人物气质完整展示。", 0.04, 0.12, 0.23, 0.50),
            _cell("front", "正面全身", "turnaround", "正面全身，头顶到鞋底完整。", 0.29, 0.12, 0.075, 0.23),
            _cell("profile", "侧面全身", "turnaround", "90度侧面全身，头顶到鞋底完整。", 0.38, 0.12, 0.075, 0.23),
            _cell("back", "背面全身", "turnaround", "180度背面全身，头顶到鞋底完整。", 0.47, 0.12, 0.075, 0.23),
            _cell("headshot_a", "正面头像", "portrait", "正面头像特写，头部和肩部完整。", 0.56, 0.12, 0.11, 0.23),
            _cell("expression_a", "微笑表情", "expression", "温柔微笑，头肩特写。", 0.69, 0.12, 0.11, 0.23),
            _cell("expression_b", "开心表情", "expression", "自然开心，头肩特写。", 0.56, 0.38, 0.11, 0.23),
            _cell("expression_c", "生气表情", "expression", "克制生气，头肩特写。", 0.69, 0.38, 0.11, 0.23),
            _cell("detail_eye", "面部细节", "detail", "眼睛、眼镜和妆容细节特写。", 0.29, 0.38, 0.075, 0.23),
            _cell("detail_hand", "手部细节", "detail", "手部姿态和配饰特写。", 0.38, 0.38, 0.075, 0.23),
            _cell("detail_costume", "服装细节", "detail", "领口和服装结构细节。", 0.47, 0.38, 0.075, 0.23),
            _cell("detail_fabric_1", "面料细节 1", "detail", "主面料纹理特写。", 0.04, 0.66, 0.11, 0.27),
            _cell("detail_fabric_2", "面料细节 2", "detail", "服装褶皱和纹理特写。", 0.15, 0.66, 0.11, 0.27),
            _cell("detail_fabric_3", "面料细节 3", "detail", "纽扣、缝线和材质细节。", 0.26, 0.66, 0.11, 0.27),
            _cell("detail_fabric_4", "面料细节 4", "detail", "袖口或边缘纹理细节。", 0.37, 0.66, 0.11, 0.27),
            _cell("detail_accessory", "标志配饰", "detail", "标志性项链或配饰完整特写。", 0.48, 0.66, 0.11, 0.27),
            _cell("action_a", "动作姿态 A", "hero", "角色动态站姿 A，全身完整。", 0.60, 0.66, 0.11, 0.27),
            _cell("action_b", "动作姿态 B", "hero", "角色动态站姿 B，全身完整。", 0.73, 0.66, 0.11, 0.27),
        ],
    },
    {
        "id": "custom_grid",
        "name": "自由九宫格",
        "description": "九格自由卡版，适合自定分镜、表情或动作组合。",
        "width": 1920,
        "height": 1080,
        "defaults": {
            "title": "未命名角色",
            "subtitle": "自由角色卡",
            "style": "统一角色设定卡，干净背景，清晰分格，专业排版",
            "background": "#f3f4f6",
            "accent": "#597e9e",
        },
        "cells": [
            _cell("cell_1", "画格 01", "custom", "描述这一格的角色状态、镜头、动作与构图。", 0.025, 0.14, 0.30, 0.25),
            _cell("cell_2", "画格 02", "custom", "描述这一格的角色状态、镜头、动作与构图。", 0.35, 0.14, 0.30, 0.25),
            _cell("cell_3", "画格 03", "custom", "描述这一格的角色状态、镜头、动作与构图。", 0.675, 0.14, 0.30, 0.25),
            _cell("cell_4", "画格 04", "custom", "描述这一格的角色状态、镜头、动作与构图。", 0.025, 0.40, 0.30, 0.25),
            _cell("cell_5", "画格 05", "custom", "描述这一格的角色状态、镜头、动作与构图。", 0.35, 0.40, 0.30, 0.25),
            _cell("cell_6", "画格 06", "custom", "描述这一格的角色状态、镜头、动作与构图。", 0.675, 0.40, 0.30, 0.25),
            _cell("cell_7", "画格 07", "custom", "描述这一格的角色状态、镜头、动作与构图。", 0.025, 0.665, 0.30, 0.25),
            _cell("cell_8", "画格 08", "custom", "描述这一格的角色状态、镜头、动作与构图。", 0.35, 0.665, 0.30, 0.25),
            _cell("cell_9", "画格 09", "custom", "描述这一格的角色状态、镜头、动作与构图。", 0.675, 0.665, 0.30, 0.25),
        ],
    },
]

TEMPLATE_BY_ID = {template["id"]: template for template in TEMPLATES}
FIVE_TEMPLATE_IDS = [
    "turnaround_3",
    "reference_profile_18",
    "costume_breakdown",
    "turnaround_hero",
    "character_profile_12",
]
FIVE_TEMPLATE_OPTIONS = [f"{template_id} | {TEMPLATE_BY_ID[template_id]['name']}" for template_id in FIVE_TEMPLATE_IDS]
TEMPLATE_OPTIONS = [f"{template['id']} | {template['name']}" for template in TEMPLATES]
DEFAULT_TEMPLATE_OPTION = next(
    (option for option in TEMPLATE_OPTIONS if option.startswith("reference_profile_18 |")),
    TEMPLATE_OPTIONS[0],
)
SOURCE_TEMPLATE_OPTIONS = ["source | 与输入卡版相同", *TEMPLATE_OPTIONS]


def get_templates_payload() -> dict[str, Any]:
    return {
        "version": 1,
        "templates": copy.deepcopy(TEMPLATES),
        "defaultNegative": DEFAULT_NEGATIVE,
    }


def get_template(template_id: str | None) -> dict[str, Any]:
    return TEMPLATE_BY_ID.get(str(template_id or ""), TEMPLATES[0])


def template_from_option(value: str | None, *, allow_source: bool = False) -> dict[str, Any] | None:
    text = str(value or "").strip()
    if allow_source and text.startswith("source |"):
        return None
    template_id = text.split("|", 1)[0].strip()
    return TEMPLATE_BY_ID.get(template_id, TEMPLATES[0])


def one_click_state(
    template: dict[str, Any],
    title: str,
    character_prompt: str,
    style: str,
    show_labels: bool,
) -> dict[str, Any]:
    defaults = template.get("defaults", {})
    return {
        "templateId": template["id"],
        "title": _safe_text(title, defaults.get("title", "未命名角色"), 120),
        "subtitle": defaults.get("subtitle", template.get("name", "角色设定卡")),
        "identity": _safe_text(character_prompt, "", 3000),
        "appearance": _safe_text(character_prompt, "", 3000),
        "outfit": "",
        "palette": "",
        "style": _safe_text(style, defaults.get("style", ""), 1200),
        "negativePrompt": DEFAULT_NEGATIVE,
        "background": defaults.get("background", "#f3f4f6"),
        "accent": defaults.get("accent", "#d86b73"),
        "showLabels": bool(show_labels),
        "width": template.get("width", 2048),
        "height": template.get("height", 1152),
        "slots": [],
        "library": [],
    }


def parse_state(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return copy.deepcopy(raw)
    if not raw:
        return {}
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {}
        except (TypeError, ValueError):
            return {}
    return {}


def _clamp_int(value: Any, low: int, high: int, default: int) -> int:
    try:
        number = int(float(value))
    except (TypeError, ValueError):
        number = default
    number = max(low, min(high, number))
    return int(round(number / 16.0) * 16)


def _safe_text(value: Any, default: str = "", limit: int = 4000) -> str:
    text = str(value if value is not None else default)
    text = text.replace("\x00", "").strip()
    return text[:limit]


def _safe_float(value: Any, default: float, low: float, high: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    return max(low, min(high, number))


def _safe_image_name(value: Any) -> str:
    text = str(value or "").replace("\\", "/").strip()
    text = re.sub(r"[\r\n\t]", "", text)
    return text[:512]


def normalise_state(raw_state: Any, width: int, height: int) -> tuple[dict[str, Any], dict[str, Any]]:
    raw = parse_state(raw_state)
    template = get_template(raw.get("templateId") or raw.get("template_id"))
    defaults = template.get("defaults", {})
    cells = template.get("cells", [])
    previous_slots = raw.get("slots") if isinstance(raw.get("slots"), list) else []

    state: dict[str, Any] = {
        "version": 1,
        "templateId": template["id"],
        "title": _safe_text(raw.get("title"), defaults.get("title", "未命名角色"), 120),
        "subtitle": _safe_text(raw.get("subtitle"), defaults.get("subtitle", "角色设定卡"), 160),
        "identity": _safe_text(raw.get("identity"), "", 3000),
        "appearance": _safe_text(raw.get("appearance"), "", 3000),
        "outfit": _safe_text(raw.get("outfit"), "", 3000),
        "palette": _safe_text(raw.get("palette"), "", 500),
        "style": _safe_text(raw.get("style"), defaults.get("style", ""), 1200),
        "negativePrompt": _safe_text(raw.get("negativePrompt"), DEFAULT_NEGATIVE, 2400),
        "background": _safe_text(raw.get("background"), defaults.get("background", "#f3f4f6"), 32),
        "accent": _safe_text(raw.get("accent"), defaults.get("accent", "#d86b73"), 32),
        "showLabels": bool(raw.get("showLabels", False)),
        "width": _clamp_int(width, 512, 4096, int(template.get("width", 2048))),
        "height": _clamp_int(height, 512, 4096, int(template.get("height", 1152))),
        "slots": [],
        "library": [],
    }

    for index, cell in enumerate(cells):
        source = previous_slots[index] if index < len(previous_slots) and isinstance(previous_slots[index], dict) else {}
        state["slots"].append(
            {
                "id": _safe_text(source.get("id"), f"slot_{index + 1}", 80),
                "cellId": cell["id"],
                "label": _safe_text(source.get("label"), cell.get("label", f"画格 {index + 1}"), 120),
                "role": _safe_text(source.get("role"), cell.get("role", "custom"), 80),
                "prompt": _safe_text(source.get("prompt"), cell.get("prompt", ""), 2400),
                "image": _safe_image_name(source.get("image")),
                "subfolder": _safe_image_name(source.get("subfolder")),
                "fit": (
                    "contain"
                    if str(source.get("fit") or ("contain" if cell.get("role") in {"turnaround", "hero"} else "cover")) == "contain"
                    else "cover"
                ),
                "zoom": round(_safe_float(source.get("zoom"), 1.0, 0.5, 3.0), 3),
                "offsetX": round(_safe_float(source.get("offsetX"), 0.0, -1.0, 1.0), 3),
                "offsetY": round(_safe_float(source.get("offsetY"), 0.0, -1.0, 1.0), 3),
                "lockIdentity": bool(source.get("lockIdentity", True)),
                "enabled": bool(source.get("enabled", True)),
            }
        )

    library = raw.get("library") if isinstance(raw.get("library"), list) else []
    seen: set[tuple[str, str]] = set()
    for item in library:
        if not isinstance(item, dict):
            continue
        image = _safe_image_name(item.get("image") or item.get("name"))
        subfolder = _safe_image_name(item.get("subfolder"))
        if not image:
            continue
        key = (subfolder, image)
        if key in seen:
            continue
        seen.add(key)
        state["library"].append(
            {
                "image": image,
                "subfolder": subfolder,
                "name": _safe_text(item.get("name") or image.rsplit("/", 1)[-1], image, 240),
                "useForIdentity": bool(item.get("useForIdentity", True)),
            }
        )

    # Keep every slot image in the identity library even for older workflows.
    for slot in state["slots"]:
        image = slot.get("image")
        if not image:
            continue
        key = (slot.get("subfolder", ""), image)
        if key not in seen:
            seen.add(key)
            state["library"].append(
                {
                    "image": image,
                    "subfolder": slot.get("subfolder", ""),
                    "name": image.rsplit("/", 1)[-1],
                    "useForIdentity": True,
                }
            )

    return state, template


def _clean_sentence(text: str) -> str:
    value = _safe_text(text, "", 2400)
    value = re.sub(r"\s+", " ", value)
    return value.rstrip("。；; ")


def compile_prompt(state: dict[str, Any], template: dict[str, Any]) -> str:
    width = int(state.get("width") or template.get("width") or 2048)
    height = int(state.get("height") or template.get("height") or 1152)
    title = state.get("title") or "未命名角色"
    subtitle = state.get("subtitle") or template.get("name") or "角色设定卡"
    enabled_slots = [slot for slot in state.get("slots", []) if slot.get("enabled", True)]

    lines = [
        "生成一张完整的角色设定卡，输入图1是版式与素材参考图。",
        f"输出画布为 {width}×{height} 的横向设定卡，使用清晰、整齐、专业的分格排版，"
        f"浅色统一背景，细线分隔，所有画格之间保留稳定的间距。",
        "严格保持所有画格中的角色为同一个人：脸型、五官、瞳色、发型、发色、肤色、"
        "身体比例、服装版型、配饰位置和整体色彩必须完全一致。",
        "所有全身画格必须完整显示从头顶到鞋底的整个人物，头顶和脚底保留安全边距，"
        "不得裁掉头部、脚部或鞋履，严禁把全身照裁成半身照。",
    ]

    if state.get("identity"):
        lines.append(f"角色身份与性格：{_clean_sentence(state['identity'])}。")
    if state.get("appearance"):
        lines.append(f"外貌锁定：{_clean_sentence(state['appearance'])}。")
    if state.get("outfit"):
        lines.append(f"服装与配饰锁定：{_clean_sentence(state['outfit'])}。")
    if state.get("palette"):
        lines.append(f"固定色板：{_clean_sentence(state['palette'])}。")
    if state.get("style"):
        lines.append(f"统一风格：{_clean_sentence(state['style'])}。")

    lines.append(f"卡版类型：{template.get('name', subtitle)}；标题：{title}；副标题：{subtitle}。")
    lines.append("按以下顺序从左到右、从上到下生成每一个画格：")
    for index, slot in enumerate(enabled_slots, start=1):
        label = _clean_sentence(slot.get("label") or f"画格 {index}")
        prompt = _clean_sentence(slot.get("prompt") or "保持角色一致")
        lines.append(f"{index}. {label}：{prompt}。")

    if state.get("showLabels"):
        labels = "、".join(
            f"“{_clean_sentence(slot.get('label') or f'画格 {index}')}”"
            for index, slot in enumerate(enabled_slots, start=1)
        )
        lines.append(
            f"每个画格下方使用简洁中文标签，标签文字必须准确为：{labels}。"
            "文字排版统一，不出现错字、乱码、额外字母或水印。"
        )
    else:
        lines.append("画面内不生成说明文字、字母、数字、logo 或水印，只保留纯视觉角色资产。")

    lines.extend(
        [
            "输入图1只提供角色外观、配色、服装和版式参考；最终画面中的角色必须完整、自然、可独立阅读。",
            "保持每一格的主体居中、比例正确、手部自然、面部稳定，避免同一画格出现重复人物。",
            "最终输出应当是一张可以直接用于角色资产库的高完成度角色卡，而不是拼贴草稿。",
        ]
    )
    return "\n".join(lines)


def card_schema_for_ui() -> dict[str, Any]:
    return {
        "version": 1,
        "fields": [
            "templateId",
            "title",
            "subtitle",
            "identity",
            "appearance",
            "outfit",
            "palette",
            "style",
            "negativePrompt",
            "background",
            "accent",
            "showLabels",
            "width",
            "height",
            "slots",
            "library",
        ],
    }
