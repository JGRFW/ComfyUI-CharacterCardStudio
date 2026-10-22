# -*- coding: utf-8 -*-
"""Character-card layout definitions and prompt compilation."""

from __future__ import annotations

import copy
import json
import re
from typing import Any


DEFAULT_NEGATIVE = (
    "低质量，模糊，畸形，多余肢体，错误手指，身份漂移，脸部崩坏，性别漂移，"
    "服装结构错误，配饰缺失，面板布局混乱，重复人物，复制同一张脸，"
    "画格数量错误，多出画格，缺少画格，画格合并，九宫格误生成，"
    "文字乱码，水印，logo，头部裁切，脚部裁切，鞋履裁切，半身替代全身，断脚，切头，"
    "灰色背景，深灰背景，暗背景，渐变背景，纹理背景，阴影背景"
)

ROLE_NAMES = {
    "hero": "单人大幅主立绘",
    "turnaround": "单人物完整全身",
    "portrait": "单人物头肩肖像",
    "expression": "单人物表情头肩",
    "detail": "局部微距细节",
    "scene_anchor": "场景正面参考图",
    "scene_view": "场景多视角",
    "scene_panorama": "360°场景全景",
    "scene_detail": "场景材质细节",
}


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
    {
        "id": "bighead_body3",
        "name": "四格·偏立",
        "description": "左侧一个大的正面头肩肖像，右侧并列正面/侧面/背面三个完整全身。",
        "layout_prompt": "左右两栏：左栏只有1个大头肩肖像；右栏只有3个等宽全身竖格，依次为正面、侧面、背面。总共4格。",
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
            _cell("head_big", "正面大头像", "portrait", "正面头肩肖像，头部到肩部完整入镜，五官和发饰清晰，正视镜头，画面里只有一个人。", 0.03, 0.03, 0.40, 0.94),
            _cell("body_front", "正面全身", "turnaround", "正面完整全身站姿，双臂自然下垂，从头顶到鞋底完整不裁切，画面里只有一个人。", 0.46, 0.12, 0.16, 0.78),
            _cell("body_side", "侧面全身", "turnaround", "严格90度左侧面完整全身，人物朝画面右侧，只能看到左半边脸和左耳，从头顶到鞋底完整不裁切。", 0.635, 0.12, 0.16, 0.78),
            _cell("body_back", "背面全身", "turnaround", "严格180度背面完整全身，只能看到后脑和后背，从头顶到鞋底完整不裁切。", 0.81, 0.12, 0.16, 0.78),
        ],
    },
    {
        "id": "dualfour_ref",
        "name": "四格·双帧",
        "description": "等分2×2：上排正面和四分之三头肩，下排正面和背面全身。",
        "layout_prompt": "等分2行×2列：上排左格正面头肩、右格四分之三头肩；下排左格正面全身、右格背面全身。总共4格，不能增加第三排。",
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
            _cell("head_front", "正面头像", "portrait", "正面头肩特写，头部到肩部完整入镜，正视镜头，不出现第二个人。", 0.03, 0.03, 0.46, 0.43),
            _cell("head_three_quarter", "四分之三头像", "portrait", "四分之三侧脸头肩特写，脸朝画面右前方，能同时看到两侧脸颊轮廓，眼神看向镜头。", 0.51, 0.03, 0.46, 0.43),
            _cell("body_front", "正面全身", "turnaround", "正面完整全身站姿，正视镜头，从头顶到鞋底完整不裁切，画面里只有一个人。", 0.03, 0.52, 0.46, 0.45),
            _cell("body_back", "背面全身", "turnaround", "严格180度背面完整全身，只能看到后脑和后背，从头顶到鞋底完整不裁切。", 0.51, 0.52, 0.46, 0.45),
        ],
    },
    {
        "id": "fiveref",
        "name": "五格·正反",
        "description": "上排正面和四分之三头肩，下排正面/侧面/背面三个完整全身。",
        "layout_prompt": "两排结构：上排只有2格，都是头肩肖像；下排只有3格，都是完整全身。总共5格。",
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
            _cell("head_front", "正面头像", "portrait", "正面头肩特写，头部到肩部完整入镜，正视镜头。", 0.03, 0.03, 0.47, 0.43),
            _cell("head_three_quarter", "四分之三头像", "portrait", "四分之三侧脸头肩特写，脸朝画面右前方，眼神看向镜头，与正面头像角度明显不同。", 0.50, 0.03, 0.47, 0.43),
            _cell("body_front", "正面全身", "turnaround", "正面完整全身站姿，从头顶到鞋底完整不裁切，画面里只有一个人。", 0.03, 0.52, 0.305, 0.45),
            _cell("body_side", "侧面全身", "turnaround", "严格90度左侧面完整全身，人物朝画面右侧，从头顶到鞋底完整不裁切。", 0.348, 0.52, 0.305, 0.45),
            _cell("body_back", "背面全身", "turnaround", "严格180度背面完整全身，只能看到后脑和后背，从头顶到鞋底完整不裁切。", 0.665, 0.52, 0.305, 0.45),
        ],
    },
    {
        "id": "head_body_6",
        "name": "六格·三视图",
        "description": "上排正面/侧面/后脑三个头肩，下排正面/侧面/背面三个完整全身。",
        "layout_prompt": "等分2排×3列：上排3格全是头肩肖像，下排3格全是完整全身。总共6格，不能生成九宫格。",
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
            _cell("head_front", "正面头像", "portrait", "正面头肩特写，头部到肩部完整入镜，正视镜头。", 0.03, 0.03, 0.303, 0.43),
            _cell("head_side", "侧面头像", "portrait", "严格90度侧面头肩特写，人物朝画面右侧，只能看到左半边脸和左耳。", 0.345, 0.03, 0.303, 0.43),
            _cell("head_back", "后脑头像", "portrait", "背面头肩特写，只能看到后脑和发型，看不到脸。", 0.66, 0.03, 0.303, 0.43),
            _cell("body_front", "正面全身", "turnaround", "正面完整全身站姿，从头顶到鞋底完整不裁切，画面里只有一个人。", 0.03, 0.52, 0.303, 0.45),
            _cell("body_side", "侧面全身", "turnaround", "严格90度左侧面完整全身，人物朝画面右侧，从头顶到鞋底完整不裁切。", 0.345, 0.52, 0.303, 0.45),
            _cell("body_back", "背面全身", "turnaround", "严格180度背面完整全身，只能看到后脑和后背，从头顶到鞋底完整不裁切。", 0.66, 0.52, 0.303, 0.45),
        ],
    },
    {
        "id": "sixtilt_ref",
        "name": "六格·主视觉",
        "description": "左侧大幅主立绘；右侧两排双格，底部横条面料细节。",
        "layout_prompt": "非等分布局：左侧1个大幅主立绘；右侧上排2格（正面头像、微笑），中排2格（侧面全身、动作全身），右下1个横向面料细节条。总共6格。",
        "width": 1920,
        "height": 1280,
        "defaults": {
            "title": "未命名角色",
            "subtitle": "主视觉设定",
            "style": "统一角色资产，纯白棚拍背景，柔和棚拍光，写实电影级",
            "background": "#ffffff",
            "accent": "#9b7dd8",
        },
        "cells": [
            _cell("hero", "主立绘", "hero", "正面完整全身主立绘，自然站姿，从头顶到鞋底完整入镜，画面里只有一个人。", 0.03, 0.08, 0.39, 0.84),
            _cell("head_front", "正面头像", "portrait", "正面头肩特写，头部到肩部完整入镜，正视镜头。", 0.45, 0.08, 0.26, 0.25),
            _cell("ex_smile", "微笑表情", "expression", "头肩微笑特写，嘴角上扬、眼睛微弯，和正面冷静头像表情明显不同。", 0.735, 0.08, 0.235, 0.25),
            _cell("body_side", "侧面全身", "turnaround", "严格90度左侧面完整全身，人物朝画面右侧，从头顶到鞋底完整不裁切。", 0.45, 0.36, 0.26, 0.27),
            _cell("action_pose", "动作全身", "turnaround", "动态站姿完整全身，手臂动作与主立绘明显不同，从头顶到鞋底完整不裁切。", 0.735, 0.36, 0.235, 0.27),
            _cell("de_fabric", "面料细节", "detail", "横向服饰面料与刺绣微距，只展示纹理、褶皱和金线，不出现人物脸部或全身。", 0.45, 0.66, 0.52, 0.26),
        ],
    },
    {
        "id": "expr_body_8",
        "name": "八格·表情谱",
        "description": "上排4个不同表情头肩，下排正面/侧面/背面/动作四个完整全身。",
        "layout_prompt": "等分2排×4列：上排4格全部是不同表情的头肩；下排4格全部是完整全身。总共8格。",
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
            _cell("head_neutral", "平静", "expression", "头肩特写，中性平静，嘴唇闭合，目光平视，面部放松。", 0.03, 0.03, 0.225, 0.43),
            _cell("head_happy", "开心大笑", "expression", "头肩特写，张嘴露齿开心大笑，眼睛弯成月牙，和第一格表情明显不同。", 0.268, 0.03, 0.225, 0.43),
            _cell("head_serious", "认真", "expression", "头肩特写，嘴唇紧抿、眉头微蹙，严肃直视镜头。", 0.505, 0.03, 0.225, 0.43),
            _cell("head_surprised", "惊讶", "expression", "头肩特写，眼睛圆睁、眉毛抬高、嘴巴微张呈惊讶表情。", 0.743, 0.03, 0.225, 0.43),
            _cell("body_front", "正面全身", "turnaround", "正面完整全身站姿，双臂自然下垂，从头顶到鞋底完整不裁切。", 0.03, 0.52, 0.225, 0.45),
            _cell("body_profile", "左侧面全身", "turnaround", "严格90度左侧面完整全身，人物朝画面右侧，从头顶到鞋底完整不裁切。", 0.268, 0.52, 0.225, 0.45),
            _cell("body_back", "背面全身", "turnaround", "严格180度背面完整全身，只能看到后脑和后背，从头顶到鞋底完整不裁切。", 0.505, 0.52, 0.225, 0.45),
            _cell("body_action", "动作全身", "turnaround", "自然行走动作完整全身，步态与前三格站姿不同，从头顶到鞋底完整不裁切。", 0.743, 0.52, 0.225, 0.45),
        ],
    },
    {
        "id": "school_ref",
        "name": "十格·设定集",
        "description": "左侧主立绘；右侧上排三视图、中排三表情、下排三细节。",
        "layout_prompt": "左右两栏：左栏只有1个大幅主立绘；右栏3列×3行，依次为上排3格全身、中排3格表情头肩、下排3格局部细节。总共10格。",
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
            _cell("hero", "主立绘", "hero", "单个人物正面完整全身主立绘，自然站姿，从头顶到鞋底完整入镜，画面里不能出现第二个人或拼贴。", 0.03, 0.08, 0.30, 0.86),
            _cell("body_front", "正面全身", "turnaround", "正面完整全身站姿，从头顶到鞋底完整不裁切。", 0.36, 0.08, 0.20, 0.40),
            _cell("body_side", "侧面全身", "turnaround", "严格90度左侧面完整全身，人物朝画面右侧，从头顶到鞋底完整不裁切。", 0.58, 0.08, 0.20, 0.40),
            _cell("body_back", "背面全身", "turnaround", "严格180度背面完整全身，只能看到后脑和后背，从头顶到鞋底完整不裁切。", 0.80, 0.08, 0.17, 0.40),
            _cell("ex_1", "甜美微笑", "expression", "头肩特写，张嘴露齿甜笑，眼睛弯起，表情明亮。", 0.36, 0.52, 0.20, 0.20),
            _cell("ex_2", "低头沉思", "expression", "头肩特写，低头垂眼，不看镜头，表情安静克制。", 0.58, 0.52, 0.20, 0.20),
            _cell("ex_3", "惊讶张嘴", "expression", "头肩特写，眼睛睁大、眉毛抬高、嘴巴张开，表情惊讶。", 0.80, 0.52, 0.17, 0.20),
            _cell("de_1", "服装细节", "detail", "制服领口、徽章和衣料纹理的局部微距，不出现完整人物。", 0.36, 0.75, 0.20, 0.20),
            _cell("de_2", "配饰细节", "detail", "领结或发饰的局部微距，不出现人物脸部。", 0.58, 0.75, 0.20, 0.20),
            _cell("de_3", "鞋履细节", "detail", "鞋履结构和材质的局部微距，不出现完整人物。", 0.80, 0.75, 0.17, 0.20),
        ],
    },
    {
        "id": "xianxia_ref",
        "name": "十四格·全图鉴",
        "description": "左侧四全身+三头像，右侧四表情+三细节，最后一行横条面料。",
        "layout_prompt": "左右两栏：左栏上排4个全身，下排3个头像；右栏上排3个表情，中排3格（1个表情+2个细节），底部1个横条面料细节。总共14格，不能多出第4行。",
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
            _cell("body_front", "正面全身", "turnaround", "正面完整全身站姿，从头顶到鞋底完整不裁切，画面里只有一个人。", 0.02, 0.03, 0.125, 0.42),
            _cell("body_right", "右侧面全身", "turnaround", "严格90度右侧面完整全身，人物朝画面左侧，只能看到右半边脸和右耳，从头顶到鞋底完整不裁切。", 0.155, 0.03, 0.125, 0.42),
            _cell("body_back", "背面全身", "turnaround", "严格180度背面完整全身，只能看到后脑和后背，从头顶到鞋底完整不裁切。", 0.29, 0.03, 0.125, 0.42),
            _cell("body_left", "左侧面全身", "turnaround", "严格90度左侧面完整全身，人物朝画面右侧，只能看到左半边脸和左耳，与右侧面方向相反。", 0.425, 0.03, 0.125, 0.42),
            _cell("head_1", "正面头像", "portrait", "正面头肩肖像，头部到肩部完整入镜，平静正视镜头。", 0.02, 0.47, 0.15, 0.43),
            _cell("head_2", "侧面头像", "portrait", "严格90度侧面头肩肖像，人物朝画面右侧，展示侧脸轮廓。", 0.18, 0.47, 0.15, 0.43),
            _cell("head_3", "斜侧头像", "portrait", "四分之三斜侧头肩肖像，脸朝画面右前方，眼神看向镜头。", 0.34, 0.47, 0.15, 0.43),
            _cell("ex_1", "温柔微笑", "expression", "头肩特写，闭唇温柔微笑，嘴角微扬，眼神柔和。", 0.58, 0.03, 0.12, 0.25),
            _cell("ex_2", "惊讶张嘴", "expression", "头肩特写，眼睛圆睁、眉毛抬起、嘴巴微张，表情惊讶。", 0.71, 0.03, 0.12, 0.25),
            _cell("ex_3", "闭眼沉思", "expression", "头肩特写，双眼闭合，头部微低，嘴唇轻抿，表情安静。", 0.84, 0.03, 0.12, 0.25),
            _cell("ex_4", "蹙眉清冷", "expression", "头肩特写，眉头微蹙，眼神冷峻直视，和微笑表情明显不同。", 0.58, 0.30, 0.12, 0.25),
            _cell("de_1", "眼部细节", "detail", "单只眼睛的微距特写，展示瞳色、虹膜纹理和睫毛，不出现整张脸。", 0.71, 0.30, 0.12, 0.25),
            _cell("de_2", "配饰细节", "detail", "项链、耳环或发饰的微距特写，不出现人物脸部。", 0.84, 0.30, 0.12, 0.25),
            _cell("de_3", "面料细节", "detail", "横向服饰面料与刺绣微距，只展示布料纹理、褶皱和图案，不出现人物。", 0.58, 0.57, 0.38, 0.37),
        ],
    },
    {
        "id": "scene_six_view",
        "kind": "scene",
        "name": "场景·360°环视",
        "description": "上传任意一张场景图，按0°、90°、180°、270°生成完整环视，并补充360°全景条和环境细节。",
        "layout_prompt": "上排4格从左到右依次为0°正面参考、90°右向、180°反向、270°左向；下排左侧为360°连续全景长条，右侧为环境细节。总共6格。",
        "width": 1920,
        "height": 1280,
        "defaults": {
            "title": "未命名场景",
            "subtitle": "360°场景环视设定",
            "style": "写实场景概念设计，统一空间结构、材质、透视和光照",
            "background": "#ffffff",
            "accent": "#4f8a8b",
        },
        "cells": [
            _cell("scene_front", "0°正面参考", "scene_anchor", "保留上传的场景图作为唯一空间锚点，不重绘、不改变构图；若没有上传参考图，则生成一张场景0°正面主视图。场景为主，不新增人物或动物。", 0.03, 0.03, 0.217, 0.43),
            _cell("scene_right", "90°右向", "scene_view", "从0°相机位置向右转约90度，拍摄同一场景的右侧；必须出现0°画面中未展示的右方空间，延续地形、建筑、道路、植被、主要物件、材质和光照。场景为主，不新增人物或动物。", 0.271, 0.03, 0.217, 0.43),
            _cell("scene_back", "180°反向", "scene_view", "从0°相机位置转身约180度，拍摄同一场景的反方向视角；必须与0°和90°构成连续空间，保持尺度、主要物件位置和光照方向一致。场景为主，不新增人物或动物。", 0.512, 0.03, 0.217, 0.43),
            _cell("scene_left", "270°左向", "scene_view", "从0°相机位置向左转约90度，也就是270°方向；必须出现0°画面中未展示的左方空间，并与90°、180°首尾连续。场景为主，不新增人物或动物。", 0.753, 0.03, 0.217, 0.43),
            _cell("scene_panorama", "360°全景", "scene_panorama", "生成同一场景的横向360°连续全景展开图，画面从左到右按0°、90°、180°、270°、回到0°的顺序自然衔接，地形、建筑、道路、植被、主要物件、材质和光照连续。场景为主，不新增人物或动物。", 0.03, 0.50, 0.64, 0.45),
            _cell("scene_detail", "环境细节", "scene_detail", "提取该场景中最有辨识度的材质、纹理、植被、建筑构件或装饰细节，做一张局部微距；颜色和材质必须与环境一致。场景为主，不新增人物或动物。", 0.70, 0.50, 0.27, 0.45),
        ],
    },
]


TEMPLATE_BY_ID = {template["id"]: template for template in TEMPLATES}
CARD_TEMPLATE_IDS = [template["id"] for template in TEMPLATES]
# Keep the old names import-compatible with existing workflows.
FIVE_TEMPLATE_IDS = CARD_TEMPLATE_IDS
FIVE_TEMPLATE_OPTIONS = [f"{template_id} | {TEMPLATE_BY_ID[template_id]['name']}" for template_id in CARD_TEMPLATE_IDS]
TEMPLATE_OPTIONS = [f"{template['id']} | {template['name']}" for template in TEMPLATES]
CHARACTER_TEMPLATE_OPTIONS = [
    f"{template['id']} | {template['name']}"
    for template in TEMPLATES
    if template.get("kind") != "scene"
]
DEFAULT_TEMPLATE_OPTION = next(
    (option for option in TEMPLATE_OPTIONS if option.startswith("head_body_6 |")),
    TEMPLATE_OPTIONS[0],
)
SOURCE_TEMPLATE_OPTIONS = ["source | 与输入卡版相同", *TEMPLATE_OPTIONS]


def get_templates_payload() -> dict[str, Any]:
    return {
        "version": 3,
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
    is_scene = str(template.get("kind") or "") == "scene"
    subject_prompt = character_prompt
    subject_style = style
    if is_scene and (not str(subject_prompt).strip() or str(subject_prompt).startswith("原创角色")):
        subject_prompt = "完整场景，空间结构清晰，地形、建筑、道路、植被或主要物件关系明确，真实材质与统一光照。"
    if is_scene and str(subject_style).startswith("电影级角色设定"):
        subject_style = defaults.get("style", "写实场景概念设计，统一空间结构、材质、透视和光照")
    subject_title = "未命名场景" if is_scene and str(title or "") in {"", "未命名角色"} else title
    return {
        "templateId": template["id"],
        "title": _safe_text(subject_title, defaults.get("title", "未命名场景" if is_scene else "未命名角色"), 120),
        "subtitle": defaults.get("subtitle", template.get("name", "设定卡")),
        "identity": _safe_text(subject_prompt, "", 3000),
        "appearance": _safe_text(subject_prompt, "", 3000),
        "outfit": "",
        "palette": "",
        "style": _safe_text(subject_style, defaults.get("style", ""), 1200),
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


def _matching_slot(previous_slots: list[Any], cell: dict[str, Any], index: int) -> dict[str, Any]:
    """Match by stable cell id first, with a legacy index fallback for old cards."""
    for item in previous_slots:
        if isinstance(item, dict) and str(item.get("cellId") or "") == str(cell.get("id") or ""):
            return item
    if index < len(previous_slots) and isinstance(previous_slots[index], dict):
        candidate = previous_slots[index]
        if not candidate.get("cellId"):
            return candidate
    return {}


def normalise_state(raw_state: Any, width: int, height: int) -> tuple[dict[str, Any], dict[str, Any]]:
    raw = parse_state(raw_state)
    template = get_template(raw.get("templateId") or raw.get("template_id"))
    defaults = template.get("defaults", {})
    cells = template.get("cells", [])
    previous_slots = raw.get("slots") if isinstance(raw.get("slots"), list) else []

    state: dict[str, Any] = {
        "version": 2,
        "templateId": template["id"],
        "title": _safe_text(raw.get("title"), defaults.get("title", "未命名角色"), 120),
        "subtitle": _safe_text(raw.get("subtitle"), defaults.get("subtitle", "角色设定卡"), 160),
        "identity": _safe_text(raw.get("identity"), "", 3000),
        "appearance": _safe_text(raw.get("appearance"), "", 3000),
        "outfit": _safe_text(raw.get("outfit"), "", 3000),
        "palette": _safe_text(raw.get("palette"), "", 500),
        "style": _safe_text(raw.get("style"), defaults.get("style", ""), 1200),
        "negativePrompt": _safe_text(raw.get("negativePrompt"), DEFAULT_NEGATIVE, 2400),
        "background": _safe_text(raw.get("background"), defaults.get("background", "#ffffff"), 32),
        "accent": _safe_text(raw.get("accent"), defaults.get("accent", "#d86b73"), 32),
        "showLabels": bool(raw.get("showLabels", False)),
        "width": _clamp_int(raw.get("width") or width, 512, 4096, int(template.get("width", 2048))),
        "height": _clamp_int(raw.get("height") or height, 512, 4096, int(template.get("height", 1152))),
        "slots": [],
        "library": [],
    }

    for index, cell in enumerate(cells):
        source = _matching_slot(previous_slots, cell, index)
        default_fit = "contain" if cell.get("role") in {"turnaround", "hero", "detail", "scene_anchor"} else "cover"
        state["slots"].append(
            {
                "id": _safe_text(source.get("id"), f"slot_{index + 1}", 80),
                "cellId": cell["id"],
                "label": cell.get("label", f"画格 {index + 1}"),
                "role": cell.get("role", "custom"),
                "prompt": cell.get("prompt", ""),
                "image": _safe_image_name(source.get("image")),
                "subfolder": _safe_image_name(source.get("subfolder")),
                "fit": str(source.get("fit") or default_fit) if str(source.get("fit") or default_fit) in {"contain", "cover"} else default_fit,
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

    for slot in state["slots"]:
        image = slot.get("image")
        if not image:
            continue
        key = (slot.get("subfolder", ""), image)
        if key in seen:
            continue
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


def _cell_box(cell: dict[str, Any], width: int, height: int) -> tuple[int, int, int, int]:
    x1 = max(0, min(width - 1, int(round(float(cell.get("x", 0.0)) * width))))
    y1 = max(0, min(height - 1, int(round(float(cell.get("y", 0.0)) * height))))
    x2 = max(x1 + 1, min(width, int(round((float(cell.get("x", 0.0)) + float(cell.get("w", 1.0))) * width))))
    y2 = max(y1 + 1, min(height, int(round((float(cell.get("y", 0.0)) + float(cell.get("h", 1.0))) * height))))
    return x1, y1, x2, y2


def active_slots(state: dict[str, Any]) -> list[dict[str, Any]]:
    slots = state.get("slots") if isinstance(state.get("slots"), list) else []
    return [slot for slot in slots if isinstance(slot, dict) and slot.get("enabled", True)]


def compile_prompt(state: dict[str, Any], template: dict[str, Any]) -> str:
    width = int(state.get("width") or template.get("width") or 2048)
    height = int(state.get("height") or template.get("height") or 1152)
    enabled_slots = active_slots(state)
    cell_by_id = {cell["id"]: cell for cell in template.get("cells", [])}
    cell_count = len(enabled_slots)
    is_scene = str(template.get("kind") or "") == "scene"
    card_kind = "场景设定卡" if is_scene else "角色设定卡"
    subject_name = "场景" if is_scene else "角色"

    lines = [
        f"生成一张完整的{card_kind}。输入图1是唯一且必须逐格复制的版式参考图。",
        f"输出画布为 {width}×{height}，横竖比例、外边距和总格数必须与版式参考图完全一致。",
        f"严格保留输入图1中的 {cell_count} 个矩形画格：位置、长宽比例、行列关系和大小层级必须一致。",
        "禁止增加画格、删除画格、合并画格、拆分画格或在空白处补画新主体。",
        f"固定布局：{_clean_sentence(template.get('layout_prompt') or template.get('description') or '')}。",
        "输入图中的空白格、内容剪影、编号和辅助文字只代表画格位置与内容类型；"
        "最终图要替换为真实画面，不要保留占位图标、编号、辅助线或版式草稿痕迹。",
        "画格之间使用干净的细线或窄白缝分隔，保持专业、统一、可直接用于资产库的完成度。",
    ]

    if is_scene:
        lines.extend(
            [
                "所有视角必须属于同一个场景：地形、建筑、道路、植被、主要物件、材质、"
                "颜色、主光方向和空间尺度必须连续且一致。",
                "正面参考格必须尽量保留上传原图的透视、构图、主要物件位置和光线，不得擅自重做场景。",
                "按0°、90°、180°、270°的相机方位依次补全场景；每个方向必须展示前一方向看不到的空间，"
                "四个方向必须首尾连续。",
                "360°全景长条必须把0°、90°、180°、270°按顺序无缝展开，不能重复四张相同照片。",
                "场景为主，不新增与参考无关的人物或动物，不出现文字、水印或破坏空间连续性的装饰。",
            ]
        )
    else:
        lines.extend(
            [
                "所有人物画格必须是同一个人：脸型、五官、瞳色、发型、发色、肤色、身体比例、"
                "服装版型、配饰位置和整体色彩保持一致。",
                "同一个角色可以出现多次，但绝不允许直接把同一张构图复制到多个格子里。"
                "每个格的姿势、朝向、表情或裁切范围必须按清单变化。",
                "所有全身格必须从头顶到鞋底完整显示，头顶和脚底留有安全边距，不得裁成半身。",
            ]
        )

    if state.get("identity"):
        label = "场景类型与氛围" if is_scene else "角色身份与性格"
        lines.append(f"{label}：{_clean_sentence(state['identity'])}。")
    if state.get("appearance"):
        label = "空间结构与主要物件锁定" if is_scene else "外貌锁定"
        lines.append(f"{label}：{_clean_sentence(state['appearance'])}。")
    if state.get("outfit"):
        label = "材质、环境与光照锁定" if is_scene else "服装与配饰锁定"
        lines.append(f"{label}：{_clean_sentence(state['outfit'])}。")
    if state.get("palette"):
        lines.append(f"固定色板：{_clean_sentence(state['palette'])}。")
    if state.get("style"):
        lines.append(f"统一风格：{_clean_sentence(state['style'])}。")

    lines.append("逐格清单如下，必须严格按编号、位置和内容逐项完成：")
    for index, slot in enumerate(enabled_slots, start=1):
        cell = cell_by_id.get(str(slot.get("cellId") or ""), {})
        x1, y1, x2, y2 = _cell_box(cell, width, height)
        role = str(cell.get("role") or slot.get("role") or "custom")
        role_name = ROLE_NAMES.get(role, "单主体画格")
        label = _clean_sentence(slot.get("label") or cell.get("label") or f"画格 {index}")
        prompt = _clean_sentence(slot.get("prompt") or cell.get("prompt") or f"保持{subject_name}一致")
        lines.append(
            f"{index:02d}. 位置：左{x1}px、上{y1}px、右{x2}px、下{y2}px；"
            f"尺寸：{x2 - x1}×{y2 - y1}px；类型：{role_name}；"
            f"标签：{label}；内容：{prompt}。"
        )

    if is_scene:
        lines.extend(
            [
                "每个视角之间的相机方位必须有明确差异，不能把同一张场景照片复制、镜像或轻微裁切后重复使用。",
                "环境细节格只展示局部材质或构件，不生成新的整套场景，也不新增人物或动物。",
            ]
        )
    else:
        lines.extend(
            [
                "表情格之间必须有可辨认的差异，至少同时改变眉眼、嘴型或视线，不能只换标签。",
                "细节格只展示眼睛、配饰、面料或鞋履等局部，不得画成头像或全身。",
                "所有画格主体居中，比例自然，手部完整，面部稳定；每一格只放一个主体。",
            ]
        )

    if state.get("showLabels"):
        title = _clean_sentence(state.get("title") or ("未命名场景" if is_scene else "未命名角色"))
        subtitle = _clean_sentence(state.get("subtitle") or template.get("name") or "设定卡")
        labels = "、".join(
            f"“{_clean_sentence(slot.get('label') or f'画格 {index}')}”"
            for index, slot in enumerate(enabled_slots, start=1)
        )
        lines.append(f"在画布顶部显示标题“{title}”和副标题“{subtitle}”，文字必须清晰且不遮挡画格。")
        lines.append(
            f"每个画格下方显示对应中文标签，文字必须与下列标签一致：{labels}。"
            "不得出现错字、乱码、额外字母或水印。"
        )
    else:
        lines.append("画面内不生成标题、说明文字、字母、数字、logo 或水印，只保留纯视觉资产。")

    lines.append(f"最终输出是一张干净、空间与内容连续、可直接使用的{card_kind}，不是拼贴草稿。")
    return "\n".join(lines)

def card_schema_for_ui() -> dict[str, Any]:
    return {
        "version": 3,
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
