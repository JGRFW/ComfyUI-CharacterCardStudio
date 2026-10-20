# -*- coding: utf-8 -*-
"""Build the role-aware multi-branch character card workflow."""

from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_WORKFLOW = ROOT / "workflows" / "一键角色卡_QwenImage21.json"
TARGET = ROOT / "workflows" / "角色卡_分项生成_QwenImage21.json"
PROMPT_TARGET = ROOT / "workflows" / "角色卡_分项生成_提示词版_QwenImage21.json"


def load_templates() -> dict[int, dict]:
    workflow = json.loads(BASE_WORKFLOW.read_text(encoding="utf-8"))
    return {node["id"]: copy.deepcopy(node) for node in workflow["nodes"]}


def reset_node(node: dict, node_id: int, pos: list[int], order: int) -> None:
    node["id"] = node_id
    node["pos"] = pos
    node["order"] = order
    node["flags"] = {}
    node["mode"] = 0
    for item in node.get("inputs", []):
        item["link"] = None
    for item in node.get("outputs", []):
        item["links"] = None


def asset_prompt_node() -> dict:
    return {
        "id": 1,
        "type": "AICG3D_CharacterCardAssetPrompt",
        "pos": [-2420, 120],
        "size": [520, 420],
        "flags": {},
        "order": 0,
        "mode": 0,
        "inputs": [],
        "outputs": [
            {"label": "正面全身", "name": "正面全身", "type": "STRING", "slot_index": 0, "links": None},
            {"label": "侧面全身", "name": "侧面全身", "type": "STRING", "slot_index": 1, "links": None},
            {"label": "背面全身", "name": "背面全身", "type": "STRING", "slot_index": 2, "links": None},
            {"label": "头像", "name": "头像", "type": "STRING", "slot_index": 3, "links": None},
            {"label": "动作A", "name": "动作A", "type": "STRING", "slot_index": 4, "links": None},
            {"label": "动作B", "name": "动作B", "type": "STRING", "slot_index": 5, "links": None},
            {"label": "表情组", "name": "表情组", "type": "STRING", "slot_index": 6, "links": None},
            {"label": "细节组", "name": "细节组", "type": "STRING", "slot_index": 7, "links": None},
            {"label": "负面提示词", "name": "负面提示词", "type": "STRING", "slot_index": 8, "links": None},
            {"label": "卡版配置", "name": "卡版配置", "type": "STRING", "slot_index": 9, "links": None},
            {"label": "版式引导图", "name": "版式引导图", "type": "IMAGE", "slot_index": 10, "links": None},
            {"label": "宽度", "name": "宽度", "type": "INT", "slot_index": 11, "links": None},
            {"label": "高度", "name": "高度", "type": "INT", "slot_index": 12, "links": None},
        ],
        "properties": {"Node name for S&R": "AICG3D_CharacterCardAssetPrompt"},
        "widgets_values": [
            "reference_profile_18 | 参考角色卡18格",
            "原创男性角色，20岁，黑色短发，灰蓝色眼睛，清瘦脸型，深灰短袖、黑色长裤和白色运动鞋。",
            "未命名角色",
            "电影级角色设定，干净背景，柔和棚拍光，专业角色资产",
            False,
            "完整显示",
        ],
    }


def composer_node() -> dict:
    inputs = []
    for name, label in [
        ("full_front", "正面全身"),
        ("full_profile", "侧面全身"),
        ("full_back", "背面全身"),
        ("action_a", "动作A"),
        ("action_b", "动作B"),
        ("headshot", "头像"),
        ("expression_sheet", "表情组"),
        ("detail_sheet", "细节组"),
        ("card_config", "卡版配置"),
    ]:
        item = {"label": label, "name": name, "type": "IMAGE" if name != "card_config" else "STRING", "link": None}
        inputs.append(item)
    return {
        "id": 500,
        "type": "AICG3D_CharacterCardAssetComposer",
        "pos": [620, 640],
        "size": [460, 420],
        "flags": {},
        "order": 40,
        "mode": 0,
        "inputs": inputs,
        "outputs": [
            {"label": "角色卡", "name": "角色卡", "type": "IMAGE", "slot_index": 0, "links": None},
            {"label": "资产批次", "name": "资产批次", "type": "IMAGE", "slot_index": 1, "links": None},
            {"label": "组合报告", "name": "组合报告", "type": "STRING", "slot_index": 2, "links": None},
        ],
        "properties": {"Node name for S&R": "AICG3D_CharacterCardAssetComposer"},
        "widgets_values": [],
    }


def main() -> None:
    templates = load_templates()
    nodes: list[dict] = []
    links: list[list] = []
    by_id: dict[int, dict] = {}

    def add(node: dict) -> dict:
        nodes.append(node)
        by_id[node["id"]] = node
        return node

    def connect(origin_id: int, origin_slot: int, target_id: int, target_slot: int, kind: str) -> None:
        link_id = len(links) + 1
        links.append([link_id, origin_id, origin_slot, target_id, target_slot, kind])
        origin = by_id[origin_id]["outputs"][origin_slot]
        if origin.get("links") is None:
            origin["links"] = []
        origin["links"].append(link_id)
        by_id[target_id]["inputs"][target_slot]["link"] = link_id

    asset_prompt = add(asset_prompt_node())
    load_image = copy.deepcopy(templates[11])
    reset_node(load_image, 100, [-3060, 120], 1)
    load_image["widgets_values"] = ["", "image"]
    load_image["outputs"][0]["links"] = None
    add(load_image)

    unet = copy.deepcopy(templates[2])
    reset_node(unet, 2, [-1840, 100], 2)
    add(unet)
    clip = copy.deepcopy(templates[3])
    reset_node(clip, 3, [-1840, 260], 3)
    add(clip)
    vae = copy.deepcopy(templates[4])
    reset_node(vae, 4, [-1840, 450], 4)
    add(vae)

    branch_specs = [
        ("full_front", 101, 201, 301, 401, 0, 0, 768, 1152),
        ("full_profile", 102, 202, 302, 402, 1, 1, 768, 1152),
        ("full_back", 103, 203, 303, 403, 2, 2, 768, 1152),
        ("headshot", 104, 204, 304, 404, 3, 5, 1024, 1024),
        ("action_a", 105, 205, 305, 405, 4, 3, 768, 1152),
        ("action_b", 106, 206, 306, 406, 5, 4, 768, 1152),
        ("expression_sheet", 107, 207, 307, 407, 6, 6, 1536, 1024),
        ("detail_sheet", 108, 208, 308, 408, 7, 7, 1536, 1536),
    ]

    decoders: list[dict] = []
    for index, (_, text_id, latent_id, sampler_id, decode_id, _, _, width, height) in enumerate(branch_specs):
        col = index % 4
        row = index // 4
        base_x = -1300 + col * 560
        base_y = 40 + row * 980
        text = copy.deepcopy(templates[5])
        reset_node(text, text_id, [base_x, base_y], 10 + index * 4)
        text["size"] = [330, 300]
        text["widgets_values"] = ["", "", 1024]
        add(text)
        latent = copy.deepcopy(templates[6])
        reset_node(latent, latent_id, [base_x, base_y + 350], 11 + index * 4)
        latent["widgets_values"] = [width, height, 1]
        add(latent)
        sampler = copy.deepcopy(templates[7])
        reset_node(sampler, sampler_id, [base_x + 370, base_y], 12 + index * 4)
        sampler["widgets_values"] = [42 + index, "fixed", 20, 4, "euler", "simple", 1]
        add(sampler)
        decode = copy.deepcopy(templates[8])
        reset_node(decode, decode_id, [base_x + 370, base_y + 630], 13 + index * 4)
        add(decode)
        decoders.append(decode)

    composer = add(composer_node())
    preview = copy.deepcopy(templates[9])
    reset_node(preview, 501, [1120, 120], 50)
    preview["size"] = [760, 760]
    add(preview)
    save = copy.deepcopy(templates[10])
    reset_node(save, 502, [1120, 930], 51)
    save["size"] = [620, 760]
    save["widgets_values"] = ["角色卡_分项生成"]
    add(save)
    asset_preview = copy.deepcopy(templates[9])
    reset_node(asset_preview, 503, [620, 1100], 52)
    asset_preview["size"] = [460, 520]
    add(asset_preview)

    # Prompt, reference and model routing.
    for index, (_, text_id, latent_id, sampler_id, decode_id, prompt_slot, composer_slot, _, _) in enumerate(branch_specs):
        connect(1, prompt_slot, text_id, 3, "STRING")
        connect(1, 8, text_id, 4, "STRING")
        connect(100, 0, text_id, 1, "IMAGE")
        connect(3, 0, text_id, 0, "CLIP")
        connect(4, 0, text_id, 2, "VAE")
        connect(2, 0, sampler_id, 0, "MODEL")
        connect(text_id, 0, sampler_id, 1, "CONDITIONING")
        connect(text_id, 1, sampler_id, 2, "CONDITIONING")
        connect(latent_id, 0, sampler_id, 3, "LATENT")
        connect(sampler_id, 0, decode_id, 0, "LATENT")
        connect(4, 0, decode_id, 1, "VAE")
        connect(decode_id, 0, 500, composer_slot, "IMAGE")
    connect(1, 9, 500, 8, "STRING")
    connect(500, 0, 501, 0, "IMAGE")
    connect(500, 0, 502, 0, "IMAGE")
    connect(500, 1, 503, 0, "IMAGE")

    workflow = {
        "id": "e4b9c7d2-4c34-4a13-8a77-roleawarecardqwen21",
        "revision": 0,
        "last_node_id": 503,
        "last_link_id": len(links),
        "nodes": nodes,
        "links": links,
        "groups": [
            {"id": 1, "title": "角色输入与分项提示词", "bounding": [-3080, 20, 1120, 620], "color": "#3f789e", "flags": {}},
            {"id": 2, "title": "千问 Image 2.1 · 六路独立生成", "bounding": [-1880, 0, 2440, 1900], "color": "#8a6d3b", "flags": {}},
            {"id": 3, "title": "角色卡专业自动排版", "bounding": [600, 600, 1300, 1100], "color": "#3f789e", "flags": {}},
        ],
        "config": {},
        "extra": {"frontendVersion": "1.53.6"},
        "version": 0.4,
    }
    TARGET.write_text(json.dumps(workflow, ensure_ascii=False, indent=2), encoding="utf-8")
    print(TARGET)

    prompt_only = copy.deepcopy(workflow)
    prompt_only["id"] = "e4b9c7d2-4c34-4a13-8a77-roleawarepromptqwen21"
    prompt_only["nodes"] = [node for node in prompt_only["nodes"] if node["type"] != "LoadImage"]
    for node in prompt_only["nodes"]:
        if node["type"] == "TextEncodeQwenImage21":
            node["inputs"][1]["link"] = None
    prompt_only["links"] = [link for link in prompt_only["links"] if not (link[1] == 100 and link[2] == 0)]
    # Re-number links while preserving endpoints.
    remap = {}
    new_links = []
    for new_id, link in enumerate(prompt_only["links"], start=1):
        remap[link[0]] = new_id
        new_links.append([new_id, *link[1:]])
    prompt_only["links"] = new_links
    prompt_only["last_link_id"] = len(new_links)
    for node in prompt_only["nodes"]:
        for item in node.get("inputs", []):
            if item.get("link") in remap:
                item["link"] = remap[item["link"]]
        for item in node.get("outputs", []):
            if item.get("links"):
                item["links"] = [remap.get(value, value) for value in item["links"]]
    PROMPT_TARGET.write_text(json.dumps(prompt_only, ensure_ascii=False, indent=2), encoding="utf-8")
    print(PROMPT_TARGET)


if __name__ == "__main__":
    main()
