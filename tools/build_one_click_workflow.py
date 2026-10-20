# -*- coding: utf-8 -*-
"""Create the one-click image/prompt-to-character-card workflow."""

from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "workflows" / "角色卡_QwenImage21.json"
TARGET = ROOT / "workflows" / "一键角色卡_QwenImage21.json"


def main() -> None:
    workflow = json.loads(SOURCE.read_text(encoding="utf-8"))
    nodes = {node["id"]: node for node in workflow["nodes"]}
    panel_order = ",".join(str(index) for index in range(1, 18))

    studio = nodes[1]
    studio["type"] = "AICG3D_CharacterCardOneClick"
    studio["size"] = [520, 460]
    studio["outputs"] = [
        {"label": "提示词", "name": "提示词", "type": "STRING", "slot_index": 0, "links": [1]},
        {"label": "负面提示词", "name": "负面提示词", "type": "STRING", "slot_index": 1, "links": [2]},
        {"label": "版式引导图", "name": "版式引导图", "type": "IMAGE", "slot_index": 2, "links": None},
        {"label": "卡版JSON", "name": "卡版JSON", "type": "STRING", "slot_index": 3, "links": [18]},
        {"label": "宽度", "name": "宽度", "type": "INT", "slot_index": 4, "links": [4]},
        {"label": "高度", "name": "高度", "type": "INT", "slot_index": 5, "links": [5]},
        {"label": "卡版选项", "name": "卡版选项", "type": "STRING", "slot_index": 6, "links": None},
    ]
    studio["properties"] = {"Node name for S&R": "AICG3D_CharacterCardOneClick"}
    studio["widgets_values"] = [
        "character_profile_12 | 角色设定卡",
        "原创男性角色，20岁，黑色短发，灰蓝色眼睛，清瘦脸型，深灰短袖、黑色长裤和白色运动鞋。",
        "未命名角色",
        "电影级角色设定卡，干净背景，柔和棚拍光，专业排版",
        False,
        "1-17",
        "完整显示",
        0.008,
    ]

    load_image = {
        "id": 11,
        "type": "LoadImage",
        "pos": [-1620, 120],
        "size": [330, 360],
        "flags": {},
        "order": 0,
        "mode": 0,
        "inputs": [
            {
                "label": "图像",
                "name": "image",
                "type": "COMBO",
                "widget": {"name": "image"},
                "link": None,
            },
            {
                "label": "上传",
                "name": "upload",
                "type": "IMAGEUPLOAD",
                "widget": {"name": "upload"},
                "link": None,
            },
        ],
        "outputs": [
            {"label": "图像", "name": "IMAGE", "type": "IMAGE", "slot_index": 0, "links": [3]},
            {"label": "遮罩", "name": "MASK", "type": "MASK", "slot_index": 1, "links": None},
        ],
        "properties": {"Node name for S&R": "LoadImage"},
        "widgets_values": ["", "image"],
    }

    splitter = {
        "id": 12,
        "type": "AICG3D_CharacterSheetSplitter",
        "pos": [1660, 120],
        "size": [460, 390],
        "flags": {},
        "order": 7,
        "mode": 0,
        "inputs": [
            {"label": "角色卡", "name": "images", "type": "IMAGE", "link": 14},
            {"label": "卡版配置", "name": "card_config", "type": "STRING", "link": 18},
        ],
        "outputs": [
            {"label": "重排角色卡", "name": "重排角色卡", "type": "IMAGE", "slot_index": 0, "links": [15, 16]},
            {"label": "切片批次", "name": "切片批次", "type": "IMAGE", "slot_index": 1, "links": [17]},
            {"label": "切分报告", "name": "切分报告", "type": "STRING", "slot_index": 2, "links": None},
        ],
        "properties": {"Node name for S&R": "AICG3D_CharacterSheetSplitter"},
        "widgets_values": [],
    }

    panel_preview = {
        "id": 14,
        "type": "PreviewImage",
        "pos": [1840, 900],
        "size": [520, 520],
        "flags": {},
        "order": 9,
        "mode": 0,
        "inputs": [{"label": "切片批次", "name": "images", "type": "IMAGE", "link": 17}],
        "outputs": [],
        "properties": {"Node name for S&R": "PreviewImage"},
        "widgets_values": [],
    }

    text_encode = nodes[5]
    text_encode["inputs"][1]["link"] = 3
    text_encode["inputs"][3]["link"] = 1
    text_encode["inputs"][4]["link"] = 2
    text_encode["outputs"][0]["links"] = [10]
    text_encode["outputs"][1]["links"] = [11]

    empty_latent = nodes[6]
    empty_latent["inputs"][0]["link"] = 4
    empty_latent["inputs"][1]["link"] = 5
    empty_latent["outputs"][0]["links"] = [12]

    unet = nodes[2]
    unet["outputs"][0]["links"] = [9]
    clip = nodes[3]
    clip["outputs"][0]["links"] = [6]
    vae = nodes[4]
    vae["outputs"][0]["links"] = [7, 8]

    sampler = nodes[7]
    for index, link_id in enumerate([9, 10, 11, 12]):
        sampler["inputs"][index]["link"] = link_id
    sampler["outputs"][0]["links"] = [13]

    decode = nodes[8]
    decode["inputs"][0]["link"] = 13
    decode["inputs"][1]["link"] = 8
    decode["outputs"][0]["links"] = [14]

    preview = nodes[9]
    preview["pos"] = [2180, 120]
    preview["inputs"][0]["link"] = 15

    save = nodes[10]
    save["pos"] = [2180, 900]
    save["inputs"][0]["link"] = 16

    workflow["nodes"] = [
        nodes[11] if 11 in nodes else load_image,
        studio,
        unet,
        clip,
        vae,
        text_encode,
        empty_latent,
        sampler,
        decode,
        splitter,
        preview,
        save,
        panel_preview,
    ]
    workflow["last_node_id"] = 14
    workflow["last_link_id"] = 18
    workflow["links"] = [
        [1, 1, 0, 5, 3, "STRING"],
        [2, 1, 1, 5, 4, "STRING"],
        [3, 11, 0, 5, 1, "IMAGE"],
        [4, 1, 4, 6, 0, "INT"],
        [5, 1, 5, 6, 1, "INT"],
        [6, 3, 0, 5, 0, "CLIP"],
        [7, 4, 0, 5, 2, "VAE"],
        [8, 4, 0, 8, 1, "VAE"],
        [9, 2, 0, 7, 0, "MODEL"],
        [10, 5, 0, 7, 1, "CONDITIONING"],
        [11, 5, 1, 7, 2, "CONDITIONING"],
        [12, 6, 0, 7, 3, "LATENT"],
        [13, 7, 0, 8, 0, "LATENT"],
        [14, 8, 0, 12, 0, "IMAGE"],
        [15, 12, 0, 9, 0, "IMAGE"],
        [16, 12, 0, 10, 0, "IMAGE"],
        [17, 12, 1, 14, 0, "IMAGE"],
        [18, 1, 3, 12, 1, "STRING"],
    ]
    workflow["groups"] = [
        {"id": 1, "title": "输入角色图 / 提示词", "bounding": [-1640, 20, 2230, 680], "color": "#3f789e", "flags": {}},
        {"id": 2, "title": "千问生成", "bounding": [-60, 20, 1250, 680], "color": "#8a6d3b", "flags": {}},
        {"id": 3, "title": "自动切片与重排", "bounding": [1600, 20, 1160, 1440], "color": "#3f789e", "flags": {}},
    ]
    workflow["id"] = "a3cc4e6a-65a3-4e3f-9f10-oneclickcardqwen21"
    TARGET.write_text(json.dumps(workflow, ensure_ascii=False, indent=2), encoding="utf-8")
    print(TARGET)

    prompt_only = copy.deepcopy(workflow)
    prompt_only["id"] = "a3cc4e6a-65a3-4e3f-9f10-promptcardqwen21"
    prompt_only["nodes"] = [node for node in prompt_only["nodes"] if node["type"] != "LoadImage"]
    for node in prompt_only["nodes"]:
        if node["type"] == "TextEncodeQwenImage21":
            node["inputs"][1]["link"] = None
    prompt_only["links"] = [link for link in prompt_only["links"] if link[0] != 3]
    prompt_only["groups"][0]["title"] = "人物提示词"
    prompt_target = ROOT / "workflows" / "一键角色卡_提示词版_QwenImage21.json"
    prompt_target.write_text(json.dumps(prompt_only, ensure_ascii=False, indent=2), encoding="utf-8")
    print(prompt_target)


if __name__ == "__main__":
    main()
