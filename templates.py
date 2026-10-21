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
    "，头部裁切，脚部裁切，鞋履裁切，半身构图，断脚，切头，"
    "灰色背景，深灰背景，暗背景，渐变背景，纹理背景，阴影背景"
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
    mirror: bool = False,
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
        "mirror": mirror,
    }


TEMPLATES: list[dict[str, Any]] = [
    # ===== 1. 四格·偏立（4格：左大头像 + 右3全身竖排）=====
    {
        "id": "bighead_body3",
        "name": "四格·偏立",
        "description": "左侧一个超大头肩特写，右侧竖排正面/侧面/背面三个完整全身。",
        "width": 1920,
        "height": 1200,
        "defaults": {
            "title": "未命名角色",
            "subtitle": "角色设定",
            "style": "统一角色资产，纯白棚拍背景，柔和棚拍光，写实电影级",
            "background": "#ffffff",
            "accent": "#d86b73",
        },
        "cells": [
            _cell("head_big", "大头像", "portrait", "超大头肩正面特写，五官清晰，正视镜头。", 0.03, 0.03, 0.40, 0.94),
            _cell("body_front", "正面全身", "turnaround", "完整正面全身，头顶到鞋底。", 0.46, 0.12, 0.16, 0.78),
            _cell("body_side", "侧面全身", "turnaround", "纯侧面全身，人物面朝画面正右方，只能看到左半边脸和左耳，头顶到鞋底。", 0.635, 0.12, 0.16, 0.78),
            _cell("body_back", "背面全身", "turnaround", "完整180度背面全身，头顶到鞋底。", 0.81, 0.12, 0.16, 0.78),
        ],
    },
    # ===== 2. 四格·双帧（4格：上排2头 + 下排2全身）=====
    {
        "id": "dualfour_ref",
        "name": "四格·双帧",
        "description": "上排正面头像+侧面头像，下排正面全身+背面全身。",
        "width": 1920,
        "height": 1200,
        "defaults": {
            "title": "未命名角色",
            "subtitle": "双视设定",
            "style": "统一角色资产，纯白棚拍背景，柔和棚拍光，写实电影级",
            "background": "#ffffff",
            "accent": "#6b8dd8",
        },
        "cells": [
            _cell("head_front", "正面头像", "portrait", "头肩正面特写，正视镜头。", 0.03, 0.03, 0.46, 0.43),
            _cell("head_side", "侧面头像", "portrait", "头肩90度侧面特写，人物面朝画面正右方，只能看到左半边脸和左耳。", 0.51, 0.03, 0.46, 0.43),
            _cell("body_front", "正面全身", "turnaround", "完整正面全身，正视镜头，头顶到鞋底。", 0.03, 0.52, 0.46, 0.45),
            _cell("body_back", "背面全身", "turnaround", "完整180度背面全身，头顶到鞋底。", 0.51, 0.52, 0.46, 0.45),
        ],
    },
    # ===== 3. 五格·正反（5格：上排2头 + 下排3全身）=====
    {
        "id": "fiveref",
        "name": "五格·正反",
        "description": "上排正面头像+背面头像，下排正面/侧面/背面三个完整全身。",
        "width": 1920,
        "height": 1200,
        "defaults": {
            "title": "未命名角色",
            "subtitle": "五视设定",
            "style": "统一角色资产，纯白棚拍背景，柔和棚拍光，写实电影级",
            "background": "#ffffff",
            "accent": "#65a89a",
        },
        "cells": [
            _cell("head_front", "正面头像", "portrait", "头肩正面特写，正视镜头。", 0.03, 0.03, 0.47, 0.43),
            _cell("head_back", "背面头像", "portrait", "头肩背面特写，展示后脑发型。", 0.50, 0.03, 0.47, 0.43),
            _cell("body_front", "正面全身", "turnaround", "完整正面全身，正视镜头，头顶到鞋底。", 0.03, 0.52, 0.305, 0.45),
            _cell("body_side", "侧面全身", "turnaround", "纯侧面全身，人物面朝画面正右方，只能看到左半边脸和左耳，头顶到鞋底。", 0.348, 0.52, 0.305, 0.45),
            _cell("body_back", "背面全身", "turnaround", "完整180度背面全身，头顶到鞋底。", 0.665, 0.52, 0.305, 0.45),
        ],
    },
    # ===== 4. 六格·三视图（6格：上排3头 + 下排3全身）=====
    {
        "id": "head_body_6",
        "name": "六格·三视图",
        "description": "上排头肩正面/侧面/后脑，下排正面/侧面/背面完整全身。",
        "width": 1920,
        "height": 1280,
        "defaults": {
            "title": "未命名角色",
            "subtitle": "三视图设定",
            "style": "统一角色资产，纯白棚拍背景，柔和棚拍光，写实电影级",
            "background": "#ffffff",
            "accent": "#6b8dd8",
        },
        "cells": [
            _cell("head_front", "正面头像", "portrait", "头肩正面特写，正视镜头。", 0.03, 0.03, 0.303, 0.43),
            _cell("head_side", "侧面头像", "portrait", "头肩90度侧面特写，人物面朝画面正右方，只能看到左半边脸和左耳。", 0.345, 0.03, 0.303, 0.43),
            _cell("head_back", "后脑头像", "portrait", "头肩背面特写，展示后脑发型。", 0.66, 0.03, 0.303, 0.43),
            _cell("body_front", "正面全身", "turnaround", "完整正面全身，正视镜头，头顶到鞋底。", 0.03, 0.52, 0.303, 0.45),
            _cell("body_side", "侧面全身", "turnaround", "纯侧面全身，人物面朝画面正右方，只能看到左半边脸和左耳，头顶到鞋底。", 0.345, 0.52, 0.303, 0.45),
            _cell("body_back", "背面全身", "turnaround", "完整180度背面全身，头顶到鞋底。", 0.66, 0.52, 0.303, 0.45),
        ],
    },
    # ===== 5. 六格·斜帧（6格：上排3头含四分之三视角 + 下排3全身）=====
    {
        "id": "sixtilt_ref",
        "name": "六格·斜帧",
        "description": "上排正面/四分之三斜侧/后脑三个头像，下排正面/侧面/背面三个完整全身。",
        "width": 1920,
        "height": 1280,
        "defaults": {
            "title": "未命名角色",
            "subtitle": "斜侧设定",
            "style": "统一角色资产，纯白棚拍背景，柔和棚拍光，写实电影级",
            "background": "#ffffff",
            "accent": "#9b7dd8",
        },
        "cells": [
            _cell("head_front", "正面头像", "portrait", "头肩正面特写，正视镜头。", 0.03, 0.03, 0.303, 0.43),
            _cell("head_three_quarter", "斜侧头像", "portrait", "头肩四分之三斜侧特写，脸朝画面右前方，眼神看向镜头。", 0.345, 0.03, 0.303, 0.43),
            _cell("head_back", "后脑头像", "portrait", "头肩背面特写，展示后脑发型。", 0.66, 0.03, 0.303, 0.43),
            _cell("body_front", "正面全身", "turnaround", "完整正面全身，正视镜头，头顶到鞋底。", 0.03, 0.52, 0.303, 0.45),
            _cell("body_side", "侧面全身", "turnaround", "纯侧面全身，人物面朝画面正右方，只能看到左半边脸和左耳，头顶到鞋底。", 0.345, 0.52, 0.303, 0.45),
            _cell("body_back", "背面全身", "turnaround", "完整180度背面全身，头顶到鞋底。", 0.66, 0.52, 0.303, 0.45),
        ],
    },
    # ===== 6. 八格·表情谱（8格：上排4表情 + 下排4全身）=====
    {
        "id": "expr_body_8",
        "name": "八格·表情谱",
        "description": "上排4个头肩表情，下排4个完整全身（正/侧/背/另一侧）。",
        "width": 1920,
        "height": 1200,
        "defaults": {
            "title": "未命名角色",
            "subtitle": "多视图设定",
            "style": "统一角色资产，纯白棚拍背景，柔和棚拍光，写实电影级",
            "background": "#ffffff",
            "accent": "#d86b73",
        },
        "cells": [
            _cell("head_neutral", "平静", "expression", "头肩特写，中性平静，嘴唇闭合，正视镜头，面无表情。", 0.03, 0.03, 0.225, 0.43),
            _cell("head_happy", "开心大笑", "expression", "头肩特写，开心大笑，张嘴露齿，眼睛弯成月牙。", 0.268, 0.03, 0.225, 0.43),
            _cell("head_serious", "认真", "expression", "头肩特写，认真严肃，眉头微蹙，嘴唇紧抿，直视镜头。", 0.505, 0.03, 0.225, 0.43),
            _cell("head_angry", "生气", "expression", "头肩特写，明显生气，皱眉瞪眼，嘴角下撇，怒视镜头。", 0.743, 0.03, 0.225, 0.43),
            _cell("body_front", "正面全身", "turnaround", "完整正面全身，正视镜头，双臂自然下垂，头顶到鞋底。", 0.03, 0.52, 0.225, 0.45),
            _cell("body_profile", "左侧面全身", "turnaround", "纯侧面全身，人物面朝画面正右方，只能看到左半边脸和左耳，头顶到鞋底。", 0.268, 0.52, 0.225, 0.45),
            _cell("body_profile2", "右侧面全身", "turnaround", "纯侧面全身，人物面朝画面正左方，只能看到右半边脸和右耳，与左侧面互为镜像，头顶到鞋底。", 0.505, 0.52, 0.225, 0.45, mirror=True),
            _cell("body_back", "背面全身", "turnaround", "完整180度背面全身，只能看到后脑和后背，头顶到鞋底。", 0.743, 0.52, 0.225, 0.45),
        ],
    },
    # ===== 7. 十格·设定集（10格：主立绘+3全身+3表情+3细节）=====
    {
        "id": "school_ref",
        "name": "十格·设定集",
        "description": "左侧主立绘，右上三视图，右下表情参考与细节拆解。",
        "width": 2000,
        "height": 1400,
        "defaults": {
            "title": "未命名角色",
            "subtitle": "角色设定集",
            "style": "统一角色资产，纯白棚拍背景，柔和棚拍光",
            "background": "#ffffff",
            "accent": "#e08a9a",
        },
        "cells": [
            _cell("hero", "主立绘", "hero", "完整全身主立绘，自然站姿，头顶到鞋底。", 0.03, 0.08, 0.30, 0.86),
            _cell("body_front", "正面", "turnaround", "完整正面全身，正视镜头，头顶到鞋底。", 0.36, 0.08, 0.20, 0.40),
            _cell("body_side", "侧面", "turnaround", "纯侧面全身，人物面朝画面正右方，只能看到左半边脸和左耳，头顶到鞋底。", 0.58, 0.08, 0.20, 0.40),
            _cell("body_back", "背面", "turnaround", "完整180度背面全身，头顶到鞋底。", 0.80, 0.08, 0.17, 0.40),
            _cell("ex_1", "微笑", "expression", "头肩特写，张嘴露齿微笑，眼睛弯成月牙，充满活力。", 0.36, 0.52, 0.20, 0.20),
            _cell("ex_2", "沉思", "expression", "头肩特写，低头眼帘下垂，侧脸不看镜头，表情安静。", 0.58, 0.52, 0.20, 0.20),
            _cell("ex_3", "惊讶", "expression", "头肩特写，张嘴惊呼，眼睛瞪大。", 0.80, 0.52, 0.17, 0.20),
            _cell("de_1", "服装细节", "detail", "服饰面料特写。", 0.36, 0.75, 0.20, 0.20),
            _cell("de_2", "配饰细节", "detail", "配饰特写。", 0.58, 0.75, 0.20, 0.20),
            _cell("de_3", "鞋履细节", "detail", "鞋履特写。", 0.80, 0.75, 0.17, 0.20),
        ],
    },
    # ===== 8. 十四格·全图鉴（14格：4全身+3头+3表情+3细节+1面料）=====
    {
        "id": "xianxia_ref",
        "name": "十四格·全图鉴",
        "description": "左上4个完整全身，左下3个头肩特写，右侧表情6宫格+细节拆解。",
        "width": 2200,
        "height": 1300,
        "defaults": {
            "title": "未命名角色",
            "subtitle": "完整图鉴",
            "style": "统一角色资产，纯白棚拍背景，柔和棚拍光，写实精致",
            "background": "#ffffff",
            "accent": "#7a9bd8",
        },
        "cells": [
            _cell("body_front", "正面全身", "turnaround", "完整正面全身，正视镜头，头顶到鞋底。", 0.02, 0.03, 0.125, 0.38),
            _cell("body_right", "右侧面全身", "turnaround", "纯侧面全身，人物面朝画面正左方，只能看到右半边脸和右耳，头顶到鞋底。", 0.155, 0.03, 0.125, 0.38, mirror=True),
            _cell("body_back", "背面全身", "turnaround", "完整180度背面全身，只能看到后脑和后背，头顶到鞋底。", 0.29, 0.03, 0.125, 0.38),
            _cell("body_left", "左侧面全身", "turnaround", "纯侧面全身，人物面朝画面正右方，只能看到左半边脸和左耳，与右侧面互为镜像，头顶到鞋底。", 0.425, 0.03, 0.125, 0.38),
            _cell("head_1", "正面特写", "portrait", "头肩正面特写，正视镜头，面无表情。", 0.02, 0.44, 0.15, 0.22),
            _cell("head_2", "侧面特写", "portrait", "头肩90度侧面特写，脸朝右，展示侧脸轮廓。", 0.18, 0.44, 0.15, 0.22),
            _cell("head_3", "斜侧特写", "portrait", "头肩四分之三斜侧特写，眼神看向镜头。", 0.34, 0.44, 0.15, 0.22),
            _cell("ex_1", "温柔微笑", "expression", "头肩特写，温柔微笑，嘴角微上扬不露齿，眼神柔和。", 0.58, 0.03, 0.12, 0.19),
            _cell("ex_2", "惊讶张嘴", "expression", "头肩特写，惊讶张嘴，眼睛圆睁，嘴呈O型。", 0.71, 0.03, 0.12, 0.19),
            _cell("ex_3", "闭眼沉思", "expression", "头肩特写，闭眼沉思，眼帘低垂，嘴唇微抿。", 0.84, 0.03, 0.12, 0.19),
            _cell("ex_4", "蹙眉清冷", "expression", "头肩特写，蹙眉清冷，眉头微皱，眼神冷峻直视。", 0.58, 0.24, 0.12, 0.19),
            _cell("de_1", "眼部细节", "detail", "眼睛微距特写，展示瞳色和睫毛。", 0.71, 0.24, 0.12, 0.19),
            _cell("de_2", "配饰细节", "detail", "配饰微距特写。", 0.84, 0.24, 0.12, 0.19),
            _cell("de_3", "面料细节", "detail", "服饰面料微距特写。", 0.58, 0.45, 0.38, 0.19),
        ],
    },
]

TEMPLATE_BY_ID = {template["id"]: template for template in TEMPLATES}
FIVE_TEMPLATE_IDS = [
    "bighead_body3",
    "dualfour_ref",
    "fiveref",
    "head_body_6",
    "sixtilt_ref",
    "expr_body_8",
    "school_ref",
    "xianxia_ref",
]
FIVE_TEMPLATE_OPTIONS = [f"{template_id} | {TEMPLATE_BY_ID[template_id]['name']}" for template_id in FIVE_TEMPLATE_IDS]
TEMPLATE_OPTIONS = [f"{template['id']} | {template['name']}" for template in TEMPLATES]
DEFAULT_TEMPLATE_OPTION = next(
    (option for option in TEMPLATE_OPTIONS if option.startswith("head_body_6 |")),
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
        "background": defaults.get("background", "#ffffff"),
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
        f"纯白色背景（#FFFFFF），细线分隔，所有画格之间保留稳定的间距。"
        f"严禁灰色、深色、渐变或纹理背景，所有画格背景必须为统一纯白色。",
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
            "所有表情画格必须姿态、眼神、嘴型各不相同，严禁两个表情画格长得一样，"
            "每个表情必须有明确的动作差异（如露齿vs不露齿、睁眼vs闭眼、直视vs侧视）。",
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
