# -*- coding: utf-8 -*-
"""Local smoke test for template compilation and Pillow rendering."""

from __future__ import annotations

import json
import os
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import renderer
import templates


class FolderPaths:
    @staticmethod
    def get_input_directory():
        return os.environ.get("CCS_TEST_INPUT", str(Path.cwd()))


renderer.folder_paths = FolderPaths()


def main() -> None:
    image_name = os.environ.get(
        "CCS_TEST_IMAGE",
        "22785d770f0efdcf632f8e8a954a4b05032b63a4ac5a92e74da551fed6020ab2.jpg",
    )
    raw = {
        "templateId": "character_profile_12",
        "title": "顾辰",
        "subtitle": "角色设定集",
        "identity": "20岁男性角色，冷静克制。",
        "appearance": "黑色短发，灰蓝色眼睛，清瘦脸型。",
        "outfit": "深灰短袖与黑色长裤，白色运动鞋。",
        "style": "电影级角色设定，柔和棚拍光。",
        "showLabels": True,
        "slots": [],
        "library": [],
    }
    state, template = templates.normalise_state(json.dumps(raw, ensure_ascii=False), 2400, 1500)
    for index, slot in enumerate(state["slots"]):
        slot["image"] = image_name
        slot["fit"] = "cover" if index % 3 else "contain"
    state["library"] = [
        {
            "image": image_name,
            "subfolder": "",
            "name": "reference.jpg",
            "useForIdentity": True,
        }
    ]
    prompt = templates.compile_prompt(state, template)
    layout = renderer.render_layout(state, template)
    identity = renderer.render_identity_sheet(state, layout)
    output = Path("_render_test")
    output.mkdir(exist_ok=True)
    layout.save(output / "layout.png")
    identity.save(output / "identity.png")
    (output / "prompt.txt").write_text(prompt, encoding="utf-8")
    print(
        json.dumps(
            {
                "layout": layout.size,
                "identity": identity.size,
                "slots": len(state["slots"]),
                "prompt_chars": len(prompt),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
