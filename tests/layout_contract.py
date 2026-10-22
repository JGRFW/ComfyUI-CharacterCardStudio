# -*- coding: utf-8 -*-
"""Structural checks for all bundled character-card layouts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from templates import CHARACTER_TEMPLATE_OPTIONS, TEMPLATES, compile_prompt, normalise_state, one_click_state


def _overlap(left: dict, right: dict) -> float:
    x_overlap = max(0.0, min(left["x"] + left["w"], right["x"] + right["w"]) - max(left["x"], right["x"]))
    y_overlap = max(0.0, min(left["y"] + left["h"], right["y"] + right["h"]) - max(left["y"], right["y"]))
    return x_overlap * y_overlap


def main() -> None:
    assert len(TEMPLATES) == 9
    assert len({template["id"] for template in TEMPLATES}) == 9
    assert len(CHARACTER_TEMPLATE_OPTIONS) == 8

    for template in TEMPLATES:
        cells = template["cells"]
        assert cells, template["id"]
        assert len({cell["id"] for cell in cells}) == len(cells), template["id"]
        assert len({cell["label"] for cell in cells}) == len(cells), template["id"]
        assert all(cell["role"] in {"hero", "turnaround", "portrait", "expression", "detail", "scene_anchor", "scene_view", "scene_detail"} for cell in cells)
        assert all(0.0 <= cell["x"] <= 1.0 and 0.0 <= cell["y"] <= 1.0 for cell in cells)
        assert all(cell["x"] + cell["w"] <= 1.0001 and cell["y"] + cell["h"] <= 1.0001 for cell in cells)
        for index, cell in enumerate(cells):
            for other in cells[index + 1 :]:
                assert _overlap(cell, other) <= 0.000001, (template["id"], cell["id"], other["id"])

        state, resolved = normalise_state(
            {"templateId": template["id"], "title": "测试角色"},
            int(template["width"]),
            int(template["height"]),
        )
        prompt = compile_prompt(state, resolved)
        assert prompt.count("位置：") == len(cells), template["id"]
        assert "右半区只有3行" not in prompt, template["id"]
        assert f"严格保留输入图1中的 {len(cells)} 个矩形画格" in prompt
        assert "在画布顶部显示标题" not in prompt

    scene = next(template for template in TEMPLATES if template.get("kind") == "scene")
    scene_state, scene_resolved = normalise_state(
        {"templateId": scene["id"], "title": "测试场景"},
        int(scene["width"]),
        int(scene["height"]),
    )
    scene_prompt = compile_prompt(scene_state, scene_resolved)
    assert scene_prompt.count("位置：") == len(scene["cells"])
    assert "所有视角必须属于同一个场景" in scene_prompt
    assert "不新增与参考无关的人物或动物" in scene_prompt
    assert "所有人物画格必须是同一个人" not in scene_prompt
    assert "室内" not in scene_prompt
    scene_defaults = one_click_state(
        scene,
        "未命名角色",
        "原创角色，写实电影级",
        "电影级角色设定，干净背景",
        False,
    )
    assert scene_defaults["title"] == "未命名场景"
    assert scene_defaults["identity"].startswith("完整场景")
    assert scene_defaults["style"].startswith("写实场景")

    template = TEMPLATES[0]
    state, resolved = normalise_state(
        {
            "templateId": template["id"],
            "slots": [
                {
                    "id": "kept",
                    "cellId": "body_front",
                    "enabled": False,
                    "image": "body.png",
                }
            ],
        },
        int(template["width"]),
        int(template["height"]),
    )
    body = next(slot for slot in state["slots"] if slot["cellId"] == "body_front")
    assert body["enabled"] is False
    assert body["image"] == "body.png"
    assert body["label"] == "正面全身"
    disabled_prompt = compile_prompt(state, resolved)
    assert disabled_prompt.count("位置：") == len(template["cells"]) - 1

    print(json.dumps({"templates": len(TEMPLATES), "cells": [len(item["cells"]) for item in TEMPLATES]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
